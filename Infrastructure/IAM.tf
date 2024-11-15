resource "google_service_account" "local_testing_service_account" {
  account_id   = "nompc-service-account"
  display_name = "Local Testing Service Account"
}

resource "google_storage_bucket_iam_member" "local_testing_iam_member" {
  bucket = google_storage_bucket.buckcat.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_project_iam_custom_role" "buckcat_services_tasks_custom_role" {
  role_id     = "buckcat_services_tasks_custom_role"
  title       = "Buckcat Services Tasks Custom Role"
  description = "Allows the BuckCat services to read and write tasks to GCP task queues."
  permissions = ["cloudtasks.tasks.list", "cloudtasks.tasks.get", "cloudtasks.tasks.create", "cloudtasks.tasks.delete"]
}

resource "google_cloud_tasks_queue_iam_member" "front_to_back_queue_iam_member" {
  name     = google_cloud_tasks_queue.front_to_back_queue.name
  location = var.region
  role     = "projects/${var.project}/roles/${google_project_iam_custom_role.buckcat_services_tasks_custom_role.role_id}"
  member   = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}

resource "google_cloud_tasks_queue_iam_member" "back_to_front_queue_iam_member" {
  name     = google_cloud_tasks_queue.back_to_front_queue.name
  location = var.region
  role     = "projects/${var.project}/roles/${google_project_iam_custom_role.buckcat_services_tasks_custom_role.role_id}"
  member   = "serviceAccount:${google_service_account.local_testing_service_account.email}"
}
