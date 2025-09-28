#!/bin/bash
# Build the Docker image for the Flask app

# Ensure ./data directory exists
mkdir -p ./data

docker build -t cerulean-v4 .
