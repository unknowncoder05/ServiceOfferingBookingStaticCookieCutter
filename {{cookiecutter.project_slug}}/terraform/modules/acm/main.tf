# ACM Module - Wildcard SSL Certificate
# Automatically creates *.yerson.co certificate if ARNs not provided

# CloudFront certificate (must be in us-east-1)
resource "aws_acm_certificate" "cloudfront" {
  count = var.frontend_certificate_arn == "" && var.hosted_zone_name != "" ? 1 : 0

  provider          = aws.us-east-1
  domain_name       = var.hosted_zone_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.hosted_zone_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "${var.project_name}-cloudfront-cert"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# API Gateway certificate (regional)
resource "aws_acm_certificate" "api" {
  count = var.api_certificate_arn == "" && var.hosted_zone_name != "" && var.create_regional_cert ? 1 : 0

  domain_name       = var.hosted_zone_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.hosted_zone_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "${var.project_name}-api-cert"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Get Route53 hosted zone
data "aws_route53_zone" "main" {
  count = var.hosted_zone_name != "" ? 1 : 0
  name  = var.hosted_zone_name
}

# DNS validation records for CloudFront certificate
resource "aws_route53_record" "cloudfront_validation" {
  for_each = var.frontend_certificate_arn == "" && var.hosted_zone_name != "" ? {
    for dvo in aws_acm_certificate.cloudfront[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    } if dvo.domain_name != ""
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main[0].zone_id
}

# DNS validation records for API certificate
resource "aws_route53_record" "api_validation" {
  for_each = var.api_certificate_arn == "" && var.hosted_zone_name != "" && var.create_regional_cert ? {
    for dvo in aws_acm_certificate.api[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record   = dvo.resource_record_value
      type   = dvo.resource_record_type
    } if dvo.domain_name != ""
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main[0].zone_id
}

# Wait for CloudFront certificate validation
resource "aws_acm_certificate_validation" "cloudfront" {
  count = var.frontend_certificate_arn == "" && var.hosted_zone_name != "" ? 1 : 0

  provider                = aws.us-east-1
  certificate_arn         = aws_acm_certificate.cloudfront[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cloudfront_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}

# Wait for API certificate validation
resource "aws_acm_certificate_validation" "api" {
  count = var.api_certificate_arn == "" && var.hosted_zone_name != "" && var.create_regional_cert ? 1 : 0

  certificate_arn         = aws_acm_certificate.api[0].arn
  validation_record_fqdns = [for record in aws_route53_record.api_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}
