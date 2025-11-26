# Operations

Guide for maintaining this project

## Monitoring

Metrics like invocations, errors, and duration are available in AWS CloudWatch.

View Lambda functions in the [AWS Lambda Console](https://console.aws.amazon.com/lambda/home?region=us-east-1).

## Logging

CloudWatch Logs are available for all Lambda functions. 
The logs can be viewed in the [AWS CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups).

The `LOG_LEVEL` environment variable is set per Lambda function in `infrastructure/main.tf` and controls the verbosity of the logs.

## Terraform State Management

Terraform state is stored remotely in S3:
- **Bucket**: `767398000173-us-east-1-tfstate-product`
- **Key**: `serverless-aws-fec-data-collectionor.tfstate`
- **Lock Table**: `tf-locktable-product`

**Important**: Always run Terraform from the `infrastructure/` directory. The remote backend ensures state is shared and locked to prevent conflicts.

## Deployment Process

1. Make changes to code in `lambdas/src/` or infrastructure in `infrastructure/main.tf`
2. Review changes: `cd infrastructure && make plan`
3. Apply changes: `cd infrastructure && make apply`
4. Monitor in CloudWatch for any issues

## Troubleshooting

- **State lock errors**: Another Terraform operation may be in progress. Wait or check the DynamoDB lock table.
- **Permission errors**: Ensure you're authenticated to account `767398000173` and the assume role has proper permissions.
- **Lambda errors**: Check CloudWatch Logs for the specific function to see error details. 
