terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # Uncomment and configure for remote state
  # backend "s3" {
  #   bucket         = "ProjectManager-terraform-state"
  #   key            = "prod/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ProjectManager"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Provider alias for ACM certificates (CloudFront requires us-east-1)
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "ProjectManager"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Get default VPC and subnets (or create your own)
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ACM Module - SSL Certificates (creates *.yerson.co if none provided)
module "acm" {
  source = "../../modules/acm"

  providers = {
    aws.us-east-1 = aws.us-east-1
  }

  project_name              = var.project_name
  environment               = var.environment
  hosted_zone_name          = var.hosted_zone_name
  frontend_certificate_arn  = var.frontend_certificate_arn
  api_certificate_arn       = var.api_certificate_arn
  create_regional_cert      = var.aws_region != "us-east-1"  # Only create separate cert if not in us-east-1
  aws_region                = var.aws_region
}

# CloudFront Module - CDN for frontend (create first to get OAI)
module "cloudfront" {
  source = "../../modules/cloudfront"

  project_name        = var.project_name
  environment         = var.environment
  frontend_bucket_id  = var.frontend_bucket_name  # Bucket name, will be created by S3 module
  domain_aliases      = var.frontend_domain_aliases
  certificate_arn     = module.acm.cloudfront_certificate_arn
}

# S3 Module - Frontend and Database storage
module "s3" {
  source = "../../modules/s3"

  project_name            = var.project_name
  environment             = var.environment
  frontend_bucket_name    = var.frontend_bucket_name
  database_bucket_name    = var.database_bucket_name
  cloudfront_oai_iam_arn  = module.cloudfront.origin_access_identity_iam_arn
}

# ECR Module - Container registry
module "ecr" {
  source = "../../modules/ecr"

  repository_name = var.ecr_repository_name
  environment     = var.environment
}

# ECS Module - On-demand backend tasks
module "ecs" {
  source = "../../modules/ecs"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = data.aws_vpc.default.id
  subnet_ids                = data.aws_subnets.default.ids
  ecr_repository_url        = module.ecr.repository_url
  database_bucket_id        = module.s3.database_bucket_id
  database_access_policy_arn = module.s3.database_access_policy_arn
  task_cpu                  = var.ecs_task_cpu
  task_memory               = var.ecs_task_memory
  aws_region                = var.aws_region
  environment_variables     = merge(
    var.backend_environment_variables,
    {
      CLOUDWATCH_NAMESPACE     = var.cloudwatch_namespace
      PING_FREQUENCY_SECONDS   = tostring(var.ping_frequency_seconds)
      PROJECT_NAME             = var.project_name
      ENVIRONMENT              = var.environment
    }
  )
  secrets                   = var.backend_secrets
}

# Lambda Module - Task lifecycle management
module "lambda" {
  source = "../../modules/lambda"

  project_name             = var.project_name
  environment              = var.environment
  ecs_cluster_name         = module.ecs.cluster_name
  task_definition_family   = module.ecs.task_definition_family
  subnet_ids               = data.aws_subnets.default.ids
  security_group_id        = module.ecs.security_group_id
  ecs_task_role_arn        = module.ecs.task_role_arn
  ecs_execution_role_arn   = module.ecs.execution_role_arn
  task_lifetime_seconds    = var.task_lifetime_seconds
  api_gateway_id           = module.apigateway.api_id
  api_integration_id       = module.apigateway.backend_integration_id
  backend_port             = var.backend_port
  cloudwatch_namespace     = "ProjectManager/Backend"
  aws_region               = var.aws_region
}

# API Gateway Module - HTTP API
module "apigateway" {
  source = "../../modules/apigateway"

  project_name                = var.project_name
  environment                 = var.environment
  task_manager_function_name  = module.lambda.task_manager_function_name
  task_manager_invoke_arn     = module.lambda.task_manager_invoke_arn
  domain_name                 = var.api_domain_name
  certificate_arn             = module.acm.api_certificate_arn != "" ? module.acm.api_certificate_arn : module.acm.cloudfront_certificate_arn
}

# Route53 Module - DNS management
module "route53" {
  source = "../../modules/route53"

  hosted_zone_name            = var.hosted_zone_name
  frontend_subdomain          = var.frontend_subdomain
  api_subdomain               = var.api_subdomain
  cloudfront_domain_name      = module.cloudfront.distribution_domain_name
  cloudfront_hosted_zone_id   = module.cloudfront.distribution_hosted_zone_id
  api_gateway_domain_target   = module.apigateway.custom_domain_target
  api_gateway_hosted_zone_id  = module.apigateway.custom_domain_hosted_zone_id
  create_api_record           = var.api_domain_name != "" && var.api_subdomain != ""
}

# IAM Deployment User Module - Credentials for deployment scripts
module "deployment_user" {
  source = "../../modules/iam-deployment-user"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  frontend_bucket_arn         = module.s3.frontend_bucket_arn
  database_bucket_arn         = module.s3.database_bucket_arn
  cloudfront_distribution_arn = module.cloudfront.distribution_arn
  ecr_repository_arn          = module.ecr.repository_arn
  create_access_key           = var.create_deployment_user
}

# CloudWatch Module - Monitoring and alarms for backend inactivity
module "cloudwatch" {
  source = "../../modules/cloudwatch"

  project_name                = var.project_name
  environment                 = var.environment
  cloudwatch_namespace        = var.cloudwatch_namespace
  task_shutdown_lambda_arn    = module.lambda.task_shutdown_function_arn
  task_shutdown_lambda_name   = module.lambda.task_shutdown_function_name
  inactivity_timeout_minutes  = var.inactivity_timeout_minutes
  alarm_period_seconds        = var.inactivity_timeout_minutes * 60
  evaluation_periods          = 1
}
