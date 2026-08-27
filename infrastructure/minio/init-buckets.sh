#!/bin/bash
set -e

echo "Waiting for MinIO to start..."
until curl -sf http://minio:9000/minio/health/live; do
    sleep 2
done

echo "MinIO started. Creating default buckets..."
mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
mc mb --ignore-existing myminio/fidio-media
mc mb --ignore-existing myminio/fidio-renders

mc anonymous set download myminio/fidio-renders
echo "MinIO initialization complete."
