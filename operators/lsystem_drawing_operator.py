import bpy
import os
from math import radians
from ..lsystem_interpretation import draw_lsystem
from .. import globals
import time
import numpy as np


class LSystemDrawingOperator(bpy.types.Operator):
    """Draw the L-System in the scene. Depends on the result of the L-System generation operation"""

    bl_idname = "lsys.draw"
    bl_label = "Draw the L-System"
    bl_options = {"REGISTER"}

    def execute(self, context):
        # Check if the L-System generation operation has been run
        if len(globals.global_lstring_states) == 0:
            return {"FINISHED"}

        draw_state_index = bpy.context.scene.PlantProps.iteration_step

        props = bpy.context.scene.PlantProps
        np.random.seed(props.canopy_seed)

        start_time = time.time()
        lpy_collection = clean_scene(context)
        for x in range(props.canopy_plants_x):
            for y in range(props.canopy_plants_y):
                plant_index = x * props.canopy_plants_y + y
                create_plant(
                    context,
                    globals.global_lstring_states[plant_index][draw_state_index],
                    x,
                    y,
                    lpy_collection,
                )
        end_time = time.time()
        print(f"Time taken to draw all plants {end_time - start_time} seconds")
        return {"FINISHED"}


def create_plant(context, lstring, x, y, lpy_collection):
    """Draw a single plant of the canopy"""
    props = bpy.context.scene.PlantProps

    root_object = bpy.data.objects.new(f"Plant_{x}_{y}", None)
    # Place plant at correct location, (0, 0) is defined as the center of the field
    dx = np.random.normal(loc=0, scale=props.plant_placement_standard_deviation)
    dy = np.random.normal(loc=0, scale=props.plant_placement_standard_deviation)
    location = (
        ((x - (props.canopy_plants_x - 1) / 2.0) * props.canopy_distance_x) + dx,
        ((y - (props.canopy_plants_y - 1) / 2.0) * props.canopy_distance_y) + dy,
        0,
    )
    root_object.location = location
    lpy_collection.objects.link(root_object)

    draw_lsystem.interpret(
        lstring,
        lpy_collection,
        root_object,
        props.step_size,
        props.line_width,
        props.width_growth_factor,
        globals.plant_models[props.model][1],
    )


def clean_scene(context):
    # Remove blender default light and cube
    if bpy.data.objects.get("Light", None) is not None:
        bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)
    if bpy.data.objects.get("Cube", None) is not None:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    if bpy.data.objects.get("Camera", None) is not None:
        bpy.context.scene.camera = bpy.data.objects["Camera"]
        context.scene.camera.data.clip_end = 5000

    # Remove previous collection and all its objects
    old_collection = bpy.data.collections.get("lpy_collection", None)
    if old_collection is not None:
        for obj in old_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)
    else:
        # In first run import template objects
        import_template_objects(context)
        import_materials(context)
        create_skybox(context)

    lpy_collection = bpy.data.collections.new("lpy_collection")
    bpy.context.scene.collection.children.link(lpy_collection)

    # Create a plane with x nodes
    if bpy.data.objects.get("GroundPlane", None) is None:
        bpy.ops.mesh.primitive_plane_add(
            size=5000, enter_editmode=True, align="WORLD", location=(0, 0, 0)
        )
        bpy.ops.mesh.subdivide(number_cuts=1000)
        plane = bpy.context.object

        # Select the middle part of the plane
        bpy.ops.mesh.select_all(action="DESELECT")

        bpy.ops.object.mode_set(mode="OBJECT")

        radius = 200
        for vertice in plane.data.vertices:
            if -radius < vertice.co.x < radius and -radius < vertice.co.y < radius:
                vertice.select = True
        bpy.ops.object.mode_set(mode="EDIT")

        # Subdivide the middle part more
        bpy.ops.mesh.subdivide(number_cuts=5000)
        bpy.ops.object.mode_set(mode="OBJECT")
        plane.name = "GroundPlane"
        lpy_collection.objects.link(plane)
        plane.data.materials.append(bpy.data.materials.get("Field", None))

    return lpy_collection


def clean_scene_and_render(context, lstring):
    """Remove previous results from scene and draw lsystem"""

    props = bpy.context.scene.PlantProps

    # Remove previous collection and all its objects
    old_collection = bpy.data.collections.get("lpy_collection", None)
    if old_collection is not None:
        for obj in old_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)
    else:
        import_template_objects(context)

    lpy_collection = bpy.data.collections.new("lpy_collection")
    bpy.context.scene.collection.children.link(lpy_collection)

    root_object = bpy.data.objects.new("Root", None)
    lpy_collection.objects.link(root_object)

    draw_lsystem.interpret(
        lstring,
        lpy_collection,
        root_object,
        props.step_size,
        props.line_width,
        props.width_growth_factor,
        globals.plant_models[props.model][1],
    )


def import_template_objects(context):
    """Import all objects from the 'template_objects' folder"""
    extension_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_directory = os.path.join(extension_folder, "template_objects")
    obj_files = [
        f
        for f in os.listdir(template_directory)
        if f.endswith(".obj") and os.path.isfile(os.path.join(template_directory, f))
    ]

    for obj_file in obj_files:
        bpy.ops.wm.obj_import(filepath=os.path.join(template_directory, obj_file))

    # Hide objects
    object_names = ["WheatOriginal"]
    for object_name in object_names:
        object = bpy.data.objects.get(object_name)
        object.hide_viewport = True
        object.hide_render = True

    # Hide in render
    object_names = ["Human"]
    for object_name in object_names:
        object = bpy.data.objects.get(object_name)
        object.hide_render = True


def import_materials(context):
    """Import ground texture"""
    extension_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    material_folder = os.path.join(extension_folder, "materials")
    ground_material = os.path.join(material_folder, "Ground_Pack.blend")
    if not os.path.exists(ground_material):
        print("Ground material not found, create dummy material")
        material = bpy.data.materials.new(name="Field")
        material.use_nodes = True
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (
                0.55,
                0.27,
                0.07,
                1,
            )  # Brown color
        return

    with bpy.data.libraries.load(
        os.path.join(material_folder, "Ground_Pack.blend"), link=False
    ) as (data_from, data_to):
        data_to.materials = [name for name in data_from.materials if name == "Field"]

    if data_to.materials:
        print("Field material found")
        material = bpy.data.materials.get("Field")
    else:
        print("Field material not found")
        return

    if material.node_tree:
        # Fix ground texture values
        nodes = material.node_tree.nodes
        mapping_node = nodes.get("Mapping")
        if mapping_node:
            mapping_node.inputs["Scale"].default_value[0] = 25
            mapping_node.inputs["Scale"].default_value[1] = 25
            mapping_node.inputs["Scale"].default_value[2] = 25

        displacement_node = nodes.get("Displacement")
        if displacement_node:
            displacement_node.inputs["Scale"].default_value = 6
            displacement_node.inputs["Midlevel"].default_value = 0.5

        # Add Hue/Saturation/Value node between Base Color and Multiply node
        hue_sat_node = nodes.new(type="ShaderNodeHueSaturation")

        # Find the Base Color node and Multiply node
        base_color_node = next(
            (
                node
                for node in nodes
                if node.type == "TEX_IMAGE" and "Albedo" in node.image.name
            ),
            None,
        )
        multiply_node = nodes.get("Mix")

        if base_color_node and multiply_node:
            # Connect Base Color to Hue/Saturation/Value node
            material.node_tree.links.new(
                base_color_node.outputs["Color"], hue_sat_node.inputs["Color"]
            )

            # Connect Hue/Saturation/Value node to Multiply node
            material.node_tree.links.new(
                hue_sat_node.outputs["Color"], multiply_node.inputs["A"]
            )

            hue_sat_node.location = (
                base_color_node.location.x + 200,
                base_color_node.location.y,
            )
            hue_sat_node.inputs["Saturation"].default_value = 1.1
            hue_sat_node.inputs["Value"].default_value = 0.3


def create_skybox(context):
    bpy.ops.sky.dyn()
    sky = bpy.data.worlds["Dynamic_1"]
    context.scene.world = sky
