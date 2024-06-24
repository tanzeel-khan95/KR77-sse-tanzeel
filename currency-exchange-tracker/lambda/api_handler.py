import json
import boto3
import os
from decimal import Decimal
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def lambda_handler(event, context):
    table_name = os.environ['TABLE_NAME']
    
    # Fetch current exchange rates
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    response = requests.get(url)
    
    # Parse the XML data
    root = ET.fromstring(response.content)
    namespace = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
    
    exchange_rates = {}
    for cube in root.findall(".//ns:Cube[@currency]", namespace):
        currency = cube.attrib['currency']
        rate = Decimal(cube.attrib['rate'])
        exchange_rates[currency] = rate
    
    # Fetch previous day's rates from DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('date').eq(yesterday)
    )
    
    previous_rates = {item['currency']: Decimal(item['rate']) for item in response['Items']}
    
    rates_with_change = {}
    for currency, rate in exchange_rates.items():
        previous_rate = previous_rates.get(currency, None)
        if previous_rate is not None:
            change_percent = ((rate - previous_rate) / previous_rate) * 100
            rates_with_change[currency] = {
                'rate': str(rate),  # Convert Decimal to string
                'change_percent': change_percent
            }
        else:
            rates_with_change[currency] = {
                'rate': str(rate),  # Convert Decimal to string
                'change_percent': None  # If no previous rate, change percent is None
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps(rates_with_change, default=decimal_default)
    }
