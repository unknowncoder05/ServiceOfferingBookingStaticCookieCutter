# ACM Module Outputs

output "cloudfront_certificate_arn" {
  description = "ARN of CloudFront SSL certificate (us-east-1)"
  value       = var.frontend_certificate_arn != "" ? var.frontend_certificate_arn : try(aws_acm_certificate_validation.cloudfront[0].certificate_arn, "")
}

output "api_certificate_arn" {
  description = "ARN of API Gateway SSL certificate"
  value       = var.api_certificate_arn != "" ? var.api_certificate_arn : try(aws_acm_certificate_validation.api[0].certificate_arn, "")
}

output "cloudfront_certificate_id" {
  description = "ID of CloudFront SSL certificate"
  value       = try(aws_acm_certificate.cloudfront[0].id, "")
}

output "api_certificate_id" {
  description = "ID of API Gateway SSL certificate"
  value       = try(aws_acm_certificate.api[0].id, "")
}
