output "api_id" {
  description = "ID of the API Gateway"
  value       = aws_apigatewayv2_api.main.id
}

output "api_endpoint" {
  description = "Default endpoint URL of the API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "api_url" {
  description = "Full URL to the API Gateway stage"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/${var.environment}"
}

output "custom_domain_name" {
  description = "Custom domain name (if configured)"
  value       = var.domain_name != "" ? aws_apigatewayv2_domain_name.main[0].domain_name : ""
}

output "custom_domain_target" {
  description = "Target domain name for Route53 record"
  value       = var.domain_name != "" ? aws_apigatewayv2_domain_name.main[0].domain_name_configuration[0].target_domain_name : ""
}

output "backend_integration_id" {
  description = "ID of the HTTP integration for backend proxy"
  value       = aws_apigatewayv2_integration.backend_proxy.id
}

output "custom_domain_hosted_zone_id" {
  description = "Hosted Zone ID for the custom domain (for Route53 alias)"
  value       = var.domain_name != "" ? aws_apigatewayv2_domain_name.main[0].domain_name_configuration[0].hosted_zone_id : ""
}
