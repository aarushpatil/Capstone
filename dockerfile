# Use an ARM-compatible Python base image (3.11.11-slim for arm64)
FROM python:3.11.11-slim

# Set the working directory in the container
WORKDIR /app

# Use clang as the C/C++ compiler instead of gcc
ENV CC=clang
ENV CXX=clang++

ENV CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DLLAMA_METAL=OFF -DLLAMA_AVX=OFF -DLLAMA_FMA=OFF -DLLAMA_DOTPROD=OFF"

# Install required system packages:
# - clang, cmake, git, ninja-build, vim, build-essential, curl: your original requirements.
# - sqlite3: provides the SQLite command-line tool.
# - libsqlite3-dev: provides the SQLite development libraries (helpful for certain C extensions).
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    cmake \
    git \
    ninja-build \
    vim \
    build-essential \
    curl \
    sqlite3 \
    libsqlite3-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy over the Python requirements.
COPY requirements.txt .

# Install Python packages from requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Install npm and node
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    node -v && npm -v

# Copy entire project to the container
COPY . .

# Install frontend dependencies (assumes the frontend is in /app/frontend)
RUN bash -c "cd frontend && npm install"


#build the image with when in directory with dockerfile:
#docker build -t final_image .

# frontend:
# docker run -p 3000:3000 -v "$(pwd):/app" -w /app -it final_image /bin/bash

# backend:
# docker run -p 5050:5050 -v "$(pwd):/app" -w /app -it final_image /bin/bash