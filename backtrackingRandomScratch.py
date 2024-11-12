# backtrackingRandom.py

import copy
import logging

# Configure logging for debugging purposes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ZebraRandomSolver:
    def __init__(self, attributes, constraints, num_houses=5):
        """
        Initialize the ZebraRandomSolver with attributes and dynamically generated constraints.

        :param attributes: A dictionary where keys are attribute names (e.g., 'color') and values are lists of possible values.
        :param constraints: A list of dynamically generated constraints.
        :param num_houses: The number of houses in the puzzle (default is 5).
        """
        self.attributes = copy.deepcopy(attributes)
        self.constraints = copy.deepcopy(constraints)
        self.num_houses = num_houses
        self.solution = None

        # Initialize domains for each attribute value
        # Domain is the set of possible house numbers (1 to num_houses)
        self.domains = {}
        for attr, values in self.attributes.items():
            for val in values:
                self.domains[val] = set(range(1, self.num_houses + 1))
        logging.debug(f"Initialized domains: {self.domains}")

    def solve(self):
        """
        Solve the Zebra Puzzle using backtracking with forward checking.

        :return: A list of dictionaries representing each house's attributes if a solution is found; otherwise, False.
        """
        # Make a deep copy of domains to manipulate during solving
        assignment = {}
        success = self.backtrack(assignment, self.domains)
        if success:
            logging.debug("ZebraRandomSolver: Solution found.")
            return self._format_solution()
        else:
            logging.debug("ZebraRandomSolver: No solution found with the given constraints.")
            return False

    def backtrack(self, assignment, domains):
        """
        Recursive backtracking algorithm with forward checking.

        :param assignment: Current assignment of variables.
        :param domains: Current domains of variables.
        :return: True if a solution is found; otherwise, False.
        """
        # If all variables are assigned, return True
        if len(assignment) == len(self.domains):
            self.solution = assignment.copy()
            return True

        # Select the next unassigned variable (attribute value) using Minimum Remaining Values (MRV) heuristic
        var = self.select_unassigned_variable(assignment, domains)
        logging.debug(f"Backtracking: Selected variable '{var}' with domain {domains[var]}")

        for value in sorted(domains[var]):
            logging.debug(f"Trying to assign '{var}' to house {value}")
            if self.is_consistent(var, value, assignment):
                # Assign the value
                assignment[var] = value
                logging.debug(f"Assigned '{var}' to house {value}")

                # Forward Checking: Reduce domains of other variables
                removed = self.forward_check(var, value, domains, assignment)
                if removed is not False:
                    # Continue with the next variable
                    result = self.backtrack(assignment, domains)
                    if result:
                        return True

                    # Undo the assignment and restore domains
                    del assignment[var]
                    self.restore_domains(domains, removed)
                else:
                    # Conflict detected, undo the assignment and continue
                    del assignment[var]
                    # Do not attempt to restore domains since 'removed' is False
                    continue

        # If no valid assignment found, return False
        return False

    def select_unassigned_variable(self, assignment, domains):
        """
        Select the next variable to assign using the Minimum Remaining Values (MRV) heuristic.

        :param assignment: Current assignment of variables.
        :param domains: Current domains of variables.
        :return: The selected variable.
        """
        unassigned_vars = [v for v in self.domains if v not in assignment]
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
        # Check AllDifferent constraints: No two variables of the same attribute can have the same value
        attr = self.get_attribute(var)
        for other_var, other_val in assignment.items():
            other_attr = self.get_attribute(other_var)
            if other_attr == attr and other_val == value:
                logging.debug(f"Consistency Check Failed: '{var}' cannot be assigned to house {value} as '{other_var}' is already assigned to house {value}.")
                return False

        # Check dynamic constraints
        for constraint in self.constraints:
            if 'same_house' in constraint:
                pairs = constraint['same_house']
                if len(pairs) == 2:
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    if var == val1:
                        # The other variable must be assigned the same house
                        if val2 in assignment and assignment[val2] != value:
                            logging.debug(f"Consistency Check Failed: '{var}' and '{val2}' must be in the same house, but house {value} != house {assignment[val2]}.")
                            return False
                    elif var == val2:
                        if val1 in assignment and assignment[val1] != value:
                            logging.debug(f"Consistency Check Failed: '{var}' and '{val1}' must be in the same house, but house {value} != house {assignment[val1]}.")
                            return False
            elif 'next_to' in constraint:
                pairs = constraint['next_to']
                if len(pairs) == 2:
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    if var == val1:
                        if val2 in assignment and abs(assignment[val2] - value) != 1:
                            logging.debug(f"Consistency Check Failed: '{var}' must be next to '{val2}', but |{assignment[val2]} - {value}| != 1.")
                            return False
                    elif var == val2:
                        if val1 in assignment and abs(assignment[val1] - value) != 1:
                            logging.debug(f"Consistency Check Failed: '{var}' must be next to '{val1}', but |{assignment[val1]} - {value}| != 1.")
                            return False
            elif 'left_of' in constraint:
                pairs = constraint['left_of']
                if len(pairs) == 2:
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    if var == val1:
                        if val2 in assignment and (value + 1) != assignment[val2]:
                            logging.debug(f"Consistency Check Failed: '{var}' must be immediately to the left of '{val2}', but {value} + 1 != {assignment[val2]}.")
                            return False
            else:
                logging.warning(f"Unknown constraint type: {constraint}")

        return True

    def forward_check(self, var, value, domains, assignment):
        """
        Perform forward checking by removing incompatible values from the domains of unassigned variables.

        :param var: The variable that was just assigned.
        :param value: The value that was just assigned to the variable.
        :param domains: Current domains of variables.
        :param assignment: Current assignment of variables.
        :return: A list of (variable, removed_value) tuples if successful; otherwise, False.
        """
        removed = []

        for other_var in self.domains:
            if other_var != var and other_var not in assignment:
                if value in domains[other_var]:
                    domains[other_var].remove(value)
                    removed.append((other_var, value))
                    logging.debug(f"Forward Check: Removed house {value} from '{other_var}' domain.")

                # Apply constraints
                for constraint in self.constraints:
                    if 'same_house' in constraint:
                        pairs = constraint['same_house']
                        if (var, value) in pairs or (other_var, value) in pairs:
                            # Variables that must be in the same house
                            for pair in pairs:
                                if pair[1] == other_var:
                                    target_var = pair[1]
                                    if target_var in assignment and assignment[target_var] != value:
                                        logging.debug(f"Forward Check: '{other_var}' must be in the same house as '{var}', but house {value} != house {assignment[target_var]}.")
                                        return False
                    elif 'next_to' in constraint:
                        pairs = constraint['next_to']
                        if (var, value) in pairs or (other_var, value) in pairs:
                            # Variables that must be next to each other
                            possible_values = set()
                            for v in domains[other_var]:
                                if abs(v - value) == 1:
                                    possible_values.add(v)
                            if not possible_values:
                                logging.debug(f"Forward Check Failed: No possible houses next to house {value} for '{other_var}'.")
                                return False
                            if domains[other_var] != possible_values:
                                removed_values = domains[other_var] - possible_values
                                for rv in removed_values:
                                    domains[other_var].remove(rv)
                                    removed.append((other_var, rv))
                                    logging.debug(f"Forward Check: '{other_var}' must be next to '{var}'. Removed house {rv} from '{other_var}' domain.")
                    elif 'left_of' in constraint:
                        pairs = constraint['left_of']
                        if (var, value) in pairs or (other_var, value) in pairs:
                            # Variables that must be immediately to the left of others
                            possible_values = set()
                            for v in domains[other_var]:
                                if (v - 1) == value:
                                    possible_values.add(v)
                            if not possible_values:
                                logging.debug(f"Forward Check Failed: No possible houses to the right of house {value} for '{other_var}'.")
                                return False
                            if domains[other_var] != possible_values:
                                removed_values = domains[other_var] - possible_values
                                for rv in removed_values:
                                    domains[other_var].remove(rv)
                                    removed.append((other_var, rv))
                                    logging.debug(f"Forward Check: '{other_var}' must be immediately to the right of '{var}'. Removed house {rv} from '{other_var}' domain.")
                    else:
                        logging.warning(f"Unknown constraint type: {constraint}")

        return removed

    def restore_domains(self, domains, removed):
        """
        Restore the removed values to the domains.

        :param domains: Current domains of variables.
        :param removed: A list of (variable, removed_value) tuples.
        """
        for var, val in removed:
            domains[var].add(val)
            logging.debug(f"Restore Domains: Restored house {val} to '{var}' domain.")

    def get_attribute(self, var):
        """
        Get the attribute type of a given variable.

        :param var: The variable (attribute value).
        :return: The attribute name.
        """
        for attr, values in self.attributes.items():
            if var in values:
                return attr
        return None

    def _format_solution(self):
        """
        Format the CSP solution into a list of house attribute dictionaries.

        :return: List of dictionaries representing each house's attributes.
        """
        houses = [{} for _ in range(self.num_houses)]

        for attr, values in self.attributes.items():
            for val in values:
                house_num = self.solution.get(val)
                if house_num is not None:
                    houses[house_num - 1][attr] = val

        logging.debug(f"Formatted Solution: {houses}")
        return houses
