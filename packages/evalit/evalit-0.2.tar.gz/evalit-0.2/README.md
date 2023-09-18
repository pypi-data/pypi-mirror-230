# eval-it

Eval-it 用于训练模型的评估。

![Python](https://img.shields.io/badge/python-3.10-blue.svg) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Features

local:
- 本地使用的简单图片分拣GUI
- AD / 左右箭头移动, 自定义的快捷键放到对应目录
- [UI长这样](https://imgur.com/yjVnJvH)

webuiapi:
- batch xyz plot

## Usage

install:
```bash
pip install evalit
```

to launch a eval gui:
```
PS C:\Users\Andre> eval-it local --help
Usage: eval-it local [OPTIONS]

  Launch the local evaluation GUI; can be used for sorting images or ranking
  them. Uses the default configs. :return:

Options:
  -i, --img_dir TEXT  Path to the root directory of the images.
  -o, --out_dir TEXT  Path to the root directory of the output.
  -m, --move BOOLEAN  Move the images instead of copying.
  --help              Show this message and exit.
```
```bash
eval-it local -i E:\_benchmark\small -o E:\_benchmark_done  -m False
```

to generate images with webuiapi:
```
eval-it webuiapi --config configs/webui_step_conf.yaml
```
