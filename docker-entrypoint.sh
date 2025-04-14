#!/bin/bash

# Start MongoDB in the background
mongod --dbpath /data/db --bind_ip_all &

# Wait for MongoDB to be ready
sleep 5

# Start backend (adjust as needed)
cd backend
python main.py

