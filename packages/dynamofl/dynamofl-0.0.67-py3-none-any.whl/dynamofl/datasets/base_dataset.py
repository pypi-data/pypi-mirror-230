import logging


class BaseDataset:
    def __init__(
        self,
        request,
        key,
        name,
        config,
    ) -> None:
        self.key = key
        self.name = name
        self.request = request
        self.logger = logging.getLogger("BaseDataset")
        params = {"key": key, "name": name, "config": config}
        created_dataset = self.request._make_request("POST", "/dataset", params=params)
        self._id = created_dataset["_id"]
        self.logger.info("Dataset created: {}".format(created_dataset))
