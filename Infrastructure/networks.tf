resource "google_compute_network" "buckcat_frontend_network" {
  name = "buckcat-frontend-network"
}

resource "google_compute_network" "buckcat_backend_network" {
  name = "buckcat-backend-network"
}

resource "google_compute_firewall" "backend_firewall" {
  name    = "buckcat-backend-firewall"
  network = google_compute_network.buckcat_backend_network.name

  source_ranges = var.nom_ip

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = [22, 80, 8080]
  }
}

resource "google_cloud_tasks_queue" "front_to_back_queue" {
  name     = "front-to-back-queue"
  location = var.region
}

resource "google_cloud_tasks_queue" "back_to_front_queue" {
  name     = "back-to-front-queue"
  location = var.region
}
