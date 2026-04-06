# ── Function service account ──────────────────────────────────────────────────

resource "google_service_account" "function" {
  project      = var.project_id
  account_id   = "gmail-routine-sa"
  display_name = "Gmail Routine Cloud Function"

  depends_on = [google_project_service.apis]
}

# Allow the function SA to read Secret Manager secrets
resource "google_project_iam_member" "function_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.function.email}"
}

# ── Scheduler service account ─────────────────────────────────────────────────

resource "google_service_account" "scheduler" {
  project      = var.project_id
  account_id   = "gmail-scheduler-sa"
  display_name = "Gmail Routine Scheduler"

  depends_on = [google_project_service.apis]
}

# Allow the scheduler SA to invoke the Cloud Function (Gen 2 uses Cloud Run)
resource "google_cloudfunctions2_function_iam_member" "scheduler_invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.gmail_routine.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.scheduler.email}"
}

# Gen 2 functions run on Cloud Run — also grant run.invoker
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.gmail_routine.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}
