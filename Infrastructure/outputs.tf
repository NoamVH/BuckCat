output "dev_service_account_email" {
  value = google_service_account.local_testing_service_account.email
}

output "github_service_account_email" {
  value = google_service_account.github_workload_identity_service_account.email
}

output "buckat_instances_service_account_email" {
  value = google_service_account.servers_service_account.email
}

output "github_federation_identity_identifier" {
  value = google_iam_workload_identity_pool_provider.buckcat_github_identity_federation.id
}
