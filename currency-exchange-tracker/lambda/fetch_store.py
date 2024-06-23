import requests
from decimal import Decimal
import xml.etree.ElementTree as ET
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    table_name = os.environ['TABLE_NAME']
    
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
    
    # Store data in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    with table.batch_writer() as batch:
        for currency, rate in exchange_rates.items():
            item = {
                'date': today,
                'currency': currency,
                'rate': rate
            }
            batch.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': 'Exchange rates stored successfully'
    }
