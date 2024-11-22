output "ip" {
  value = google_compute_instance.vm_instance.network_interface.0.network_ip
}

output "dev_service_account_email" {
  value = google_service_account.local_testing_service_account.email
}

output "github_service_account_email" {
  value = google_service_account.github_workload_identity_service_account.email
}
