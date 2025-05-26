import bpy
from ..operators.leaf_drawing_operator import LeafGeneratorOperator


class DebugPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lsytem_debug"
    bl_label = "Leaf Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Leaf Debug"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Leaf Debug")

    def draw(self, context):
        layout = self.layout
        layout.operator(LeafGeneratorOperator.bl_idname, text="Create Leaf")
