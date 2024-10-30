# backTracking.py

import constraint
from collections import defaultdict

class ZebraPuzzleSolver:
    def __init__(self, attributes, clues, debug=False, forwardcheck=True):
        """
        Initialize the ZebraPuzzleSolver with attributes and clues.

        :param attributes: Dictionary containing attribute types as keys and lists of possible values.
                           Example:
                           {
                               "color": ["red", "green", "ivory", "yellow", "blue"],
                               "nationality": ["Englishman", "Spaniard", "Ukrainian", "Norwegian", "Japanese"],
                               "beverage": ["coffee", "tea", "milk", "orange juice", "water"],
                               "cigarette": ["Old Gold", "Kools", "Chesterfields", "Lucky Strike", "Parliaments"],
                               "pet": ["dog", "snails", "fox", "horse", "zebra"]
                           }
        :param clues: List of clues where each clue is a dictionary with 'id' and 'description'.
                      Example:
                      [
                          {"id": 1, "description": "There are five houses."},
                          {"id": 2, "description": "The Englishman lives in the red house."},
                          ...
                      ]
        :param debug: Boolean flag to enable debug mode for verbose output.
        """
        self.attributes = attributes
        self.clues = clues
        self.debug = debug
        self.forwardcheck = forwardcheck
        self.problem = constraint.Problem()

        self.num_houses = 5
        self.houses = list(range(1, self.num_houses + 1))  # House 1 to House 5 .. i.e. 6-1=5 total 

        self.setup_variables()
        self.setup_constraints()

    def setup_variables(self):
        """
        Define variables and their domains for the CSP problem.
        Each attribute for each house is treated as a separate variable.
        Additionally, enforce that each attribute's values are all different across houses.
        """
        for attr, values in self.attributes.items():
            var_names = [f"{attr}_{house}" for house in self.houses]
            self.problem.addVariables(var_names, values)
            if self.debug:
                print(f"Added variables for attribute '{attr}': {var_names}")

        # Enforce AllDifferent constraint for each attribute across houses
        for attr in self.attributes:
            var_names = [f"{attr}_{house}" for house in self.houses]
            self.problem.addConstraint(constraint.AllDifferentConstraint(), var_names)
            if self.debug:
                print(f"Added AllDifferent constraint for attribute '{attr}'")

    def setup_constraints(self):
        """
        Apply the clues as constraints to the CSP problem.
        Constraints are defined based on the provided clues.
        """
        for clue in self.clues:
            description = clue["description"].lower()
            if self.debug:
                print(f"Processing clue {clue['id']}: {clue['description']}")

            if "englishman" in description and "red house" in description:
                self._add_same_attribute_constraint("nationality", "Englishman", "color", "red")
            elif "spaniard" in description and "owns the dog" in description:
                self._add_same_attribute_constraint("nationality", "Spaniard", "pet", "dog")
            elif "ukrainian" in description and "drinks tea" in description:
                self._add_same_attribute_constraint("nationality", "Ukrainian", "beverage", "tea")
            elif "coffee" in description and "green house" in description:
                self._add_same_attribute_constraint("beverage", "coffee", "color", "green")
            elif "green house" in description and "immediately to the right of the ivory house" in description:
                self._add_relative_position_constraint("color", "ivory", "color", "green", direction="right")
            elif "old gold smoker" in description and "owns snails" in description:
                self._add_same_attribute_constraint("cigarette", "Old Gold", "pet", "snails")
            elif "kools" in description and "yellow house" in description:
                self._add_same_attribute_constraint("cigarette", "Kools", "color", "yellow")
            elif ("milk is drunk in the center house" in description) or ("milk is drunk in the middle house" in description) or (("center house" in description or "middle house" in description) and "milk" in description):
                center_house = 3
                self.problem.addConstraint(lambda beverage: beverage == "milk", [f"beverage_{center_house}"])
                if self.debug:
                    print("Added constraint: Milk is drunk in the center/middle house.")
            elif "norwegian" in description and "first house" in description:
                self.problem.addConstraint(lambda nationality: nationality == "Norwegian", ["nationality_1"])
                if self.debug:
                    print("Added constraint: The Norwegian lives in the first house.")
            elif "chesterfields" in description and "next to the man with the fox" in description:
                self._add_next_to_constraint("cigarette", "Chesterfields", "pet", "fox")
            elif "kools" in description and "next to the house where the horse is kept" in description:
                self._add_next_to_constraint("cigarette", "Kools", "pet", "horse")
            elif "lucky strike" in description and "drinks orange juice" in description:
                self._add_same_attribute_constraint("cigarette", "Lucky Strike", "beverage", "orange juice")
            elif "japanese" in description and "smokes parliaments" in description:
                self._add_same_attribute_constraint("nationality", "Japanese", "cigarette", "Parliaments")
            elif "norwegian" in description and "next to the blue house" in description:
                self._add_next_to_constraint("nationality", "Norwegian", "color", "blue")
            elif "japanese" in description and "owns the zebra" in description:
                self._add_same_attribute_constraint("nationality", "Japanese", "pet", "zebra")
            elif "there are five houses" in description:
                # Already handled by variable definitions
                if self.debug:
                    print("Clue 1: There are five houses. Already defined.")
            else:
                if self.debug:
                    print(f"Clue {clue['id']} not recognized or not implemented.")

    def _add_same_attribute_constraint(self, attr1, value1, attr2, value2):
        """
        Add a constraint that attr1=value1 implies attr2=value2 for the same house.

        :param attr1: First attribute type (e.g., 'nationality')
        :param value1: Value for the first attribute (e.g., 'Englishman')
        :param attr2: Second attribute type (e.g., 'color')
        :param value2: Value for the second attribute (e.g., 'red')
        """
        for house in self.houses:
            self.problem.addConstraint(
                lambda a1, a2: (a1 != value1) or (a2 == value2),
                (f"{attr1}_{house}", f"{attr2}_{house}")
            )
            if self.debug:
                print(f"Added constraint: If {attr1}_{house} == {value1} then {attr2}_{house} == {value2}")

    def _add_relative_position_constraint(self, attr1, value1, attr2, value2, direction="right"):
        """
        Add a constraint that attr2=value2 is immediately to the right/left of attr1=value1.

        :param attr1: First attribute type (e.g., 'color')
        :param value1: Value for the first attribute (e.g., 'ivory')
        :param attr2: Second attribute type (e.g., 'color')
        :param value2: Value for the second attribute (e.g., 'green')
        :param direction: 'right' or 'left' indicating the relative position
        """
        vars_attr1 = [f"{attr1}_{house}" for house in self.houses]
        vars_attr2 = [f"{attr2}_{house}" for house in self.houses]

        def relative_position_constraint(*args):
            attr1_values = args[:self.num_houses]
            attr2_values = args[self.num_houses:]

            for i in range(self.num_houses - 1):
                if direction == "right":
                    if attr1_values[i] == value1 and attr2_values[i + 1] == value2:
                        return True
                elif direction == "left":
                    if attr1_values[i] == value1 and attr2_values[i - 1] == value2:
                        return True
            return False

        self.problem.addConstraint(relative_position_constraint, vars_attr1 + vars_attr2)
        if self.debug:
            print(f"Added constraint: The {attr2} house is immediately to the {direction} of the {attr1} house.")

    def _add_next_to_constraint(self, attr1, value1, attr2, value2):
        """
        Add a constraint that a house with attr1=value1 is next to a house with attr2=value2.

        :param attr1: The first attribute type (e.g., 'cigarette')
        :param value1: The value for the first attribute (e.g., 'Chesterfields')
        :param attr2: The second attribute type (e.g., 'pet')
        :param value2: The value for the second attribute (e.g., 'fox')
        """
        vars_attr1 = [f"{attr1}_{house}" for house in self.houses]
        vars_attr2 = [f"{attr2}_{house}" for house in self.houses]

        def next_to_constraint(*args):
            attr1_values = args[:self.num_houses]
            attr2_values = args[self.num_houses:]

            # Find all house indices where attr1 == value1
            attr1_houses = [i for i, val in enumerate(attr1_values, start=1) if val == value1]
            # Find all house indices where attr2 == value2
            attr2_houses = [i for i, val in enumerate(attr2_values, start=1) if val == value2]

            # Check if any house with attr1=value1 is next to any house with attr2=value2
            for h1 in attr1_houses:
                for h2 in attr2_houses:
                    if abs(h1 - h2) == 1:
                        return True
            return False

        self.problem.addConstraint(next_to_constraint, vars_attr1 + vars_attr2)
        if self.debug:
            print(f"Added constraint: {attr1}={value1} is next to {attr2}={value2}.")

    def solve(self):
        """
        Solve the CSP problem and return the solution.

        :return: List of dictionaries where each dictionary represents a house with its attributes.
                 Example:
                 [
                     {"number": "1", "color": "yellow", "nationality": "Norwegian", "beverage": "water", 
                      "cigarette": "Kools", "pet": "fox"},
                     ...
                 ]
                 Returns None if no solution is found.
        """
        solutions = self.problem.getSolutions() #Automatic Python library to get backtracking w/ forward checking result
        if self.debug:
            print(f"Number of solutions found: {len(solutions)}")

        if solutions:
            # Assuming we only need the first solution
            solution = solutions[0]
            if self.debug:
                print("Solution:")
                for var, val in solution.items():
                    print(f"  {var} = {val}")

            # Transform the solution into a list of house dictionaries
            houses_solution = defaultdict(dict)
            for var, val in solution.items():
                attr, house_num = var.rsplit('_', 1)
                houses_solution[int(house_num)][attr] = val

            # Convert defaultdict to a sorted list based on house number
            sorted_houses = []
            for house_num in sorted(houses_solution.keys()):
                house_attrs = houses_solution[house_num]
                house_attrs["number"] = str(house_num)
                sorted_houses.append(house_attrs)

            return sorted_houses
        else:
            if self.debug:
                print("No solution found.")
            return None