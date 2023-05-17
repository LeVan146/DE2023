terraform {
    required_version = ">= 1.0"
    backend "local" {} # Change to "gcs" for GCP, "s3" for AWS
    required_providers {
        google = {
            source = "hashicorp/google"
        }
    }
}

provider "google" {
    project = var.project_name
    region = var.region
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
    name = "${local.data_lake_bucket}_${var.project_name}"
    location = var.region

    storage_class = var.storage_class
    uniform_bucket_level_access = true

    versioning {
        enabled = true
    }

    lifecycle_rule {
        action {
            type =  "Delete"
        }
        condition {
            age = 30 // days
        }
    }

    force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
    dataset_id = var.bq_dataset_name
    project = var.project_name
    location = var.region
}