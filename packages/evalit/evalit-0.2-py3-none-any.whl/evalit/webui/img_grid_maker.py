import os.path
from typing import List
from PIL import Image, ImageFont, ImageDraw
import math
import textwrap
# from util import utils
from tqdm.auto import tqdm
from unibox import UniLogger


import datetime

def get_date_str():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    return date_str

class GridMaker:
    def __init__(self):
        self.padding = 5
        self.font = ImageFont.truetype("arial.ttf", size=50)
        self.font.size = 50
        # print(type(self.font))
        # print(dir(self.font))

        self.comment_font = ImageFont.truetype("arial.ttf", size=35)
        self.font_color = (200, 200, 200)  # 字体颜色
        self.bg_color = (33, 33, 33)  # 底色
        self.logger = UniLogger()

    def concat_images(
            self,
            binary_imgs: List,
            x_count: int = -1,
            x_tags_list: List[str] = None,
            y_tags_list: List[str] = None,
            caption: str = "",
            save_image: bool = False,
    ) -> Image:
        x_len = x_count if x_count != -1 else round(math.sqrt(len(binary_imgs)))

        bbox = self.font.getbbox("x")
        height = bbox[3] - bbox[1]
        padding = height // 2  # Replacing getsize with getbbox

        tags = x_tags_list if x_tags_list else [""]
        y_tags = y_tags_list if y_tags_list else [""]

        # Calculate dimensions of the resulting image grid
        width, height = binary_imgs[0].size
        y_len = math.ceil((len(binary_imgs) / x_len))
        label_height = max(height // 10, 10)

        y_label_width_font = max([self.font.getbbox(tag)[2] - self.font.getbbox(tag)[0] for tag in
                                  y_tags]) + padding  # Replacing getsize with getbbox
        y_label_width = max(y_label_width_font, label_height)

        # Create a new image with the appropriate dimensions and background color
        xy_width = width * x_len + padding * (x_len - 1) + y_label_width
        xy_height = height * y_len + label_height + padding
        result = Image.new("RGB", (xy_width, xy_height), self.bg_color)

        # Draw the labels on the top of each column
        draw = ImageDraw.Draw(result)
        for i in range(x_len):
            label = tags[i] if i < len(tags) else ""
            label_size = (self.font.getbbox(label)[2] - self.font.getbbox(label)[0],
                          self.font.getbbox(label)[3] - self.font.getbbox(label)[1])  # Replacing getsize with getbbox
            offset = (i) * width + (width - label_size[0]) // 2 + y_label_width
            draw.text((offset, padding), label, font=self.font, fill=self.font_color)

        # Draw the labels on the left of each row
        for i in range(y_len):
            label = y_tags[i] if i < len(y_tags) else ""
            label_size = (self.font.getbbox(label)[2] - self.font.getbbox(label)[0],
                          self.font.getbbox(label)[3] - self.font.getbbox(label)[1])  # Replacing getsize with getbbox
            offset = label_height + i * (height + padding) + (height - label_size[1]) // 2
            draw.text((padding, offset), label, font=self.font, fill=self.font_color)

        # Paste each image into the appropriate location in the grid
        for i in tqdm(range(len(binary_imgs)), desc="making grid"):
            x = ((i % x_len)) * (width + padding) + y_label_width
            y = (i // x_len) * (height + padding) + label_height + padding
            result.paste(binary_imgs[i], (x, y))

        if not caption:
            the_caption = f"{get_date_str} | {len(binary_imgs)} images concatenated"
        else:
            the_caption = caption

        captioned = self.add_caption(result, the_caption)

        if save_image:
            self.logger.info("saving image")
            if not os.path.exists("images"):
                os.mkdir("images")
            filename = f"{get_date_str()}_len{len(binary_imgs)}.jpg"
            result.save(os.path.join("images", filename), quality=95)

        return captioned

    def add_caption(self, image: Image, caption_text: str) -> Image:
        """给一张图片的底部添加更多小字信息"""
        # Define the font for the caption text
        font = self.comment_font
        if image.width < 1200:
            self.comment_font.size = 18

        bbox = font.getbbox("x")
        height = bbox[3] - bbox[1]
        padding = height  # Increasing padding to prevent truncation

        max_width = int(image.width * 0.98)

        # Wrap the caption text into multiple lines if it is too long to fit on a single line
        lines = textwrap.wrap(caption_text, width=max_width // (bbox[2] - bbox[0]))

        # Create a new image with the same width as the original image, and a height that will fit the caption text
        caption_height = len(lines) * height + padding * 2  # Increase padding here if necessary
        caption_image = Image.new(
            "RGB", (image.width, caption_height), color=self.bg_color
        )

        # Draw the caption text onto the new image with padding
        draw = ImageDraw.Draw(caption_image)
        for i, line in enumerate(lines):
            draw.text(
                (padding, i * height + padding),
                line,
                font=font,
                fill=self.font_color,
            )

        # Combine the original image and the caption image into a new image
        new_image = Image.new(
            "RGB", (image.width, image.height + caption_height + padding), color=self.bg_color  # Increase padding here if necessary
        )
        new_image.paste(image, (0, 0))
        new_image.paste(caption_image, (0, image.height))

        return new_image



if __name__ == "__main__":
    images = [
        Image.open("img1.png"),
        Image.open("img2.png"),
        Image.open("img3.png"),
    ] * 3
    tags = ["Tag1", "Tag2", "Tag3"]
    y_tags = ["Row 1", "Row 2", "Row 3"]  # List of tags for the rows

    x_len = 3  # Number of columns in the resulting image grid

    image_grid = GridMaker()
    result_image = image_grid.concat_images(images, x_len, tags, y_tags)
    result_image.save("result.png")  # Save the resulting image to a file