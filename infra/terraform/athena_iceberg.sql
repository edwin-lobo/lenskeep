-- Adjust database/table names as needed.
CREATE DATABASE IF NOT EXISTS media_catalog;

-- Create an Apache Iceberg table for your VSCO metadata.
-- NOTE: Athena Iceberg uses Glue as the catalog by default.
CREATE TABLE IF NOT EXISTS media_catalog.media
(
  username        string,
  vsco_id         string,
  media_type      string,  -- 'photo' | 'video'
  url             string,
  file_path       string,  -- your local path or future s3 pointer for media
  created_at      timestamp,
  downloaded_at   timestamp
)
LOCATION 's3://REPLACE_THIS_WAREHOUSE_BUCKET/warehouse/media/'
TBLPROPERTIES (
  'table_type'='ICEBERG',
  'format'='parquet'
);
