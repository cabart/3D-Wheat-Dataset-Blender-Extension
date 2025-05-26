from ..parametric_objects.leaf_colors import MaterialType
from ..parametric_objects.leaf_textures import (
    create_grass_texture,
    create_head_texture,
    create_stem_texture,
    create_indexed_grass_texture,
)
from ..parametric_objects.spline import Spline2D
import bpy
from . import parametric_lsystem
import random
import numpy as np


def restore_material(material_name: str, create_function, *args, **kwargs):
    material = bpy.data.materials.get(material_name, None)
    if material is not None:
        bpy.data.materials.remove(material, do_unlink=True)
    assert bpy.data.materials.get(material_name, None) is None

    create_function(material_name, *args, **kwargs)


def restore_materials(materials):
    for material_name, (create_function, args, kwargs) in materials.items():
        restore_material(material_name, create_function, *args, **kwargs)


def wheat(
    derivation_length, plant_seed, base_mask_index, mask_indices, current_plant_index
):
    """L-System for wheat"""

    """Material cleanup"""
    # TODO: Make these materials unique per plant and name them accordingly or move them out of here
    materials = {
        "LeafMaterial": (create_grass_texture, [], {}),
        "StemMaterial": (create_stem_texture, [], {}),
        "HeadMaterial": (create_head_texture, [], {}),
    }
    num_leaf_materials = 10
    for i in range(num_leaf_materials):
        materials[f"LeafMaterial_{i}"] = (
            create_indexed_grass_texture,
            [],
            {"index": i, "material_type": MaterialType.LEAF},
        )
    num_head_materials = 10
    for i in range(num_head_materials):
        materials[f"HeadMaterial_{i}"] = (
            create_indexed_grass_texture,
            [],
            {"index": i, "small": True, "material_type": MaterialType.HEAD},
        )
    restore_materials(materials)

    PLASTOCHRON = 2  # Time between leaf production
    dT = 1  # Time step size
    LeafLen = 30  # Scaling factor for leaf length, 'base leaf length'
    IntLen = 10  # Scaling factor for internode length, 'base internode length'
    BrAngle = 0  # Scaling factor for branching angle (0 = 0 Degrees, 1 = 90 degrees)
    TopInternodeLength = 13  # Length of the top internode

    MaxLeafs = 8  # Not properly used yet

    GerminationDuration = 8 + random.randrange(-2, 2, 1)
    SeedlingTilleringDuration = 45 + random.randrange(-2, 2, 1)
    StemElongationDuration = 25 + random.randrange(-2, 2, 1)
    BootingDuration = 20 + random.randrange(-2, 2, 1)
    HeadingDuration = 8 + random.randrange(-1, 1, 1)
    FloweringDuration = 5 + random.randrange(-1, 1, 1)

    TotalLeafAge = SeedlingTilleringDuration  #  + StemElongationDuration

    TotalWheatAge = (
        GerminationDuration
        + SeedlingTilleringDuration
        + StemElongationDuration
        + BootingDuration
        + HeadingDuration
        + FloweringDuration
    )
    print("Final wheat age:", TotalWheatAge)

    random.seed(plant_seed)
    start_rotation = random.uniform(0, 360)
    head_rotation = random.uniform(0, 360)
    head_tilt = random.uniform(0, 0.3)

    stem_noise = [random.randrange(-2, 2) for x in range(MaxLeafs)]

    leaf_material_index = [
        random.randrange(0, num_leaf_materials, 1) for x in range(MaxLeafs)
    ]
    head_material_index = random.randrange(0, num_head_materials, 1)

    # A(Age, rank)
    axiom = f"/({start_rotation})A(0,1)"

    def get_leaf_rank_in_range(n):
        return min(float(n) / MaxLeafs, 1)

    def get_leaf_age_in_range(age):
        return min(float(age) / TotalLeafAge, 1)

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

    def leaf_angle(n):
        return (n % 2) * 180 if n < 4 else 110 * n

    def apex_production_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)

        age = params_int[0]
        n = params_int[1]

        age += dT

        if n == MaxLeafs:
            if age > TotalLeafAge + StemElongationDuration:
                return f"H(0,0)"
            else:
                return f"A({age},{n})"

        if age >= PLASTOCHRON:
            age = age - PLASTOCHRON
            return f"I({age}, {n})[/({leaf_angle(n)})L({age},{n})])A({age},{n + 1})"
        else:
            return f"A({age},{n})"

    def get_internode_age_in_range(age):
        if age < TotalLeafAge:
            return 0
        return min(float(age - TotalLeafAge) / StemElongationDuration, 1)

    InternodeLengthSpline = Spline2D(
        np.array([[0, 0], [0.1, 0.1], [0.2, 0.1], [0.6, 0.1], [0.9, 1], [1, 1]])
    )

    def internode_length(age):
        return InternodeLengthSpline.evaluate(get_internode_age_in_range(age))[1]

    InternodeTargetLen = Spline2D(np.array([[0, 0.5], [0.3, 1.1], [0.7, 0.8], [1, 1]]))

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
        return (
            f"_({wid})+({stem_noise[n]})F({len},StemMaterial,{base_mask_index + n + 1})"
        )

    LeafTargetLen = Spline2D(np.array([[0, 0.5], [0.3, 1.2], [0.7, 1.0], [1, 0.5]]))

    def leaf_target_len(n):
        return LeafTargetLen.evaluate(get_leaf_rank_in_range(n))[1]

    # LeafLengthSpline = Spline2D(np.array([[0,0.05], [0.1, 0.8], [0.3,1],[0.5, 1],[1, 1]]))
    LeafLengthSpline = Spline2D(np.array([[0, 0.1], [0.1, 0.1], [0.2, 0.3], [1, 1]]))

    def leaf_length(age):
        return LeafLengthSpline.evaluate(get_leaf_age_in_range(age))[1]

    LeafBend = Spline2D(np.array([[0, 0], [0.3, 0], [0.7, 0.05], [1, 0.1]]))

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
        return f"L({leaf_width},{len},{leaf_bend},{orientation},{n},{plant_seed},LeafMaterial_{leaf_material_index[n]},{base_mask_index + n + MaxLeafs + 2},{internode_width(n)},{min(float(age) / (TotalLeafAge + StemElongationDuration + BootingDuration + HeadingDuration), 1)})"

    def aging_production_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)
        age = params_int[0]
        n = params_int[1]
        return f"{symbol}({age + 1},{n})"

    def head_production_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)
        age = params_int[0]
        n = params_int[1]

    FINAL_SPIKELETS = random.randrange(50, 58, 1)
    HeadEmergence = Spline2D(
        np.array(
            [
                [0, 5],
                [0.33, FINAL_SPIKELETS / 3],
                [0.66, FINAL_SPIKELETS * 2 / 3],
                [1, FINAL_SPIKELETS],
            ]
        )
    )

    def head_interpretation_rule(symbol, params_string):
        params_int = parametric_lsystem.parse_parameters(params_string, int)
        age = params_int[0]
        n = params_int[1]  # Not needed

        spikelets = HeadEmergence.evaluate(min(float(age) / HeadingDuration, 1))[1]

        final_internode_length = TopInternodeLength * max(
            0, min((float(age) - float(HeadingDuration)) / float(FloweringDuration), 1)
        )
        scale = max(0.3, min(float(age) / float(HeadingDuration), 1))

        return f"F({final_internode_length},StemMaterial,{base_mask_index + MaxLeafs + 1})/({head_rotation})H({spikelets},HeadMaterial_{head_material_index},{base_mask_index},{head_tilt},{plant_seed},{scale})"

    production_rules = {
        lambda s: s.startswith("A"): apex_production_rule,
        lambda s: s.startswith("I"): aging_production_rule,
        lambda s: s.startswith("L"): aging_production_rule,
        lambda s: s.startswith("H"): aging_production_rule,
    }

    interpretation_rules = {
        lambda s: s.startswith("I"): internode_interpretation_rule,
        lambda s: s.startswith("L"): leaf_interpretation_rule,
        lambda s: s.startswith("H"): head_interpretation_rule,
    }

    mask_indices[current_plant_index] = {
        "head": base_mask_index,
        "internodes": [base_mask_index + i + 1 for i in range(MaxLeafs + 1)],
        "leaves": [base_mask_index + i + MaxLeafs + 2 for i in range(MaxLeafs)],
    }

    lsystem = parametric_lsystem.ParametricLSystem(
        axiom=axiom,
        production_rules=production_rules,
        iterations=derivation_length,
        interpretation_rules=interpretation_rules,
    )
    return lsystem.generate(), base_mask_index + MaxLeafs * 2 + 2, mask_indices
