import base64
import requests
from PIL import Image
from io import BytesIO
from evalit.webui import WebuiXyzArgs


class WebuiT2iClient:
    def __init__(
        self,
        prompt="",
        negative_prompt="",
        sampler_name="Euler",
        xyz_script_args=None,
        url="http://127.0.0.1:7860/sdapi/v1/txt2img",
    ):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.request_body = {
            "enable_hr": False,
            "seed": -1,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 15,
            "cfg_scale": 7,
            "denoising_strength": 0.7,
            "width": 480,
            "height": 872,
            "sampler_index": "Euler",
            "send_images": True,
            "script_name": "x/y/z plot",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "sampler_name": sampler_name,
            "script_args": list(xyz_script_args) if xyz_script_args else [],
            # Add default values for other parameters if needed
        }

    def set_prompt(self, prompt):
        self.request_body["prompt"] = prompt

    def set_negative_prompt(self, negative_prompt):
        self.request_body["negative_prompt"] = negative_prompt

    def set_sampler_name(self, sampler_name):
        self.request_body["sampler_name"] = sampler_name

    def set_script_args(self, script_args):
        self.request_body["script_args"] = script_args

    def send_request(self):
        response = requests.post(self.url, json=self.request_body, headers=self.headers)

        if response.status_code == 200:
            print("Client has received the request successfully.")
            return self.fetch_results(response.json())
        else:
            print(
                "Error! Status Code:", response.status_code, "Response:", response.text
            )
            return None

    def fetch_results(self, response_json):
        images_base64 = response_json.get("images", [])
        images_pil = [
            self._decode_base64_image(img_base64) for img_base64 in images_base64
        ]
        response_json["images"] = images_pil
        return response_json

    @staticmethod
    def _decode_base64_image(img_base64):
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data))
        return img


if __name__ == "__main__":

    # x_axis=["Steps", "12, 20"]
    # x_axis=["CFG Scale", "6, 8"]
    # x_axis=["Checkpoint name", "awesome,amazing"]


    args = WebuiXyzArgs(
        x_axis=["Checkpoint name", "twitter-checkpoint-two-fp16-clip-fix.safetensors [076d862c05],TropiK_neo2_fp16.ckpt [0e3b2c1e36]"]
        # y_axis=["Seed", "12345, 54321"],
        # z_axis=["Nothing", ""],
    )
    args_list = list(args)


    # 可用: 1, 8 (2图),  "pen_feel.ckpt [54131aa569],pai115_noema_novae.ckpt [76963b8c78]

    for i in range (0, 39):
        args_list[0] = i

        client = WebuiT2iClient(
            prompt="1girl",
            negative_prompt="(worst quality, large head, low quality, extra digits:1.4), :o",
            sampler_name="DPM++ 2S a Karras",
            xyz_script_args=args_list,
        )

        res = client.send_request()

        if not res:
            print("No response received.")
            continue
        images = res["images"]
        if not images:
            print("No images returned.")
            continue
        else:
            print("Received images: at index", i) # 0, 8, 27
            for i, img in enumerate(images):
                img.show()
            print("Here are the images:")


    print("DONE")
