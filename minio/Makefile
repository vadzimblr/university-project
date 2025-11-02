.PHONY: up down restart logs ps health console buckets create-bucket delete-bucket bucket-info

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart minio

logs:
	docker-compose logs -f minio

ps:
	docker-compose ps

health:
	@echo "Checking MinIO health..."
	@curl -s http://localhost:9000/minio/health/live || echo "MinIO is not responding"

console:
	@echo "MinIO Console is available at: http://localhost:9001"
	@echo "Username: $$(grep MINIO_ROOT_USER .env | cut -d '=' -f2)"
	@echo "Password: $$(grep MINIO_ROOT_PASSWORD .env | cut -d '=' -f2)"

# Install mc (MinIO Client) inside container
install-mc:
	docker-compose exec minio sh -c "curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc"

# Configure mc alias
configure-mc:
	docker-compose exec minio mc alias set myminio http://localhost:9000 $$(grep MINIO_ROOT_USER .env | cut -d '=' -f2) $$(grep MINIO_ROOT_PASSWORD .env | cut -d '=' -f2)

# List all buckets
buckets:
	docker-compose exec minio mc ls myminio

# Create a new bucket
create-bucket:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc mb myminio/$$bucket

# Delete a bucket
delete-bucket:
	@read -p "Enter bucket name to delete: " bucket; \
	docker-compose exec minio mc rb myminio/$$bucket

# Get bucket info
bucket-info:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc stat myminio/$$bucket

# List objects in bucket
list-objects:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc ls myminio/$$bucket

# Upload file to bucket
upload:
	@read -p "Enter bucket name: " bucket; \
	read -p "Enter local file path: " filepath; \
	docker-compose exec -T minio mc cp - myminio/$$bucket/$$(basename $$filepath) < $$filepath

# Download file from bucket
download:
	@read -p "Enter bucket name: " bucket; \
	read -p "Enter object name: " object; \
	read -p "Enter destination path: " dest; \
	docker-compose exec minio mc cp myminio/$$bucket/$$object - > $$dest

# Set bucket policy to public
set-public:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc anonymous set download myminio/$$bucket

# Set bucket policy to private
set-private:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc anonymous set none myminio/$$bucket

# Get bucket policy
get-policy:
	@read -p "Enter bucket name: " bucket; \
	docker-compose exec minio mc anonymous get myminio/$$bucket

# Clean old volumes
clean:
	docker-compose down -v

# Show storage info
info:
	docker-compose exec minio mc admin info myminio

