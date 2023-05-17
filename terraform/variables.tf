# locals {
#     data_lake_bucket = "lego_data_lake"
# }

# variable "project" {
#     description = "Your GCP project ID"
#     default = "vande2023"
#     type = string
# }

# variable "region" {
#     description = "Region for GCP resources"
#     default = "us-central1"
#     type = string
# }

# variable "bucket_name" {
#     description = "The name of the Google Cloud Storage bucket. Must be globally unique"
#     default="van_de2023"
# }

# variable "storage_class" {
#     description = "Storage class type for your bucket"
#     default = "STANDARD"
# }

# variable "BQ_DATASET" {
#     description = "BigQuery Dataset that raw data (from GCS) will be written to"
#     type = string
#     default = "vande2023"
# }

locals {
    data_lake_bucket = "lego_data_lake"
}

variable "project_name" {
    description = "Your GCP project ID"
    type = string
}

variable "region" {
    description = "Region for GCP resources"
    type = string
}

variable "bucket_name" {
    description = "The name of the Google Cloud Storage bucket. Must be globally unique"
    type = string
}

variable "storage_class" {
    description = "Storage class type for your bucket"
    type = string
}

variable "bq_dataset_name" {
    description = "BigQuery Dataset that raw data (from GCS) will be written to"
    type = string
}
