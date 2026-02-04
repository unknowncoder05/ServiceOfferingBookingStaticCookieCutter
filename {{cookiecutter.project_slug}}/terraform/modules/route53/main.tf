# Route53 Module - DNS management

# Get existing hosted zone
data "aws_route53_zone" "main" {
  count = var.hosted_zone_name != "" ? 1 : 0
  name  = var.hosted_zone_name
}

# A record for frontend CloudFront distribution
resource "aws_route53_record" "frontend" {
  count   = var.frontend_subdomain != "" && var.hosted_zone_name != "" ? 1 : 0
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = var.frontend_subdomain
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

# A record for API Gateway
# Note: Only created if create_api_record is true (must be known at plan time)
resource "aws_route53_record" "api" {
  count   = var.create_api_record && var.api_subdomain != "" && var.hosted_zone_name != "" ? 1 : 0
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = var.api_subdomain
  type    = "A"

  alias {
    name                   = var.api_gateway_domain_target
    zone_id                = var.api_gateway_hosted_zone_id
    evaluate_target_health = false
  }
}
