import base64
import hashlib
import os
from io import BufferedReader
from dynamofl.Request import _Request

import requests

from dynamofl.datasets.dataset import Dataset
from dynamofl.models.model import Model

CHUNK_SIZE = 1024 * 1024  # 1MB


class LocalModel(Model):
    def __init__(
        self,
        request,
        name: str,
        key: str,
        id: str,
        config,
    ) -> None:
        self.request = request
        super().__init__(
            request=request,
            name=name,
            key=key,
            config=config,
            type="LOCAL",
            id=id,
        )

    @staticmethod
    def create_and_upload(
        request: _Request,
        name: str,
        key: str,
        model_file_path: str,
        config,
    ):
        upload_response = LocalModel.upload_model_file(
            request=request, key=key, model_file_path=model_file_path
        )
        new_key = upload_response["entityKey"]
        config["objKey"] = upload_response["objKey"]

        model_id = Model.create_ml_model_and_get_id(
            request=request,
            name=name,
            key=new_key,
            type="LOCAL",
            config=config,
        )

        return LocalModel(
            request=request,
            name=name,
            key=new_key,
            config=config,
            id=model_id,
        )

    @staticmethod
    def calculate_sha1_hash_base64(f: BufferedReader):
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

    @staticmethod
    def upload_file(request: _Request, key: str, file_path: str, endpoint_url: str):
        with open(file_path, "rb") as f:
            file_name = os.path.basename(file_path)
            sha1_hash = LocalModel.calculate_sha1_hash_base64(f)
            # Seek back to the beginning of the file
            f.seek(0)
            params = {
                "filename": file_name,
                "key": key,
                "sha1Checksum": sha1_hash,
            }
            res = request._make_request("POST", endpoint_url, params=params)
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

    @staticmethod
    def upload_model_file(request: _Request, key: str, model_file_path: str):
        res = LocalModel.upload_file(
            request, key, model_file_path, "/ml-model/presigned-url"
        )
        return res
