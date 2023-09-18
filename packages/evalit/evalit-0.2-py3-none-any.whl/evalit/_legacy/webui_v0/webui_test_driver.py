from evalit.webui import WebuiXyzArgs, WebuiT2iClient
from tqdm import tqdm
import json
import os
import logging
from typing import List, Optional

class WebuiTestDriver:
    def __init__(
        self,
        prompts_file: str,
        output_folder: str,
        checkpoint_names_str: str,
        url: str = "http://127.0.0.1:7860/sdapi/v1/txt2img",
        sampler_name: str = "Euler",
        y_axis: Optional[List[str]] = None,
        z_axis: Optional[List[str]] = None,
        negative_prompt: Optional[str] = None,
    ):
        """Initialize the test driver."""
        self.prompts_file = prompts_file
        self.output_folder = output_folder
        self.checkpoint_names_str = checkpoint_names_str
        self.url = url
        self.sampler_name = sampler_name
        self.y_axis = y_axis if y_axis else ["Nothing", ""]
        self.z_axis = z_axis if z_axis else ["Nothing", ""]
        self.negative_prompt = negative_prompt if negative_prompt else ""
        logging.basicConfig(filename="webui_test_driver.log", level=logging.INFO)

    def run_test(self):
        """Run the test by processing the prompts."""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        with open(self.prompts_file, "r") as file:
            prompts = file.readlines()

        for prompt in tqdm(prompts, desc="Processing Prompts"):
            prompt = prompt.strip()
            try:
                self.process_prompt(prompt)
            except Exception as e:
                logging.error(f"Error processing prompt '{prompt}': {str(e)}")

    def process_prompt(self, prompt: str):
        """Process a single prompt."""
        args = WebuiXyzArgs(
            x_axis=["Checkpoint name", self.checkpoint_names_str],
            y_axis=self.y_axis,
            z_axis=self.z_axis,
        )
        args_list = list(args)

        client = WebuiT2iClient(
            prompt=prompt,
            negative_prompt=self.negative_prompt,
            sampler_name=self.sampler_name,
            xyz_script_args=args_list,
            url=self.url,
        )

        res = client.send_request()
        if res:
            self.save_results(res, prompt)

    def save_results(self, results, prompt: str):
        """Save the results to the output folder."""
        images = results.pop("images", [])
        json_file_path = os.path.join(self.output_folder, f"{prompt}.json")
        with open(json_file_path, "w") as file:
            json.dump(results, file)

        for i, img in enumerate(images):
            image_file_path = os.path.join(self.output_folder, f"{prompt}_{i}.png")
            img.save(image_file_path)

        logging.info(f"Results for prompt '{prompt}' saved successfully.")


if __name__ == "__main__":

    checkpoints = [
        "twitter-checkpoint-two-fp16-clip-fix",
        "pne30_offset",
        ]

    test_driver = WebuiTestDriver(
        prompts_file="D:\CSC\eval-it\_data\prompts_1691290044.txt",
        output_folder="output",
        checkpoint_names_str=", ".join(checkpoints),
    )
    test_driver.run_test()
