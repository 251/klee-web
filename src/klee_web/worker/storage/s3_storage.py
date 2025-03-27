import boto3
import os


class S3Storage():
    BUCKET = 'klee-output'

    def __init__(self, access_key=None, secret_key=None):
        s3_access_key = access_key or os.environ['AWS_ACCESS_KEY']
        s3_secret_key = secret_key or os.environ['AWS_SECRET_KEY']

        self.s3 = boto3.client('s3', aws_access_key_id=s3_access_key,
                               aws_secret_access_key=s3_secret_key)
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        """Create the bucket if it doesn't already exist."""
        existing_buckets = [
            bucket['Name'] for bucket in self.s3.list_buckets()['Buckets']
        ]
        if S3Storage.BUCKET not in existing_buckets:
            self.s3.create_bucket(Bucket=S3Storage.BUCKET)

    def store_file(self, file_path):
        """Upload a file to S3 and return its public URL."""
        file_name = os.path.basename(file_path)

        self.s3.upload_file(
            file_path,  # Local file path
            S3Storage.BUCKET,  # S3 bucket name
            file_name,  # S3 key (file name)
            ExtraArgs={'ACL': 'public-read'}  # Make the file public
        )

        # Generate and return a public URL
        return f"https://{S3Storage.BUCKET}.s3.amazonaws.com/{file_name}"
