# Zip the function source; the MD5 in the object name forces redeploy on code changes
data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "${path.root}/../google_cloud_functions/gmail"
  output_path = "${path.root}/.build/function-source.zip"
}

resource "google_storage_bucket_object" "function_source" {
  name   = "function-source-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.function_source.output_path
}

resource "google_cloudfunctions2_function" "gmail_routine" {
  project  = var.project_id
  location = var.region
  name     = "gmail-routine"

  build_config {
    runtime     = "python312"
    entry_point = "run_gmail_routine"

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.function.email
    timeout_seconds       = 540 # 9 min — scanning two accounts can be slow
    available_memory      = "256M"
    max_instance_count    = 1

    environment_variables = {
      ANTHROPIC_API_KEY = var.anthropic_api_key
    }

    secret_environment_variables {
      key        = "GMAIL_TOKEN_ROBERT"
      secret     = google_secret_manager_secret.gmail_token_robert.secret_id
      version    = "latest"
      project_id = var.project_id
    }

    secret_environment_variables {
      key        = "GMAIL_TOKEN_KATERINA"
      secret     = google_secret_manager_secret.gmail_token_katerina.secret_id
      version    = "latest"
      project_id = var.project_id
    }
  }

  depends_on = [
    google_project_service.apis,
    google_project_iam_member.function_secret_accessor,
  ]
}
