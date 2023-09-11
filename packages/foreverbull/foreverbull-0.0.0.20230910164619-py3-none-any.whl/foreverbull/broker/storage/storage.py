import os

import minio

from .backtest import Backtest


class Storage:
    def __init__(self, address, access_key, secret_key, secure=False):
        self.client = minio.Minio(address, access_key=access_key, secret_key=secret_key, secure=secure)
        self.backtest: Backtest = Backtest(self.client)

    @classmethod
    def from_environment(cls, env=os.environ):
        return cls(
            address=env.get("STORAGE_ENDPOINT", "localhost:9000"),
            access_key=env.get("STORAGE_ACCESS_KEY", "minioadmin"),
            secret_key=env.get("STORAGE_SECRET_KEY", "minioadmin"),
            secure=bool(env.get("STORAGE_SECURE", False)),
        )

    def create_bucket(self, bucket_name):
        self.client.make_bucket(bucket_name)
