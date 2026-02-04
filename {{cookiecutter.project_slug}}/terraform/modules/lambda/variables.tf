variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "task_definition_family" {
  description = "Family name of the ECS task definition"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
}

variable "task_lifetime_seconds" {
  description = "Task lifetime in seconds"
  type        = number
  default     = 300
}

variable "api_gateway_id" {
  description = "ID of the API Gateway"
  type        = string
  default     = ""
}

variable "api_integration_id" {
  description = "ID of the API Gateway HTTP integration to update"
  type        = string
  default     = ""
}

variable "backend_port" {
  description = "Port on which the backend listens"
  type        = string
  default     = "8000"
}

variable "cloudwatch_namespace" {
  description = "CloudWatch namespace for custom metrics"
  type        = string
  default     = "StoryArchitect/Backend"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
