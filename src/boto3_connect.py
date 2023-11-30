import boto3

from .config import conf


class awsSdk:
    def __init__(self) -> None:
        self.client = None

    def iam_connect(self):
        self.client = boto3.client(
            "iam",
            aws_access_key_id=conf["aws_access_key_id"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )

    def trail_connect(self):
        self.client = boto3.client(
            "cloudtrail",
            region_name="us-east-1",
            aws_access_key_id=conf["aws_access_key_id"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )

    def session_connect(self):
        self.session = boto3.Session(
            aws_access_key_id=conf["aws_access_key_id"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )

    def iam_close(self):
        self.client.close()


aws_sdk = awsSdk()
