#!/bin/bash

# Download Python Wheels
python -m pip download --only-binary :all: --dest wheels --no-cache numpy==2.2.3
python -m pip download --only-binary :all: --dest wheels --no-cache pillow==11.1.0
python -m pip download --only-binary :all: --dest wheels --no-cache scipy==1.15.2
python -m pip download --only-binary :all: --dest wheels --no-cache tqdm==4.67.1