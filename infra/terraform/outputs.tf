output "warehouse_bucket" {
  value = aws_s3_bucket.warehouse.bucket
}

output "athena_results_bucket" {
  value = aws_s3_bucket.athena_results.bucket
}

output "glue_database" {
  value = aws_glue_catalog_database.db.name
}

output "athena_workgroup" {
  value = aws_athena_workgroup.iceberg.name
}

output "iceberg_warehouse_path" {
  value = "s3://${aws_s3_bucket.warehouse.bucket}/warehouse/"
}
