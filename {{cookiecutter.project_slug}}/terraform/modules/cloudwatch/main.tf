# CloudWatch Module - Monitoring and alarms for backend inactivity

# SNS Topic for alarm notifications
resource "aws_sns_topic" "backend_inactivity" {
  name = "${var.project_name}-backend-inactivity-${var.environment}"

  tags = {
    Name        = "Backend Inactivity Notifications"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# SNS Topic Subscription for task shutdown Lambda
resource "aws_sns_topic_subscription" "task_shutdown" {
  topic_arn = aws_sns_topic.backend_inactivity.arn
  protocol  = "lambda"
  endpoint  = var.task_shutdown_lambda_arn
}

# Allow SNS to invoke the task shutdown Lambda
resource "aws_lambda_permission" "allow_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = var.task_shutdown_lambda_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.backend_inactivity.arn
}

# CloudWatch Alarm - Triggers when no activity for specified period
resource "aws_cloudwatch_metric_alarm" "backend_inactivity" {
  alarm_name          = "${var.project_name}-backend-inactivity-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.evaluation_periods
  metric_name         = "BackendActivity"
  namespace           = var.cloudwatch_namespace
  period              = var.alarm_period_seconds
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "breaching"  # Treat missing data as breaching (no activity = breach)

  alarm_description = "Triggers when backend has been inactive for ${var.inactivity_timeout_minutes} minutes"
  alarm_actions     = [aws_sns_topic.backend_inactivity.arn]

  dimensions = {
    Environment = var.environment
    Project     = var.project_name
  }

  tags = {
    Name        = "Backend Inactivity Alarm"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# CloudWatch Log Group for task shutdown Lambda
resource "aws_cloudwatch_log_group" "task_shutdown_logs" {
  name              = "/aws/lambda/${var.task_shutdown_lambda_name}"
  retention_in_days = 7

  tags = {
    Name        = "Task Shutdown Lambda Logs"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
