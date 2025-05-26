"""Global values for whole Blender extension"""

from .operators.camera_sampling_methods import (
    fibonacci_lattice_sampling_hemisphere,
    fibonacci_lattice_sampling_cap,
    fibonacci_lattice_sampling_cap_inverse,
    fibonacci_lattice_sampling_hemisphere_inverse_spiral,
    FIP_cameras,
    colmap_cameras,
    random_sampling_hemisphere,
    circle_on_sphere_sampling,
)
from .lsystem_generation import example_model, maize_model, wheat_model
from .lsystem_interpretation import draw_lsystem

import importlib

importlib.reload(example_model)
importlib.reload(wheat_model)
importlib.reload(maize_model)
importlib.reload(draw_lsystem)


def init():
    # Two-dimensional list of lstring states for each plant model
    global global_lstring_states
    global_lstring_states = []

    global plant_models
    plant_models = {
        "wheat": (wheat_model.wheat, draw_lsystem.DrawWheat),
        "maize": (maize_model.maize, draw_lsystem.DrawMaize),
        "simple": (example_model.example_plant, draw_lsystem.DrawLSystem),
    }

    global plant_labels
    plant_labels = dict()

    global max_plant_label
    max_plant_label = 0

    global camera_placements
    camera_placements = {
        "fip_cameras": FIP_cameras,
        "colmap_cameras": colmap_cameras,
        "fibonacci_lattice_hemisphere": fibonacci_lattice_sampling_hemisphere,
        "fibonacci_lattice_hemisphere_inverse_spiral": fibonacci_lattice_sampling_hemisphere_inverse_spiral,
        "fibonacci_lattice_cap": fibonacci_lattice_sampling_cap,
        "fibonacci_lattice_cap_inverse": fibonacci_lattice_sampling_cap_inverse,
        "random_sampling_hemisphere": random_sampling_hemisphere,
        "circle_on_sphere": circle_on_sphere_sampling,
    }
