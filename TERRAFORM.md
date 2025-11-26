# Terraform Infrastructure

This directory contains Terraform configuration for deploying the FEC data collection infrastructure to AWS.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Docker (for Lambda packaging with Python dependencies)

## Quick Start

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the plan:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

## Configuration

### Variables

Key variables can be set via:
- `terraform.tfvars` file (create from example below)
- Command line: `terraform apply -var="stage=prod"`
- Environment variables: `TF_VAR_stage=prod terraform apply`

### Example terraform.tfvars

```hcl
aws_region = "us-east-1"
stage      = "dev"
backfill   = 0
loader_concurrency = 1
```

## Resources Created

- **S3 Buckets**: Deployment bucket and copy-from bucket
- **SQS Queues**: 11 queues (6 main + 5 DLQs) for data processing
- **SNS Topic**: RSS feed fanout topic
- **Lambda Functions**: 13 functions for data collection and processing
- **IAM Roles**: Lambda execution role with necessary permissions
- **EventBridge Rules**: Scheduled triggers for Lambda functions
- **CloudWatch Log Groups**: Log retention for all Lambda functions

## Module Structure

The configuration uses the `terraform-aws-modules/lambda/aws` module which:
- Automatically packages Python code and dependencies
- Handles Docker-based builds for Python dependencies
- Manages Lambda function deployment

## Migration from Serverless Framework

This Terraform configuration replaces the previous Serverless Framework setup. Key differences:
- All infrastructure defined in Terraform
- Lambda packaging handled by terraform-aws-modules
- State management via Terraform state files

## Outputs

After deployment, view outputs with:
```bash
terraform output
```

Outputs include:
- S3 bucket names and ARNs
- SQS queue names and ARNs
- SNS topic ARN
- Lambda function ARNs

## Notes

- The `requirements.txt` file is automatically copied to `src/` during deployment for Lambda packaging
- Lambda functions use Python 3.11 runtime
- All resources are tagged with environment and ownership information

