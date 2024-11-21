resource "google_service_account" "local_testing_service_account" {
  account_id   = "nompc-service-account"
  display_name = "Local Testing Service Account"
}

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
