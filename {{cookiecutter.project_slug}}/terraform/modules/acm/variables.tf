variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
}

variable "hosted_zone_name" {
  description = "Route53 hosted zone name (e.g., yerson.co)"
  type        = string
}

variable "frontend_certificate_arn" {
  description = "Existing CloudFront certificate ARN (leave empty to create new)"
  type        = string
  default     = ""
}

variable "api_certificate_arn" {
  description = "Existing API Gateway certificate ARN (leave empty to create new)"
  type        = string
  default     = ""
}

variable "create_regional_cert" {
  description = "Create separate certificate for API Gateway (if different region from us-east-1)"
  type        = bool
  default     = false
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}
