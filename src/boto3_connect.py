import boto3

from config import conf


class awsIamClient:
    def __init__(self) -> None:
        self.client = None

    def connect(self):
        self.client = boto3.client(
            "iam",
            aws_access_key_id=conf["aws_access_key"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )

    def close(self):
        self.client.close()


iam_client = awsIamClient()
