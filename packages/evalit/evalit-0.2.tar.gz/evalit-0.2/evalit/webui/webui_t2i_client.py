import os
import json
import base64
import requests
from io import BytesIO
from datetime import datetime
from omegaconf import OmegaConf
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from typing import List, Dict, Tuple
from tqdm.auto import tqdm

from evalit.webui.webui_options_manager import OptionsManager
from evalit.webui.img_grid_maker import GridMaker


@dataclass
class GenerationConfig:
    """
    传给webui api的参数, 完整参数列表可以在向api发送请求后, 从返回的json中获取
    """
    width: int = 512
    height: int = 768
    sampler_name: str = "DPM++ 2S a Karras"
    steps: int = 25
    cfg_scale: int = 7
    enable_hr: bool = False
    denoising_strength: int = 1
    seed: int = 8888
    batch_size: int = 1
    n_iter: int = 1
    send_images: bool = True
    y_axis_param: str = 'cfg_scale'


class WebuiT2iClient:
    def __init__(self, baseurl: str = "http://127.0.0.1:7860"):
        self.baseurl = baseurl
        self.endpoint: str = f"{baseurl}/sdapi/v1/txt2img"
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}

    def generate(self, prompt: str, negative_prompt: str,
                 config: GenerationConfig) -> Tuple[List[Image.Image], List[str], Dict]:
        request_body = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            **config.__dict__
        }
        # Override the y_axis_param dynamically if it exists in config
        if config.y_axis_param in request_body:
            request_body[config.y_axis_param] = config.__dict__[config.y_axis_param]

        response = requests.post(self.endpoint, json=request_body, headers=self.headers)

        if response.status_code != 200:
            raise RuntimeError(f"Error! Status Code: {response.status_code}, Response: {response.text}")

        json_response = response.json()
        images_base64 = json_response.get("images", [])
        images_pil = [self._decode_base64_image(i) for i in images_base64]
        api_args = json_response.get("parameters", {})
        info = json_response.get("info", "")

        parsed_info = json.loads(info)
        param_strs = parsed_info.get("infotexts", [])

        return images_pil, param_strs, api_args

    @staticmethod
    def _decode_base64_image(img_base64: str) -> Image.Image:
        img_data = base64.b64decode(img_base64)
        return Image.open(BytesIO(img_data))


def get_timestamp():
    return datetime.now().strftime('%Y%m%d_%H-%M-%S')


def save_images(checkpoint: str, api_args: Dict, images: List[Image.Image],
                params: List[str], img_dir: str, config: GenerationConfig) -> List[str]:
    os.makedirs(img_dir, exist_ok=True)
    saved_files = []  # List to hold saved file paths
    y_axis_value = api_args.get(config.y_axis_param, 'unknown_value')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    for i, (image, param) in enumerate(zip(images, params)):
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", param)
        pnginfo.add_text("api_args", json.dumps(api_args))

        file_name = f"{checkpoint}_{config.y_axis_param}{y_axis_value}_{timestamp}_{i}.png"
        file_path = os.path.join(img_dir, file_name)
        image.save(file_path, pnginfo=pnginfo)
        saved_files.append(file_path)  # Add the saved file path to the list

    return saved_files


def stitch(rows: List[List[Image.Image]], x_titles: List[str], y_titles: List[str],
           caption: str = None) -> Image.Image:
    """
    takes a 2d list of images (one row of images per sublist), stitches into a large image by rules
    :param rows: 每行n张PIL.Image.Image
    :param x_titles: list of x-axis titles
    :param y_titles: list of y-axis titles
    :param caption: caption for the stitched image (optional)
    :return:
    """
    flat_images = [image for row in rows for image in row]
    x_len = len(x_titles)
    y_len = len(y_titles)

    if x_len == 0 or y_len == 0:
        raise ValueError("Number of rows and columns should be greater than zero.")

    grid_maker = GridMaker()
    stitched_image = grid_maker.concat_images(flat_images, x_len, x_titles, y_titles, caption=caption)
    return stitched_image


def stitch_and_save_images(y_axis_values, image_paths_data, stitch_dir, config: GenerationConfig):
    os.makedirs(stitch_dir, exist_ok=True)
    for prompt, checkpoints_data in image_paths_data.items():
        rows = []
        y_titles = []
        x_titles = list(checkpoints_data.keys())

        for y_value in y_axis_values:
            row = []
            for checkpoint in x_titles:
                file_paths = checkpoints_data[checkpoint].get(y_value, [])
                images = [Image.open(path) for path in file_paths]  # Read the images from the file paths
                row.extend(images)
            rows.append(row)
            y_titles.append(f"{config.y_axis_param}:{y_value}")

        stitched_image = stitch(rows, x_titles, y_titles, caption=prompt)
        img_path = os.path.join(stitch_dir, f"stitched_{prompt}_{get_timestamp()}.png")
        stitched_image.save(img_path)


def driver(y_axis_values, checkpoint_list, client: WebuiT2iClient, config: GenerationConfig, prompts, img_dir,
           stitch_dir):
    # initialize options manager
    client_base_url = client.baseurl
    options_manager = OptionsManager(client_base_url)

    # Initialize tqdm progress bar
    total_progress = len(checkpoint_list) * len(prompts) * len(y_axis_values)
    pbar = tqdm(total=total_progress, desc="Generating Images", ascii=True)

    # Data structure to hold images, organized by prompt, checkpoint, and y_axis_values
    image_paths_data = {prompt: {} for prompt in prompts}  # New dictionary to hold image paths

    # Generate images and save them with metadata
    for checkpoint in checkpoint_list:
        options_manager.set_checkpoint(checkpoint)  # Set the checkpoint

        # Get the checkpoint string
        options = options_manager.get_options()
        checkpoint_str = options.get('sd_model_checkpoint').split(" ")[0]

        for prompt in prompts:
            for y_value in y_axis_values:
                # Dynamically set the value for y_axis_param
                setattr(config, config.y_axis_param, y_value)

                images, param_strs, api_args = client.generate(prompt, "Negative Prompt", config)

                if checkpoint not in image_paths_data[prompt]:
                    image_paths_data[prompt][checkpoint] = {}

                # Save individual images with metadata; adds the saved file paths to the image_paths_data dictionary
                saved_file_paths = save_images(checkpoint_str, api_args, images, param_strs, img_dir, config)
                image_paths_data[prompt][checkpoint][y_value] = saved_file_paths  # Store file paths

                # Update tqdm progress bar
                pbar.update(1)

    # Close tqdm progress bar
    pbar.close()

    # Stitch and save images
    stitch_and_save_images(y_axis_values, image_paths_data, stitch_dir, config)


def launch_webui_api_eval(config_path: str):
    """
    :param config_path: 例子见 configs/webui_step_config.yaml as a example; 完整参数列表见 GenerationConfig;
    :return:
    """

    # Load the configuration
    conf = OmegaConf.load(config_path)

    # Initialize GenerationConfig from YAML
    config = GenerationConfig(**conf.generation_config)

    # Initialize WebuiT2iClient
    client = WebuiT2iClient(baseurl=conf.baseurl)

    # Run the driver function
    driver(
        y_axis_values=conf.y_axis_params,
        checkpoint_list=conf.checkpoint_list,
        client=client,
        config=config,
        prompts=conf.prompts,
        img_dir=conf.img_dir,
        stitch_dir=conf.stitch_dir
    )


if __name__ == "__main__":
    config_file = r"D:\CSC\eval-it\configs\webui_step_conf.yaml"
    launch_webui_api_eval(config_file)
