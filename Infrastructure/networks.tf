resource "google_compute_network" "buckcat_frontend_network" {
  name = "buckcat-frontend-network"
}

resource "google_compute_address" "frontend_static_ip_address" {
  name   = "frontend-static-ip-address"
  region = var.region
}

resource "google_compute_firewall" "allow_internet_access" {
  name    = "allow-internet-access"
  network = google_compute_network.buckcat_frontend_network.name

  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["443", "80", "8080"]
  }
}

resource "google_compute_firewall" "allow_icmp_ssh" {
  name    = "allow-icmp-ssh"
  network = google_compute_network.buckcat_frontend_network.name

  source_ranges = [var.nom_ip, "35.235.240.0/20"]

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_network" "buckcat_backend_network" {
  name = "buckcat-backend-network"
}

resource "google_compute_firewall" "backend_firewall" {
  name    = "buckcat-backend-firewall"
  network = google_compute_network.buckcat_backend_network.name

  source_ranges = [var.nom_ip, "35.235.240.0/20"]

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}
