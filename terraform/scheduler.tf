resource "google_cloud_scheduler_job" "gmail_routine" {
  project  = var.project_id
  region   = var.region
  name     = "gmail-routine-daily"
  schedule = var.scheduler_schedule

  http_target {
    uri         = google_cloudfunctions2_function.gmail_routine.service_config[0].uri
    http_method = "POST"
    body        = base64encode("{}")

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloudfunctions2_function.gmail_routine.service_config[0].uri
    }
  }

  depends_on = [google_project_service.apis]
}
