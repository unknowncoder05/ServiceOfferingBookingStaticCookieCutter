output "frontend_fqdn" {
  description = "Fully qualified domain name for frontend"
  value       = var.frontend_subdomain != "" ? aws_route53_record.frontend[0].fqdn : ""
}

output "api_fqdn" {
  description = "Fully qualified domain name for API"
  value       = var.api_subdomain != "" && var.api_gateway_domain_target != "" && var.api_gateway_hosted_zone_id != "" ? aws_route53_record.api[0].fqdn : ""
}
