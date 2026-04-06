# Secret resources are created here; values must be added manually:
#   echo -n 'PASTE_TOKEN_JSON' | gcloud secrets versions add GMAIL_TOKEN_ROBERT --data-file=-
#   echo -n 'PASTE_TOKEN_JSON' | gcloud secrets versions add GMAIL_TOKEN_KATERINA --data-file=-

resource "google_secret_manager_secret" "gmail_token_robert" {
  project   = var.project_id
  secret_id = "GMAIL_TOKEN_ROBERT"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "gmail_token_katerina" {
  project   = var.project_id
  secret_id = "GMAIL_TOKEN_KATERINA"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}
