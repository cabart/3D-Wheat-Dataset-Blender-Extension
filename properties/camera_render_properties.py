from ..properties.enum_objects import RenderMode
import bpy
from .. import globals


class CameraRenderProps(bpy.types.PropertyGroup):
    seed: bpy.props.IntProperty(
        name="Camera Seed",
        description="Seed for random camera placement",
        default=1,
        min=1,
        soft_max=1000,
    )

    camera_placement_train: bpy.props.EnumProperty(
        name="Train Camera Placement",
        description="Camera placement for training images rendering",
        items=[(x, x, x) for x in globals.camera_placements.keys()],
        # update=update_selection  # Optional: Callback function when the selection changes
    )

    camera_placement_test: bpy.props.EnumProperty(
        name="Test Camera Placement",
        description="Camera placement for testing images rendering",
        items=[(x, x, x) for x in globals.camera_placements.keys()],
        # update=update_selection  # Optional: Callback function when the selection changes
    )

    radius_train: bpy.props.FloatProperty(
        name="Sphere Radius",
        description="Radius of camera sphere",
        default=200,
        min=0.01,
        soft_max=100,
    )

    radius_test: bpy.props.FloatProperty(
        name="Sphere Radius",
        description="Radius of camera sphere",
        default=200,
        min=0.01,
        soft_max=100,
    )

    center_train: bpy.props.FloatVectorProperty(
        name="Value of the center",
        description="Center of the sphere",
        default=(0, 0, 0),
        size=3,
        unit="LENGTH",
    )

    center_test: bpy.props.FloatVectorProperty(
        name="Value of the center",
        description="Center of the sphere",
        default=(0, 0, 0),
        size=3,
        unit="LENGTH",
    )

    cap_angle_train: bpy.props.FloatProperty(
        name="Cutoff angle for capped hemisphere",
        description="",
        default=45,
        min=0.01,
        max=90,
    )

    cap_angle_test: bpy.props.FloatProperty(
        name="Cutoff angle for capped hemisphere",
        description="",
        default=45,
        min=0.01,
        max=90,
    )

    colmap_path_train: bpy.props.StringProperty(
        name="Colmap path train",
        description="",
        default="/home/cabart/Documents/MasterThesisData/camera_setup_fip/translated_positions",
        subtype="FILE_PATH",
    )

    colmap_path_test: bpy.props.StringProperty(
        name="Colmap path test",
        description="",
        default="/home/cabart/Documents/MasterThesisData/camera_setup_fip/translated_positions",
        subtype="FILE_PATH",
    )

    train_frames_total: bpy.props.IntProperty(
        name="Train frames total",
        description="Number of train frames in total",
        default=50,
        min=1,
        soft_max=500,
    )

    test_frames_total: bpy.props.IntProperty(
        name="Test frames total",
        description="Number of test frames in total",
        default=20,
        min=1,
        soft_max=500,
    )

    save_path: bpy.props.StringProperty(
        name="Rendering File path",
        description="",
        default="/home/cabart/Documents/coding/master-thesis/results/test/",
        subtype="FILE_PATH",
    )

    render: bpy.props.BoolProperty(
        name="Render frames",
        description="Actually render train and test frames",
        default=False,
    )

    current_render_mode: bpy.props.IntProperty(
        name="Current render mode",
        description="Use for internal use only (int stands for Enum)",
        default=RenderMode.TRAIN.value,
    )

    original_camera: bpy.props.StringProperty(
        name="Original Camera",
        description="Original camera",
        default="Camera",
    )

    render_samples: bpy.props.IntProperty(
        name="Render Samples",
        description="Number of samples for rendering",
        default=512,
        min=1,
        soft_max=10000,
    )

    point_cloud_samples: bpy.props.IntProperty(
        name="Number of points in point cloud",
        description="Randomly distributed points on the surface of all plants",
        default=100000,
        min=100,
        soft_max=1000000,
    )

    dummy_render: bpy.props.BoolProperty(
        name="Dummy render",
        description="Render dummy images",
        default=False,
    )

    time_lapse: bpy.props.BoolProperty(
        name="Time lapse",
        description="Render time lapse images with sun movement. Only use this with continuous camera sampling methods (e.g. circle)",
        default=False,
    )

    render_in_progress: bpy.props.BoolProperty(
        name="Render animation",
        description="Internal use only",
        default=False,
    )
