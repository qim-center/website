+++
title = "InSegt3D"
description = "Interactive 3D segmentation tool providing real-time full image segmentation from minimal user input."
authors = ["William Laprade"]
tags = ["Segmentation", "GUI", "Deep Learning"]
image = "images/tools/insegt3d.png"
source_url = "https://github.com/qim-center/insegt3d"
+++

## Overview

InSegt3D is an interactive segmentation tool that utilizes the U-Net deep learning architecture to quickly and efficiently segment 3D volumetric images. By providing a few scribbles, you get a complete segmentation of your 3D dataset. It utilizes the Zarr storage format to enable the segmentation of extremely large images.

## Features

- Real-time segmentation updates powered by deep learning
- Interactive scribble-based annotation
- Works with large 3D volumetric data via Zarr storage format
- Minimal user input required — just a few scribbles per class
- GPU-accelerated inference
- Supports up to 10 segmentation classes

## Installation

Install directly from GitHub with pip:

```bash
pip install git+https://github.com/qim-center/insegt3d
```

## Usage

After installation, run the tool from the command line:

```bash
insegt3d --project_folder "path/to/project_folder" --num_classes 2
```

This will create a project folder at the specified location, set up a user interface for a two-class segmentation task, and provide a link that can be opened in any web browser. To segment more than two classes, increase the `--num_classes` argument (maximum 10). A random port is used by default, but you can specify one with `--port 9090`. Use `insegt3d --help` for a full list of optional arguments.

The tool expects data to be stored in multi-scale Zarr files with a `uint8` datatype. Chunk sizes of 32×32×32 or 64×64×64 are optimal for efficient navigation.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Left click | Paint displayed color |
| Shift + Left Click | Push overlay onto annotation map |
| Mouse Wheel | Adjust brush size |
| C | Cycle through colors |
| D | Toggle prediction overlay |
| Ctrl + Z | Undo last paint stroke |
| Ctrl + Y | Redo last paint stroke |
| Ctrl + Left Click + Drag | Pan / translate view |
| Ctrl + Mouse Wheel | Zoom in / out |
| Ctrl + Right Click + Drag | Scroll through slices |
| Ctrl + Middle Mouse + Drag | Rotate plane |

## Setup Guides

### Local (Conda)

```bash
conda create --name unet python=3.11
conda activate unet
pip install git+https://github.com/qim-center/insegt3d
insegt3d --project_folder "path/to/project_folder" --num_classes 2
```

### DTU Thinlinc (GPU cluster)

```bash
sxm2sh -X
conda create --name unet python=3.11
conda activate unet
pip install git+https://github.com/qim-center/insegt3d
insegt3d --project_folder "path/to/project_folder" --num_classes 2
```

> **Note:** On Thinlinc, the interface is only accessible from the browser inside the ThinLinc Client.
