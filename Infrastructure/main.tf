terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_storage_bucket" "buckcat" {
  name          = "buckcat"
  location      = var.region
  storage_class = "COLDLINE"
  #force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_artifact_registry_repository" "buckcat_registry" {
  location      = var.region
  repository_id = "buckcat-registry"
  description   = "BuckCat's Docker Repository"
  format        = "DOCKER"

  cleanup_policies {
    id     = "delete-untagged"
    action = "DELETE"
    condition {
      tag_state = "UNTAGGED"
    }
  }
}

resource "google_compute_instance" "buckcat_frontend_instance" {
  name         = "buckcat-frontend-instance"
  machine_type = "e2-micro"

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = google_compute_network.buckcat_frontend_network.name
    access_config {
      nat_ip = google_compute_address.frontend_static_ip_address.address
    }
  }

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.servers_service_account.email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_instance" "buckcat_backend_instance" {
  name                      = "buckcat-backend-instance"
  machine_type              = "e2-micro"
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = google_compute_network.buckcat_backend_network.name
    access_config {
      # Ephemeral IP address.
    }
  }

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.servers_service_account.email
    scopes = ["cloud-platform"]
  }
}
