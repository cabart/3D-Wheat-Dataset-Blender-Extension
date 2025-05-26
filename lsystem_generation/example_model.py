from . import parametric_lsystem


def example_plant(
    derivation_length, plant_seed, base_mask_index, mask_indices, current_plant_index
):
    """Used for testing if basic lsystem generation and drawing works, does not implement correct plant part indexing"""
    axiom = "!(2)B(0)"

    def rule1(symbol, params_string):
        params_float = [int(num) for num in params_string.split(",")]
        n = params_float[0]
        if n % 2:
            return f"F(10)[+F(10)&F(10)]B({n + 1})"
        else:
            return f"F(10)[-F(10)^F(10)]B({n + 1})"

    production_rules = {lambda s: s.startswith("B"): rule1}

    lsystem = parametric_lsystem.ParametricLSystem(
        axiom=axiom, production_rules=production_rules, iterations=derivation_length
    )

    return lsystem.generate(), base_mask_index, mask_indices


if __name__ == "__main__":
    example_plant()
