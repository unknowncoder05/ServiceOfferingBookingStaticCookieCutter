variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
}

variable "task_manager_function_name" {
  description = "Name of the task manager Lambda function"
  type        = string
}

variable "task_manager_invoke_arn" {
  description = "Invoke ARN of the task manager Lambda function"
  type        = string
}

variable "domain_name" {
  description = "Custom domain name for API Gateway (e.g., storyarchitect.yerson.co)"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ARN of ACM certificate for custom domain"
  type        = string
  default     = ""
}
