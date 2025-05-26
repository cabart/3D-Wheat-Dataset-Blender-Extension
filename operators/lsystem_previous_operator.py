import bpy


class LSystemPreviousOperator(bpy.types.Operator):
    bl_idname = "lsys.previous"
    bl_label = "Draw previous iteraton step of the L-System"
    bl_options = {"REGISTER"}

    def execute(self, context):
        props = bpy.context.scene.PlantProps
        props.iteration_step -= 1
        bpy.ops.lsys.draw()
        return {"FINISHED"}
