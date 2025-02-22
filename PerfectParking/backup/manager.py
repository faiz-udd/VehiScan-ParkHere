import boto3
import os
import datetime
import subprocess
import logging
from django.conf import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.backup_bucket = settings.AWS_BACKUP_BUCKET
        self.backup_path = settings.BACKUP_PATH
        self.db_settings = settings.DATABASES['default']

    def create_database_backup(self):
        """Create a database backup"""
        try:
            # Add file cleanup in case of failure
            filepath = None
            try:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"db_backup_{timestamp}.sql"
                filepath = os.path.join(self.backup_path, filename)

                # Ensure backup directory exists
                os.makedirs(self.backup_path, exist_ok=True)

                # Create backup using pg_dump
                command = [
                    'pg_dump',
                    f"--host={self.db_settings['HOST']}",
                    f"--username={self.db_settings['USER']}",
                    f"--dbname={self.db_settings['NAME']}",
                    '--format=custom',
                    f"--file={filepath}"
                ]

                env = os.environ.copy()
                env['PGPASSWORD'] = self.db_settings['PASSWORD']

                subprocess.run(command, env=env, check=True)
                
                # Upload to S3
                self._upload_to_s3(filepath, f"database/{filename}")
                
                logger.info(f"Database backup created successfully: {filename}")
                return filepath
            except Exception as e:
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                raise
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            raise

    def create_media_backup(self):
        """Create a backup of media files"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"media_backup_{timestamp}.tar.gz"
        filepath = os.path.join(self.backup_path, filename)

        try:
            # Create tar archive of media files
            command = [
                'tar',
                '-czf',
                filepath,
                '-C',
                settings.MEDIA_ROOT,
                '.'
            ]
            
            subprocess.run(command, check=True)
            
            # Upload to S3
            self._upload_to_s3(filepath, f"media/{filename}")
            
            logger.info(f"Media backup created successfully: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Media backup failed: {str(e)}")
            raise

    def restore_database(self, backup_file):
        """Restore database from backup"""
        try:
            if backup_file.startswith('s3://'):
                # Download from S3 first
                local_file = os.path.join(self.backup_path, os.path.basename(backup_file))
                self._download_from_s3(backup_file, local_file)
                backup_file = local_file

            command = [
                'pg_restore',
                f"--host={self.db_settings['HOST']}",
                f"--username={self.db_settings['USER']}",
                f"--dbname={self.db_settings['NAME']}",
                '--clean',
                backup_file
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_settings['PASSWORD']

            subprocess.run(command, env=env, check=True)
            logger.info(f"Database restored successfully from {backup_file}")

        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            raise

    def _upload_to_s3(self, local_path, s3_path):
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(
                local_path,
                self.backup_bucket,
                s3_path,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    def _download_from_s3(self, s3_path, local_path):
        """Download file from S3"""
        try:
            bucket = s3_path.split('s3://')[1].split('/')[0]
            key = '/'.join(s3_path.split('s3://')[1].split('/')[1:])
            
            self.s3_client.download_file(bucket, key, local_path)
        except ClientError as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise

    def cleanup_old_backups(self, days_to_keep=30):
        """Clean up old backups"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            
            # List objects in S3 bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.backup_bucket):
                for obj in page.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=self.backup_bucket,
                            Key=obj['Key']
                        )
                        logger.info(f"Deleted old backup: {obj['Key']}")

        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise 