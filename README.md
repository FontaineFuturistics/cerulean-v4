This is the initial implementation of Cerulean V4.

Install docker: apt install docker.io
Build the container: docker build -t cerulean-v4 .
Run the container: 
docker run -d \
  --name cerulean-v4 \
  -p 443:443 \
  -v "$(pwd)/data:/data" \
  --restart unless-stopped \
  cerulean-v4

Check if the container is running: docker ps

TODO change trash icon