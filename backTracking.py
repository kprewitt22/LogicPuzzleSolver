import time

class ZebraPuzzleSolver:
    def __init__(self, domains, clues):
        self.domains = domains
        self.clues = clues
        self.solution = None

    def solve_with_backtracking(self):
        """Standard backtracking solver."""
        start_time = time.time()
        success = self.backtracking_search()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Backtracking solution {'found' if success else 'not found'} in {elapsed_time:.4f} seconds.")
        return elapsed_time

    def solve_with_forward_checking(self):
        """Backtracking with forward checking solver."""
        start_time = time.time()
        success = self.backtracking_search(forward_check=True)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Forward Checking solution {'found' if success else 'not found'} in {elapsed_time:.4f} seconds.")
        return elapsed_time

    def backtracking_search(self, forward_check=False):
        """Recursive backtracking search function."""
        return self.recursive_backtracking({}, forward_check)

    def recursive_backtracking(self, assignment, forward_check):
        """Backtracking search with optional forward checking."""
        if len(assignment) == 5:
            if self.is_solution(assignment):
                self.solution = assignment
                return True
            return False

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            if self.is_consistent(var, value, assignment):
                assignment[var] = value

                if forward_check and not self.forward_check(var, assignment):
                    del assignment[var]
                    continue

                if self.recursive_backtracking(assignment, forward_check):
                    return True

                del assignment[var]

        return False

    def is_solution(self, assignment):
        """Implement solution check logic based on puzzle constraints."""
        for clue in self.clues:
            if not self.check_clue(clue, assignment):
                return False
        return True

    def check_clue(self, clue, assignment):
        """Check if a single clue is satisfied by the current assignment."""
        desc = clue['description']

        # Process each clue based on its description
        if "Englishman" in desc and "red" in desc:
            if not (assignment.get('nationality_Englishman') == 'red'):
                return False
        if "Spaniard" in desc and "dog" in desc:
            if not (assignment.get('nationality_Spaniard') == 'dog'):
                return False
        if "Ukrainian" in desc and "tea" in desc:
            if not (assignment.get('nationality_Ukrainian') == 'tea'):
                return False
        if "green house" in desc and "ivory house" in desc:
            green_index = assignment.get('color_green')
            ivory_index = assignment.get('color_ivory')
            if green_index is None or ivory_index is None or green_index != ivory_index + 1:
                return False
        if "Norwegian" in desc and "first house" in desc:
            if assignment.get('nationality_Norwegian') != 1:
                return False
        if "Kools" in desc and "yellow house" in desc:
            if not (assignment.get('cigarette_Kools') == 'yellow'):
                return False
        if "milk" in desc and "center house" in desc:
            if assignment.get('beverage_milk') != 3:
                return False
        if "Chesterfields" in desc and "fox" in desc:
            if not self.check_adjacent(assignment, 'cigarette_Chesterfields', 'pet_fox'):
                return False
        if "Kools" in desc and "horse" in desc:
            if not self.check_adjacent(assignment, 'cigarette_Kools', 'pet_horse'):
                return False
        if "Lucky Strike" in desc and "orange juice" in desc:
            if not (assignment.get('cigarette_LuckyStrike') == 'orange juice'):
                return False
        if "Japanese" in desc and "Parliaments" in desc:
            if not (assignment.get('nationality_Japanese') == 'Parliaments'):
                return False
        if "Norwegian" in desc and "blue house" in desc:
            norwegian_index = assignment.get('nationality_Norwegian')
            blue_index = assignment.get('color_blue')
            if blue_index is None or abs(norwegian_index - blue_index) != 1:
                return False

        return True

    def check_adjacent(self, assignment, var1, var2):
        """Check if two variables (houses) are adjacent."""
        index1 = None
        index2 = None

        for i in range(1, 6):  # Assuming house numbers are from 1 to 5
            if assignment.get(f'{var1}_{i}') is not None:
                index1 = i
            if assignment.get(f'{var2}_{i}') is not None:
                index2 = i

        # Check if they are adjacent
        return index1 is not None and index2 is not None and abs(index1 - index2) == 1

    

    def select_unassigned_variable(self, assignment):
        for var in self.domains:
            if var not in assignment:
                return var

    def is_consistent(self, var, value, assignment):
        """Check if assigning value to var is consistent with the assignment."""
        # Ensure that the value does not conflict with existing assignments
        for other_var in assignment:
            if assignment[other_var] == value:
                return False
        return True

    def forward_check(self, var, assignment):
        """Implement forward checking logic."""
    # Remove values from domains that conflict with the current assignment
        for other_var in self.domains:
            if other_var != var and other_var not in assignment:
                if assignment.get(var) in self.domains[other_var]:
                    self.domains[other_var].remove(assignment[var])
                if not self.domains[other_var]:  # If the domain is empty, no solution
                    return False
        return True
