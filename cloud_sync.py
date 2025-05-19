# cloud_sync.py
import boto3
from db_manager import DBManager


class CloudSync:
    def __init__(self, db_manager: DBManager, aws_config):
        self.db = db_manager
        # Create a copy of aws_config to avoid modifying the original
        s3_client_params = aws_config.copy()
        # Pop 'bucket' as it's not a direct client config, but used in operations
        self.bucket_name = s3_client_params.pop('bucket', None)

        if not self.bucket_name:
            # If you intend CloudSync to always require a bucket,
            # you might want to raise an error here.
            # For bypassing, we'll allow it to be None if aws_config doesn't have it.
            print("Warning: S3 bucket name not found in aws_config for CloudSync.")

        self.s3 = boto3.client("s3", **s3_client_params)

    def upload_db(self):
        self.s3.upload_file(self.db.db_path, self.bucket_name, "free_games.db")

    def download_db(self):
        self.s3.download_file(self.bucket_name, "free_games.db", self.db.db_path)
