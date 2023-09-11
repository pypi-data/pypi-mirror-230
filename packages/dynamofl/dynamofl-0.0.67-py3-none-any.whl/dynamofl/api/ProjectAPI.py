import base64
import hashlib
import logging
import os
import pathlib
from io import BufferedReader

import requests

from ..Request import _Request

logger = logging.getLogger("ProjectAPI")

CHUNK_SIZE = 1024 * 1024  # 1MB


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


class ProjectAPI:
    def __init__(self, request: _Request):
        self.request = request

    def create_project(self, params=None):
        res = self.request._make_request("POST", "/projects", params=params)
        if not res:
            raise Exception("No response")

        return res

    def get_info(self, key):
        return self.request._make_request("GET", f"/projects/{key}")

    def get_projects(self):
        res = self.request._make_request("GET", "/projects", list=True)
        if not res:
            raise Exception("No response")

        return res

    def complete(self, key):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"isComplete": True}
        )

    def update_rounds(self, key, rounds):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"rounds": rounds}
        )

    def update_schedule(self, key, schedule):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"schedule": schedule}
        )

    def update_paused(self, key, paused):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"paused": paused}
        )

    def update_auto_increment(self, key, auto_increment):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"autoIncrement": auto_increment}
        )

    def update_optimizer_params(self, key, optimizer_params):
        return self.request._make_request(
            "POST", f"/projects/{key}", params={"optimizerParams": optimizer_params}
        )

    def update_contributor(self, key, email, role):
        return self.request._make_request(
            "POST", f"/projects/{key}/contributors/{email}", params={"role": role}
        )

    def set_dynamic_trainer(self, key, dynamic_trainer_key):
        return self.request._make_request(
            "POST",
            f"/projects/{key}/files/dynamic-trainers",
            params={"dynamicTrainerKey": dynamic_trainer_key},
        )

    def delete_project(self, key):
        return self.request._make_request("DELETE", f"/projects/{key}")

    def add_contributor(self, key, email, role="member"):
        return self.request._make_request(
            "POST",
            f"/projects/{key}/contributors",
            params={"email": email, "role": role},
        )

    def delete_contributor(self, key, email):
        return self.request._make_request(
            "DELETE", f"/projects/{key}/contributors", params={"email": email}
        )

    def get_next_schedule(self, key):
        return self.request._make_request("GET", f"/projects/{key}/schedule")

    def increment_round(self, key):
        return self.request._make_request("POST", f"/projects/{key}/increment")

    def get_rounds(self, key):
        return self.request._make_request("GET", f"/projects/{key}/rounds", list=True)

    def get_round(self, key, round):
        return self.request._make_request("GET", f"/projects/{key}/rounds/{round}")

    def get_stats(self, key, params={}):
        return self.request._make_request(
            "GET", f"/projects/{key}/stats", params, list=True
        )

    def get_stats_avg(self, key):
        return self.request._make_request("GET", f"/projects/{key}/stats/avg")

    def get_submissions(self, key, params={}):
        return self.request._make_request(
            "GET", f"/projects/{key}/submissions", params, list=True
        )

    def upload_optimizer(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/optimizers", files={"optimizer": f}
            )

    def upload_file(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/files", files={"file": f}
            )

    def upload_dynamic_trainer(self, key, path):
        with open(path, "rb") as f:
            self.request._make_request(
                "POST", f"/projects/{key}/files/dynamicTrainer", files={"file": f}
            )

    def report_stats(self, key, stats):
        return self.request._make_request(
            "POST", f"/projects/{key}/stats", params=stats
        )

    """
    Bridge APIs
    """

    def create_bridge(self, params):
        return self.request._make_request("POST", "/bridges", params=params)

    def get_bridges_for_datasource(self, datasource_key):
        return self.request._make_request(
            "GET", "/bridges", params={"datasourceKey": datasource_key}
        )

    def get_bridges_for_project(self, project_key):
        return self.request._make_request(
            "GET", "/bridges", {"projectKey": project_key}, list=True
        )

    def get_bridge_of_project_and_datasource(self, project_key, datasource_key):
        res = self.request._make_request(
            "GET",
            "/bridges",
            params={"projectKey": project_key, "datasourceKey": datasource_key},
        )
        if not res:
            raise Exception("No response")

        return res

    """
    Moved from Projects
    """

    def pull_model(
        self,
        project_key,
        filepath,
        datasource_key=None,
        round=None,
        federated_model=None,
    ):
        params = {"usePresignedUrl": True}
        if round is not None:
            params["round"] = round
        if federated_model is not None:
            params["federatedModel"] = federated_model

        if datasource_key is None:
            url = f"/projects/{project_key}/models"
        else:
            url = f"/projects/{project_key}/models/{datasource_key}"
        logger.debug(f"Params: {params}")
        res = self.request._make_request("GET", url, params=params)
        if not res:
            raise Exception(f"No response from {url}")
        download_url = res["url"]
        if "sha1Checksum" not in res:
            logger.warn(
                f"Checksum not found for {filepath} and {download_url}, round: {round}"
            )
        logger.debug(f"Downloading model from {download_url}")
        directory = os.path.dirname(filepath)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        r = requests.get(download_url, stream=True)
        if not r.ok:
            logger.error(r.text)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=None):
                f.write(chunk)

        if "sha1Checksum" in res:
            logger.debug(f"Verifying checksum for {filepath} and {download_url}")
            with open(filepath, "rb") as f:
                sha1_hash = calculate_sha1_hash_base64(f)
            if sha1_hash != res["sha1Checksum"]:
                raise Exception(
                    f"Checksum mismatch for {filepath} and {download_url} and {round}\nExpected: {res['sha1Checksum']}, Actual: {sha1_hash}"
                )
        else:
            logger.warn(f"Checksum not found for {filepath} and {download_url}")

    def push_model(self, project_key, path, datasource_key, round=None, params=None):
        if params is not None:
            self.request._make_request(
                "POST",
                f"/projects/{project_key}/models/{datasource_key}/params",
                params={"params": params},
            )

        if datasource_key is None:
            url = f"/projects/{project_key}/models"
        else:
            url = f"/projects/{project_key}/models/{datasource_key}"
        with open(path, "rb") as f:
            file_name = os.path.basename(path)
            sha1_hash = calculate_sha1_hash_base64(f)
            # Seek back to the beginning of the file
            f.seek(0)

            params = {
                "filename": file_name,
                "datasourceKey": datasource_key,
                "sha1Checksum": sha1_hash,
            }

            if round is not None:
                params["round"] = round

            res = self.request._make_request(
                "GET", f"/projects/{project_key}/models/presigned-url", params=params
            )
            if not res:
                raise Exception(
                    f"No response from /projects/{project_key}/models/presigned-url"
                )
            upload_url = res["url"]
            logger.debug(f"sha1 hash: {sha1_hash}")
            logger.debug(f"Upload url: {upload_url}")
            r = requests.put(
                upload_url,
                data=f,
                headers={
                    # Specifying this header is important for AWS to verify the checksum.
                    # If you'll omit it, you'll receive a signature mismatch error.
                    # If you'll specify it incorrectly, you'll receive a checksum mismatch error.
                    "x-amz-checksum-sha1": sha1_hash,
                },
            )
            if not r.ok:
                logger.error(r.text)
            r.raise_for_status()
            params = {
                "sha1Checksum": sha1_hash,
            }

            if round is not None:
                params["round"] = round

            try:
                self.request._make_request(
                    "POST", url, params=params, print_error=False
                )
            except Exception as e:
                if str(e).find("Model will not be uploaded."):
                    logger.error("Model not sampled.")
                else:
                    raise e
