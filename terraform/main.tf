terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # Pre-create this bucket once:
  #   gcloud storage buckets create gs://YOUR_TF_STATE_BUCKET --project=YOUR_PROJECT_ID
  backend "gcs" {
    bucket = "YOUR_TF_STATE_BUCKET"
    prefix = "gmail-routine"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
