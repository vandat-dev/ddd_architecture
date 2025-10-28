from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from app.core.setting import settings


class MinIOConfig:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.public_endpoint = settings.MINIO_PUBLIC_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.secure = settings.MINIO_SECURE
        self.public_secure = settings.MINIO_PUBLIC_SECURE

        # Initialize MinIO client
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        self.ensure_bucket()

    def ensure_bucket(self):
        """Create the bucket if it doesn't exist."""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file, object_name: str, content_type: str):
        """
        Upload any file (image, video, etc.) with no compression or quality loss.
        - file: file-like object (e.g., UploadFile.file in FastAPI)
        - object_name: path/key inside MinIO bucket
        - content_type: MIME type (e.g., 'image/jpeg', 'video/mp4')
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file,
                length=-1,  # stream mode (no need to load entire file into memory)
                part_size=10 * 1024 * 1024,  # split into 10MB parts (for large files)
                content_type=content_type,
            )
        except S3Error as e:
            raise RuntimeError(f"Upload failed: {e}")

        return self.get_public_url(object_name)

    def get_public_url(self, object_name: str) -> str:
        """Return the public URL for a given object."""
        protocol = "https" if self.public_secure else "http"
        return f"{protocol}://{self.public_endpoint}/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str, expires: int = 86400) -> str:
        """Generate a temporary presigned URL (default: 24 hours)."""
        try:
            return self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to generate presigned URL: {e}")
