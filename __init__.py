"""Registers all custom Blender operators, panels and properties"""

import bpy

import importlib
from . import globals

importlib.reload(globals)
globals.init()

from .parametric_objects import leaf, leaf_textures
from .lsystem_generation import parametric_lsystem
from .lsystem_interpretation import draw_lsystem
from .parametric_objects import wheat_head
from .properties import camera_render_properties, plant_properties
from .panels import debug_panel, plant_panel
from .operators import (
    lsystem_generation_operator,
    lsystem_drawing_operator,
    lsystem_next_operator,
    lsystem_previous_operator,
    camera_render_operator,
    leaf_drawing_operator,
)


importlib.reload(parametric_lsystem)
importlib.reload(leaf)
importlib.reload(leaf_textures)
importlib.reload(wheat_head)
importlib.reload(plant_properties)
importlib.reload(camera_render_properties)
importlib.reload(plant_panel)
importlib.reload(draw_lsystem)
importlib.reload(lsystem_generation_operator)
importlib.reload(lsystem_drawing_operator)
importlib.reload(lsystem_next_operator)
importlib.reload(lsystem_previous_operator)
importlib.reload(camera_render_operator)
importlib.reload(leaf_drawing_operator)
importlib.reload(debug_panel)

CLASSES = [
    plant_properties.PlantProps,
    camera_render_properties.CameraRenderProps,
    lsystem_generation_operator.LSystemGeneratorOperator,
    lsystem_drawing_operator.LSystemDrawingOperator,
    lsystem_next_operator.LSystemNextOperator,
    lsystem_previous_operator.LSystemPreviousOperator,
    camera_render_operator.CameraRenderOperator,
    plant_panel.Plant3DPanel,
    leaf_drawing_operator.LeafGeneratorOperator,
    debug_panel.DebugPanel,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.PlantProps = bpy.props.PointerProperty(
        type=plant_properties.PlantProps
    )
    bpy.types.Scene.CameraRenderProps = bpy.props.PointerProperty(
        type=camera_render_properties.CameraRenderProps
    )

    bpy.app.handlers.frame_change_post.append(
        camera_render_operator.rendering_camera_update
    )
    bpy.app.handlers.render_complete.append(camera_render_operator.post_render)
    bpy.app.handlers.render_cancel.append(camera_render_operator.post_render)


def unregister():
    bpy.app.handlers.frame_change_post.remove(
        camera_render_operator.rendering_camera_update
    )
    bpy.app.handlers.render_complete.remove(camera_render_operator.post_render)
    bpy.app.handlers.render_cancel.remove(camera_render_operator.post_render)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.PlantProps
    del bpy.types.Scene.CameraRenderProps
