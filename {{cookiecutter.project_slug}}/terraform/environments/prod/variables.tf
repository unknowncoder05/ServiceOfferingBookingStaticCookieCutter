variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "{{ cookiecutter.aws_region }}"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "{{ cookiecutter.project_slug_dashed }}"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# S3 Configuration
variable "frontend_bucket_name" {
  description = "Name of S3 bucket for frontend hosting"
  type        = string
  default     = "{{ cookiecutter.project_slug_dashed }}-frontend-prod"
}

variable "database_bucket_name" {
  description = "Name of S3 bucket for database storage"
  type        = string
  default     = "{{ cookiecutter.project_slug_dashed }}-database-prod"
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "Name of ECR repository for backend images"
  type        = string
  default     = "{{ cookiecutter.project_slug_dashed }}-backend"
}

# ECS Configuration
variable "ecs_task_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "512"
}

variable "ecs_task_memory" {
  description = "Memory for ECS task (MB)"
  type        = string
  default     = "1024"
}

variable "task_lifetime_seconds" {
  description = "How long the task stays alive after last ping (seconds)"
  type        = number
  default     = 300  # 5 minutes
}

# Domain Configuration
variable "hosted_zone_name" {
  description = "Route53 hosted zone name (e.g., yerson.co)"
  type        = string
  default     = ""  # Set this to your domain
}

variable "frontend_subdomain" {
  description = "Subdomain for frontend (e.g., app.yerson.co)"
  type        = string
  default     = ""  # Set this to your desired subdomain
}

variable "api_subdomain" {
  description = "Subdomain for API (e.g., storyarchitect.yerson.co or api.yerson.co)"
  type        = string
  default     = ""  # Set this to your desired subdomain
}

variable "frontend_domain_aliases" {
  description = "List of domain aliases for CloudFront distribution"
  type        = list(string)
  default     = []  # e.g., ["app.yerson.co"]
}

variable "api_domain_name" {
  description = "Custom domain name for API Gateway"
  type        = string
  default     = ""  # e.g., "storyarchitect.yerson.co"
}

# Certificate Configuration
variable "frontend_certificate_arn" {
  description = "ARN of ACM certificate for CloudFront (must be in us-east-1)"
  type        = string
  default     = ""
}

variable "api_certificate_arn" {
  description = "ARN of ACM certificate for API Gateway (must be in same region as API)"
  type        = string
  default     = ""
}

# IAM Deployment User
variable "create_deployment_user" {
  description = "Create IAM user for deployment with access keys"
  type        = bool
  default     = true
}

# Backend Application Configuration
variable "backend_environment_variables" {
  description = "Additional environment variables for the backend container"
  type        = map(string)
  default     = {}
  # Example:
  # {
  #   "DEBUG" = "false"
  #   "LOG_LEVEL" = "INFO"
  # }
}

variable "backend_secrets" {
  description = "Secrets for the backend container (stored in Secrets Manager with KMS encryption)"
  type        = map(string)
  default     = {}
  sensitive   = true
  # Example:
  # {
  #   "DJANGO_SECRET_KEY" = "your-secret-key-here"
  #   "DATABASE_PASSWORD" = "your-db-password"
  #   "OPENAI_API_KEY" = "your-openai-key"
  # }
}

# CloudWatch Configuration
variable "cloudwatch_namespace" {
  description = "CloudWatch namespace for custom metrics"
  type        = string
  default     = "{{ cookiecutter.project_name }}/Backend"
}

variable "inactivity_timeout_minutes" {
  description = "Minutes of inactivity before shutting down backend (X = 10 minutes)"
  type        = number
  default     = 10
}

variable "ping_frequency_seconds" {
  description = "Frequency for frontend to ping backend (Y = 5 minutes = 300 seconds)"
  type        = number
  default     = 300  # 5 minutes
}

variable "backend_port" {
  description = "Port on which the backend server listens"
  type        = string
  default     = "8000"
}
