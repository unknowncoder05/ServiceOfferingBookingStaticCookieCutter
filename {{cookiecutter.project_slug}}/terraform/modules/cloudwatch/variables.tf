# CloudWatch Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (prod, dev, staging)"
  type        = string
}

variable "cloudwatch_namespace" {
  description = "CloudWatch namespace for custom metrics"
  type        = string
  default     = "StoryArchitect/Backend"
}

variable "task_shutdown_lambda_arn" {
  description = "ARN of the Lambda function to invoke on inactivity"
  type        = string
}

variable "task_shutdown_lambda_name" {
  description = "Name of the Lambda function to invoke on inactivity"
  type        = string
}

variable "inactivity_timeout_minutes" {
  description = "Minutes of inactivity before triggering alarm (X)"
  type        = number
  default     = 10
}

variable "alarm_period_seconds" {
  description = "Period for CloudWatch alarm evaluation (should match inactivity timeout)"
  type        = number
  default     = 600  # 10 minutes
}

variable "evaluation_periods" {
  description = "Number of periods to evaluate (1 means check once per period)"
  type        = number
  default     = 1
}
