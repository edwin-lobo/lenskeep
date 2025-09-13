locals {
  name    = var.project
  wh_bkt  = coalesce(var.warehouse_bucket, "${var.project}-warehouse-${random_id.suffix.hex}")
  res_bkt = coalesce(var.athena_results_bucket, "${var.project}-athena-results-${random_id.suffix.hex}")
  db_name = "media_catalog"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# --- S3: Warehouse (Iceberg tables) ---
resource "aws_s3_bucket" "warehouse" {
  bucket = local.wh_bkt
}

resource "aws_s3_bucket_public_access_block" "warehouse" {
  bucket                  = aws_s3_bucket.warehouse.id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_versioning" "warehouse" {
  bucket = aws_s3_bucket.warehouse.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "warehouse" {
  bucket = aws_s3_bucket.warehouse.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- S3: Athena results ---
resource "aws_s3_bucket" "athena_results" {
  bucket = local.res_bkt
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket                  = aws_s3_bucket.athena_results.id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- Glue database (Iceberg will register tables here) ---
resource "aws_glue_catalog_database" "db" {
  name = local.db_name
}

# --- Athena workgroup (Engine v3 supports Iceberg) ---
resource "aws_athena_workgroup" "iceberg" {
  name = "${local.name}-wg"

  configuration {
    engine_version {
      selected_engine_version = "Athena engine version 3"
    }
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/"
    }
    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true
  }

  state = "ENABLED"
  description = "Workgroup for ${local.name} using Athena Engine v3 (Iceberg)"
}
