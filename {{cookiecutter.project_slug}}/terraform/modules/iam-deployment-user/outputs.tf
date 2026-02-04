output "user_name" {
  description = "IAM username for deployment"
  value       = aws_iam_user.deployment.name
}

output "user_arn" {
  description = "ARN of the deployment user"
  value       = aws_iam_user.deployment.arn
}

output "access_key_id" {
  description = "Access key ID (only available immediately after creation)"
  value       = var.create_access_key ? aws_iam_access_key.deployment[0].id : null
  sensitive   = true
}

output "secret_access_key" {
  description = "Secret access key (only available immediately after creation)"
  value       = var.create_access_key ? aws_iam_access_key.deployment[0].secret : null
  sensitive   = true
}

output "ssm_access_key_parameter" {
  description = "SSM parameter name for access key ID"
  value       = var.create_access_key ? aws_ssm_parameter.access_key_id[0].name : null
}

output "ssm_secret_key_parameter" {
  description = "SSM parameter name for secret access key"
  value       = var.create_access_key ? aws_ssm_parameter.secret_access_key[0].name : null
}
