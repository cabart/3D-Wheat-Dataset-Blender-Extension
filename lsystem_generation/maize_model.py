import math

from ..parametric_objects.leaf_textures import create_grass_texture
from ..parametric_objects.spline import Spline2D
import bpy
from . import parametric_lsystem
import random
import numpy as np


def maize(
    derivation_length, plant_seed, base_mask_index, mask_indices, current_plant_index
):
    """L-System for maize"""

    # Material cleanup
    old_leaf_material = bpy.data.materials.get("LeafMaterial", None)
    if old_leaf_material is not None:
        for obj in bpy.data.objects:
            if obj.type == "MESH" and old_leaf_material.name in obj.data.materials:
                for i, mat in enumerate(obj.data.materials):
                    if mat == old_leaf_material:
                        obj.data.materials.pop(index=i)
        bpy.data.materials.remove(old_leaf_material, do_unlink=True)

    old_leaf_material = bpy.data.materials.get("LeafMaterial", None)
    if old_leaf_material is None:
        leaf_material = create_grass_texture("LeafMaterial")
    else:
        leaf_material = old_leaf_material
    leaf_material.diffuse_color = (0, 1, 0, 1)
    leaf_material.specular_intensity = 0.1

    PLASTOCHRON = 5
    dT = 1  # Time step size
    LeafLen = 30  # Scaling factor for leaf length, 'base leaf length'
    IntLen = 10  # Scaling factor for internode length, 'base internode length'
    BrAngle = 0.8  # Scaling factor for branching angle (0 = 0 Degrees, 1 = 90 degrees)

    MaxLeafs = 20  # Not properly used yet
    MaxLeafAge = 40

    axiom = f"A(0,1)"

    def get_leaf_rank_in_range(n):
        return min(float(n) / MaxLeafs, 1)

    def get_leaf_age_in_range(age):
        return min(float(age) / MaxLeafAge, 1)

    target_angle_spline = Spline2D(
        np.array([[0, 0.4], [0.3, 0.2], [0.5, 0.25], [1, 0.1]])
    )

    def br_target_angle(n):
        return target_angle_spline.evaluate(get_leaf_rank_in_range(n))[1]

    branching_angle_spline = Spline2D(
        np.array([[0, 0.01], [0.2, 0.05], [0.3, 0.2], [0.5, 0.6], [1, 1]])
    )

    def br_angle(age):
        return branching_angle_spline.evaluate(get_leaf_age_in_range(age))[1]

    def apex_production_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)

        age = params_int[0]
        n = params_int[1]

        age += dT

        if age >= PLASTOCHRON:
            age = age - PLASTOCHRON
            return f"I({age}, {n})[L({age},{n})]/(180)A({age},{n + 1})"
        else:
            return f"A({age},{n})"

    def internode_length(age):
        length = float(age) / MaxLeafAge
        return min(1, max(0.2, length))

    InternodeTargetLen = Spline2D(np.array([[0, 0.1], [0.3, 1.1], [0.7, 0.8], [1, 1]]))

    def internode_target_length(n):
        return InternodeTargetLen.evaluate(get_leaf_rank_in_range(n))[1]

    def internode_width(n):
        return 0.4

    def internode_interpretation_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)

        age = params_int[0]
        n = params_int[1]

        len: float = IntLen * internode_target_length(n) * internode_length(age)
        wid: float = internode_width(n)
        return f"_({wid})F({len})"

    LeafTargetLen = Spline2D(np.array([[0, 0.1], [0.3, 1.2], [0.7, 1.0], [1, 0.5]]))

    def leaf_target_len(n):
        return LeafTargetLen.evaluate(get_leaf_rank_in_range(n))[1]

    def leaf_length(age):
        return get_leaf_age_in_range(age)

    LeafLengthSpline = Spline2D(
        np.array([[0, 0.01], [0.2, 0.05], [0.3, 0.2], [0.5, 0.6], [1, 1]])
    )

    def leaf_length(age):
        return LeafLengthSpline.evaluate(get_leaf_age_in_range(age))[1]

    LeafBend = Spline2D(np.array([[0, 0.1], [0.3, 0.2], [0.7, 0.3], [1, 0.3]]))

    def leaf_interpretation_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)
        age = params_int[0]
        n = params_int[1]

        len: float = LeafLen * leaf_target_len(n) * leaf_length(age)

        # Angle between horizontal and vertical between [0,1]
        orientation = BrAngle * br_angle(age) * br_target_angle(n)
        leaf_bend = LeafBend.evaluate(get_leaf_age_in_range(age))[1]

        # TODO: Calculate dynamic leaf width
        leaf_width = 0.12 * len
        return f"L({leaf_width},{len},{leaf_bend},{orientation},{n},{plant_seed},LeafMaterial)"

    def aging_production_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)
        age = params_int[0]
        n = params_int[1]
        return f"{symbol}({age + 1},{n})"

    production_rules = {
        lambda s: s.startswith("A"): apex_production_rule,
        lambda s: s.startswith("I"): aging_production_rule,
        lambda s: s.startswith("L"): aging_production_rule,
    }

    interpretation_rules = {
        lambda s: s.startswith("I"): internode_interpretation_rule,
        lambda s: s.startswith("L"): leaf_interpretation_rule,
    }

    lsystem = parametric_lsystem.ParametricLSystem(
        axiom=axiom,
        production_rules=production_rules,
        iterations=derivation_length,
        interpretation_rules=interpretation_rules,
    )
    return lsystem.generate(), 0, mask_indices
