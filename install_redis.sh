#!/bin/bash
# Quick Redis installation

echo "Installing Redis..."
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping
echo "Redis installed and running!"
