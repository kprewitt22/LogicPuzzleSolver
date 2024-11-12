# backtrackingOriginal.py

import copy
import logging
from collections import defaultdict

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
                               "pet": ["dog", "snail", "fox", "horse", "zebra"]
                           }
        :param clues: List of clues where each clue is a dictionary with 'id' and 'description'.
                      Example:
                      [
                          {"id": 1, "description": "There are five houses."},
                          {"id": 2, "description": "The Englishman lives in the red house."},
                          ...
                      ]
        :param debug: Boolean flag to enable debug mode for verbose output.
        :param forwardcheck: Boolean flag to enable forward checking.
        """
        self.attributes = copy.deepcopy(attributes)
        self.clues = clues
        self.debug = debug
        self.forwardcheck = forwardcheck
        self.num_houses = 5
        self.houses = list(range(1, self.num_houses + 1))  # House numbers 1 to 5

        # Initialize variables and domains
        self.variables = self.setup_variables()
        self.domains = self.setup_domains()

        # Initialize constraints
        self.constraints = defaultdict(list)  # Constraints are per variable
        self.setup_constraints()

    def setup_variables(self):
        """
        Define variables for the CSP.
        Each attribute for each house is treated as a separate variable.
        :return: List of variable names.
        """
        variables = []
        for house in self.houses:
            for attr, values in self.attributes.items():
                var = f"{attr}_{house}"
                variables.append(var)
        if self.debug:
            print(f"Variables: {variables}")
        return variables

    def setup_domains(self):
        """
        Define the domain for each variable.
        :return: Dictionary mapping variable names to their possible values.
        """
        domains = {}
        for var in self.variables:
            attr, house = var.rsplit('_', 1)
            domains[var] = set(self.attributes[attr])
        if self.debug:
            print(f"Initial Domains: {domains}")
        return domains

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
                self._add_same_house_constraint("nationality", "Englishman", "color", "red")
            elif "spaniard" in description and "owns the dog" in description:
                self._add_same_house_constraint("nationality", "Spaniard", "pet", "dog")
            elif "ukrainian" in description and "drinks tea" in description:
                self._add_same_house_constraint("nationality", "Ukrainian", "beverage", "tea")
            elif "coffee" in description and "green house" in description:
                self._add_same_house_constraint("beverage", "coffee", "color", "green")
            elif "green house" in description and "immediately to the right of the ivory house" in description:
                self._add_relative_position_constraint("color", "ivory", "color", "green", direction="right")
            elif "old gold smoker" in description and "owns snails" in description:
                self._add_same_house_constraint("cigarette", "Old Gold", "pet", "snail")
            elif "kools" in description and "yellow house" in description:
                self._add_same_house_constraint("cigarette", "Kools", "color", "yellow")
            elif ("milk is drunk in the center house" in description) or ("milk is drunk in the middle house" in description) or (("center house" in description or "middle house" in description) and "milk" in description):
                center_house = 3
                var = f"beverage_{center_house}"
                self.constraints[var].append(("fixed", "milk"))
                if self.debug:
                    print("Added constraint: Milk is drunk in the center/middle house.")
            elif "norwegian" in description and "first house" in description:
                var = f"nationality_{1}"
                self.constraints[var].append(("fixed", "Norwegian"))
                if self.debug:
                    print("Added constraint: The Norwegian lives in the first house.")
            elif "chesterfields" in description and "next to the man with the fox" in description:
                self._add_next_to_constraint("cigarette", "Chesterfields", "pet", "fox")
            elif "kools" in description and "next to the house where the horse is kept" in description:
                self._add_next_to_constraint("cigarette", "Kools", "pet", "horse")
            elif "lucky strike" in description and "drinks orange juice" in description:
                self._add_same_house_constraint("cigarette", "Lucky Strike", "beverage", "orange juice")
            elif "japanese" in description and "smokes parliaments" in description:
                self._add_same_house_constraint("nationality", "Japanese", "cigarette", "Parliaments")
            elif "norwegian" in description and "next to the blue house" in description:
                self._add_next_to_constraint("nationality", "Norwegian", "color", "blue")
            elif "japanese" in description and "owns the zebra" in description:
                self._add_same_house_constraint("nationality", "Japanese", "pet", "zebra")
            elif "there are five houses" in description:
                # Already handled by variable definitions
                if self.debug:
                    print("Clue 1: There are five houses. Already defined.")
            else:
                if self.debug:
                    print(f"Clue {clue['id']} not recognized or not implemented.")

    def _add_same_house_constraint(self, attr1, value1, attr2, value2):
        """
        Add a constraint that attr1=value1 implies attr2=value2 for the same house.

        :param attr1: First attribute type (e.g., 'nationality')
        :param value1: Value for the first attribute (e.g., 'Englishman')
        :param attr2: Second attribute type (e.g., 'color')
        :param value2: Value for the second attribute (e.g., 'red')
        """
        for house in self.houses:
            var1 = f"{attr1}_{house}"
            var2 = f"{attr2}_{house}"
            # Constraint: If var1 == value1 then var2 == value2
            # Represented as ('implies', trigger_val, var2, expected_val)
            self.constraints[var1].append(("implies", value1, var2, value2))
            if self.debug:
                print(f"Added constraint: If {var1} == '{value1}', then {var2} == '{value2}'")

    def _add_relative_position_constraint(self, attr1, value1, attr2, value2, direction="right"):
        """
        Add a constraint that attr2=value2 is immediately to the right/left of attr1=value1.

        :param attr1: First attribute type (e.g., 'color')
        :param value1: Value for the first attribute (e.g., 'ivory')
        :param attr2: Second attribute type (e.g., 'color')
        :param value2: Value for the second attribute (e.g., 'green')
        :param direction: 'right' or 'left' indicating the relative position
        """
        # For 'immediately to the right', house_n must be house_m + 1
        # We'll handle this in the forward checking by constraining the positions
        self.constraints["relative_position"].append((attr1, value1, attr2, value2, direction))
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
        # 'next_to' is bidirectional; we'll enforce both directions
        self.constraints["next_to"].append((attr1, value1, attr2, value2))
        self.constraints["next_to"].append((attr2, value2, attr1, value1))
        if self.debug:
            print(f"Added constraints: {attr1}='{value1}' is next to {attr2}='{value2}', and vice versa.")

    def solve(self):
        """
        Solve the CSP problem using backtracking with forward checking.

        :return: List of dictionaries where each dictionary represents a house with its attributes.
                 Example:
                 [
                     {"number": "1", "color": "yellow", "nationality": "Norwegian", "beverage": "water", 
                      "cigarette": "Kools", "pet": "fox"},
                     ...
                 ]
                 Returns None if no solution is found.
        """
        assignment = {}
        result = self.backtrack(assignment, copy.deepcopy(self.domains))
        if self.debug:
            if result:
                print("Solution found:")
                for house in result:
                    print(house)
            else:
                print("No solution found.")
        return result

    def backtrack(self, assignment, domains):
        """
        Recursive backtracking algorithm with forward checking.

        :param assignment: Current assignment of variables.
        :param domains: Current domains of variables.
        :return: List of house dictionaries if a solution is found; otherwise, None.
        """
        # If all variables are assigned, return the formatted solution
        if len(assignment) == len(self.variables):
            return self._format_solution(assignment)

        # Select the next unassigned variable using the Minimum Remaining Values (MRV) heuristic
        var = self.select_unassigned_variable(assignment, domains)
        if self.debug:
            print(f"Backtracking: Selected variable '{var}' with domain {domains[var]}")

        for value in sorted(domains[var]):
            if self.is_consistent(var, value, assignment):
                # Assign the value
                assignment[var] = value
                if self.debug:
                    print(f"Assigned '{var}' = '{value}'")

                # Create a deep copy of domains for forward checking
                new_domains = copy.deepcopy(domains)
                new_domains[var] = {value}

                # Forward Checking: Remove inconsistent values from domains
                if self.forwardcheck:
                    consistent, new_domains = self.forward_check(var, value, assignment, new_domains)
                    if not consistent:
                        if self.debug:
                            print(f"Forward checking failed after assigning '{var}' = '{value}'")
                        del assignment[var]
                        continue

                # Recursive call
                result = self.backtrack(assignment, new_domains)
                if result:
                    return result

                # If failure, remove the assignment and try next value
                if self.debug:
                    print(f"Backtracking: Removing assignment '{var}' = '{value}'")
                del assignment[var]

        # If no valid assignment found, return None
        return None

    def select_unassigned_variable(self, assignment, domains):
        """
        Select the next variable to assign using the Minimum Remaining Values (MRV) heuristic.

        :param assignment: Current assignment of variables.
        :param domains: Current domains of variables.
        :return: The selected variable.
        """
        unassigned_vars = [v for v in self.variables if v not in assignment]
        # MRV: choose the variable with the smallest domain
        var = min(unassigned_vars, key=lambda var: len(domains[var]))
        return var

    def is_consistent(self, var, value, assignment):
        """
        Check if assigning 'var' to 'value' is consistent with the current assignment and constraints.

        :param var: The variable to assign.
        :param value: The value to assign to the variable.
        :param assignment: Current assignment of variables.
        :return: True if consistent; otherwise, False.
        """
        # Check 'fixed' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "fixed":
                fixed_val = constraint[1]
                if value != fixed_val:
                    if self.debug:
                        print(f"Consistency Check Failed: '{var}' is fixed to '{fixed_val}', but trying to assign '{value}'")
                    return False

        # Check 'implies' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "implies":
                _, trigger_val, var2, expected_val = constraint
                if value == trigger_val:
                    if var2 in assignment and assignment[var2] != expected_val:
                        if self.debug:
                            print(f"Consistency Check Failed: '{var}' == '{value}' implies '{var2}' == '{expected_val}', but '{var2}' == '{assignment[var2]}'")
                        return False

        # Check 'next_to' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "next_to":
                _, val1, _, val2 = constraint
                if value == val1:
                    # Find houses where attr2 == val2
                    houses_with_val2 = [house for house in self.houses if f"{self.get_attribute(var)}_{house}" != var]
                    adjacent_houses = set()
                    house_num = int(var.rsplit('_', 1)[1])
                    if house_num > 1:
                        adjacent_houses.add(house_num - 1)
                    if house_num < self.num_houses:
                        adjacent_houses.add(house_num + 1)
                    # Check if any adjacent house has attr2 == val2
                    exists = False
                    for adj_house in adjacent_houses:
                        adj_var = f"{self.get_attribute(var)}_{adj_house}"
                        if adj_var in assignment:
                            if assignment[adj_var] == val2:
                                exists = True
                                break
                        elif val2 in self.domains[adj_var]:
                            exists = True
                            break
                    if not exists:
                        if self.debug:
                            print(f"Consistency Check Failed: '{var}' == '{value}' requires an adjacent house with '{val2}' in '{self.get_attribute(var)}'")
                        return False

        # Check 'relative_position' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "relative_position":
                _, val1, _, val2, direction = constraint
                if value == val1:
                    house_num = int(var.rsplit('_', 1)[1])
                    if direction == "right":
                        target_house = house_num + 1
                        if target_house > self.num_houses:
                            if self.debug:
                                print(f"Consistency Check Failed: '{var}' assigned to '{value}' cannot have a '{self.get_attribute(var)}' to the right.")
                            return False
                        target_var = f"{self.get_attribute(var)}_{target_house}"
                        if target_var in assignment:
                            if assignment[target_var] != val2:
                                if self.debug:
                                    print(f"Consistency Check Failed: '{var}' == '{value}' requires '{target_var}' == '{val2}', but found '{assignment[target_var]}'")
                                return False
                        else:
                            if val2 not in self.domains[target_var]:
                                if self.debug:
                                    print(f"Consistency Check Failed: '{var}' == '{value}' requires '{target_var}' to be '{val2}', which is not in its domain.")
                                return False
                    elif direction == "left":
                        target_house = house_num - 1
                        if target_house < 1:
                            if self.debug:
                                print(f"Consistency Check Failed: '{var}' assigned to '{value}' cannot have a '{self.get_attribute(var)}' to the left.")
                            return False
                        target_var = f"{self.get_attribute(var)}_{target_house}"
                        if target_var in assignment:
                            if assignment[target_var] != val2:
                                if self.debug:
                                    print(f"Consistency Check Failed: '{var}' == '{value}' requires '{target_var}' == '{val2}', but found '{assignment[target_var]}'")
                                return False
                        else:
                            if val2 not in self.domains[target_var]:
                                if self.debug:
                                    print(f"Consistency Check Failed: '{var}' == '{value}' requires '{target_var}' to be '{val2}', which is not in its domain.")
                                return False

        return True

    def forward_check(self, var, value, assignment, domains):
        """
        Perform forward checking by removing inconsistent values from the domains of unassigned variables.

        :param var: The variable that was just assigned.
        :param value: The value that was just assigned to the variable.
        :param assignment: Current assignment of variables.
        :param domains: Current domains of variables.
        :return: Tuple (is_consistent, updated_domains)
        """
        # Remove 'value' from all other variables' domains for the same attribute (AllDifferent)
        attr, house = var.rsplit('_', 1)
        for other_house in self.houses:
            if other_house != int(house):
                other_var = f"{attr}_{other_house}"
                if value in domains[other_var]:
                    domains[other_var].remove(value)
                    if self.debug:
                        print(f"Forward Check: Removed '{value}' from domain of '{other_var}' due to AllDifferent constraint.")

                if not domains[other_var]:
                    if self.debug:
                        print(f"Forward Check Failed: Domain of '{other_var}' is empty.")
                    return False, domains

        # Handle 'implies' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "implies":
                _, trigger_val, var2, expected_val = constraint
                if value == trigger_val:
                    if expected_val not in domains[var2]:
                        if self.debug:
                            print(f"Forward Check Failed: '{var2}' cannot be '{expected_val}' as required by implies constraint.")
                        return False, domains
                    if self.debug:
                        print(f"Forward Check: Setting '{var2}' to '{expected_val}' due to implies constraint.")
                    # Set var2's domain to only expected_val
                    domains[var2] = {expected_val}
                    # If var2 is already assigned, check consistency
                    if var2 in assignment:
                        if assignment[var2] != expected_val:
                            if self.debug:
                                print(f"Forward Check Failed: '{var2}' already assigned to '{assignment[var2]}' which contradicts the implies constraint.")
                            return False, domains

        # Handle 'next_to' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "next_to":
                _, val1, _, val2 = constraint
                if value == val1:
                    house_num = int(var.rsplit('_', 1)[1])
                    adjacent_houses = []
                    if house_num > 1:
                        adjacent_houses.append(house_num - 1)
                    if house_num < self.num_houses:
                        adjacent_houses.append(house_num + 1)
                    # For 'next_to', at least one adjacent house must have val2
                    possible = False
                    for adj_house in adjacent_houses:
                        adj_var = f"{self.get_attribute(var)}_{adj_house}"
                        if val2 in domains[adj_var]:
                            possible = True
                            break
                    if not possible:
                        if self.debug:
                            print(f"Forward Check Failed: No adjacent house can have '{self.get_attribute(var)}' = '{val2}'")
                        return False, domains

        # Handle 'relative_position' constraints
        for constraint in self.constraints.get(var, []):
            if constraint[0] == "relative_position":
                _, val1, _, val2, direction = constraint
                if value == val1:
                    house_num = int(var.rsplit('_', 1)[1])
                    if direction == "right":
                        target_house = house_num + 1
                        if target_house > self.num_houses:
                            if self.debug:
                                print(f"Forward Check Failed: '{var}' assigned to '{value}' cannot have a '{self.get_attribute(var)}' to the right.")
                            return False, domains
                        target_var = f"{self.get_attribute(var)}_{target_house}"
                        if target_var in assignment:
                            if assignment[target_var] != val2:
                                if self.debug:
                                    print(f"Forward Check Failed: '{var}' == '{value}' requires '{target_var}' == '{val2}', but found '{assignment[target_var]}'")
                                return False, domains
                        else:
                            if val2 not in domains[target_var]:
                                if self.debug:
                                    print(f"Forward Check Failed: '{var}' == '{value}' requires '{target_var}' to be '{val2}', which is not in its domain.")
                                return False, domains
                            # Restrict target_var's domain to only val2
                            domains[target_var] = {val2}
                            if self.debug:
                                print(f"Forward Check: Set '{target_var}' to '{val2}' due to relative position constraint.")
                    elif direction == "left":
                        target_house = house_num - 1
                        if target_house < 1:
                            if self.debug:
                                print(f"Forward Check Failed: '{var}' assigned to '{value}' cannot have a '{self.get_attribute(var)}' to the left.")
                            return False, domains
                        target_var = f"{self.get_attribute(var)}_{target_house}"
                        if target_var in assignment:
                            if assignment[target_var] != val2:
                                if self.debug:
                                    print(f"Forward Check Failed: '{var}' == '{value}' requires '{target_var}' == '{val2}', but found '{assignment[var2]}'")
                                return False, domains
                        else:
                            if val2 not in domains[target_var]:
                                if self.debug:
                                    print(f"Forward Check Failed: '{var}' == '{value}' requires '{target_var}' to be '{val2}', which is not in its domain.")
                                return False, domains
                            # Restrict target_var's domain to only val2
                            domains[target_var] = {val2}
                            if self.debug:
                                print(f"Forward Check: Set '{target_var}' to '{val2}' due to relative position constraint.")

        return True, domains

    def _format_solution(self, assignment):
        """
        Format the assignment into a list of house dictionaries.

        :param assignment: Final assignment of variables.
        :return: List of dictionaries representing each house's attributes.
        """
        houses_solution = defaultdict(dict)
        for var, val in assignment.items():
            attr, house_num = var.rsplit('_', 1)
            houses_solution[int(house_num)][attr] = val

        # Convert defaultdict to a sorted list based on house number
        sorted_houses = []
        for house_num in sorted(houses_solution.keys()):
            house_attrs = houses_solution[house_num]
            house_attrs["number"] = str(house_num)
            sorted_houses.append(house_attrs)

        if self.debug:
            print("Formatted Solution:")
            for house in sorted_houses:
                print(house)

        return sorted_houses

    def get_attribute(self, var):
        """
        Extract the attribute type from a variable name.

        :param var: Variable name (e.g., 'nationality_1')
        :return: Attribute type (e.g., 'nationality')
        """
        return var.rsplit('_', 1)[0]
