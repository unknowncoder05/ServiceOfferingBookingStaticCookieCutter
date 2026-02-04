variable "frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend hosting"
  type        = string
}

variable "database_bucket_name" {
  description = "Name of the S3 bucket for SQLite database storage"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "storyarchitect"
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
}

variable "cloudfront_oai_iam_arn" {
  description = "IAM ARN of CloudFront Origin Access Identity (for bucket policy)"
  type        = string
  default     = ""
}
