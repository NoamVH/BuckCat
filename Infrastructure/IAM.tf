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

resource "google_pubsub_subscription_iam_member" "local_testing_cats_requests_subscriber" {
  subscription = google_pubsub_subscription.cats_requests_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "local_testing_cats_requests_publisher" {
  topic  = google_pubsub_topic.cats_requests_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "local_testing_cats_urls_subscriber" {
  subscription = google_pubsub_subscription.cats_urls_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "local_testing_cats_urls_publisher" {
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

resource "google_service_account" "github_workload_identity_service_account" {
  account_id   = "github-service-account"
  display_name = "GitHub Workload Identity Service Acccount"
  project      = var.project
}

resource "google_service_account_iam_member" "github_workload_identity_iam_memeber" {
  service_account_id = google_service_account.github_workload_identity_service_account.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.buckcat_workload_identity_pool.name}/*"
}

resource "google_artifact_registry_repository_iam_member" "github_workload_identity_gar_writer" {
  project    = var.project
  location   = google_artifact_registry_repository.buckcat_registry.location
  repository = google_artifact_registry_repository.buckcat_registry.name
  role       = "roles/artifactregistry.repoAdmin"
  member     = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

resource "google_compute_instance_iam_member" "github_frontend_updater" {
  project       = var.project
  zone          = var.zone
  instance_name = google_compute_instance.buckcat_frontend_instance.name
  role          = "roles/compute.instanceAdmin.v1"
  member        = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

resource "google_compute_instance_iam_member" "github_backend_updater" {
  project       = var.project
  zone          = var.zone
  instance_name = google_compute_instance.buckcat_backend_instance.name
  role          = "roles/compute.instanceAdmin.v1"
  member        = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

resource "google_project_iam_member" "github_compute_viewer" {
  project = var.project
  role    = "roles/compute.viewer"
  member  = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

resource "google_service_account_iam_member" "github_service_account_user" {
  service_account_id = google_service_account.servers_service_account.id
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

resource "google_iap_tunnel_iam_member" "github_iap_tunnel_resource_accessor" {
  project = var.project
  role    = "roles/iap.tunnelResourceAccessor"
  member  = "serviceAccount:${google_service_account.github_workload_identity_service_account.email}"
}

# Compute Instances Permissions
resource "google_service_account" "servers_service_account" {
  account_id   = "instances-service-account"
  display_name = "BuckCat Instances Service Account"
}

resource "google_artifact_registry_repository_iam_member" "backend_instance_gar_reader" {
  project    = var.project
  location   = google_artifact_registry_repository.buckcat_registry.location
  repository = google_artifact_registry_repository.buckcat_registry.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_storage_bucket_iam_member" "buckcat_instance_buckcat_reader" {
  bucket = google_storage_bucket.buckcat.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_service_account_iam_member" "buckcat_instance_buckcat_signer" {
  service_account_id = google_service_account.servers_service_account.id
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "buckcat_instance_cats_requests_subscriber" {
  subscription = google_pubsub_subscription.cats_requests_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "buckcat_instance_cats_requests_publisher" {
  topic  = google_pubsub_topic.cats_requests_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "buckcat_instance_cats_urls_subscriber" {
  subscription = google_pubsub_subscription.cats_urls_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.servers_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "buckcat_instance_cats_urls_publisher" {
  topic  = google_pubsub_topic.cats_urls_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.servers_service_account.email}"
}

# GKE Permissions

resource "google_service_account" "gke_service_account" {
  account_id   = "gke-service-account"
  display_name = "BuckCat GKE Service Account"
}

resource "google_project_iam_member" "gke_gar_reader" {
  project = var.project
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_storage_bucket_iam_member" "gke_buckcat_reader" {
  bucket = google_storage_bucket.buckcat.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_service_account_iam_member" "gke_buckcat_signer" {
  service_account_id = google_service_account.gke_service_account.id
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "gke_cats_requests_subscriber" {
  subscription = google_pubsub_subscription.cats_requests_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "gke_cats_requests_publisher" {
  topic  = google_pubsub_topic.cats_requests_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_pubsub_subscription_iam_member" "gke_cats_urls_subscriber" {
  subscription = google_pubsub_subscription.cats_urls_subscription.id
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.gke_service_account.email}"
}

resource "google_pubsub_topic_iam_member" "gke_cats_urls_publisher" {
  topic  = google_pubsub_topic.cats_urls_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.gke_service_account.email}"
}
