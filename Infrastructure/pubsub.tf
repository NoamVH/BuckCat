resource "google_pubsub_topic" "cats_urls_topic" {
  name = "cats_urls"

  # labels = {
  #   foo = "bar"
  # }

  message_retention_duration = "86600s"
}

resource "google_pubsub_topic" "cats_requests_topic" {
  name = "cats_requests"

  # labels = {
  #   foo = "bar"
  # }

  message_retention_duration = "86600s"
}

resource "google_pubsub_subscription" "cats_requests_subscription" {
  name  = "cats_requests_subscription"
  topic = google_pubsub_topic.cats_requests_topic.id

  # 20 minutes
  message_retention_duration = "1200s"
  retain_acked_messages      = true

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "300000.5s"
  }

  retry_policy {
    minimum_backoff = "10s"
  }

  enable_message_ordering = false
}

resource "google_pubsub_subscription" "cats_urls_subscription" {
  name  = "cats_urls_subscription"
  topic = google_pubsub_topic.cats_urls_topic.id

  #   labels = {
  #     foo = "bar"
  #   }

  # 20 minutes
  message_retention_duration = "1200s"
  retain_acked_messages      = true

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "300000.5s"
  }

  retry_policy {
    minimum_backoff = "10s"
  }

  enable_message_ordering = false
}
