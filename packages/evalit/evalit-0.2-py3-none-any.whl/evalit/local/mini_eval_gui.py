"""
setup:
    pip install pysimplegui tqdm pillow pyperclip

usage:
    1. modify category_mapping to set directory
    2. input root_dir; set move=True if to move original images instead of copy
    3. press keys defined in category_mapping to move images to corresponding dirs
    4. use [a / d] or [← / →] to switch images
"""

import os
import json
import platform
import pyperclip
from tqdm.auto import tqdm
from PIL import Image, ImageTk
import PySimpleGUI as sg
import shutil


class ImageViewer:
    MAX_IMAGE_SIZE = (1300, 1300)
    PREVIEW_COUNT = 4
    METRICS_SIZE = (70, 25)

    def __init__(self, root_folder, category_mapping, move=False):
        self.root_folder = root_folder
        self.category_mapping = category_mapping
        self.move = move
        self.image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp', '.ico', '.jfif', '.svg')
        self.images = self.load_images()
        self.current_image = 0
        self.window = self.create_window()
        self.preview_cache = {}

    def load_images(self):
        """Load images from the root folder."""
        image_paths = [os.path.join(self.root_folder, f) for f in os.listdir(self.root_folder) if
                       f.lower().endswith(self.image_extensions)]
        return image_paths

    def get_image_info(self, image_path):
        """Retrieve image information such as file path, size, and resolution."""
        image = Image.open(image_path)
        return {
            "File path": image_path,
            "Size": f"{os.path.getsize(image_path) / 1024:.2f}KB",
            "Resolution": {"width": image.width, "height": image.height},
        }

    def get_resized_image(self, image_path, max_size):
        """Resize the image to the specified size, using caching to optimize repeated resizing."""
        cache_key = (image_path, max_size)
        if cache_key in self.preview_cache:
            return self.preview_cache[cache_key]
        image = Image.open(image_path)
        image.thumbnail(max_size, Image.LANCZOS)
        self.preview_cache[cache_key] = image
        return image

    def update_main_image(self):
        """Update the launch_webui_api_eval image and its metrics in the window."""
        image_path = self.images[self.current_image]
        main_image_data = self.get_resized_image(image_path, self.MAX_IMAGE_SIZE)
        main_metrics = json.dumps(self.get_image_info(image_path), indent=4)
        self.window['image'].update(data=ImageTk.PhotoImage(main_image_data))
        self.window['info'].update(main_metrics)

    def update_previews(self):
        preview_indexes = list(
            range(self.current_image - self.PREVIEW_COUNT, self.current_image + self.PREVIEW_COUNT + 1))
        preview_indexes = [idx % len(self.images) for idx in preview_indexes]

        # Reverse the order of previous previews before updating
        for i, idx in enumerate(preview_indexes[:self.PREVIEW_COUNT][::-1]):
            image_path = self.images[idx]
            preview_image = self.get_resized_image(image_path, (100, 100))
            self.window[f'prev_{i}'].update(data=ImageTk.PhotoImage(preview_image))

        # Update current preview
        image_path = self.images[preview_indexes[self.PREVIEW_COUNT]]
        curr_preview_image = self.get_resized_image(image_path, (100, 100))
        self.window['curr'].update(data=ImageTk.PhotoImage(curr_preview_image))

        # Update next previews
        for i, idx in enumerate(preview_indexes[self.PREVIEW_COUNT + 1:]):
            image_path = self.images[idx]
            preview_image = self.get_resized_image(image_path, (100, 100))
            self.window[f'preview_{i}'].update(data=ImageTk.PhotoImage(preview_image))

    def copy_image_to_category(self, key):
        for category, mapping in self.category_mapping.items():
            if mapping['key'] == key.upper():
                folder_path = mapping['folder_path']
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                new_filepath = os.path.join(folder_path, os.path.basename(self.images[self.current_image]))
                if self.move:
                    shutil.move(self.images[self.current_image], new_filepath)
                    print(f"Key pressed: {key}, moving {self.images[self.current_image]} to {new_filepath}")
                    self.images.pop(self.current_image)  # Remove the image from the list
                    if self.current_image >= len(self.images):
                        self.current_image = 0
                else:
                    shutil.copy(self.images[self.current_image], new_filepath)
                    print(f"Key pressed: {key}, copying {self.images[self.current_image]} to {new_filepath}")
                break

    def create_window(self):
        prev_elements = [sg.Image(key=f'prev_{i}') for i in range(self.PREVIEW_COUNT)]
        curr_element = [sg.Image(key='curr')]
        preview_elements = [sg.Image(key=f'preview_{i}') for i in range(self.PREVIEW_COUNT)]
        hotkey_text = "\n".join(
            [f"{mapping['key']}: {category}" for category, mapping in self.category_mapping.items()])
        right_column = [
            [sg.Text('Prev:'), sg.Column([prev_elements])],
            [sg.Text('Curr:'), sg.Column([curr_element])],
            [sg.Text('Next:'), sg.Column([preview_elements])],
            [sg.Text(hotkey_text, key='custom_text')],
            [sg.Multiline("", size=self.METRICS_SIZE, key='info', disabled=True)],
            [sg.Button('Prev [A]'), sg.Button('Next [D]'),
             sg.Button('Copy Path', key='copy_path', button_color=('white', 'green'))]  # Updated button
        ]
        layout = [
            [sg.Image(key='image'), sg.Column(right_column)]
        ]
        window = sg.Window('Image Viewer', layout, return_keyboard_events=True, finalize=True)
        window.bind('<Right>', '-NEXT-')  # Bind the arrow keys
        window.bind('<Left>', '-PREV-')
        return window

    def copy_path_to_clipboard(self):
        """Copy the image file path to the clipboard, considering the OS type."""
        image_path = self.images[self.current_image]
        # Convert the path according to the operating system
        copied_path = image_path.replace("\\", "/") if platform.system() == "Linux" else image_path
        pyperclip.copy(copied_path)
        print(f"Image path copied to clipboard: {copied_path}")

    def main(self):
        progress_bar = tqdm(total=len(self.images), desc="Tagging Progress")

        self.update_main_image()
        self.update_previews()

        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            if event in ('Next', '-NEXT-', 'd', 'D'):
                self.current_image += 1
                if self.current_image >= len(self.images):
                    self.current_image = 0
            elif event in ('Prev', '-PREV-', 'a', 'A'):
                self.current_image -= 1
                if self.current_image < 0:
                    self.current_image = len(self.images) - 1
            elif event == 'copy_path':  # Updated event handling
                self.copy_path_to_clipboard()
            elif any(mapping['key'] == event.upper() for mapping in self.category_mapping.values()):
                self.copy_image_to_category(event)
                progress_bar.update(1)
                continue

            self.update_main_image()
            self.update_previews()

        progress_bar.close()
        self.window.close()


def generate_category_mapping(category_key_pairs, output_dir):
    """
    Generate a category mapping dictionary.

    :param category_key_pairs: List of (category, key) pairs.
    :param output_dir: The root output directory.
    :return: A dictionary mapping each category to its key and folder path.
    """
    return {
        category: {
            'key': key,
            'folder_path': os.path.join(output_dir, category)
        }
        for category, key in category_key_pairs
    }


def launch_eval_gui(img_root_dir:str, output_root_dir:str, move_images:bool=False):
    """

    :param img_root_dir: where images are located
    :param output_root_dir: where sorted images will be moved to
    :param move_images: whether to move images or copy images
    :return:
    """
    category_key_pairs = [
        ("good", "Q"),
        ("cliche", "W"),
        ("wrong", "E"),
        ("bad", "R"),
        ("nuance", "F")
    ]
    category_mapping = generate_category_mapping(category_key_pairs, output_root_dir)
    viewer = ImageViewer(img_root_dir, category_mapping, move=move_images)
    viewer.main()


if __name__ == "__main__":
    img_root_folder = r"D:\Andrew\Pictures\表情包\done"
    output_root_dir = r"E:\Generated\COMFY_RANDOM"
    move_images = False
    launch_eval_gui(img_root_folder, output_root_dir)
