resource "google_compute_network" "buckcat_frontend_network" {
  name = "buckcat-frontend-network"
}

resource "google_compute_firewall" "allow_ssh_nom_ip" {
  name    = "allow-ssh-nom-ip"
  network = google_compute_network.buckcat_frontend_network.name

  source_ranges = var.nom_ip

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "allow_http_internet" {
  name    = "allow-http-internet"
  network = google_compute_network.buckcat_frontend_network.name

  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
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
