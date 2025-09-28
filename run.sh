#!/bin/bash
# Run the Docker container for the Flask app

docker run -p 8080:80 -v $(pwd)/data:/data cerulean-v4
