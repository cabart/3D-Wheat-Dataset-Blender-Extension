import random
import bpy


class ParametricLSystem:
    def __init__(
        self, axiom: str, production_rules, iterations: int, interpretation_rules={}
    ):
        self.axiom = axiom
        self.production_rules = production_rules
        self.iterations = iterations
        self.interpretation_rules = interpretation_rules

    def apply_rules(self, symbol, parameters, mode):
        if mode == "production":
            rules = self.production_rules
        elif mode == "interpretation":
            rules = self.interpretation_rules
        else:
            raise ValueError

        # Check if there is a matching rule and apply it
        for pattern, transformation in rules.items():
            if pattern(symbol):
                return transformation(symbol, parameters)
        # If no matching rule, return unchanged
        if parameters == "":
            return symbol
        return f"{symbol}({parameters})"

    def apply_production_rules(self, symbol, parameters):
        return self.apply_rules(symbol, parameters, "production")

    def apply_interpretation_rules(self, symbol, parameters):
        return self.apply_rules(symbol, parameters, "interpretation")

    def generate(self):
        """Returns a list of strings holding all intermediate steps of the generated model"""
        all_production_states = [self.axiom]
        all_interpretation_states = [""]  # TODO: Interpret axiom

        result = self.axiom
        for i in range(self.iterations):
            new_result = ""
            interpretation_result = ""
            index = 0
            while index < len(result):
                symbol = result[index]

                parameters = ""
                if index + 1 < len(result) and result[index + 1] == "(":
                    start = index + 2
                    end = result.index(")", start)
                    parameters = result[start:end]
                    index = end
                transformed = self.apply_production_rules(symbol, parameters)
                new_result += transformed
                interpretation_result += self.apply_interpretation_rules(
                    symbol, parameters
                )
                index += 1

            result = new_result
            all_production_states.append(result)
            all_interpretation_states.append(interpretation_result)
        return all_interpretation_states


def parse_parameters(params_string, convert_type=float):
    """Convert a string of the form '(a,b,c)' into a list of numbers. If substring is not a number return as string instead."""

    def parse_num(num):
        try:
            return convert_type(num)
        except:
            return num

    return [parse_num(num) for num in params_string.split(",")]
