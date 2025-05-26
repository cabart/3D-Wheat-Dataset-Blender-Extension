import sys
import argparse
import bpy
import os
import shutil
import json
from mathutils import Vector


def clear_directory(path):
    if os.path.exists(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


def load_config(config_path):
    with open(config_path, "r") as file:
        return json.load(file)


# Run by using `blender --background --python various_images_pipeline.py -- -n 10 -p /path/to/save -c /path/to/config.json`
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_images", type=int, nargs="+", required=True)
    parser.add_argument("-c", "--config_file", type=str, required=True)
    parser.add_argument("-p", "--save_path", type=str, required=True)

    args = parser.parse_known_args(argv)[0]

    if not os.path.exists(args.save_path):
        print("Create save directory")
        os.makedirs(args.save_path)
    if os.listdir(args.save_path):
        response = input(
            f"The directory {args.save_path} is not empty. Do you want to overwrite its contents? (y/n): "
        )
        if response.lower() in ["y", "yes"]:
            clear_directory(args.save_path)
        else:
            print("Exiting...")
            sys.exit(1)

    plant_props = bpy.context.scene.PlantProps
    camera_props = bpy.context.scene.CameraRenderProps

    # Load parameters from the config file
    config = load_config(args.config_file)

    plant_props.derivation_length = config["plants"]["iteration_step"]
    plant_props.canopy_seed = config["plants"]["canopy_seed"]
    plant_props.model = config["plants"]["model"]
    plant_props.canopy_plants_x = config["plants"]["canopy_plants_x"]
    plant_props.canopy_plants_y = config["plants"]["canopy_plants_y"]
    plant_props.canopy_distance_x = config["plants"]["canopy_distance_x"]
    plant_props.canopy_distance_y = config["plants"]["canopy_distance_y"]

    # Train cameras
    camera_props.camera_placement_train = config["rendering"]["camera_placement_train"]
    camera_props.radius_train = config["rendering"]["radius_train"]
    camera_props.center_train = Vector(config["rendering"]["center_train"])
    camera_props.train_frames_total = config["rendering"]["train_frames_total"]

    # Test cameras
    camera_props.camera_placement_test = config["rendering"]["camera_placement_test"]
    camera_props.radius_test = config["rendering"]["radius_test"]
    camera_props.center_test = Vector(config["rendering"]["center_test"])
    camera_props.test_frames_total = config["rendering"]["test_frames_total"]

    camera_props.render_samples = config["rendering"]["render_samples"]
    camera_props.point_cloud_samples = config["rendering"]["point_cloud_samples"]

    camera_props.render = True

    # Generate the lsystem strings
    bpy.ops.lsys.generate()

    plant_props.iteration_step = config["plants"]["iteration_step"]

    # For each number of train images, render the images
    for current_num_images in args.num_images:
        camera_props.train_frames_total = current_num_images
        base_path = args.save_path
        camera_props.save_path = os.path.join(
            base_path, f"train_images_{current_num_images}"
        )

        # Draw the plant models
        bpy.ops.lsys.draw()

        # Render the images
        bpy.ops.lsys.render()

        # Save config file for specific run

        config["rendering"]["train_frames_total"] = current_num_images
        with open(
            os.path.join(camera_props.save_path, "input_config.json"), "w"
        ) as file:
            json.dump(config, file, indent=4)
