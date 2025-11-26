terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "stage" {
  description = "Deployment stage"
  type        = string
  default     = "dev"
}

variable "backfill" {
  description = "Reserved concurrency for backfill functions"
  type        = number
  default     = 0
}

variable "loader_concurrency" {
  description = "Reserved concurrency for loader functions"
  type        = number
  default     = 1
}

variable "message_retention_period" {
  description = "SQS message retention period in seconds"
  type        = number
  default     = 1209600 # 14 days
}

variable "redrive_count" {
  description = "Max receive count for redrive policy"
  type        = number
  default     = 5
}

variable "deployment_bucket_name" {
  description = "Base name for deployment bucket"
  type        = string
  default     = "serverless-deploymentbucket"
}

variable "copy_from_bucket_name" {
  description = "Base name for copy-from bucket"
  type        = string
  default     = "copy-from"
}

variable "redshift_copy_role" {
  description = "ARN of Redshift copy role"
  type        = string
  default     = "arn:aws:iam::648881544937:role/copyFromRedshiftRole"
}

locals {
  service_name                = "FEC-loader"
  deployment_bucket_full_name = "${var.deployment_bucket_name}-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"
  copy_from_bucket_full_name  = "${var.copy_from_bucket_name}-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"

  common_tags = {
    Owner     = "Rhythmic Engineering"
    Namespace = "aws-AdvertisingAnalytics"
    Env       = var.stage
    ManagedBy = "Terraform"
  }

  # Lambda source path - points to lambdas/src directory and requirements.txt
  lambda_source_path = [
    {
      path            = "${path.module}/../lambdas/"
      pip_requirements = "${path.module}/../requirements.txt"
    }
  ]
}

########################################
# CloudFormation Stack (Prerequisites)
########################################

resource "aws_cloudformation_stack" "prerequisites" {
  name         = "fec-datasync-resources"
  template_body = file("${path.module}/prerequisite-cloudformation-resources.yml")

  parameters = {
    MessageRetentionPeriod      = var.message_retention_period
    CopyFromBucketName          = var.copy_from_bucket_name
    DeploymentBucketName        = var.deployment_bucket_name
    CandidateSyncQueueName      = "candidate-sync-queue"
    CommitteeSyncQueueName      = "committee-sync-queue"
    FinancialSummaryQueueName   = "fec-financialsummary-queue"
    FilingSEQueueName           = "fec-se-queue"
    FilingSBQueueName           = "fec-sb-queue"
    FilingF1SQueueName          = "fec-f1s-queue"
    RSSFeedTopicName            = "fec-new-filing-rss-fanout"
    CandidateDeadLetterQueueName = "candidate-dead-letter-queue"
    CommitteeDeadLetterQueueName = "committee-dead-letter-queue"
    FilingDeadLetterQueueName    = "filing-dead-letter-queue"
    RedriveCount                = var.redrive_count
  }

  tags = local.common_tags

  lifecycle {
    # Ignore changes to outputs since they're managed by CloudFormation
    ignore_changes = [outputs]
  }
}

# Data source to get stack outputs (for referencing in other resources)
data "aws_cloudformation_stack" "prerequisites" {
  name = aws_cloudformation_stack.prerequisites.name
}

# Data sources for queues not in stack outputs
data "aws_sqs_queue" "results_q" {
  name = "fec-results-q"
}

########################################
# IAM Role for Lambda Functions
########################################

resource "aws_iam_role" "lambda" {
  name = "${local.service_name}-${var.stage}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

# CloudWatch Logs permissions
resource "aws_iam_role_policy" "lambda_logs" {
  name = "${local.service_name}-${var.stage}-lambda-logs"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.service_name}-${var.stage}-*"
    }]
  })
}

# SSM Parameter Store permissions
resource "aws_iam_role_policy" "lambda_ssm" {
  name = "${local.service_name}-${var.stage}-lambda-ssm"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:DescribeParameters"
      ]
      Resource = [
        "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/global/openfec-api/api_key",
        "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/global/fec-schema/*"
      ]
    }]
  })
}

# SQS permissions
resource "aws_iam_role_policy" "lambda_sqs" {
  name = "${local.service_name}-${var.stage}-lambda-sqs"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl",
        "sqs:ReceiveMessage",
        "sqs:SendMessage"
      ]
      Resource = [
        data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueArn"],
        data.aws_cloudformation_stack.prerequisites.outputs["FilingSBQueueArn"],
        data.aws_cloudformation_stack.prerequisites.outputs["FinancialSummaryQueueArn"],
        data.aws_cloudformation_stack.prerequisites.outputs["FilingSEQueueArn"],
        data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueArn"],
        data.aws_cloudformation_stack.prerequisites.outputs["FilingF1SQueueArn"]
      ]
    }]
  })
}

# SNS permissions
resource "aws_iam_role_policy" "lambda_sns" {
  name = "${local.service_name}-${var.stage}-lambda-sns"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sns:Publish"
      ]
      Resource = [
        data.aws_cloudformation_stack.prerequisites.outputs["RSSFeedTopicArn"]
      ]
    }]
  })
}

# S3 permissions
resource "aws_iam_role_policy" "lambda_s3" {
  name = "${local.service_name}-${var.stage}-lambda-s3"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ]
      Resource = [
        data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketArn"],
        "${data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketArn"]}/*"
      ]
    }]
  })
}

# DynamoDB permissions
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "${local.service_name}-${var.stage}-lambda-dynamodb"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:*"
      ]
      Resource = "*"
    }]
  })
}

########################################
# Lambda Functions using terraform-aws-modules
########################################

module "lambda_get_db_stats" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-GetDBStats"
  description   = "Get database statistics"
  handler       = "src.get_db_stats.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_sync" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CandidateSync"
  description   = "Polls OpenFEC API (once) for candidates that have filed recently and sends the IDs to SQS"
  handler       = "src.CandidateSync.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_backfill" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CandidateBackfill"
  description   = "Backfills candidates queue"
  handler       = "src.CandidateSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 90

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_loader" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CandidateLoader"
  description   = "Triggered by SQS it receives Messages and writes candidate data to the DB"
  handler       = "src.CandidateLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 300

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_sync" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CommitteeSync"
  description   = "Polls OpenFEC API (once) for committees that have filed recently and sends the IDs to SQS"
  handler       = "src.CommitteSync.committeSync"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_backfill" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CommitteeBackfill"
  description   = "Backfills committee sync queue"
  handler       = "src.CommitteSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 90

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_loader" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-CommitteeLoader"
  description   = "Receives committee Ids from SQS, queries api for committee info, updates DB"
  handler       = "src.CommitteLoader.committeLoader"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_filing_sync" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FilingSync"
  description   = "Scrapes FEC RSS feed for recent filings, pushes the new filings to SNS and SQS"
  handler       = "src.FilingSync.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 180

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    RSS_SNS_TOPIC_ARN    = data.aws_cloudformation_stack.prerequisites.outputs["RSSFeedTopicArn"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_filing_backfill" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FilingBackfill"
  description   = "Crawls back in time over filings"
  handler       = "src.FilingSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    RSS_SNS_TOPIC_ARN    = data.aws_cloudformation_stack.prerequisites.outputs["RSSFeedTopicArn"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_financial_summary_loader" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FinancialSummaryLoader"
  description   = "Takes new filings from SQS, queries api, writes to DB"
  handler       = "src.FinancialSummaryLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["FinancialSummaryQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_fec_file_loader_sb" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSB"
  description   = "Gets FEC file url from SQS, downloads, parses for Schedule B filings, loads into DB"
  handler       = "src.FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    FILING_TYPE          = "SB"
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketName"]
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSBQueueName"]
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_fec_file_loader_se" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSE"
  description   = "Gets FEC file url from SQS, downloads, parses for Schedule E filings, loads into DB"
  handler       = "src.FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketName"]
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSEQueueName"]
    FILING_TYPE          = "SE"
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_fec_file_loader_supp" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 8.0"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSupp"
  description   = "Gets FEC file url from SQS, downloads, parses for Form 1 Supplemental Data, loads into DB"
  handler       = "src.FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = local.lambda_source_path
  build_in_docker = true

  # Docker build options to ensure correct platform for Lambda (linux/amd64)
  # This is critical for native extensions like cryptography's Rust bindings
  docker_additional_options = ["--platform", "linux/amd64"]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
  s3_prefix   = "${local.service_name}/${var.stage}/"

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = data.aws_sqs_queue.results_q.name
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketName"]
    SQS_QUEUE_NAME       = data.aws_cloudformation_stack.prerequisites.outputs["FilingF1SQueueName"]
    FILING_TYPE          = "F1S"
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

########################################
# EventBridge Rules (CloudWatch Events)
########################################

resource "aws_cloudwatch_event_rule" "get_db_stats" {
  name                = "${local.service_name}-${var.stage}-GetDBStats-schedule"
  description         = "Trigger GetDBStats every 60 minutes"
  schedule_expression = "rate(60 minutes)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "get_db_stats" {
  rule      = aws_cloudwatch_event_rule.get_db_stats.name
  target_id = "GetDBStatsTarget"
  arn       = module.lambda_get_db_stats.lambda_function_arn
}

resource "aws_lambda_permission" "get_db_stats" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_get_db_stats.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.get_db_stats.arn
}

resource "aws_cloudwatch_event_rule" "candidate_sync" {
  name                = "${local.service_name}-${var.stage}-CandidateSync-schedule"
  description         = "Trigger CandidateSync daily at 4 AM"
  schedule_expression = "cron(0 4 * * ? *)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "candidate_sync" {
  rule      = aws_cloudwatch_event_rule.candidate_sync.name
  target_id = "CandidateSyncTarget"
  arn       = module.lambda_candidate_sync.lambda_function_arn
}

resource "aws_lambda_permission" "candidate_sync" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_candidate_sync.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.candidate_sync.arn
}

resource "aws_cloudwatch_event_rule" "candidate_backfill" {
  name                = "${local.service_name}-${var.stage}-CandidateBackfill-schedule"
  description         = "Trigger CandidateBackfill every minute"
  schedule_expression = "rate(1 minute)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "candidate_backfill" {
  rule      = aws_cloudwatch_event_rule.candidate_backfill.name
  target_id = "CandidateBackfillTarget"
  arn       = module.lambda_candidate_backfill.lambda_function_arn
}

resource "aws_lambda_permission" "candidate_backfill" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_candidate_backfill.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.candidate_backfill.arn
}

resource "aws_cloudwatch_event_rule" "committee_sync" {
  name                = "${local.service_name}-${var.stage}-CommitteeSync-schedule"
  description         = "Trigger CommitteeSync daily at midnight"
  schedule_expression = "cron(0 0 * * ? *)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "committee_sync" {
  rule      = aws_cloudwatch_event_rule.committee_sync.name
  target_id = "CommitteeSyncTarget"
  arn       = module.lambda_committee_sync.lambda_function_arn
}

resource "aws_lambda_permission" "committee_sync" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_committee_sync.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.committee_sync.arn
}

resource "aws_cloudwatch_event_rule" "committee_backfill" {
  name                = "${local.service_name}-${var.stage}-CommitteeBackfill-schedule"
  description         = "Trigger CommitteeBackfill every minute"
  schedule_expression = "rate(1 minute)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "committee_backfill" {
  rule      = aws_cloudwatch_event_rule.committee_backfill.name
  target_id = "CommitteeBackfillTarget"
  arn       = module.lambda_committee_backfill.lambda_function_arn
}

resource "aws_lambda_permission" "committee_backfill" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_committee_backfill.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.committee_backfill.arn
}

resource "aws_cloudwatch_event_rule" "filing_sync" {
  name                = "${local.service_name}-${var.stage}-FilingSync-schedule"
  description         = "Trigger FilingSync daily at midnight"
  schedule_expression = "cron(0 0 * * ? *)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "filing_sync" {
  rule      = aws_cloudwatch_event_rule.filing_sync.name
  target_id = "FilingSyncTarget"
  arn       = module.lambda_filing_sync.lambda_function_arn
}

resource "aws_lambda_permission" "filing_sync" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_filing_sync.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.filing_sync.arn
}

resource "aws_cloudwatch_event_rule" "filing_backfill" {
  name                = "${local.service_name}-${var.stage}-FilingBackfill-schedule"
  description         = "Trigger FilingBackfill every minute"
  schedule_expression = "rate(1 minute)"

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "filing_backfill" {
  rule      = aws_cloudwatch_event_rule.filing_backfill.name
  target_id = "FilingBackfillTarget"
  arn       = module.lambda_filing_backfill.lambda_function_arn
}

resource "aws_lambda_permission" "filing_backfill" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_filing_backfill.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.filing_backfill.arn
}

########################################
# SQS Event Source Mappings
########################################

resource "aws_lambda_event_source_mapping" "candidate_loader" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueArn"]
  function_name    = module.lambda_candidate_loader.lambda_function_arn
  batch_size       = 10
}

resource "aws_lambda_event_source_mapping" "committee_loader" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueArn"]
  function_name    = module.lambda_committee_loader.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "financial_summary_loader" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["FinancialSummaryQueueArn"]
  function_name    = module.lambda_financial_summary_loader.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_sb" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["FilingSBQueueArn"]
  function_name    = module.lambda_fec_file_loader_sb.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_se" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["FilingSEQueueArn"]
  function_name    = module.lambda_fec_file_loader_se.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_supp" {
  event_source_arn = data.aws_cloudformation_stack.prerequisites.outputs["FilingF1SQueueArn"]
  function_name    = module.lambda_fec_file_loader_supp.lambda_function_arn
  batch_size       = 1
}

########################################
# Outputs
########################################

output "deployment_bucket_name" {
  description = "Name of the deployment bucket"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]
}

output "deployment_bucket_arn" {
  description = "ARN of the deployment bucket"
  value       = "arn:aws:s3:::${data.aws_cloudformation_stack.prerequisites.outputs["DeploymentBucketName"]}"
}

output "copy_from_bucket_name" {
  description = "Name of the copy-from bucket"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketName"]
}

output "copy_from_bucket_arn" {
  description = "ARN of the copy-from bucket"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CopyFromBucketArn"]
}

output "candidate_sync_queue_name" {
  description = "Name of the candidate sync queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueName"]
}

output "candidate_sync_queue_arn" {
  description = "ARN of the candidate sync queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CandidateSyncQueueArn"]
}

output "committee_sync_queue_name" {
  description = "Name of the committee sync queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueName"]
}

output "committee_sync_queue_arn" {
  description = "ARN of the committee sync queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["CommitteeSyncQueueArn"]
}

output "financial_summary_queue_name" {
  description = "Name of the financial summary queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FinancialSummaryQueueName"]
}

output "financial_summary_queue_arn" {
  description = "ARN of the financial summary queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FinancialSummaryQueueArn"]
}

output "filing_se_queue_name" {
  description = "Name of the filing SE queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSEQueueName"]
}

output "filing_se_queue_arn" {
  description = "ARN of the filing SE queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSEQueueArn"]
}

output "filing_sb_queue_name" {
  description = "Name of the filing SB queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSBQueueName"]
}

output "filing_sb_queue_arn" {
  description = "ARN of the filing SB queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingSBQueueArn"]
}

output "filing_f1s_queue_name" {
  description = "Name of the filing F1S queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingF1SQueueName"]
}

output "filing_f1s_queue_arn" {
  description = "ARN of the filing F1S queue"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["FilingF1SQueueArn"]
}

output "rss_feed_topic_arn" {
  description = "ARN of the RSS feed SNS topic"
  value       = data.aws_cloudformation_stack.prerequisites.outputs["RSSFeedTopicArn"]
}

output "lambda_function_arns" {
  description = "ARNs of all Lambda functions"
  value = {
    GetDBStats             = module.lambda_get_db_stats.lambda_function_arn
    CandidateSync          = module.lambda_candidate_sync.lambda_function_arn
    CandidateBackfill      = module.lambda_candidate_backfill.lambda_function_arn
    CandidateLoader        = module.lambda_candidate_loader.lambda_function_arn
    CommitteeSync          = module.lambda_committee_sync.lambda_function_arn
    CommitteeBackfill      = module.lambda_committee_backfill.lambda_function_arn
    CommitteeLoader        = module.lambda_committee_loader.lambda_function_arn
    FilingSync             = module.lambda_filing_sync.lambda_function_arn
    FilingBackfill         = module.lambda_filing_backfill.lambda_function_arn
    FinancialSummaryLoader = module.lambda_financial_summary_loader.lambda_function_arn
    FECFileLoaderSB        = module.lambda_fec_file_loader_sb.lambda_function_arn
    FECFileLoaderSE        = module.lambda_fec_file_loader_se.lambda_function_arn
    FECFileLoaderSupp      = module.lambda_fec_file_loader_supp.lambda_function_arn
  }
}

