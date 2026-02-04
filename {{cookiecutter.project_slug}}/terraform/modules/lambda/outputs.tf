output "task_manager_function_name" {
  description = "Name of the task manager Lambda function"
  value       = aws_lambda_function.task_manager.function_name
}

output "task_manager_function_arn" {
  description = "ARN of the task manager Lambda function"
  value       = aws_lambda_function.task_manager.arn
}

output "task_manager_invoke_arn" {
  description = "Invoke ARN of the task manager Lambda function"
  value       = aws_lambda_function.task_manager.invoke_arn
}

output "task_shutdown_function_name" {
  description = "Name of the task shutdown Lambda function"
  value       = aws_lambda_function.task_shutdown.function_name
}

output "task_shutdown_function_arn" {
  description = "ARN of the task shutdown Lambda function"
  value       = aws_lambda_function.task_shutdown.arn
}

output "task_shutdown_invoke_arn" {
  description = "Invoke ARN of the task shutdown Lambda function"
  value       = aws_lambda_function.task_shutdown.invoke_arn
}
