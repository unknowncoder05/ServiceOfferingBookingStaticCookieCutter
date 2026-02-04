output "frontend_bucket_name" {
  description = "Name of the frontend S3 bucket"
  value       = module.s3.frontend_bucket_id
}

output "database_bucket_name" {
  description = "Name of the database S3 bucket"
  value       = module.s3.database_bucket_id
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "task_definition_family" {
  description = "Family of the ECS task definition"
  value       = module.ecs.task_definition_family
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = module.apigateway.api_url
}

output "api_start_endpoint" {
  description = "Full URL to start backend task"
  value       = "${module.apigateway.api_url}/start"
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain" {
  description = "Domain name of CloudFront distribution"
  value       = module.cloudfront.distribution_domain_name
}

output "frontend_url" {
  description = "URL of the frontend application"
  value       = var.frontend_subdomain != "" ? "https://${var.frontend_subdomain}" : "https://${module.cloudfront.distribution_domain_name}"
}

output "task_manager_function_name" {
  description = "Name of the task manager Lambda function"
  value       = module.lambda.task_manager_function_name
}

# SSL Certificate Outputs
output "frontend_certificate_arn" {
  description = "ARN of the CloudFront SSL certificate (us-east-1)"
  value       = module.acm.cloudfront_certificate_arn
}

output "api_certificate_arn" {
  description = "ARN of the API Gateway SSL certificate"
  value       = module.acm.api_certificate_arn
}

output "certificates_created" {
  description = "Whether certificates were automatically created"
  value       = var.frontend_certificate_arn == "" && var.hosted_zone_name != "" ? "Yes - Wildcard certificate for *.${var.hosted_zone_name} created" : "No - Using provided certificate ARNs"
}

output "deployment_user_name" {
  description = "IAM username for deployment"
  value       = var.create_deployment_user ? module.deployment_user.user_name : "Not created"
}

output "deployment_access_key_id" {
  description = "Deployment user access key ID (sensitive, retrieve from SSM)"
  value       = var.create_deployment_user ? "Stored in SSM Parameter Store" : "Not created"
}

output "deployment_instructions" {
  description = "Instructions for completing the setup"
  value = <<-EOT

  ===================================
  ProjectManager Infrastructure Setup
  ===================================

  1. Frontend Deployment:
     - Bucket: ${module.s3.frontend_bucket_id}
     - CloudFront ID: ${module.cloudfront.distribution_id}
     - URL: ${var.frontend_subdomain != "" ? "https://${var.frontend_subdomain}" : "https://${module.cloudfront.distribution_domain_name}"}

  2. Backend Deployment:
     - ECR Repository: ${module.ecr.repository_url}
     - Push images: docker push ${module.ecr.repository_url}:latest

  3. API Gateway:
     - Start Endpoint: ${module.apigateway.api_url}/start
     - Custom Domain: ${var.api_domain_name != "" ? "https://${var.api_domain_name}/start" : "Not configured"}

  4. Database Storage:
     - S3 Bucket: ${module.s3.database_bucket_id}
     - SQLite file will be synced automatically

  5. Deployment Credentials:
     ${var.create_deployment_user ? "IAM User: ${module.deployment_user.user_name}\n     Retrieve credentials: ./scripts/get-deployment-credentials.sh" : "Deployment user not created - use your own AWS credentials"}

  6. Environment Variables (.env file):
     - AWS_REGION: ${var.aws_region}
     - FRONTEND_S3_BUCKET: ${module.s3.frontend_bucket_id}
     - CLOUDFRONT_DISTRIBUTION_ID: ${module.cloudfront.distribution_id}
     - DATABASE_S3_BUCKET: ${module.s3.database_bucket_id}
     - ECR_REPOSITORY: ${var.ecr_repository_name}

  7. Next Steps:
     - Get deployment credentials: ./scripts/get-deployment-credentials.sh
     - Configure .env file with values above
     - Push backend image: make deploy-backend
     - Deploy frontend: make deploy-frontend
     - Test API endpoint: curl ${module.apigateway.api_url}/start

  EOT
}
