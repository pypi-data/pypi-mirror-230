import tempfile
from sawsi.aws import shared


class S3:
    def __init__(self, boto3_session, region=shared.DEFAULT_REGION):
        self.client = boto3_session.client('s3', region_name=region)
        self.resource = boto3_session.resource('s3', region_name=region)
        self.region = region

    def init_bucket(self, bucket_name, acl='private'):
        self.create_bucket(bucket_name, acl)

    def create_bucket(self, bucket_name, acl='private'):
        response = self.client.create_bucket(
            ACL=acl,
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': self.region
            }
        )
        return response

    def upload_binary(self, bucket_name, file_name, binary):
        with tempfile.TemporaryFile() as tmp:
            tmp.write(binary)
            tmp.seek(0)
            response = self.client.upload_fileobj(tmp, bucket_name, file_name)
            return response

    def delete_binary(self, bucket_name, file_name):
        return self.resource.Object(bucket_name, file_name).delete()

    def download_binary(self, bucket_name, file_name):
        with tempfile.NamedTemporaryFile() as data:
            self.client.download_fileobj(bucket_name, file_name, data)
            data.seek(0)
            return data.read()

    def delete_bucket(self, bucket_name):
        response = self.client.delete_bucket(
            Bucket=bucket_name
        )
        return response

    def upload_file(self, bucket_name, file_bytes, file_name, content_type='text/html'):
        """
        파일을 올림, 컨텐츠 타입 고려함
        :param bucket_name:
        :param file_bytes:
        :param file_name:
        :param content_type:
        :return:
        """
        response = self.client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type,
            ACL='public-read',
        )
        return response
