resource "google_storage_bucket" "function_source" {
  project                     = var.project_id
  name                        = "${var.project_id}-gmail-routine-source"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.apis]
}
