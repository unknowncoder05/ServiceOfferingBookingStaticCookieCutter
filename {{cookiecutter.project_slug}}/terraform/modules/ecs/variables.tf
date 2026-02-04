variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for ECS tasks"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks"
  type        = list(string)
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "database_bucket_id" {
  description = "ID of the S3 bucket storing the database"
  type        = string
}

variable "database_access_policy_arn" {
  description = "ARN of the IAM policy for database access"
  type        = string
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = string
  default     = "512"
}

variable "task_memory" {
  description = "Memory for the ECS task"
  type        = string
  default     = "1024"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables to pass to the container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secrets to pass to the container (will be stored in Secrets Manager)"
  type        = map(string)
  default     = {}
  sensitive   = true
}
