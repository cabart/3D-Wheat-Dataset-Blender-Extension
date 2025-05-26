import bpy
from ..parametric_objects.leaf import create_debug_leaf


class LeafGeneratorOperator(bpy.types.Operator):
    """Create a single leaf object. Use this operator for debugging leaf generation."""

    bl_idname = "lsys.leaf"
    bl_label = "Create single leaf"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        create_debug_leaf(10, 2, "Draw_leaf", None)
        return {"FINISHED"}
