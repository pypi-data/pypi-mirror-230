"""
Utility methods
"""


class TrainArgs:
    def __init__(
        self,
        datasource_key=None,
        federated_model_path=None,
        new_model_path=None,
        project=None,
        project_info=None,
        hyper_param_values=None,
    ):
        self.datasource_key = datasource_key
        self.federated_model_path = federated_model_path
        self.new_model_path = new_model_path
        self.project = project
        self.project_info = project_info
        self.hyper_param_values = hyper_param_values


class TestArgs:
    def __init__(
        self, datasource_key=None, federated_model_path=None, project_info=None
    ):
        self.datasource_key = datasource_key
        self.federated_model_path = federated_model_path
        self.project_info = project_info


class Helpers:
    @staticmethod
    def save_state_dict_tensorflow(model):
        state_dict = {}
        for index, layer in enumerate(model.layers):
            layer_class = model.layers[index].__class__.__name__
            raw_weights = model.layers[index].weights
            layer_weights = []
            for weight_tensors in raw_weights:
                layer_weights.append(weight_tensors.numpy())
            state_dict[layer.name] = [layer_class, layer_weights]
        return state_dict

    @staticmethod
    def load_state_dict_tensorflow(model, state_dict):
        for index, layer in enumerate(model.layers):
            raw_weights = model.layers[index].weights
            for index, weight_tensors in enumerate(raw_weights):
                weight_tensors.assign(state_dict[layer.name][1][index])
