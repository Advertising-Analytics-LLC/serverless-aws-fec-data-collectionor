# Terraform Infrastructure

This directory contains Terraform configuration for deploying the FEC data collection infrastructure to AWS.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Docker (for Lambda packaging with Python dependencies)
- Access to AWS account `767398000173` (for Terraform backend)
- Permission to assume role in account `648881544937` (where resources are created)

## Remote Backend

Terraform uses a remote S3 backend for state management:

- **Backend Account**: `767398000173`
- **S3 Bucket**: `767398000173-us-east-1-tfstate-product`
- **State Key**: `serverless-aws-fec-data-collectionor.tfstate`
- **DynamoDB Lock Table**: `tf-locktable-product`
- **Region**: `us-east-1`

**Important**: You must be authenticated to account `767398000173` to run Terraform commands.

## Assume Role Configuration

Terraform assumes a role in the target account where resources are created:

- **Target Account**: `648881544937`
- **Role ARN**: `arn:aws:iam::648881544937:role/Terraform`
- **Session Name**: `terraform-workspace-production`
- **External ID**: `NG2f9P7btVBQgLJc`

This is configured in `main.tf` in the `provider "aws"` block.

## Quick Start

1. **Authenticate to AWS**:

2. **Navigate to infrastructure directory**:
   ```bash
   cd infrastructure
   ```

3. **Initialize Terraform** (configures remote backend):
   ```bash
   make init
   ```

4. **Configure variables** (optional):
   ```bash
   # Edit terraform.tfvars as needed
   ```

5. **Review the plan**:
   ```bash
   make plan
   ```

6. **Apply the configuration**:
   ```bash
   make apply
   ```


