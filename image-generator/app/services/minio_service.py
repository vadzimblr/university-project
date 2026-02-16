import logging
import base64
import os
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse
from minio import Minio
from minio.error import S3Error


class MinioService:
    def __init__(
        self, 
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.logger = logging.getLogger(__name__)
    
    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            self.logger.error(f"Failed to check bucket {bucket_name}: {e}")
            raise
    
    def create_bucket(self, bucket_name: str) -> None:
        try:
            self.client.make_bucket(bucket_name)
            self.logger.info(f"Created bucket: {bucket_name}")
        except S3Error as e:
            self.logger.error(f"Failed to create bucket {bucket_name}: {e}")
            raise
    
    def ensure_bucket(self, bucket_name: str) -> None:
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                self.logger.info(f"Created bucket: {bucket_name}")
        except S3Error as e:
            self.logger.error(f"Failed to create bucket {bucket_name}: {e}")
            raise
    
    def upload_bytes(
        self, 
        bucket_name: str, 
        object_name: str, 
        data: bytes,
        content_type: str = 'image/png'
    ) -> dict:
        try:
            self.ensure_bucket(bucket_name)
            
            data_stream = BytesIO(data)
            file_size = len(data)
            
            result = self.client.put_object(
                bucket_name,
                object_name,
                data_stream,
                file_size,
                content_type=content_type
            )
            
            self.logger.info(f"Uploaded {object_name} to {bucket_name} ({file_size} bytes)")
            
            return {
                'bucket': bucket_name,
                'object_name': object_name,
                'size': file_size,
                'etag': result.etag
            }
        except S3Error as e:
            self.logger.error(f"Failed to upload {object_name}: {e}")
            raise
    
    def download_bytes(self, bucket_name: str, object_name: str) -> bytes:
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            self.logger.info(f"Downloaded {object_name} from {bucket_name}")
            return data
        except S3Error as e:
            self.logger.error(f"Failed to download {object_name}: {e}")
            raise
    
    def download_as_base64(self, bucket_name: str, object_name: str) -> str:
        data = self.download_bytes(bucket_name, object_name)
        return base64.b64encode(data).decode('utf-8')
    
    def get_presigned_url(
        self, 
        bucket_name: str, 
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
        except S3Error as e:
            self.logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            raise

    def get_presigned_public_url(
        self,
        bucket_name: str,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        public_client = self._get_public_client(bucket_name=bucket_name)
        if not public_client:
            return self.get_presigned_url(
                bucket_name=bucket_name,
                object_name=object_name,
                expires_seconds=expires_seconds
            )

        try:
            from datetime import timedelta
            return public_client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
        except S3Error as e:
            self.logger.error(f"Failed to generate public presigned URL for {object_name}: {e}")
            raise

    @staticmethod
    def _parse_secure(value: Optional[str], default_secure: bool) -> bool:
        if value is None:
            return default_secure
        return value.lower() == "true"

    def _get_public_client(self, bucket_name: Optional[str] = None) -> Optional[Minio]:
        raw = os.getenv("MINIO_PUBLIC_BASE_URL") or os.getenv("MINIO_PUBLIC_ENDPOINT")
        if not raw:
            return None

        if "://" in raw:
            parsed = urlparse(raw)
            endpoint = parsed.netloc or parsed.path
            secure = parsed.scheme == "https"
        else:
            endpoint = raw
            secure = self._parse_secure(os.getenv("MINIO_PUBLIC_SECURE"), self.secure)

        if not endpoint:
            return None

        region = os.getenv("MINIO_PUBLIC_REGION") or os.getenv("MINIO_REGION")
        if not region and bucket_name:
            try:
                region = self.client.get_bucket_location(bucket_name) or "us-east-1"
            except (S3Error, AttributeError):
                region = "us-east-1"

        return Minio(
            endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=secure,
            region=region
        )
    
    def delete_object(self, bucket_name: str, object_name: str) -> None:
        try:
            self.client.remove_object(bucket_name, object_name)
            self.logger.info(f"Deleted {object_name} from {bucket_name}")
        except S3Error as e:
            self.logger.error(f"Failed to delete {object_name}: {e}")
            raise
    
    def list_objects(self, bucket_name: str, prefix: Optional[str] = None) -> list:
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            self.logger.error(f"Failed to list objects in {bucket_name}: {e}")
            raise
