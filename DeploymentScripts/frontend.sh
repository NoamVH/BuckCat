#!/bin/bash

docker stop $(docker ps -q)
docker container prune -f
docker image prune -a -f
docker run -d -p 80:80 us-east1-docker.pkg.dev/$PROJECT_ID/buckcat-registry/buckcat-frontend:latest
