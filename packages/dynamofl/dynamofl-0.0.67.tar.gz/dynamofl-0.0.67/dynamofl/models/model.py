import logging

from dynamofl.Request import _Request

from dynamofl.datasets.dataset import Dataset


class Model:
    def __init__(
        self,
        request,
        name: str,
        key: str,
        type: str,
        id: str = None,
        config: object = {},
    ) -> None:
        self.key = key
        self.name = name
        self.config = config
        self.request = request
        self.type = type
        self.logger = logging.getLogger("Model")
        self.id = id

    @staticmethod
    def create_ml_model_and_get_id(
        request: _Request, name: str, key: str, type: str, config
    ):
        params = {"key": key, "name": name, "config": config, "type": type}
        created_model = request._make_request("POST", "/ml-model", params=params)
        return created_model["_id"]
