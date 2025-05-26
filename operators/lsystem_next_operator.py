import bpy


class LSystemNextOperator(bpy.types.Operator):
    bl_idname = "lsys.next"
    bl_label = "Draw next iteraton step of the L-System"
    bl_options = {"REGISTER"}

    def execute(self, context):
        props = bpy.context.scene.PlantProps
        props.iteration_step += 1
        bpy.ops.lsys.draw()
        return {"FINISHED"}
