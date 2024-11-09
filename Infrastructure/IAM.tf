resource "google_service_account" "local_testing_service_account" {
  account_id   = "nompc-service-account"
  display_name = "Local Testing Service Account"
}

resource "google_storage_bucket_iam_member" "local_testing_iam_member" {
  bucket = google_storage_bucket.buckcat.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_cloud_tasks_queue_iam_member" "front_to_back_queue_iam_viewer_member" {
  name     = google_cloud_tasks_queue.front_to_back_queue.name
  location = var.region
  role     = "roles/cloudtasks.viewer"
  member   = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_cloud_tasks_queue_iam_member" "front_to_back_queue_iam_deleter_member" {
  name     = google_cloud_tasks_queue.front_to_back_queue.name
  location = var.region
  role     = "roles/cloudtasks.taskDeleter"
  member   = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}
