#!/bin/bash

rm -rf wheels

# Download Python Wheels
python -m pip download --only-binary :all: --python-version 3.11 --dest wheels --no-cache numpy==2.3.2
python -m pip download --only-binary :all: --python-version 3.11 --dest wheels --no-cache pillow==11.3.0
python -m pip download --only-binary :all: --python-version 3.11 --dest wheels --no-cache scipy==1.16.1
python -m pip download --only-binary :all: --python-version 3.11 --dest wheels --no-cache tqdm==4.67.1

python installation/update_blender_manifest.py

# Compress this directory into a tar.gz file
zip -rq ../3d-Wheat-Dataset-Blender-Extension.zip . 

echo "----"
echo "Manually install the extension in Blender by going to 
echo "    Edit > Preferences > Add-ons > Install and selecting the zip file."
echo "Alternatively, you can run the update.sh script to automate the installation process."
echo "----"