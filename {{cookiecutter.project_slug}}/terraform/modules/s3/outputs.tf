output "frontend_bucket_id" {
  description = "ID of the frontend S3 bucket"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_bucket_arn" {
  description = "ARN of the frontend S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "database_bucket_id" {
  description = "ID of the database S3 bucket"
  value       = aws_s3_bucket.database.id
}

output "database_bucket_arn" {
  description = "ARN of the database S3 bucket"
  value       = aws_s3_bucket.database.arn
}

output "database_access_policy_arn" {
  description = "ARN of the IAM policy for database access"
  value       = aws_iam_policy.database_access.arn
}
