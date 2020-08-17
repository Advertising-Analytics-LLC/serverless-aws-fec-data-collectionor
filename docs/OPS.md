# Operations
Guide for maintaining this project

## Monitoring
Metrics like invocations, errors, and duration are available on the [AWS Lambda App Console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/applications/serverless-aws-python3-fec-datasync-dev?tab=monitoring).


## Logging

CloudWatch Logs are available for all the functions. 
The logs can be viewed [from the Lambda App Console](https://console.aws.amazon.com/lambda/home?region=us-east-1#/applications/serverless-aws-python3-fec-datasync-dev)
The `LOG_LEVEL` is set in `serverless.yml` and controls the verbosity of the logs. 
