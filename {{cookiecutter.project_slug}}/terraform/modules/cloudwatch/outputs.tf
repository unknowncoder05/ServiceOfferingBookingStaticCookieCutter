# CloudWatch Module Outputs

output "sns_topic_arn" {
  description = "ARN of the SNS topic for backend inactivity notifications"
  value       = aws_sns_topic.backend_inactivity.arn
}

output "alarm_name" {
  description = "Name of the CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.backend_inactivity.alarm_name
}

output "alarm_arn" {
  description = "ARN of the CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.backend_inactivity.arn
}

output "cloudwatch_namespace" {
  description = "CloudWatch namespace used for metrics"
  value       = var.cloudwatch_namespace
}
