########################################
# Lambda VPC attachment (ENGADI-110)
#
# Puts the FEC loader lambdas inside the saas-prod VPC (built by
# adimpact-software/aws-adimpact#39, ENGADI-108) so their egress leaves through
# a single known NAT gateway. That NAT's public IP is what ENGADI-109/111
# allowlist on the Redshift security group before the 0.0.0.0/0 rule comes off.
#
# Redshift lives in a different VPC with no peering to saas-prod, so lambda ->
# Redshift traffic goes NAT -> the cluster's public endpoint. A security-group
# reference is not possible until ENGADI-111 restores the cluster into
# saas-prod's database subnets.
########################################

data "aws_vpc" "saas_prod" {
  tags = {
    Name = "saas-prod"
  }
}

data "aws_subnets" "saas_prod_private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.saas_prod.id]
  }

  tags = {
    subnet_type = "private"
  }

  lifecycle {
    postcondition {
      condition     = length(self.ids) > 0
      error_message = "No subnet_type=private subnets found in the saas-prod VPC; refusing to build an empty vpc_config."
    }
  }
}

# Outbound only. The lambdas call OpenFEC, docquery.fec.gov,
# efilingapps.fec.gov, Redshift, DynamoDB, SQS, SNS and SSM; nothing ever
# connects inbound to a lambda ENI.
resource "aws_security_group" "fec_lambda" {
  name        = "${local.service_name}-${var.stage}-lambda"
  description = "FEC loader lambdas: egress only"
  vpc_id      = data.aws_vpc.saas_prod.id

  tags = merge(local.common_tags, {
    Name = "${local.service_name}-${var.stage}-lambda"
  })
}

resource "aws_vpc_security_group_egress_rule" "fec_lambda_all" {
  security_group_id = aws_security_group.fec_lambda.id
  description       = "All outbound"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# The lambda modules set create_role = false, which makes their
# attach_network_policy input a no-op, so the ENI permissions have to be
# attached to the shared role here.
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

locals {
  lambda_vpc_subnet_ids         = data.aws_subnets.saas_prod_private.ids
  lambda_vpc_security_group_ids = [aws_security_group.fec_lambda.id]
}
