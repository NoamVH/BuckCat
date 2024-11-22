# Development Service Account
resource "google_service_account" "local_testing_service_account" {
  account_id   = "nompc-service-account"
  display_name = "Local Testing Service Account"
}

# Development Service Account Permissions
resource "google_storage_bucket_iam_member" "local_testing_iam_member" {
  bucket = google_storage_bucket.buckcat.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "cats_requests_subscriber" {
  subscription = google_pubsub_subscription.cats_requests_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "cats_requests_publisher" {
  topic  = google_pubsub_topic.cats_requests_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "cats_urls_subscriber" {
  subscription = google_pubsub_subscription.cats_urls_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "cats_urls_publisher" {
  topic  = google_pubsub_topic.cats_urls_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

# GitHub Workload Federation
resource "google_iam_workload_identity_pool" "buckcat_workload_identity_pool" {
  workload_identity_pool_id = "buckcat-workload-identity-pool"
}

resource "google_iam_workload_identity_pool_provider" "buckcat_github_identity_federation" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.buckcat_workload_identity_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "buckcat-github"
  display_name                       = "GitHub"
  description                        = "GitHub Identity Pool Provider for GitHub Actions"
  disabled                           = false
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.actor"               = "assertion.actor"
    "attribute.aud"                 = "assertion.aud"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
    "attribute.repository_id"       = "assertion.repository_id"

  }
  attribute_condition = <<EOT
      assertion.repository_owner_id == "16431599" &&
      assertion.repository_id == "609320706"
  EOT
}
