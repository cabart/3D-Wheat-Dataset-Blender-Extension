import bpy
from ..operators.lsystem_generation_operator import LSystemGeneratorOperator
from ..operators.lsystem_drawing_operator import LSystemDrawingOperator
from ..operators.lsystem_next_operator import LSystemNextOperator
from ..operators.lsystem_previous_operator import LSystemPreviousOperator
from ..operators.camera_render_operator import CameraRenderOperator
from .. import globals


class Plant3DPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lsystem"
    bl_label = "Plant 3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Plant 3D"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Plant 3D")

    def draw(self, context):
        layout = self.layout

        props = bpy.context.scene.PlantProps

        # Allow the user to select plant modeling parameters
        layout.prop(props, "model")
        layout.prop(props, "canopy_plants_x")
        layout.prop(props, "canopy_plants_y")
        layout.prop(props, "derivation_length")
        layout.prop(props, "canopy_seed")
        layout.operator(LSystemGeneratorOperator.bl_idname)

        # Allow the user to set canopy parameters
        layout.separator()
        layout.prop(props, "canopy_distance_x")
        layout.prop(props, "canopy_distance_y")
        layout.prop(props, "plant_placement_standard_deviation")

        # Allow the user to select a specific iteration step of the lstring derivation
        if len(globals.global_lstring_states) > 0:
            layout.separator()
            layout.prop(props, "iteration_step")
            layout.operator(LSystemDrawingOperator.bl_idname)
            row = layout.row()
            row.column().operator(LSystemPreviousOperator.bl_idname, text="Previous")
            row.column().operator(LSystemNextOperator.bl_idname, text="Next")

        # Allow the user to render various camera setups
        camera_props = bpy.context.scene.CameraRenderProps

        # arguments for training camera
        layout.separator()
        layout.label(text="Train Cameras", icon="VIEW_CAMERA")
        layout.prop(camera_props, "camera_placement_train")
        if camera_props.camera_placement_train not in ["fip_cameras", "colmap_cameras"]:
            layout.prop(camera_props, "train_frames_total")
        layout.prop(camera_props, "center_train")

        if camera_props.camera_placement_train in [
            "fibonacci_lattice_hemisphere",
            "fibonacci_lattice_cap",
            "fibonacci_lattice_cap_inverse",
            "colmap_cameras",
            "random_sampling_hemisphere",
            "circle_on_sphere",
        ]:
            layout.prop(camera_props, "radius_train")
        if camera_props.camera_placement_train in [
            "fibonacci_lattice_cap",
            "fibonacci_lattice_cap_inverse",
            "circle_on_sphere",
        ]:
            layout.prop(camera_props, "cap_angle_train")
        if camera_props.camera_placement_train == "colmap_cameras":
            layout.prop(camera_props, "colmap_path_train")

        # arguments for test camera
        layout.separator()
        layout.label(text="Test Cameras", icon="VIEW_CAMERA")
        layout.prop(camera_props, "camera_placement_test")
        if camera_props.camera_placement_test not in ["fip_cameras", "colmap_cameras"]:
            layout.prop(camera_props, "test_frames_total")
        layout.prop(camera_props, "center_test")

        if camera_props.camera_placement_test in [
            "fibonacci_lattice_hemisphere",
            "fibonacci_lattice_cap",
            "fibonacci_lattice_cap_inverse",
            "colmap_cameras",
            "random_sampling_hemisphere",
            "circle_on_sphere",
        ]:
            layout.prop(camera_props, "radius_test")
        if camera_props.camera_placement_test in [
            "fibonacci_lattice_cap",
            "fibonacci_lattice_cap_inverse",
            "circle_on_sphere",
        ]:
            layout.prop(camera_props, "cap_angle_test")
        if camera_props.camera_placement_test == "colmap_cameras":
            layout.prop(camera_props, "colmap_path_test")

        layout.prop(camera_props, "time_lapse")

        layout.separator()
        layout.prop(context.scene, "camera")
        layout.prop(camera_props, "seed")

        layout.prop(camera_props, "point_cloud_samples")
        layout.prop(camera_props, "save_path")
        layout.prop(camera_props, "render_samples")
        layout.prop(camera_props, "render")
        layout.operator(CameraRenderOperator.bl_idname, text="Render Plant")
