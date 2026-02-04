# IAM Deployment User Module
# Creates a dedicated user for deployment with scoped permissions

resource "aws_iam_user" "deployment" {
  name = "${var.project_name}-deployment-${var.environment}"
  path = "/service-accounts/"

  tags = {
    Name        = "${var.project_name}-deployment-user"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "Deployment automation"
  }
}

# Deployment policy with minimum required permissions
resource "aws_iam_user_policy" "deployment" {
  name = "${var.project_name}-deployment-policy"
  user = aws_iam_user.deployment.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # S3 - Frontend bucket
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:PutObjectAcl"
        ]
        Resource = [
          var.frontend_bucket_arn,
          "${var.frontend_bucket_arn}/*"
        ]
      },
      # S3 - Database bucket (read-only for backup)
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.database_bucket_arn,
          "${var.database_bucket_arn}/*"
        ]
      },
      # CloudFront - Invalidations
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
          "cloudfront:ListInvalidations",
          "cloudfront:GetDistribution"
        ]
        Resource = var.cloudfront_distribution_arn
      },
      # ECR - Push images
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:DescribeImages",
          "ecr:ListImages"
        ]
        Resource = var.ecr_repository_arn
      },
      # CloudWatch Logs - Read-only for debugging (optional)
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "logs:FilterLogEvents",
          "logs:StartQuery",
          "logs:StopQuery",
          "logs:GetQueryResults"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${var.project_name}-*"
        ]
      },
      # ECS - Read-only for task status (optional)
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeClusters",
          "ecs:DescribeTasks",
          "ecs:ListTasks",
          "ecs:DescribeTaskDefinition"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = var.aws_region
          }
        }
      }
    ]
  })
}

# Create access key for programmatic access
resource "aws_iam_access_key" "deployment" {
  count = var.create_access_key ? 1 : 0
  user  = aws_iam_user.deployment.name
}

# Store access key in SSM Parameter Store (encrypted)
resource "aws_ssm_parameter" "access_key_id" {
  count = var.create_access_key ? 1 : 0

  name        = "/${var.project_name}/${var.environment}/deployment/access-key-id"
  description = "Deployment user access key ID"
  type        = "String"
  value       = aws_iam_access_key.deployment[0].id

  tags = {
    Name        = "${var.project_name}-deployment-key-id"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ssm_parameter" "secret_access_key" {
  count = var.create_access_key ? 1 : 0

  name        = "/${var.project_name}/${var.environment}/deployment/secret-access-key"
  description = "Deployment user secret access key"
  type        = "SecureString"
  value       = aws_iam_access_key.deployment[0].secret

  tags = {
    Name        = "${var.project_name}-deployment-secret"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
