variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix for resources"
  type        = string
  default     = "vsco-archive"
}

variable "warehouse_bucket" {
  description = "S3 bucket for Iceberg warehouse (tables + metadata)"
  type        = string
  default     = null
}

variable "athena_results_bucket" {
  description = "S3 bucket for Athena query results"
  type        = string
  default     = null
}
