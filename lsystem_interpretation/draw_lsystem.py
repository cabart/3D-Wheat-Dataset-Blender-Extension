"""

NOTE: This implementation is based Lindenmaker by Nikole Leopold (https://github.com/themangosteen/lpy-lsystems-blender-addon)
but updated to work with Blender version 4.2 and modified and extended for additional functionality.

"""

import bpy
import re
from mathutils import Matrix, Vector
from math import radians
from typing import Type

from ..parametric_objects import leaf
from ..parametric_objects import wheat_head


class DrawLSystem:
    """Draw a L-System string in the scene. This class can be extended to support additional
    symbols by overwritting the custom() method.
    """

    initial_rotation = Matrix.Rotation(radians(-90), 4, "Y")

    def __init__(self, collection, root_object, step_size, line_width) -> None:
        # Look upwards in Z direction by default
        # Matrix defines location and rotation of child node relative to its parent
        self.mat = self.initial_rotation @ Matrix.Identity(4)

        self.draw_length = step_size  # Length of internodes
        self.stack = []  # Stack for nested expressions (e.g. F[+(5)F]F)
        self.parent = root_object  # Current parent object
        self.parent_stack = [root_object]  # Stack for parent/child relations
        self.collection = collection
        self.line_width = line_width

        # Create a default material for basic objects
        old_default_material = bpy.data.materials.get("DefaultMaterial", None)
        if old_default_material is None:
            self.default_material = bpy.data.materials.new(name="DefaultMaterial")
            self.default_material.diffuse_color = (0, 0.4, 0, 1)
        else:
            self.default_material = old_default_material

        # Set cursor location for new object
        bpy.types.Scene.cursor_location = Vector((0, 0, 0))

        # Add default cylinder for forward movement
        self.set_active_layer_collection()
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=1,
        )
        self.cylinder = bpy.context.object
        self.cylinder.location = (0, 0, 0.5)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        self.cylinder.select_set(False)

    def post_drawing(self):
        self.cylinder.hide_viewport = True
        self.cylinder.hide_render = True

    def custom(self, symbol, args):
        """Can be overwritten by a subclass. Allows for matching with specific characters and interpreting them in a way specific to a given plant"""
        pass

    def reset_matrix(self):
        self.mat = self.initial_rotation @ Matrix.Identity(4)

    def push(self):
        self.stack.append(self.mat.copy())
        self.parent_stack.append(self.parent)

    def pop(self):
        self.mat = self.stack.pop()
        self.parent = self.parent_stack.pop()

    def turn(self, angle_degrees):
        self._rotate(angle_degrees, "Z")

    def pitch(self, angle_degrees):
        self._rotate(angle_degrees, "Y")

    def roll(self, angle_degrees):
        self._rotate(angle_degrees, "X")

    def _rotate(self, angle_degrees, axis):
        rot = (
            Matrix.Rotation(radians(angle_degrees), 4, axis).to_3x3()
            @ self.mat.to_3x3()
        )
        self.mat = Matrix.LocRotScale(self.mat.translation, rot, None)

    def set_width(self, value):
        self.line_width = value

    def get_width(self):
        return self.line_width

    def draw_object(
        self,
        objname: str,
        scale: Vector,
        offset: Vector = Vector((0, 0, 0)),
        pass_index=0,
    ):
        """Draw an object in the scene. The object is copied from the original object, and its location, rotation and scale are set.

        Args:
            objname (str): Name of the object within Blender to be drawn.
            scale (Vector): Scale of the object in x,y,z direction.
            offset (Vector, optional): _description_. Defaults to Vector((0, 0, 0)).
            pass_index (int, optional): _description_. Defaults to 0.
        """
        self.set_active_layer_collection()
        if objname not in bpy.data.objects.keys():
            raise ValueError(f"Object '{objname}' not found in Blender data.")

        copied_object = bpy.data.objects[objname].copy()
        copied_object.data = copied_object.data.copy()
        copied_object.location = self.mat.translation + offset
        copied_object.scale = scale
        copied_object.rotation_euler = (
            self.initial_rotation.inverted()
            @ self.mat
            @ bpy.data.objects[objname].rotation_euler.to_matrix().to_4x4()
        ).to_euler()
        copied_object.parent = self.parent
        self.collection.objects.link(copied_object)

        copied_object.pass_index = pass_index

        copied_object.select_set(False)

    def set_active_layer_collection(self):
        # Set active layer collection
        layer_collection = bpy.context.view_layer.layer_collection.children[
            self.collection.name
        ]
        bpy.context.view_layer.active_layer_collection = layer_collection

    def draw_internode_module(self, length=None, material_name=None, pass_index=0):
        self.set_active_layer_collection()

        draw_length = length if length is not None else self.draw_length

        cyl = self.cylinder.copy()
        cyl.data = self.cylinder.data.copy()
        # Scale cylinder
        for vert in cyl.data.vertices:
            vert.co.x *= self.line_width
            vert.co.y *= self.line_width
            vert.co.z *= draw_length
        self.collection.objects.link(cyl)

        # Translate and rotate cylinder
        cyl.location = (0, 0, 0)
        cyl.location = self.mat.translation
        cyl.rotation_euler = (self.initial_rotation.inverted() @ self.mat).to_euler()

        if cyl.data.materials:
            if material_name is None:
                cyl.data.materials[0] = self.default_material
            else:
                cyl.data.materials[0] = bpy.data.materials[material_name]
        else:
            if material_name is None:
                cyl.data.materials.append(self.default_material)
            else:
                cyl.data.materials.append(bpy.data.materials[material_name])

        # Set parent/child relation
        cyl.parent = self.parent
        self.parent = cyl

        # Reset parent-relative matrix to 'identity'
        self.reset_matrix()

        # Set pass index for segmentation masks
        cyl.pass_index = pass_index

        cyl.select_set(False)

    def move(self, length=None):
        draw_length = length if length is not None else self.draw_length
        trans_vec = self.mat.to_3x3() @ Vector((draw_length, 0, 0))
        self.mat.translation += trans_vec


def interpret(
    lstring,
    lpy_collection,
    root_object,
    step_size,
    line_width,
    width_growth_factor,
    interpreter: Type[DrawLSystem] = DrawLSystem,
):
    drawer = interpreter(lpy_collection, root_object, step_size, line_width)

    lstring = "".join(lstring.split())

    # split into command symbols with optional parameters
    commands = re.findall(r"[^()](?:\([^()]*\))?", lstring)

    for cmd in commands:
        args = extractArgs(cmd)
        numArgs = len(args)

        match cmd[0]:
            case "F":
                if numArgs == 0:
                    drawer.draw_internode_module()
                    drawer.move()
                elif numArgs == 1:
                    drawer.draw_internode_module(args[0])
                    drawer.move(args[0])
                elif numArgs == 2:
                    drawer.draw_internode_module(args[0], args[1])
                    drawer.move(args[0])
                elif numArgs == 3:
                    drawer.draw_internode_module(args[0], args[1], int(args[2]))
                    drawer.move(args[0])
            case "[":
                drawer.push()
            case "]":
                drawer.pop()
            case "-":
                if numArgs == 0:
                    drawer.turn(-45)
                elif numArgs == 1:
                    drawer.turn(args[0])
            case "+":
                if numArgs == 0:
                    drawer.turn(45)
                elif numArgs == 1:
                    drawer.turn(args[0])
            case "&":
                if numArgs == 0:
                    drawer.pitch(-45)
                elif numArgs == 1:
                    drawer.pitch(args[0])
            case "^":
                if numArgs == 0:
                    drawer.pitch(45)
                elif numArgs == 1:
                    drawer.pitch(args[0])
            case "\\":
                if numArgs == 0:
                    drawer.roll(-45)
                elif numArgs == 1:
                    drawer.roll(args[0])
            case "/":
                if numArgs == 0:
                    drawer.roll(45)
                elif numArgs == 1:
                    drawer.roll(args[0])
            case "_":
                if len(args) == 0:
                    drawer.set_width(drawer.get_width() * width_growth_factor)
                elif len(args) == 1:
                    drawer.set_width(args[0])
            case "!":
                if len(args) == 0:
                    drawer.set_width(
                        drawer.get_width() * (1 - (width_growth_factor - 1))
                    )
                elif len(args) == 1:
                    drawer.set_width(args[0])
                drawer.set_width(max(drawer.get_width(), 0.0001))
            case "@":
                if numArgs == 2:
                    drawer.draw_object(args[0], Vector((args[1], args[1], args[1])))
            case _ as symbol:
                drawer.custom(symbol, args)
    drawer.post_drawing()


def extractArgs(command):
    """Return a list of the arguments of a command statement, e.g. A(arg1, arg2, .., argn) will return [arg1, arg2, .., argn]"""
    argstring_list = re.findall(r"\((.+)\)", command)
    if len(argstring_list) == 0:
        return []
    result = []
    for arg in re.split(",", argstring_list[0]):
        try:
            result.append(float(arg))  # try to cast to float
        except ValueError:
            result.append(arg)  # else just add string argument
    return result


class DrawWheat(DrawLSystem):
    """Draw a wheat plant in the scene. This extends the DrawLSystem class and implements an additional Leaf and Head symbol."""

    def custom(self, symbol, args):
        numArgs = len(args)
        match symbol:
            case "L":
                if numArgs == 10:
                    self.draw_leaf(
                        args[0],
                        args[1],
                        args[2],
                        args[3],
                        args[4],
                        args[5],
                        args[6],
                        int(args[7]),
                        float(args[8]),
                        float(args[9]),
                    )
                else:
                    print("Potential problem with leaf drawing")
            case "H":
                if numArgs == 3:
                    self.draw_head(args[0], args[1], int(args[2]))
                elif numArgs == 6:
                    self.draw_head(
                        args[0],
                        args[1],
                        int(args[2]),
                        float(args[3]),
                        int(args[4]),
                        float(args[5]),
                    )

    def draw_leaf(
        self,
        max_width,
        length,
        curvature,
        orientation,
        rank,
        seed,
        material_name,
        pass_index,
        internode_width,
        senescence,
    ):
        leaf.create_wheat_leaf(
            max_width,
            length,
            curvature,
            orientation,
            "Draw_leaf",
            rank,
            seed,
            material_name,
            internode_width,
            senescence,
        )
        self.draw_object("Draw_leaf", Vector((1, 1, 1)), pass_index=pass_index)
        bpy.data.objects.remove(bpy.data.objects.get("Draw_leaf"))

    def draw_head(
        self, spikelets, material_name, pass_index, head_tilt=0.0, seed=0, scale=1.0
    ):
        wheat_head.create_wheat_head(
            int(spikelets), "WheatHead", tilt=head_tilt, seed=seed
        )
        if material_name is not None:
            head = bpy.data.objects.get("WheatHead")
            head.data.materials.clear()
            head.data.materials.append(bpy.data.materials[material_name])
        self.draw_object(
            "WheatHead",
            scale * Vector((2, 2, 2)),
            Vector((0, 0, -1)),
            pass_index=pass_index,
        )
        bpy.data.objects.remove(bpy.data.objects.get("WheatHead"))


class DrawMaize(DrawLSystem):
    """Draw a maize plant in the scene. This extends the DrawLSystem class and implements an additional Leaf symbol."""

    def custom(self, symbol, args):
        numArgs = len(args)
        match symbol:
            case "L":
                if numArgs == 7:
                    self.draw_leaf(
                        args[0], args[1], args[2], args[3], args[4], args[5], args[6]
                    )

    def draw_leaf(
        self, max_width, length, curvature, orientation, rank, seed, material_name
    ):
        leaf.create_maize_leaf(
            max_width,
            length,
            curvature,
            orientation,
            "Draw_leaf",
            rank,
            seed,
            material_name,
        )
        self.draw_object("Draw_leaf", Vector((1, 1, 1)))
        bpy.data.objects.remove(bpy.data.objects.get("Draw_leaf"))
