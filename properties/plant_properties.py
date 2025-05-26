import bpy
from .. import globals


class PlantProps(bpy.types.PropertyGroup):
    step_size: bpy.props.FloatProperty(
        name="Default step size",
        description="Default length of Forward motion 'F'",
        default=2.0,
        min=0.05,
        max=100.0,
    )

    line_width: bpy.props.FloatProperty(
        name="Default line width",
        description="Default line width of internode",
        default=0.03,
        min=0.01,
        max=100.0,
    )

    width_growth_factor: bpy.props.FloatProperty(
        name="Width growth factor",
        description="Width growth for line",
        default=1.05,
        min=1,
        max=100.0,
    )

    derivation_length: bpy.props.IntProperty(
        name="Number of derivation steps",
        description="Number of derivation steps",
        default=200,
        min=1,
        max=10000,
    )

    canopy_seed: bpy.props.IntProperty(
        name="Random seed for plants generation",
        description="",
        default=1,
        min=1,
        max=10000,
    )

    def get_iteration_step(self):
        return self.get("iteration", 0)

    def set_iteration_step(self, value):
        """Don't allow for iteration step to be larger than the number of iterations the lstring has been computed for"""
        max_step = 0
        if len(globals.global_lstring_states) > 0:
            max_step = len(globals.global_lstring_states[0]) - 1

        self["iteration"] = max(0, min(value, max_step))

    iteration_step: bpy.props.IntProperty(
        name="Iteration Step",
        description="Draw lsystem at this many iteration steps",
        default=0,
        get=get_iteration_step,
        set=set_iteration_step,
    )

    model: bpy.props.EnumProperty(
        name="Plant model selection",
        description="Select a plant model from the list",
        items=[(x, x, x) for x in globals.plant_models.keys()],
        # update=update_selection  # Optional: Callback function when the selection changes
    )

    canopy_plants_x: bpy.props.IntProperty(
        name="Number of plants in x direction",
        description="Number of plants in x direction",
        default=1,
        min=1,
        max=1000,
    )

    canopy_plants_y: bpy.props.IntProperty(
        name="Number of plants in y direction",
        description="Number of plants in y direction",
        default=1,
        min=1,
        max=1000,
    )

    canopy_distance_x: bpy.props.FloatProperty(
        name="Distance between plants in x direction",
        description="Distance between plants in x direction",
        default=15.0,
        min=0.1,
        max=100.0,
    )

    canopy_distance_y: bpy.props.FloatProperty(
        name="Distance between plants in y direction",
        description="Distance between plants in y direction",
        default=15.0,
        min=0.1,
        max=100.0,
    )

    plant_placement_standard_deviation: bpy.props.FloatProperty(
        name="Plant placement standard deviation",
        description="Standard deviation from perfectly aligned location for plant placement",
        default=0.0,
        min=0.0,
        soft_max=100.0,
    )
