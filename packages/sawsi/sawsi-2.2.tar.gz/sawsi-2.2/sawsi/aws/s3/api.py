from sawsi.aws import shared
from sawsi.aws.s3 import wrapper
from secrets import token_urlsafe


class S3API:
    """
    S3 를 활용하는 커스텀 ORM 클래스
    """
    def __init__(self, bucket_name, credentials=None, region=shared.DEFAULT_REGION):
        """
        :param bucket_name:
        :param credentials: {
            "aws_access_key_id": "str",
            "aws_secret_access_key": "str",
            "region_name": "str",
            "profile_name": "str",
        }
        """
        self.boto3_session = shared.get_boto_session(credentials)
        self.cache = {}
        self.bucket_name = bucket_name
        self.s3 = wrapper.S3(self.boto3_session, region=region)

    def init_s3_bucket(self, acl='private'):
        """
        실제 버킷 생성
        :return:
        """
        return self.s3.init_bucket(self.bucket_name, acl)

    def upload_binary(self, file_name, binary):
        return self.s3.upload_binary(self.bucket_name, file_name, binary)

    def delete_binary(self, file_name):
        return self.s3.delete_binary(self.bucket_name, file_name)

    def download_binary(self, file_name):
        return self.s3.download_binary(self.bucket_name, file_name)

    def upload_file_and_return_url(self, file_bytes, extension, content_type, use_accelerate=False):
        """
        파일을 업로드하고 URL 을 반환합니다.
        만천하에 공개되기 때문에 공개해도 괜찮은 파일만 사용해야 함.
        :param file_bytes:
        :param extension:
        :param content_type:
        :param use_accelerate:
        :return:
        """
        if use_accelerate:
            base_url = f'https://{self.bucket_name}.s3-accelerate.amazonaws.com/'  # 전송 가속화
        else:
            base_url = f'https://{self.bucket_name}.s3.{self.s3.region}.amazonaws.com/'
        file_id = f'{token_urlsafe(32)}.{extension}'
        response = self.s3.upload_file(self.bucket_name, file_bytes, file_id, content_type)
        return base_url + file_id
