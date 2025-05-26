from ..parametric_objects.spline import Spline2D
import bpy
from mathutils import Vector, Euler, Quaternion
from math import radians, cos, sin
import numpy as np
import time
import random


def create_wheat_head(
    num_spikelets=1, object_name="WheatHeadDefault", tilt=0.0, seed=0
):
    spikelet = bpy.data.objects.get("WheatOriginal")
    random.seed(seed)
    num_spikelets = max(1, int(num_spikelets / 3))

    # Duplicate and set at correct position
    z = 0
    rotation_z = 0
    radius = 0
    z_diff = 0.12

    mean = 0
    std_dev = 8

    all_spikelets = []

    head_tilt = Spline2D(np.array([[0, 0], [0.5, 0], [1, tilt]]), degree=2)
    head_scale = Spline2D(
        np.array(
            [[0, random.uniform(0.3, 0.5)], [1, 1], [0, random.uniform(0.1, 0.3)]]
        ),
        degree=2,
    )

    for i in range(num_spikelets):
        # Create three spikelets at same height with rotation offset
        current_position = float(i) / num_spikelets

        _, _, angle_rotation = head_tilt.evaluate_with_tangent(current_position)

        _, scale = head_scale.evaluate(current_position)

        # Calculate rotation offset
        rotate_x = radians(0)
        if i == num_spikelets - 1:
            rotate_y = radians(-70)
            z -= z_diff * scale * 2
            scale *= 1.2
        elif i == num_spikelets - 2:
            rotate_y = radians(-65)
        else:
            rotate_y = radians(-60)
        rotate_z = radians(rotation_z)

        head_tilt_rotation = Quaternion((0, 1, 0), angle_rotation)

        base_position = Vector(
            (cos(rotate_z) * radius * scale, sin(rotate_z) * radius * scale, z)
        )
        location = head_tilt_rotation @ base_position

        # First spikelet
        rotate_x_1 = rotate_x + radians(random.normalvariate(mean, std_dev))
        rotate_y_1 = rotate_y + radians(random.normalvariate(mean, std_dev))
        rotate_z_1 = (
            rotate_z - radians(45) + radians(random.normalvariate(mean, std_dev))
        )
        rotation = (
            head_tilt_rotation
            @ Euler((rotate_x_1, rotate_y_1, rotate_z_1)).to_quaternion()
        ).to_euler()
        all_spikelets.append(create_spikelet(rotation, location, scale))

        # Second spikelet
        rotate_x_2 = rotate_x + radians(random.normalvariate(mean, std_dev))
        rotate_y_2 = rotate_y + radians(random.normalvariate(mean, std_dev))
        rotate_z_2 = rotate_z + radians(random.normalvariate(mean, std_dev))
        rotation = (
            head_tilt_rotation
            @ Euler((rotate_x_2, rotate_y_2, rotate_z_2)).to_quaternion()
        ).to_euler()
        all_spikelets.append(create_spikelet(rotation, location, scale))

        # Third spikelet
        rotate_x_3 = rotate_x + radians(random.normalvariate(mean, std_dev))
        rotate_y_3 = rotate_y + radians(random.normalvariate(mean, std_dev))
        rotate_z_3 = (
            rotate_z + radians(45) + radians(random.normalvariate(mean, std_dev))
        )
        rotation = (
            head_tilt_rotation
            @ Euler((rotate_x_3, rotate_y_3, rotate_z_3)).to_quaternion()
        ).to_euler()
        all_spikelets.append(create_spikelet(rotation, location, scale))

        # Update angle and height location
        rotation_z += 180
        z += z_diff * scale * 2

    if random.random() < 0.5:
        head_tilt_rotation = Quaternion((0, 1, 0), 0)
        _, scale = head_scale.evaluate(0)
        rotate_z = radians(180)
        base_position = Vector(
            (
                cos(rotate_z) * radius * scale,
                sin(rotate_z) * radius * scale,
                -z_diff * scale * 3,
            )
        )
        location = head_tilt_rotation @ base_position
        rotation = (
            head_tilt_rotation
            @ Euler((radians(0), radians(-65), rotate_z)).to_quaternion()
        ).to_euler()
        all_spikelets.append(create_spikelet(rotation, location, scale))
        if random.random() < 0.5:
            head_tilt_rotation = Quaternion((0, 1, 0), 0)
            _, scale = head_scale.evaluate(0)
            scale *= 0.8
            rotate_z = radians(0)
            base_position = Vector(
                (
                    cos(rotate_z) * radius * scale,
                    sin(rotate_z) * radius * scale,
                    -6 * z_diff * scale,
                )
            )
            location = head_tilt_rotation @ base_position
            rotation = (
                head_tilt_rotation
                @ Euler((radians(0), radians(-65), rotate_z)).to_quaternion()
            ).to_euler()
            all_spikelets.append(create_spikelet(rotation, location, scale))

    # Join into one object
    # bpy.ops.object.select_all(action="DESELECT")
    active_object = all_spikelets[0]
    bpy.context.view_layer.objects.active = active_object
    for spikelet in all_spikelets:
        spikelet.select_set(True)
    bpy.ops.object.join()

    active_object.location = (0, 0, 0)
    active_object.name = object_name
    active_object.select_set(False)


def create_spikelet(rotation_euler, location, scale):
    original_spikelet = bpy.data.objects.get("WheatOriginal")

    new_spikelet = original_spikelet.copy()
    new_spikelet.data = original_spikelet.data.copy()

    new_spikelet.location = location
    new_spikelet.rotation_euler = rotation_euler
    new_spikelet.scale = (scale, scale, scale)

    bpy.context.scene.collection.objects.link(new_spikelet)

    new_spikelet.hide_viewport = False
    new_spikelet.hide_render = False

    return new_spikelet
