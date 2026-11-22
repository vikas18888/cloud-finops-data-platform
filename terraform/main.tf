# Day 17: sample infrastructure for cost estimation with Infracost (nothing is deployed; use `terraform plan` / `infracost breakdown` only).
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region                      = var.region
  skip_credentials_validation = true   # allows plan/cost estimation without real AWS credentials
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  access_key                  = "mock"
  secret_key                  = "mock"
  default_tags {
    tags = { owner_team = "platform", env = var.env, cost_center = "CC-101" }   # enforces the tagging policy
  }
}

variable "region" { default = "ap-south-1" }
variable "env" { default = "prod" }
variable "app_instance_type" { default = "m5.large" }   # change to m5.2xlarge in a PR to see Infracost show the diff
variable "app_instance_count" { default = 3 }

resource "aws_instance" "app" {
  count         = var.app_instance_count
  ami           = "ami-0abcdef1234567890"
  instance_type = var.app_instance_type
  root_block_device {
    volume_size = 50
    volume_type = "gp3"
  }
}

resource "aws_db_instance" "main" {
  identifier          = "finops-db"
  engine              = "postgres"
  instance_class      = "db.r5.large"
  allocated_storage   = 200
  storage_type        = "gp3"
  multi_az            = true
  username            = "finops"
  password            = "change-me-in-real-use"
  skip_final_snapshot = true
}

resource "aws_s3_bucket" "logs" {
  bucket = "finops-demo-logs-bucket"
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    id     = "tiering"
    status = "Enabled"
    filter {}
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    expiration { days = 730 }
  }
}
