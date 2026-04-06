output "function_url" {
  description = "Cloud Function URL"
  value       = google_cloudfunctions2_function.gmail_routine.service_config[0].uri
}

output "function_sa_email" {
  description = "Function service account email"
  value       = google_service_account.function.email
}
