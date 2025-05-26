import bpy
import random
from .. import globals


class LSystemGeneratorOperator(bpy.types.Operator):
    bl_idname = "lsys.generate"
    bl_label = "Generate the L-System"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.length_unit = "CENTIMETERS"
        bpy.context.scene.unit_settings.scale_length = 0.01

        # Set view clip to larger distance due to centimeters change
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.clip_end = 10000

        props = bpy.context.scene.PlantProps

        # Set a seed for each plant of the canopy
        random.seed(props.canopy_seed)
        plant_seeds = [
            random.randint(0, 10000)
            for _ in range(props.canopy_plants_x * props.canopy_plants_y)
        ]

        # Generate the L-System for each plant while keeping track of plant part indices
        mask_indices = {}
        current_mask_index = 1
        all_plant_lstrings = []
        for plant_index in range(props.canopy_plants_x * props.canopy_plants_y):
            lstring, current_mask_index, mask_indices = globals.plant_models[
                props.model
            ][0](
                props.derivation_length,
                plant_seeds[plant_index],
                current_mask_index,
                mask_indices,
                plant_index,
            )
            all_plant_lstrings.append(lstring)
        globals.global_lstring_states = all_plant_lstrings
        globals.plant_labels = mask_indices
        globals.max_plant_label = current_mask_index - 1

        return {"FINISHED"}
