output "ip" {
  value = google_compute_instance.vm_instance.network_interface.0.network_ip
}

output "service_account_email" {
  value = google_service_account.local_testing_service_account.email
}
