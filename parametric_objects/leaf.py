import numpy as np
from .spline import Spline2D
import bpy
from mathutils import Vector, Quaternion
import random
from math import radians, sin, cos, sqrt


def create_curve(curvature=0.5):
    nodes = np.array(
        [
            [0.0, 0.0],
            [0.5 + sqrt(curvature / 2), -0.5 + sqrt(curvature / 2)],
            [1, -1],
        ]
    )
    return Spline2D(nodes, degree=2)


def get_generic_control_points(curve: Spline2D, axis="y", segments=10):
    """Get a specific number of control points along a curve

    Args:
        curve (Spline2D): Bezier curve from which to sample
        axis (str, optional): which axis the points should lie on (x or y). Defaults to "y".
        segments (int, optional): How many control points should be sampled. Defaults to 10.

    Returns:
        _type_: list of control points. Each point is a tuple of (x,y,z) coordinates
    """
    all_points = []
    for i in range(0, segments + 1):
        x, y = curve.evaluate(i * (1 / segments))
        if axis == "y":
            all_points.append((x, 0, y))
        elif axis == "x":
            all_points.append((0, x, y))

    return all_points


def blend_value(a, b, alpha):
    return alpha * a + (1.0 - alpha) * b


def blend_contour_with_cylinder(contour: Spline2D, alpha: float, segments: int):
    points = []
    for i in range(segments + 1):
        contour_point_x, contour_point_y = contour.evaluate(i * (1.0 / segments))
        contour_point_x -= 0.5

        cylinder_angle = np.pi / 2.0 + i * (2 * np.pi / segments)
        cylinder_point_x = cos(cylinder_angle)
        cylinder_point_y = sin(cylinder_angle)

        points.append(
            (
                blend_value(contour_point_x, cylinder_point_x, alpha),
                blend_value(contour_point_y, cylinder_point_y, alpha),
            )
        )
    return points


def blend_contours(a, b, alpha, segments=10):
    points = []
    for i in range(segments + 1):
        a_x, a_y = a.evaluate(i * (1.0 / segments))
        b_x, b_y = b.evaluate(i * (1.0 / segments))
        blended_x = blend_value(a_x, b_x, alpha)
        blended_y = blend_value(a_y, b_y, alpha)
        points.append((blended_x, blended_y))
    return points


# TODO: Rename function to reasonable name
def get_control_points(
    leaf_vertical_curve: Spline2D,
    leaf_horizontal_curve: Spline2D,
    leaf_profile: Spline2D,
    leaf_rotation: Spline2D,
    contour: Spline2D,
    blend_contour: Spline2D,
    length,
    width,
    segments=50,
    contour_segments=8,
    internode_width=1,
):
    """Creates list of contour curves.

    Args:
        leaf_curve (Spline2D): Curve which describes the the base curve the leaf follows
        leaf_profile (Spline2D): Curve which describes the width of the leaf at any point of the leaf
        leaf_rotation (Spline2D): Curve which describes the rotation of the leaf at any point of the leaf
        contour (Spline2D): Curve which describes the leafs contour (same for the whole leaf)
        blend_conotour (Spline2D): Curve which describes how the leaf contour is blended with a circle along the leaf
        segments (int, optional): How many segments the leaf consists of (direction of length). Defaults to 15.
        countour_segments (int, optional): How many segments the leaf contour consists of (direction of width). Defaults to 20.

    Returns:
        _type_: Two lists of control points. Each point is a tuple of (x,y,z) coordinates
    """

    # Iterate in length through whole leaf
    all_contours = []
    for i in range(0, segments + 1):
        current_position = i * (1.0 / segments)
        # Get basic center point for current leaf
        base_point_x, base_point_z, angle_vertical_rotation = (
            leaf_vertical_curve.evaluate_with_tangent(current_position)
        )
        _, base_point_y, angle_horizontal_rotation = (
            leaf_horizontal_curve.evaluate_with_tangent(current_position)
        )
        base_point_x *= length
        base_point_y *= length
        base_point_z *= length

        # Get basic parameters for this contour
        alpha = blend_contour.evaluate(current_position)[1]
        if (i < 2) and internode_width is not None:
            radius = (
                internode_width * 2
            )  # Set to internode width to match radius of stem
        elif i == 2:
            radius = (
                max(leaf_profile.evaluate(current_position)[1] * width, 0.01)
                + internode_width * 2
            ) / 2.0
        else:
            radius = max(leaf_profile.evaluate(current_position)[1] * width, 0.01)
        rotation_angle = leaf_rotation.evaluate(current_position)[1]

        # Calculate all points for current contour
        current_contour = []
        contour_points = blend_contour_with_cylinder(contour, alpha, contour_segments)
        for x, y in contour_points:
            x_rotated = cos(rotation_angle) * x - sin(rotation_angle) * y
            y_rotated = sin(rotation_angle) * x + cos(rotation_angle) * y

            # Align contour to leaf direction
            # Not an ideal solution yet, since order of rotations matter
            tmp_point = Vector((0, x_rotated * radius, y_rotated * radius))
            quat = Quaternion((0, 1, 0), -angle_vertical_rotation) @ Quaternion(
                (0, 0, 1), angle_horizontal_rotation
            )
            final = quat @ tmp_point

            final_x = final[0]
            final_y = final[1]
            final_z = final[2]

            current_contour.append(
                (base_point_x + final_x, base_point_y + final_y, base_point_z + final_z)
            )
        all_contours.append(current_contour)

    return all_contours


def create_blender_bezier_curve(control_points, object_name="BezierCurve"):
    # Create a new curve
    curve_data = bpy.data.curves.new(name=object_name, type="CURVE")
    curve_data.dimensions = "3D"

    # Add a spline to the curve
    spline = curve_data.splines.new(type="BEZIER")

    # Ensure the spline has enough points
    spline.bezier_points.add(len(control_points) - 1)

    # Set control point positions
    for i, coord in enumerate(control_points):
        spline.bezier_points[i].co = coord
        spline.bezier_points[i].handle_left_type = "AUTO"
        spline.bezier_points[i].handle_right_type = "AUTO"

    # Create an object with the curve
    curve_obj = bpy.data.objects.new(object_name, curve_data)

    # Link the object to the scene
    bpy.context.scene.collection.objects.link(curve_obj)

    # Select and center the object
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)

    return curve_obj


wheat_young_curves = [
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.3], [1, -0.8]]),
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.5], [1, -1]]),
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.4], [1, -0.9]]),
]

wheat_vertical_curves_lower = [
    # Based on ADEL-Wheat paper (3.5 Plant Geometry)
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.3], [1, -0.8]]),
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.5], [1, -1]]),
    np.array([[0, 0], [0.3, -0.1], [0.5, -0.2], [0.7, -0.4], [1, -0.9]]),
    # Additional variety
    np.array([[0, 0], [0.3, -0.15], [0.5, -0.22], [0.7, -0.38], [1, -0.9]]),
    np.array([[0, 0], [0.3, -0.08], [0.5, -0.22], [0.7, -0.53], [1, -0.96]]),
    np.array([[0, 0], [0.3, -0.13], [0.5, -0.18], [0.7, -0.35], [1, -0.94]]),
]

wheat_vertical_curves_upper = [
    np.array([[0, 0], [0.2, 0], [0.5, -0.3], [0.4, -0.9], [-0.1, -1]]),
    np.array([[0, 0], [0.2, -0.0], [0.2, -0.5], [0.1, -0.8], [-0.1, -1]]),
    np.array([[0, 0], [0.5, -0.5], [0.5, -0.5], [0.1, -0.7], [-0.5, -0.7]]),
]


def interpolate_arrays(array1, array2, alpha):
    """Interpolate between two numpy arrays of the same length based on a factor alpha.

    Args:
        array1 (np.ndarray): First array.
        array2 (np.ndarray): Second array.
        alpha (float): Interpolation factor (0.0 to 1.0).

    Returns:
        np.ndarray: Interpolated array.
    """
    if array1.shape != array2.shape:
        raise ValueError("Arrays must have the same shape for interpolation.")
    return (1 - alpha) * array1 + alpha * array2


def create_wheat_leaf(
    max_width,
    length,
    curvature,
    orientation,
    name,
    rank,
    seed,
    material_name=None,
    internode_width=1,
    senescence=1,
):
    random.seed(seed * (rank + 1))

    leaf_vertical_curve = create_curve(curvature)

    # Interpolate between upright young leaves and flatter senescent leaves
    if rank < 4:
        # Lower leaves
        curve_young_index = random.sample(range(len(wheat_young_curves)), 1)[0]
        curve_senescence_index = random.sample(
            range(len(wheat_vertical_curves_lower)), 1
        )[0]
        wheat_curve = interpolate_arrays(
            wheat_young_curves[curve_young_index],
            wheat_vertical_curves_lower[curve_senescence_index],
            senescence,
        )
        leaf_vertical_curve = Spline2D(wheat_curve)
    else:
        # Upper leaves
        curve_young_index = random.sample(range(len(wheat_young_curves)), 1)[0]
        curve_senescence_index = random.sample(
            range(len(wheat_vertical_curves_upper)), 1
        )[0]
        wheat_curve = interpolate_arrays(
            wheat_young_curves[curve_young_index],
            wheat_vertical_curves_upper[curve_senescence_index],
            senescence,
        )
        leaf_vertical_curve = Spline2D(wheat_curve)

    leaf_profile = Spline2D(
        np.array(
            [
                [0, 0.5],
                [0.1, 1],
                [0.3, 1],
                [0.5, 1],
                [0.7, 1],
                [0.8, 1],
                [1, 0],
            ]
        ),
    )

    final_length = 30  # TODO: Get this as argument of function

    horizontal = random.uniform(-1, 1)
    horizontal *= (float(length) / final_length) * 0.1
    leaf_horizontal_curve = Spline2D(
        np.array([[0, 0], [0.33, 0], [0.66, horizontal * 2.0 / 3.0], [1, horizontal]])
    )

    final_rotation = random.uniform(-1.5 * np.pi, 1.5 * np.pi)
    final_rotation *= float(length) / final_length
    leaf_rotation = Spline2D(
        np.array(
            [
                [0, 0],
                [0.25, 0.25 * final_rotation],
                [0.75, 0.75 * final_rotation],
                [1, final_rotation],
            ]
        )
    )

    leaf_contour = Spline2D(np.array([[0, 0], [0.4, -0.1], [0.6, -0.1], [1, 0]]))
    blend_contour = Spline2D(np.array([[0, 0.6], [0.05, 1], [0.2, 1], [1, 1]]))
    create_leaf(
        leaf_vertical_curve,
        leaf_horizontal_curve,
        leaf_profile,
        leaf_rotation,
        leaf_contour,
        blend_contour,
        orientation,
        max_width,
        length,
        name,
        material_name,
        internode_width,
    )


def create_maize_leaf(
    max_width, length, curvature, orientation, name, rank, seed, material_name=None
):
    random.seed(seed * (rank + 1))

    leaf_vertical_curve = create_curve(curvature)
    leaf_profile = Spline2D(
        np.array(
            [
                [0, 0.1],
                [0.1, 0.1],
                [0.3, 0.7],
                [0.5, 0.9],
                [0.7, 0.3],
                [1, 0],
            ]
        ),
    )

    horizontal = random.uniform(-1, 1)
    leaf_horizontal_curve = Spline2D(
        np.array([[0, 0], [0.33, 0], [0.66, horizontal / 3.0], [1, horizontal * 0.7]])
    )

    num = 12
    rotation_x = [float(x) / num for x in range(num)]
    lower_range = length * 0.1
    upper_range = length * 0.2
    rotation_y = [
        -random.uniform(lower_range, upper_range)
        if x % 2 == 0
        else random.uniform(lower_range, upper_range)
        for x in range(num)
    ]
    leaf_rotation = Spline2D(np.column_stack((rotation_x, rotation_y)))

    leaf_contour = Spline2D(np.array([[0, 0], [0.4, -0.2], [0.6, -0.2], [1, 0]]))
    blend_contour = Spline2D(
        np.array([[0, 0], [0.01, 0.9], [0.05, 0.9], [0.1, 1], [0.2, 1], [1, 1]])
    )
    create_leaf(
        leaf_vertical_curve,
        leaf_horizontal_curve,
        leaf_profile,
        leaf_rotation,
        leaf_contour,
        blend_contour,
        orientation,
        max_width,
        length,
        name,
        material_name,
        internode_width=0.05,
    )


def create_leaf(
    leaf_vertical_curve,
    leaf_horizontal_curve,
    leaf_profile,
    leaf_rotation,
    leaf_contour,
    blend_contour,
    orientation,
    width,
    length,
    name,
    material_name=None,
    internode_width=1,
):
    """Create 3D leaf based on B-Spline parameterization"""

    control_point_segments = get_control_points(
        leaf_vertical_curve,
        leaf_horizontal_curve,
        leaf_profile,
        leaf_rotation,
        leaf_contour,
        blend_contour,
        length,
        width,
        internode_width=internode_width,
    )

    # Put all points in one list
    all_points = []
    for segment in control_point_segments:
        all_points.extend(segment)

    # Create faces
    total_segments_length = len(control_point_segments)
    total_segments_width = len(control_point_segments[0])

    all_faces = []
    all_uvs = []
    for i in range(0, total_segments_length - 1):
        for j in range(0, total_segments_width - 1):
            all_faces.append(
                [
                    i * total_segments_width + j,
                    i * total_segments_width + j + 1,
                    (i + 1) * total_segments_width + j + 1,
                    (i + 1) * total_segments_width + j,
                ]
            )
            tsw = total_segments_width - 1
            tsl = total_segments_length - 1
            all_uvs.append(
                [
                    (j / tsw, i / tsl),
                    ((j + 1) / tsw, i / tsl),
                    ((j + 1) / tsw, (i + 1) / tsl),
                    (j / tsw, (i + 1) / tsl),
                ]
            )

    # Create Blender object
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(f"{name}", mesh)

    # Create the mesh using vertices and faces
    mesh.from_pydata(all_points, [], all_faces)
    mesh.update()

    # Add a UV map to the mesh
    uv_layer = mesh.uv_layers.new(name="CustomUVMap")

    # Assign UV coordinates to the loops
    for face_index, face in enumerate(mesh.polygons):
        for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
            loop_uv = uv_layer.data[loop_index]
            # Use the UVs from the corresponding face
            loop_uv.uv = all_uvs[face_index][loop_index - face.loop_start]

    # Rotate leaf to match orientation at stem
    obj.rotation_euler.y += radians(-90 + 90 * orientation)

    obj.name = name
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for poly in obj.data.polygons:
        poly.use_smooth = True  # Use smooth shading
    obj.select_set(False)

    if material_name is not None:
        obj.data.materials.append(bpy.data.materials[material_name])


def create_debug_leaf(length, max_width, name, material_name=None):
    # Up/Down
    leaf_vertical_curve = Spline2D(np.array([[0, 0], [0.2, 0], [0.7, -0.2], [1, -0.7]]))
    # Left/Right
    leaf_horizontal_curve = Spline2D(np.array([[0, 0], [0.2, 0], [0.7, 0], [1, 0.4]]))
    # Width of leaf
    leaf_profile = Spline2D(
        np.array([[0, 0.1], [0.1, 0.7], [0.7, 1], [0.8, 1], [1, 0]])
    )
    leaf_rotation = Spline2D(np.array([[0, 0], [0.33, 0.33], [0.66, 0.66], [1, 1]]))
    leaf_contour = Spline2D(
        np.array([[0, 0], [0.3, 0.1], [0.5, 0], [0.7, 0.1], [1, 0]])
    )
    blend_contour = Spline2D(np.array([[0, 0], [0.3, 0.8], [0.5, 1], [0.7, 1], [1, 1]]))

    length = 10
    max_width = 2

    create_leaf(
        leaf_vertical_curve,
        leaf_horizontal_curve,
        leaf_profile,
        leaf_rotation,
        leaf_contour,
        blend_contour,
        0,
        max_width,
        length,
        name,
        material_name,
        internode_width=0.2,
    )
