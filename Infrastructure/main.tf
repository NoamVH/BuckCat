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

# resource "google_cloud_run_service" "buckcat_backend_service" {
#   name     = "buckcat-backend-service"
#   location = var.region

#   template {
#     spec {
#       containers {
#         image = "nginx:latest"
#         ports {
#           container_port = 8080
#         }
#       }
#     }
#   }
# }

resource "google_compute_instance" "vm_instance" {
  name         = "buckcat-instance"
  machine_type = "e2-micro"
  #tags         = ["web", "dev"]

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = google_compute_network.buckcat_backend_network.name
    access_config {
    }
  }
}
