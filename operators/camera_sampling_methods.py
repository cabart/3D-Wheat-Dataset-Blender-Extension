from math import radians
from ..properties.enum_objects import RenderMode
import bpy
import numpy as np
from mathutils import Vector, Quaternion, Matrix
import random
from scipy.spatial.transform import Rotation as R
import os

# How to add a camera placement method:
# 1. Add a new method in this file
# 2. Add the method to the camera placement dictionary in globals.py for making the sampling method available
#
# Each camera placement method get as an input if it is a training or test placement
# Each camera placement method should return a list of camera positions and orientations


def circle_on_sphere_sampling(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps

    if mode == RenderMode.TEST:
        num_points = camera_props.test_frames_total
    elif mode == RenderMode.TRAIN:
        num_points = camera_props.train_frames_total

    radius = (
        camera_props.radius_train
        if mode == RenderMode.TRAIN
        else camera_props.radius_test
    )
    center = (
        camera_props.center_train
        if mode == RenderMode.TRAIN
        else camera_props.center_test
    )
    cap_angle = (
        camera_props.cap_angle_train
        if mode == RenderMode.TRAIN
        else camera_props.cap_angle_test
    )
    cap_angle = radians(cap_angle)

    # Generate points on a unit circle
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    points = np.array([[np.cos(angle), np.sin(angle), 0] for angle in angles])

    # Scale and translate points according to camera properties
    cameras = []
    for point in points:
        location = point * np.cos(np.pi / 2 - cap_angle) * radius + np.array(
            [0, 0, np.cos(cap_angle) * radius]
        )
        direction = center - location
        direction = Vector(direction)
        quaternion_rotation = direction.to_track_quat("-Z", "Y")
        cameras.append((location, quaternion_rotation))

    return cameras


def random_sampling_hemisphere(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps

    if mode == RenderMode.TEST:
        num_points = camera_props.test_frames_total
    elif mode == RenderMode.TRAIN:
        num_points = camera_props.train_frames_total

    radius = (
        camera_props.radius_train
        if mode == RenderMode.TRAIN
        else camera_props.radius_test
    )
    center = (
        camera_props.center_train
        if mode == RenderMode.TRAIN
        else camera_props.center_test
    )

    # Generate random points on the unit hemisphere
    points = np.random.randn(num_points, 3)
    points /= np.linalg.norm(points, axis=1)[:, np.newaxis]
    points[:, 2] = np.abs(points[:, 2])

    # Scale and translate points according to camera properties
    cameras = []
    for point in points:
        location = point * radius + center
        direction = center - location
        direction = Vector(direction)
        quaternion_rotation = direction.to_track_quat("-Z", "Y")
        cameras.append((location, quaternion_rotation))

    return cameras


def get_total_frames(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TEST:
        return camera_props.test_frames_total
    elif mode == RenderMode.TRAIN:
        return camera_props.train_frames_total


def fibonacci_lattice_sampling_hemisphere(mode: RenderMode):
    return fibonacci_lattice_hemisphere(mode, get_total_frames(mode))


def fibonacci_lattice_sampling_hemisphere_inverse_spiral(mode: RenderMode):
    return fibonacci_lattice_hemisphere(
        mode, get_total_frames(mode), inverse_direction=True
    )


def fibonacci_lattice_sampling_cap(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TEST:
        cap_angle = camera_props.cap_angle_test
    elif mode == RenderMode.TRAIN:
        cap_angle = camera_props.cap_angle_train
    return fibonacci_lattice_cap(
        mode, get_total_frames(mode), radians(cap_angle), inverse=False
    )


def fibonacci_lattice_sampling_cap_inverse(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TEST:
        cap_angle = camera_props.cap_angle_test
    elif mode == RenderMode.TRAIN:
        cap_angle = camera_props.cap_angle_train
    return fibonacci_lattice_cap(
        mode, get_total_frames(mode), radians(cap_angle), inverse=True
    )


def fibonacci_lattice_hemisphere(mode: RenderMode, num_points, inverse_direction=False):
    return fibonacci_lattice_cap(
        mode, num_points, np.pi / 2, inverse_direction=inverse_direction
    )


def fibonacci_lattice_cap(
    mode: RenderMode, num_points, cap_angle, inverse=False, inverse_direction=False
):
    """Generate points on a capped hemisphere according to fibonacci latice distribution.

    Args:
        num_points (_type_): number of generated points
        cap_angle (_type_): angle of cutoff
        inverse (bool, optional): Instead of the cap generate points on the side. Defaults to False.

    Returns:
        _type_: _description_
    """

    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TRAIN:
        radius = camera_props.radius_train
        center = camera_props.center_train
    elif mode == RenderMode.TEST:
        radius = camera_props.radius_test
        center = camera_props.center_test

    # Calculate all points on the unit hemisphere
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio
    golden_angle = 2 * np.pi / phi

    cos_alpha = np.cos(cap_angle)  # Cosine of the cap angle

    cameras = []
    for i in range(num_points):
        if inverse:
            cos_theta = cos_alpha - (cos_alpha - 0) * (i + 0.5) / num_points
        else:
            cos_theta = 1 - (1 - cos_alpha) * (i + 0.5) / num_points

        theta = np.arccos(cos_theta)  # Latitude
        phi = (i * golden_angle) % (2 * np.pi)  # Longitude

        if inverse_direction:
            # Spiral in inverse direction and rotate by 180 degrees
            phi = -phi + np.pi

        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)  # Hemisphere restriction: z >= 0

        # Scale and translate points according to camera properties
        location = np.array(
            [x * radius + center[0], y * radius + center[1], z * radius + center[2]]
        )

        # Set direction to view at center of sphere
        direction = np.array([center[0], center[1], center[2]]) - location
        direction = Vector(direction)
        quaternion_rotation = direction.to_track_quat("-Z", "Y")
        cameras.append((location, quaternion_rotation))
    return cameras


def FIP_cameras(mode: RenderMode):
    extension_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fip_cameras_folder = os.path.join(extension_folder, "fip_cameras", "12")

    # Convert size from meter to centimeter
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TRAIN:
        camera_props.radius_train = 100
    elif mode == RenderMode.TEST:
        camera_props.radius_test = 100

    return colmap_cameras_path(mode, fip_cameras_folder)


def colmap_cameras(mode: RenderMode):
    camera_props = bpy.context.scene.CameraRenderProps

    if mode == RenderMode.TRAIN:
        colmap_folder = camera_props.colmap_path_train
    elif mode == RenderMode.TEST:
        colmap_folder = camera_props.colmap_path_test

    if not os.path.exists(colmap_folder):
        raise ValueError(f"Colmap path does not exist: {colmap_folder}")

    return colmap_cameras_path(mode, colmap_folder)


def colmap_cameras_path(mode: RenderMode, colmap_folder):
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TRAIN:
        radius = camera_props.radius_train
        center = camera_props.center_train
    elif mode == RenderMode.TEST:
        radius = camera_props.radius_test
        center = camera_props.center_test

    images_file = os.path.join(colmap_folder, "images.txt")
    cameras = []
    image_information_line = False  # Only every second line is a camera position
    with open(images_file) as file:
        for line in file:
            line = line.rstrip()
            if line.startswith("#") or line == "" or image_information_line:
                image_information_line = False
                continue
            else:
                image_information_line = True

            # Read single camera location and rotation
            parts = line.split()
            image_id = int(parts[0])
            qw, qx, qy, qz = map(float, parts[1:5])
            tx, ty, tz = map(float, parts[5:8])
            camera_id = int(parts[8])
            image_name = parts[9]

            # if image_id >= 12:
            #    continue

            Q_blender = Quaternion((qx, qw, -qz, qy))
            t_blender = Quaternion((qw, qx, qy, qz)).to_matrix().transposed() @ Vector(
                (-tx * radius, -ty * radius, -tz * radius)
            )
            t_blender = Vector(
                (
                    t_blender[0] + center[0],
                    t_blender[1] + center[1],
                    t_blender[2] + center[2],
                )
            )

            cameras.append((t_blender, Q_blender))

    # Reset number of frames to number of cameras in file
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TRAIN:
        camera_props.train_frames_total = len(cameras)
    elif mode == RenderMode.TEST:
        camera_props.test_frames_total = len(cameras)

    cameras_file = os.path.join(colmap_folder, "cameras.txt")
    with open(cameras_file) as file:
        for line in file:
            line = line.rstrip()
            if line.startswith("#"):
                continue
            else:
                parts = line.split()
                camera_id = int(parts[0])
                model = parts[1]
                width = int(parts[2])
                height = int(parts[3])
                params = list(map(float, parts[4:]))

                if model != "PINHOLE":
                    raise ValueError(f"Unsupported camera model: {model}")
                else:
                    if len(params) != 4:
                        raise ValueError(f"Unsupported camera parameters: {params}")
                    fx = params[0]
                    fy = params[1]
                    cx = params[2]
                    cy = params[3]

                    scene = bpy.context.scene
                    camera = scene.camera

                    scene.render.resolution_x = width
                    scene.render.resolution_y = height
                    scene.render.resolution_percentage = 100
                    scene.render.pixel_aspect_x = 1
                    scene.render.pixel_aspect_y = 1

                    camera_data = camera.data
                    camera_data.type = "PERSP"
                    camera_data.lens_unit = "MILLIMETERS"

                    camera_data.sensor_fit = "HORIZONTAL"
                    camera_data.sensor_width = 36
                    camera_data.sensor_height = (
                        36 * height / width
                    )  # Not necessary if sensor_fit is set to HORIZONTAL
                    camera_data.lens = fx * 36 / width

                    # Should the results be inverted?
                    shift_x = (width / 2 - cx) / width
                    shift_y = -(height / 2 - cy) / height

                    camera_data.shift_x = shift_x
                    camera_data.shift_y = shift_y

                break

    return cameras
