import base64
import hashlib
import os
from io import BufferedReader

import requests

from dynamofl.datasets import base_dataset
from dynamofl.Request import _Request

CHUNK_SIZE = 1024 * 1024  # 1MB


class Dataset(base_dataset.BaseDataset):
    def __init__(self, request: _Request, name: str, key: str, file_path: str) -> None:
        self.request = request
        upload_op = self.upload_dataset_file(key=key, dataset_file_path=file_path)
        objKey = upload_op["objKey"]
        key = upload_op["entityKey"]
        config = {"objKey": objKey}
        super().__init__(request=request, name=name, key=key, config=config)

    def calculate_sha1_hash_base64(self, f: BufferedReader):
        # Read the file in chunks
        sha1 = hashlib.sha1()
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            sha1.update(data)
        # Seek back to the beginning of the file
        f.seek(0)
        return base64.b64encode(sha1.digest()).decode("utf-8")

    def upload_dataset_file(self, key: str, dataset_file_path: str):
        with open(dataset_file_path, "rb") as f:
            file_name = os.path.basename(dataset_file_path)
            sha1_hash = self.calculate_sha1_hash_base64(f)
            # Seek back to the beginning of the file
            f.seek(0)

            params = {
                "filename": file_name,
                "key": key,
                "sha1Checksum": sha1_hash,
            }

            res = self.request._make_request(
                "POST", "/dataset/presigned-url", params=params
            )
            presigned_url = res["url"]
            r = requests.put(
                presigned_url,
                data=f,
                headers={
                    # Specifying this header is important for AWS to verify the checksum.
                    # If you'll omit it, you'll receive a signature mismatch error.
                    # If you'll specify it incorrectly, you'll receive a checksum mismatch error.
                    "x-amz-checksum-sha1": sha1_hash,
                },
            )
            return res
