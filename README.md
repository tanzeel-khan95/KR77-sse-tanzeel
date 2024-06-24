# Currency Exchange Tracker

This project fetches exchange rates from the European Central Bank (ECB) and stores them in a DynamoDB table. It provides an API endpoint to retrieve these rates and calculate the percentage change compared to the previous day's rates.
Prerequisites

Before you begin, ensure you have the following installed:

    AWS CLI
    AWS CDK v2
    Python 3.8+
    Node.js
    Git

## Setup Instructions

1. Clone the Repository

```
git clone git@github.com:tanzeel-khan95/KR77-sse-tanzeel.git
cd KR77-sse-tanzeel/currency-exchange-tracker
```
   
2. Create and Activate a Virtual Environment

```
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```
  
3. Install Python Dependencies

```
cd lambda
pip install -r requirements.txt
cd ..
```

4. Configure AWS CLI

```
aws configure
```

5. Bootstrap AWS CDK

```
cdk bootstrap
```

6. Deploy the Stack

```
cdk deploy
```

7. Verify Deployment

    Once the deployment is complete, you will get the API Gateway endpoint URL in the output. Use this URL to interact with your API.

## Application Structure

    /lambda: Contains the AWS Lambda function code
    /currency-exchange-tracker: Contains the AWS CDK stack code
    requirements.txt: Lists Python dependencies for the Lambda function
    README.md: Documentation for the project

## Lambda Functions
1. Fetch and Store Exchange Rates

    This function runs daily, fetches the latest exchange rates from the ECB (https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), and stores them in the DynamoDB table.
2. Get Exchange Rates and Calculate Percentage Change

    This function is triggered by the API endpoint and retrieves the latest exchange rates from the DynamoDB table, calculates the percentage change from the previous day, and returns the result.

## CDK Stack

The CDK stack defines the following AWS resources:

- DynamoDB Table
- Lambda Functions
- API Gateway
- CloudWatch Events Rule

