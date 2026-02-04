# Lambda Module - Task lifecycle management functions

# Archive Lambda function code for task manager
data "archive_file" "task_manager" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda_functions/task_manager"
  output_path = "${path.module}/../../lambda_functions/task_manager.zip"
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Lambda Execution Role"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy for ECS and API Gateway access
resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.project_name}-lambda-policy-${var.environment}"
  description = "Policy for Lambda functions to manage ECS tasks and API Gateway integrations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:DescribeTasks",
          "ecs:ListTasks"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeNetworkInterfaces"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          var.ecs_task_role_arn,
          var.ecs_execution_role_arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "apigateway:GET",
          "apigateway:PATCH",
          "apigateway:UpdateIntegration"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_custom" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Task Manager Lambda Function
resource "aws_lambda_function" "task_manager" {
  filename         = data.archive_file.task_manager.output_path
  function_name    = "${var.project_name}-task-manager-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.lambda_handler"
  source_code_hash = data.archive_file.task_manager.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      ECS_CLUSTER_NAME       = var.ecs_cluster_name
      TASK_DEFINITION_FAMILY = var.task_definition_family
      SUBNET_IDS            = join(",", var.subnet_ids)
      SECURITY_GROUP_ID     = var.security_group_id
      TASK_LIFETIME_SECONDS = var.task_lifetime_seconds
      PROJECT_NAME          = var.project_name
      ENVIRONMENT           = var.environment
      API_GATEWAY_ID        = var.api_gateway_id
      API_INTEGRATION_ID    = var.api_integration_id
      BACKEND_PORT          = var.backend_port
      CLOUDWATCH_NAMESPACE  = var.cloudwatch_namespace
    }
  }

  tags = {
    Name        = "Task Manager Lambda"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Archive Lambda function code for task shutdown
data "archive_file" "task_shutdown" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda_functions/task_shutdown"
  output_path = "${path.module}/../../lambda_functions/task_shutdown.zip"
}

# Task Shutdown Lambda Function (triggered by CloudWatch alarm via SNS)
resource "aws_lambda_function" "task_shutdown" {
  filename         = data.archive_file.task_shutdown.output_path
  function_name    = "${var.project_name}-task-shutdown-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.lambda_handler"
  source_code_hash = data.archive_file.task_shutdown.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      ECS_CLUSTER_NAME       = var.ecs_cluster_name
      TASK_DEFINITION_FAMILY = var.task_definition_family
      PROJECT_NAME          = var.project_name
      ENVIRONMENT           = var.environment
    }
  }

  tags = {
    Name        = "Task Shutdown Lambda"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
