terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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
  service_name                = "serverless-aws-python3-fec-datasync"
  deployment_bucket_full_name = "${var.deployment_bucket_name}-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"
  copy_from_bucket_full_name  = "${var.copy_from_bucket_name}-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"

  common_tags = {
    Owner     = "Rhythmic Engineering"
    Namespace = "aws-AdvertisingAnalytics"
    Env       = var.stage
    ManagedBy = "Terraform"
  }
}

########################################
# S3 Buckets
########################################

resource "aws_s3_bucket" "deployment" {
  bucket = local.deployment_bucket_full_name

  tags = merge(local.common_tags, {
    Name = var.deployment_bucket_name
  })
}

resource "aws_s3_bucket_versioning" "deployment" {
  bucket = aws_s3_bucket.deployment.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "deployment" {
  bucket = aws_s3_bucket.deployment.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "deployment" {
  bucket = aws_s3_bucket.deployment.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "copy_from" {
  bucket = local.copy_from_bucket_full_name

  tags = merge(local.common_tags, {
    Name = var.copy_from_bucket_name
  })
}

resource "aws_s3_bucket_versioning" "copy_from" {
  bucket = aws_s3_bucket.copy_from.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "copy_from" {
  bucket = aws_s3_bucket.copy_from.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "copy_from" {
  bucket = aws_s3_bucket.copy_from.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

########################################
# SQS Queues
########################################

# Super DLQ (ultimate dead letter queue)
resource "aws_sqs_queue" "super_dlq" {
  name                      = "super-dlq"
  message_retention_seconds = var.message_retention_period

  tags = local.common_tags
}

# Results queue and DLQ
resource "aws_sqs_queue" "results_dlq" {
  name                      = "fec-results-dlq"
  message_retention_seconds = var.message_retention_period

  tags = merge(local.common_tags, {
    Name = "fec-results-dlq"
  })
}

resource "aws_sqs_queue" "results_q" {
  name                       = "fec-results-q"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.results_dlq.arn
    maxReceiveCount     = 15
  })

  tags = merge(local.common_tags, {
    Name = "fec-results-q"
  })
}

# Candidate queues
resource "aws_sqs_queue" "candidate_dlq" {
  name                      = "candidate-dead-letter-queue"
  message_retention_seconds = var.message_retention_period

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "candidate-dead-letter-queue"
  })
}

resource "aws_sqs_queue" "candidate_sync" {
  name = "candidate-sync-queue"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.candidate_dlq.arn
    maxReceiveCount     = 15
  })

  tags = merge(local.common_tags, {
    Name = "candidate-sync-queue"
  })
}

# Committee queues
resource "aws_sqs_queue" "committee_dlq" {
  name                      = "committee-dead-letter-queue"
  message_retention_seconds = var.message_retention_period

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "committee-dead-letter-queue"
  })
}

resource "aws_sqs_queue" "committee_sync" {
  name                       = "committee-sync-queue"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.committee_dlq.arn
    maxReceiveCount     = 15
  })

  tags = merge(local.common_tags, {
    Name = "committee-sync-queue"
  })
}

# Financial Summary queues
resource "aws_sqs_queue" "financial_summary_dlq" {
  name                      = "financial-summary-dlq"
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })
}

resource "aws_sqs_queue" "financial_summary" {
  name                       = "fec-financialsummary-queue"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.financial_summary_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "fec-financialsummary-queue"
  })
}

# Filing SE queues
resource "aws_sqs_queue" "filing_se_dlq" {
  name                      = "filing-se-dlq"
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })
}

resource "aws_sqs_queue" "filing_se" {
  name                       = "fec-se-queue"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.filing_se_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "fec-se-queue"
  })
}

# Filing F1S queues
resource "aws_sqs_queue" "filing_f1s_dlq" {
  name                      = "filing-f1s-dlq"
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })
}

resource "aws_sqs_queue" "filing_f1s" {
  name                       = "fec-f1s-queue"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.filing_f1s_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "fec-f1s-queue"
  })
}

# Filing SB queues
resource "aws_sqs_queue" "filing_sb_dlq" {
  name                      = "filing-sb-dlq"
  message_retention_seconds = 1209600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.super_dlq.arn
    maxReceiveCount     = var.redrive_count
  })
}

resource "aws_sqs_queue" "filing_sb" {
  name                       = "fec-sb-queue"
  visibility_timeout_seconds = 5400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.filing_sb_dlq.arn
    maxReceiveCount     = var.redrive_count
  })

  tags = merge(local.common_tags, {
    Name = "fec-sb-queue"
  })
}

########################################
# SNS Topic
########################################

resource "aws_sns_topic" "rss_feed" {
  name         = "fec-new-filing-rss-fanout"
  display_name = "fec-new-filing-rss-fanout"

  tags = merge(local.common_tags, {
    Name = "fec-new-filing-rss-fanout"
  })
}

# SNS to SQS subscriptions
resource "aws_sns_topic_subscription" "rss_to_filing_se" {
  topic_arn = aws_sns_topic.rss_feed.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.filing_se.arn
}

resource "aws_sns_topic_subscription" "rss_to_financial_summary" {
  topic_arn = aws_sns_topic.rss_feed.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.financial_summary.arn
}

resource "aws_sns_topic_subscription" "rss_to_filing_f1s" {
  topic_arn = aws_sns_topic.rss_feed.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.filing_f1s.arn
}

resource "aws_sns_topic_subscription" "rss_to_filing_sb" {
  topic_arn = aws_sns_topic.rss_feed.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.filing_sb.arn
}

# SQS Queue Policies for SNS
resource "aws_sqs_queue_policy" "rss_fanout_financial_summary" {
  queue_url = aws_sqs_queue.financial_summary.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.financial_summary.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_sns_topic.rss_feed.arn
        }
      }
    }]
  })
}

resource "aws_sqs_queue_policy" "rss_fanout_filing_se" {
  queue_url = aws_sqs_queue.filing_se.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.filing_se.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_sns_topic.rss_feed.arn
        }
      }
    }]
  })
}

resource "aws_sqs_queue_policy" "rss_fanout_filing_sb" {
  queue_url = aws_sqs_queue.filing_sb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.filing_sb.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_sns_topic.rss_feed.arn
        }
      }
    }]
  })
}

resource "aws_sqs_queue_policy" "rss_fanout_filing_f1s" {
  queue_url = aws_sqs_queue.filing_f1s.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.filing_f1s.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_sns_topic.rss_feed.arn
        }
      }
    }]
  })
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
        aws_sqs_queue.candidate_sync.arn,
        aws_sqs_queue.filing_sb.arn,
        aws_sqs_queue.financial_summary.arn,
        aws_sqs_queue.filing_se.arn,
        aws_sqs_queue.committee_sync.arn,
        aws_sqs_queue.filing_f1s.arn
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
        aws_sns_topic.rss_feed.arn
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
        aws_s3_bucket.copy_from.arn,
        "${aws_s3_bucket.copy_from.arn}/*"
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
# CloudWatch Log Groups
########################################

resource "aws_cloudwatch_log_group" "lambda" {
  for_each = toset([
    "GetDBStats",
    "CandidateSync",
    "CandidateBackfill",
    "CandidateLoader",
    "CommitteeSync",
    "CommitteeBackfill",
    "CommitteeLoader",
    "FilingSync",
    "FilingBackfill",
    "FinancialSummaryLoader",
    "FECFileLoaderSB",
    "FECFileLoaderSE",
    "FECFileLoaderSupp"
  ])

  name              = "/aws/lambda/${local.service_name}-${var.stage}-${each.key}"
  retention_in_days = 14

  tags = local.common_tags
}

########################################
# Copy requirements.txt to src/ for Lambda packaging
########################################

resource "null_resource" "copy_requirements" {
  triggers = {
    requirements_hash = filemd5("${path.module}/requirements.txt")
  }

  provisioner "local-exec" {
    command = "cp ${path.module}/requirements.txt ${path.module}/src/requirements.txt"
  }
}

########################################
# Lambda Functions using terraform-aws-modules
########################################

module "lambda_get_db_stats" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-GetDBStats"
  description   = "Get database statistics"
  handler       = "get_db_stats.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  # Store deployment package on S3 (required when package > 50MB)
  store_on_s3 = true
  s3_bucket   = "serverless-deploymentbucket-us-east-1-648881544937"
  s3_prefix   = "${var.stage}/"

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_sync" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CandidateSync"
  description   = "Polls OpenFEC API (once) for candidates that have filed recently and sends the IDs to SQS"
  handler       = "CandidateSync.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.candidate_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_backfill" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CandidateBackfill"
  description   = "Backfills candidates queue"
  handler       = "CandidateSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 90

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.candidate_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_candidate_loader" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CandidateLoader"
  description   = "Triggered by SQS it receives Messages and writes candidate data to the DB"
  handler       = "CandidateLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 300

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.candidate_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_sync" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CommitteeSync"
  description   = "Polls OpenFEC API (once) for committees that have filed recently and sends the IDs to SQS"
  handler       = "CommitteSync.committeSync"
  runtime       = "python3.11"
  timeout       = 30

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.committee_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_backfill" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CommitteeBackfill"
  description   = "Backfills committee sync queue"
  handler       = "CommitteSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 90

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.committee_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_committee_loader" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-CommitteeLoader"
  description   = "Receives committee Ids from SQS, queries api for committee info, updates DB"
  handler       = "CommitteLoader.committeLoader"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.committee_sync.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_filing_sync" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FilingSync"
  description   = "Scrapes FEC RSS feed for recent filings, pushes the new filings to SNS and SQS"
  handler       = "FilingSync.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 180

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = 1

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    RSS_SNS_TOPIC_ARN    = aws_sns_topic.rss_feed.arn
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_filing_backfill" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FilingBackfill"
  description   = "Crawls back in time over filings"
  handler       = "FilingSync.lambdaBackfillHandler"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.backfill

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    RSS_SNS_TOPIC_ARN    = aws_sns_topic.rss_feed.arn
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_financial_summary_loader" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FinancialSummaryLoader"
  description   = "Takes new filings from SQS, queries api, writes to DB"
  handler       = "FinancialSummaryLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    SQS_QUEUE_NAME       = aws_sqs_queue.financial_summary.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_fec_file_loader_sb" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSB"
  description   = "Gets FEC file url from SQS, downloads, parses for Schedule B filings, loads into DB"
  handler       = "FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    FILING_TYPE          = "SB"
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = aws_s3_bucket.copy_from.id
    SQS_QUEUE_NAME       = aws_sqs_queue.filing_sb.name
  }

  cloudwatch_logs_retention_in_days = 14

  attach_policies          = false
  attach_policy_statements = false

  create_role = false
  lambda_role = aws_iam_role.lambda.arn

  tags = local.common_tags
}

module "lambda_fec_file_loader_se" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSE"
  description   = "Gets FEC file url from SQS, downloads, parses for Schedule E filings, loads into DB"
  handler       = "FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = aws_s3_bucket.copy_from.id
    SQS_QUEUE_NAME       = aws_sqs_queue.filing_se.name
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
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.service_name}-${var.stage}-FECFileLoaderSupp"
  description   = "Gets FEC file url from SQS, downloads, parses for Form 1 Supplemental Data, loads into DB"
  handler       = "FECFileLoader.lambdaHandler"
  runtime       = "python3.11"
  timeout       = 900
  memory_size   = 3008

  source_path     = "${path.module}/src"
  build_in_docker = true

  depends_on = [null_resource.copy_requirements]

  reserved_concurrent_executions = var.loader_concurrency

  environment_variables = {
    API_KEY              = "/global/openfec-api/api_key"
    LOG_LEVEL            = "DEBUG"
    ERROR_SQS_QUEUE_NAME = aws_sqs_queue.results_q.name
    REDSHIFT_COPY_ROLE   = var.redshift_copy_role
    S3_BUCKET_NAME       = aws_s3_bucket.copy_from.id
    SQS_QUEUE_NAME       = aws_sqs_queue.filing_f1s.name
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
  event_source_arn = aws_sqs_queue.candidate_sync.arn
  function_name    = module.lambda_candidate_loader.lambda_function_arn
  batch_size       = 10
}

resource "aws_lambda_event_source_mapping" "committee_loader" {
  event_source_arn = aws_sqs_queue.committee_sync.arn
  function_name    = module.lambda_committee_loader.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "financial_summary_loader" {
  event_source_arn = aws_sqs_queue.financial_summary.arn
  function_name    = module.lambda_financial_summary_loader.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_sb" {
  event_source_arn = aws_sqs_queue.filing_sb.arn
  function_name    = module.lambda_fec_file_loader_sb.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_se" {
  event_source_arn = aws_sqs_queue.filing_se.arn
  function_name    = module.lambda_fec_file_loader_se.lambda_function_arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "fec_file_loader_supp" {
  event_source_arn = aws_sqs_queue.filing_f1s.arn
  function_name    = module.lambda_fec_file_loader_supp.lambda_function_arn
  batch_size       = 1
}

########################################
# Outputs
########################################

output "deployment_bucket_name" {
  description = "Name of the deployment bucket"
  value       = aws_s3_bucket.deployment.id
}

output "deployment_bucket_arn" {
  description = "ARN of the deployment bucket"
  value       = aws_s3_bucket.deployment.arn
}

output "copy_from_bucket_name" {
  description = "Name of the copy-from bucket"
  value       = aws_s3_bucket.copy_from.id
}

output "copy_from_bucket_arn" {
  description = "ARN of the copy-from bucket"
  value       = aws_s3_bucket.copy_from.arn
}

output "candidate_sync_queue_name" {
  description = "Name of the candidate sync queue"
  value       = aws_sqs_queue.candidate_sync.name
}

output "candidate_sync_queue_arn" {
  description = "ARN of the candidate sync queue"
  value       = aws_sqs_queue.candidate_sync.arn
}

output "committee_sync_queue_name" {
  description = "Name of the committee sync queue"
  value       = aws_sqs_queue.committee_sync.name
}

output "committee_sync_queue_arn" {
  description = "ARN of the committee sync queue"
  value       = aws_sqs_queue.committee_sync.arn
}

output "financial_summary_queue_name" {
  description = "Name of the financial summary queue"
  value       = aws_sqs_queue.financial_summary.name
}

output "financial_summary_queue_arn" {
  description = "ARN of the financial summary queue"
  value       = aws_sqs_queue.financial_summary.arn
}

output "filing_se_queue_name" {
  description = "Name of the filing SE queue"
  value       = aws_sqs_queue.filing_se.name
}

output "filing_se_queue_arn" {
  description = "ARN of the filing SE queue"
  value       = aws_sqs_queue.filing_se.arn
}

output "filing_sb_queue_name" {
  description = "Name of the filing SB queue"
  value       = aws_sqs_queue.filing_sb.name
}

output "filing_sb_queue_arn" {
  description = "ARN of the filing SB queue"
  value       = aws_sqs_queue.filing_sb.arn
}

output "filing_f1s_queue_name" {
  description = "Name of the filing F1S queue"
  value       = aws_sqs_queue.filing_f1s.name
}

output "filing_f1s_queue_arn" {
  description = "ARN of the filing F1S queue"
  value       = aws_sqs_queue.filing_f1s.arn
}

output "rss_feed_topic_arn" {
  description = "ARN of the RSS feed SNS topic"
  value       = aws_sns_topic.rss_feed.arn
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

