# 3D Wheat Dataset Blender Extension

A blender extension for creating and rendering 3D wheat plants.

## Prerequisites

- Python installation with Pip (for Python Wheels download)
- Blender (Version 4.2.3 LTS, uses Python version 3.11 internally)

## Installation

  - Install `Dynamic Sky` extension (Version 1.0.6 at time of writing)
  - Run `./install.sh` installation script (downloads the Python wheels and creates a zip file of the extension)
  - Use one of the following two options to add the extension to Blender:
    1. Manual: In Blender > Preferences > Install from disk... > (Choose zipped file in parent directory)
    2. Script (Linux only): Run `./update.sh`
  - Check rendering devices uses GPU (Preferences > System > Cycles Render Devices > CUDA)
- Python dependencies
  - They come packaged within the extension (wheel files). If this breaks in the future update the wheel versions e.g. see versions for [scipy](https://pypi.org/project/scipy/#files). `pdate the version numbers also in the blender_manifest.toml`

Notes: Downloading the repository directly from Github does not include the realistic ground texture due to licensing reasons.

## Update

- Uninstall `lsystem_extension` extension in Blender, create/get new zip file of extension and install as described above

## Realistic Ground Texture

To get realistic ground textures add 'Ground_Pack.blend' to 'materials' folder. It can be purchased from `https://superhivemarket.com/products/8k-ground-material-pack-for-environment-design`.

## Scripted Rendering in Background

Plant canopies can be created and rendered using a config file and a Python scripts. See `pipeline_scrips` for examples.

```bash
blender --background --python <python-script-to-run-at-startup> -- -a <Argument value> -b <Another argument value>
```

### Known bugs

- A '.png' is written during rendering which should not be the case (only visible during rendering)

### TODO Clean up

- [ ] Add image textures for wheat model
- [ ] Add Windows support for installation scripts