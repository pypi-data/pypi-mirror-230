import logging


class Test:
    def __init__(
        self,
        request,
        name: str,
        model_key: str,
        dataset_id: str,
        test_type: str,
        gpu: object,
        config: list,
    ) -> None:
        self.request = request
        self.name = name
        self.model_key = model_key
        self.dataset_id = dataset_id
        self.attack_type = test_type
        self.test_type = test_type
        self.gpu = gpu
        self.config = config
        self.logger = logging.getLogger("Test")
        if self.gpu is None:
            raise Exception("GPU is not set.")

        params = {
            "name": name,
            "modelKey": model_key,
            "datasetId": dataset_id,
            "type": test_type,
            "gpu": gpu,
            "config": config,
        }
        res = self.request._make_request("POST", "/attack/test", params=params)
        self.test_id = res["id"]
        self.attacks = res["attacks"]
        self.logger.info("Test created: {}".format(res))
