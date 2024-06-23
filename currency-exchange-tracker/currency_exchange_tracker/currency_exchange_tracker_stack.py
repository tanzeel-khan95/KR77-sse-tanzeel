from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
)
from constructs import Construct

class CurrencyExchangeTrackerStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create DynamoDB table
        table = dynamodb.Table(
            self, "ExchangeRates",
            partition_key={"name": "date", "type": dynamodb.AttributeType.STRING},
            sort_key={"name": "currency", "type": dynamodb.AttributeType.STRING}
        )
        
        # Create Lambda function for fetching and storing exchange rates
        fetch_store_function = _lambda.Function(
            self, "FetchStoreExchangeRatesFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="fetch_store.lambda_handler",
            code=_lambda.Code.from_asset("lambda", 
                bundling={
                    'image': _lambda.Runtime.PYTHON_3_8.bundling_image,
                    'command': [
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
                    ]
                }
            ),
            environment={
                'TABLE_NAME': table.table_name,
                'TABLE_ARN': table.table_arn
            }
        )

        # Grant Lambda function permissions to access DynamoDB table
        table.grant_read_write_data(fetch_store_function)
        
        # Additional policy for batch write (BatchWriteItem)
        fetch_store_function.add_to_role_policy(iam.PolicyStatement(
            actions=["dynamodb:BatchWriteItem"],
            resources=[table.table_arn]
        ))

        # Create Lambda function for API endpoint
        api_function = _lambda.Function(
            self, "APIExchangeRatesFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="api_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda", 
                bundling={
                    'image': _lambda.Runtime.PYTHON_3_8.bundling_image,
                    'command': [
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
                    ]
                }
            ),
            environment={
                'TABLE_NAME': table.table_name,
                'TABLE_ARN': table.table_arn
            }
        )

        # Grant read permissions for API function
        table.grant_read_data(api_function)
        
        # Create API Gateway
        api = apigateway.LambdaRestApi(
            self, "exchange-rates-api",
            handler=api_function,
            proxy=False
        )
        
        # Add /rates resource
        rates = api.root.add_resource("rates")
        rates.add_method("GET")  # GET /rates

        # Add CloudWatch Event Rule to trigger fetch_store_function daily at midnight
        rule = events.Rule(
            self, "DailyTrigger",
            schedule=events.Schedule.cron(minute="0", hour="0")
        )
        rule.add_target(targets.LambdaFunction(fetch_store_function))
