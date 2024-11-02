# backtrackingRandom.py

from constraint import Problem, AllDifferentConstraint
import copy

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

    def solve(self):
        """
        Solve the Zebra Puzzle using the python-constraint library.

        :return: A list of dictionaries representing each house's attributes if a solution is found; otherwise, False.
        """
        problem = Problem()

        # Define variables: Each attribute value is a variable with domain as house numbers 1 to num_houses
        for attr, values in self.attributes.items():
            problem.addVariables(values, range(1, self.num_houses + 1))

        # Add AllDifferent constraints for each attribute type
        for attr, values in self.attributes.items():
            problem.addConstraint(AllDifferentConstraint(), values)

        # Map dynamic constraints to CSP constraints
        self._map_constraints(problem)

        # Get all solutions (ideally one unique solution)
        solutions = problem.getSolutions()

        if not solutions:
            print("ZebraRandomSolver: No solution found with the given constraints.")
            return False

        # Assuming a unique solution, take the first one
        self.solution = solutions[0]
        return self._format_solution()

    def _map_constraints(self, problem):
        """
        Translate dynamic constraints into CSP constraints.

        :param problem: The CSP problem instance.
        """
        for constraint_dict in self.constraints:
            if 'same_house' in constraint_dict:
                pairs = constraint_dict['same_house']
                if len(pairs) == 2:
                    # Both pairs must be assigned to the same house
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    problem.addConstraint(lambda a, b: a == b, (val1, val2))
                else:
                    print(f"ZebraRandomSolver: Unsupported 'same_house' constraint format: {constraint_dict}")
            elif 'next_to' in constraint_dict:
                pairs = constraint_dict['next_to']
                if len(pairs) == 2:
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    # Add constraint that val1 is next to val2
                    problem.addConstraint(lambda a, b: abs(a - b) == 1, (val1, val2))
                else:
                    print(f"ZebraRandomSolver: Unsupported 'next_to' constraint format: {constraint_dict}")
            elif 'left_of' in constraint_dict:
                pairs = constraint_dict['left_of']
                if len(pairs) == 2:
                    attr1, val1 = pairs[0]
                    attr2, val2 = pairs[1]
                    # Add constraint that val1 is immediately to the left of val2
                    problem.addConstraint(lambda a, b: a + 1 == b, (val1, val2))
                else:
                    print(f"ZebraRandomSolver: Unsupported 'left_of' constraint format: {constraint_dict}")
            else:
                print(f"ZebraRandomSolver: Unknown constraint type: {constraint_dict}")

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

        return houses
