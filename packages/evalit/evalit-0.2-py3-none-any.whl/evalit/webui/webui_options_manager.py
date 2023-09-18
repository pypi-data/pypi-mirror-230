import requests
import difflib
import time
from typing import List, Dict, Optional, Union

from unibox import UniLogger

class OptionsManager:

    DEFAULT_URL = "http://127.0.0.1:7860"
    def __init__(self, baseurl: str = None, logger: UniLogger = None):
        """
        :param conf: OmegaConf DictConfig object containing the baseurl key;
        """
        self.baseurl = baseurl if baseurl else self.DEFAULT_URL
        self.endpoint = f"{self.baseurl}/sdapi/v1"
        self.logger = logger if logger else UniLogger(file_suffix="OptionsManager")

    def send_request(self, method: str, url: str, json_data=None) -> dict:
        if method == "GET":
            response = requests.get(url=f"{self.endpoint}{url}")
        elif method == "POST":
            response = requests.post(url=f"{self.endpoint}{url}", json=json_data)
        else:
            raise ValueError("Invalid HTTP method")

        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")

        return response.json()

    def get_sd_models(self) -> List[Dict]:
        return self.send_request("GET", "/sd-models")

    def set_options(self, options: dict) -> dict:
        return self.send_request("POST", "/options", json_data=options)

    def get_options(self) -> Dict:
        return self.send_request("GET", "/options")

    def find_closest_checkpoint(self, checkpoint_name: str, checkpoints: List[Dict]) -> Optional[Dict]:
        str_similarity = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
        closest_checkpoint = max(checkpoints, key=lambda x: str_similarity(checkpoint_name, x["model_name"]), default=None)
        return closest_checkpoint

    def set_checkpoint(self, checkpoint_name: str, find_closest=True):
        checkpoint_name = checkpoint_name.lower()
        checkpoints = self.get_sd_models()
        found_checkpoint = None

        if checkpoint_name in [checkpoint["model_name"].lower() for checkpoint in checkpoints]:
            found_checkpoint = next(filter(lambda x: x["model_name"].lower() == checkpoint_name, checkpoints))
        elif find_closest:
            found_checkpoint = self.find_closest_checkpoint(checkpoint_name, checkpoints)

        if found_checkpoint:
            found_checkpoint_name = found_checkpoint['model_name']
            self.logger.info(f"Loading checkpoint {found_checkpoint_name}")

            # Set the checkpoint
            options = {"sd_model_checkpoint": found_checkpoint_name}
            self.set_options(options)

            # Verify that the checkpoint was set correctly
            self.logger.info("sleeping & Verifying checkpoint...")
            time.sleep(1)
            current_options = self.get_options()
            self.logger.info(f"Current setting is {current_options.get('sd_model_checkpoint')}")

        else:
            self.logger.error("Checkpoint not found")


if __name__ == "__main__":
    manager = OptionsManager(baseurl="http://localhost:7860")
    # manager.set_checkpoint("pne30_offset")
    manager.set_checkpoint("twitter-checkpoint-two")
