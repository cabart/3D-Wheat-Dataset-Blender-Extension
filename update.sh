#!/bin/bash
echo "Updating 3D Wheat Dataset Blender Extension..."

# Check if blender is installed
if command -v "blender" &> /dev/null; then
    echo "Blender is installed, using the system path."
    BLENDER=blender
else
    BLENDER=~/software/blender-4.2.3-linux-x64/blender

    # Check if the specified Blender path exists
    if [ ! -e "$BLENDER" ]; then
        echo "Blender not found at $BLENDER. Please install Blender or set the correct
path."
        exit 1
    fi
fi

echo "Using Blender at $BLENDER"
$BLENDER --command extension build
$BLENDER --command extension install-file -r user_default ./*.zip -e
