# S3 Module - Frontend hosting and DB storage

# Frontend S3 bucket
resource "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name

  tags = {
    Name        = "StoryArchitect Frontend"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Keep bucket private - CloudFront will access via OAI
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Grant CloudFront OAI access to the bucket
resource "aws_s3_bucket_policy" "frontend" {
  bucket     = aws_s3_bucket.frontend.id
  depends_on = [aws_s3_bucket_public_access_block.frontend]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "CloudFrontOAIReadGetObject"
        Effect    = "Allow"
        Principal = {
          AWS = var.cloudfront_oai_iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_cors_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Database S3 bucket for SQLite storage
resource "aws_s3_bucket" "database" {
  bucket = var.database_bucket_name

  tags = {
    Name        = "StoryArchitect Database"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "database" {
  bucket = aws_s3_bucket.database.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "database" {
  bucket = aws_s3_bucket.database.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM policy for ECS tasks to access the database bucket
resource "aws_iam_policy" "database_access" {
  name        = "${var.project_name}-database-access-${var.environment}"
  description = "Allows ECS tasks to read/write SQLite database from S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.database.arn,
          "${aws_s3_bucket.database.arn}/*"
        ]
      }
    ]
  })
}
