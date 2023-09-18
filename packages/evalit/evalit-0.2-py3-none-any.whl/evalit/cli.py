import click
from evalit.local import launch_eval_gui
from evalit.webui import launch_webui_api_eval

@click.group()
def cli():
    pass


@cli.command()
@click.option('--img_dir', '-i', default=None, help='Path to the root directory of the images.')
@click.option('--out_dir', '-o', default=None, help='Path to the root directory of the output.')
@click.option('--move', '-m', default=False, help='Move the images instead of copying.')
def local(img_dir:str, out_dir:str, move:bool=False):
    """
    Launch the local evaluation GUI; can be used for sorting images or ranking them.
    Uses the default configs.
    :return:
    """
    if not img_dir:
        img_dir = click.prompt('- Path to the root directory of the images', type=int, default="./images")
    if not out_dir:
        out_dir = click.prompt('Path to the root directory of the output.', default="./sorted_images")
    if not move:
        move = click.prompt('Move the images instead of copying.', default=False)
    launch_eval_gui(img_dir, out_dir, move)


@cli.command()
@click.option('--config', '-c', default=None, help='Path to the config file.')
def webuiapi(config:str):
    """
    Call the webuiapi API to generate images and save them with metadata.
    for sample config files see configs folder.
    :param config:
    :return:
    """
    launch_webui_api_eval(config)
