# API Gateway Module - HTTP API for backend access

resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins     = ["https://storyarchitect.yerson.co"]
    allow_methods     = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
    allow_headers     = ["content-type", "authorization", "x-requested-with", "x-csrftoken", "accept", "origin", "user-agent", "cache-control", "pragma"]
    expose_headers    = ["content-type", "authorization", "x-csrftoken"]
    allow_credentials = true
    max_age           = 300
  }

  tags = {
    Name        = "StoryArchitect API Gateway"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Integration with Lambda (task manager) for /start endpoint
resource "aws_apigatewayv2_integration" "task_manager" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"

  integration_uri        = var.task_manager_invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# HTTP integration for backend proxy (updated dynamically by Lambda)
resource "aws_apigatewayv2_integration" "backend_proxy" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri    = "http://127.0.0.1:8000/{proxy}"  # Placeholder - Lambda will update this

  request_parameters = {
    "overwrite:path" = "$request.path"
  }
}

# Route for GET /start endpoint - triggers task manager Lambda
resource "aws_apigatewayv2_route" "start_get" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /start"

  target = "integrations/${aws_apigatewayv2_integration.task_manager.id}"
}

# Route for OPTIONS /start endpoint - CORS preflight (also handled by Lambda)
resource "aws_apigatewayv2_route" "start_options" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /start"

  target = "integrations/${aws_apigatewayv2_integration.task_manager.id}"
}

# Catch-all route - proxies all other requests to backend
resource "aws_apigatewayv2_route" "backend_proxy" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.backend_proxy.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = var.environment
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = {
    Name        = "API Gateway Stage"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "API Gateway Logs"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.task_manager_function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# Custom domain (if domain name is provided)
resource "aws_apigatewayv2_domain_name" "main" {
  count       = var.domain_name != "" ? 1 : 0
  domain_name = var.domain_name

  domain_name_configuration {
    certificate_arn = var.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = {
    Name        = "API Gateway Custom Domain"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# API Mapping for custom domain
resource "aws_apigatewayv2_api_mapping" "main" {
  count       = var.domain_name != "" ? 1 : 0
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main[0].id
  stage       = aws_apigatewayv2_stage.main.id
}
