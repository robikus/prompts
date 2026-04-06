variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "anthropic_api_key" {
  description = "Anthropic API key (set via TF_VAR_anthropic_api_key in CI)"
  type        = string
  sensitive   = true
}

variable "scheduler_schedule" {
  description = "Cron schedule for the Gmail routine (UTC)"
  type        = string
  default     = "0 6 * * *" # 06:00 UTC = 07:00 CET / 08:00 CEST
}
