# 3D Wheat Dataset Blender Extension

A blender extension for creating and rendering 3D wheat plants.

## Installation

- Installation of Blender (Version 4.2.3 LTS, uses Python version 3.11 internally)
  - Install `Dynamic Sky` extension (Version 1.0.6 at time of writing)
  - Create Zip file of whole repository and in Blender > Preferences > Install from disk... > (Choose zipped file)
    - Python wheels are stored on Github using GIT LFS. To get them correctly, first install git-lfs and only then clone the repository and create a zip file
    - Downloading the repository as a zip file directly from github will unfortunately not correctly download git lfs files
  - Check rendering devices uses GPU (Preferences > System > Cycles Render Devices > CUDA)
- Python dependencies
  - They come packaged within the extension (wheel files). If this breaks in the future either update the wheel files e.g. for [scipy](https://pypi.org/project/scipy/#files). Or remove them from the manifest and install them directly in the Blender Python environment.

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

- [ ] Fix maize model
