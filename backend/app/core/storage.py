"""
Storage utilities for Cloudflare R2.
Handles file uploads, downloads, and R2 bucket operations.
"""

import boto3
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, BinaryIO, List
from botocore.exceptions import ClientError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class R2StorageManager:
    """Cloudflare R2 storage manager for file operations."""
    
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.cloudflare_r2_access_key,
            aws_secret_access_key=settings.cloudflare_r2_secret_key,
        )
        
        self.s3_client = self.session.client(
            's3',
            endpoint_url=f'https://{settings.cloudflare_r2_account_id}.r2.cloudflarestorage.com',
            region_name='auto'
        )
        
        self.bucket_name = settings.cloudflare_r2_bucket_name
        self.public_url = settings.cloudflare_r2_public_url
    
    def generate_object_key(self, filename: str, category: str = "general") -> str:
        """Generate a unique object key for R2 storage."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Extract file extension
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        
        # Create organized path: category/year/month/unique_file
        year_month = datetime.utcnow().strftime("%Y/%m")
        object_key = f"{category}/{year_month}/{timestamp}_{unique_id}.{file_extension}"
        
        return object_key
    
    def get_public_url(self, object_key: str) -> str:
        """Get the public URL for an R2 object."""
        return f"{self.public_url}/{object_key}"
    
    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = "image/jpeg", 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to R2 storage."""
        try:
            extra_args = {
                'ContentType': content_type,
                'ACL': 'public-read'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Upload the file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_data,
                **extra_args
            )
            
            logger.info(f"Successfully uploaded file to R2: {object_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload file to R2: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading to R2: {str(e)}")
            return False
    
    async def delete_file(self, object_key: str) -> bool:
        """Delete a file from R2 storage."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            logger.info(f"Successfully deleted file from R2: {object_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from R2: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting from R2: {str(e)}")
            return False
    
    async def get_file_info(self, object_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a file in R2 storage."""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            return {
                'size': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"Failed to get file info from R2: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting file info from R2: {str(e)}")
            return None
    
    async def file_exists(self, object_key: str) -> bool:
        """Check if a file exists in R2 storage."""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file existence in R2: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking file existence in R2: {str(e)}")
            return False
    
    async def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file upload."""
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            return None
    
    async def list_files(self, prefix: str = "", max_keys: int = 100) -> List[Dict[str, Any]]:
        """List files in R2 storage with optional prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'public_url': self.get_public_url(obj['Key'])
                })
            
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list files from R2: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing files from R2: {str(e)}")
            return []


# Global storage manager instance
storage_manager = R2StorageManager() 