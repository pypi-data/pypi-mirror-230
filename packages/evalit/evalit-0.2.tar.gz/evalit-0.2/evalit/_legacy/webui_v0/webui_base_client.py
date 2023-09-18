import requests
from typing import List, Dict


class WebuiBaseClient:
    def __init__(self, url: str):
        """Initialize the API with the given URL."""
        self.url = url.rstrip('/')

    def _get_available_models(self) -> List[Dict]:
        """Get a list of available models."""
        response = requests.get(f'{self.url}/sdapi/v1/sd-models')
        return response.json()

    def get_available_models(self) -> List[str]:
        """Get a list of available models."""
        response = self._get_available_models()

        models_list = []
        for model in response:
            models_list.append(model['model_name'])

        return models_list

    def update_options(self, options: Dict[str, str]) -> None:
        """Update options using the provided dictionary."""
        opt = requests.get(url=f'{self.url}/sdapi/v1/options')
        opt_json = opt.json()

        original_keys = set(opt_json.keys())
        updated_keys = set(options.keys())

        if not updated_keys.issubset(original_keys):
            raise ValueError("Provided options do not overwrite the original options.")

        opt_json.update(options)
        requests.post(url=f'{self.url}/sdapi/v1/options', json=opt_json)

    def sanity_check(self, expected_options: Dict[str, str]) -> None:
        """Check that the current options match the expected options."""
        response = requests.get(url=f'{self.url}/sdapi/v1/options')
        current_options = response.json()

        for key, value in expected_options.items():
            actual_value = current_options.get(key)
            if not actual_value.startswith(value) or (actual_value[len(value):] and actual_value[len(value)] != '.'):
                raise ValueError(
                    f"Option '{key}' does not match the expected value. Expected: {value}, Actual: {actual_value}")

        print("Sanity check passed. Options are updated correctly.")

    def switch_checkpoint(self, model_name: str) -> None:
        """Switch to the given model and verify."""
        available_models = self.get_available_models()
        if model_name not in available_models:
            raise ValueError(f"Model '{model_name}' not found in the available models list.")

        new_opt_dict = {'sd_model_checkpoint': model_name}
        self.update_options(new_opt_dict)
        self.sanity_check(new_opt_dict)
        print(f"Switched to model '{model_name}' successfully.")


if __name__ == '__main__':
    url = "http://127.0.0.1:7860"
    api = WebuiBaseClient(url)

    # Get a list of available models
    models = api.get_available_models()  # has "animefull"
    api.switch_checkpoint('animefull')

    print("D")
