from sawsi.aws import shared
from sawsi.aws.sns import wrapper


class SNSAPI:
    """
    키 등을 관리하는 API
    """
    def __init__(self, region_name, credentials=None):
        """
        :param credentials: {
            "aws_access_key_id": "str",
            "aws_secret_access_key": "str",
            "region_name": "str",
            "profile_name": "str",
        }
        """
        self.boto3_session = shared.get_boto_session(credentials)
        self.region_name = region_name
        self.sns = wrapper.SNS(self.boto3_session, region_name)

    def send_message(self, topic_arn, message):
        response = self.sns.send_message_to_topic(topic_arn, message)
        return response


if __name__ == '__main__':
    pass
