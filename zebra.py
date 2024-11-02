import time
import random
import json
class ZebraPuzzleSolver:
    def __init__(self, attributes, clues, num_houses=5):
        """
        Initialize the Zebra Puzzle Solver.
        
        :param attributes: Dictionary of attribute lists (e.g., colors, nationalities, etc.).
        :param clues: List of clues as constraint functions.
        :param num_houses: Number of houses (default is 5).
        """
        self.attributes = {key: random.sample(values, len(values)) for key, values in attributes.items()}
        self.clues = clues
        self.num_houses = num_houses
        self.houses = [{} for _ in range(self.num_houses)]  # Empty houses to start

    def is_valid_assignment(self, house_index, attr, value):
        """
        Check if assigning `value` to `attr` in `house_index` is valid
        with forward checking based on clues.
        """
        # Ensure value is unique for this attribute across all houses
        for house in self.houses:
            if house.get(attr) == value:
                return False

        # Check constraints using clues
        for clue in self.clues:
            if not clue(self.houses, house_index, attr, value):
                return False
        return True

    def backtracking_solve(self, house_index=0):
        """
        Solve the puzzle using backtracking with forward checking.
        
        :param house_index: Current house index being processed.
        :return: True if a solution is found, False otherwise.
        """
        if house_index == self.num_houses:
            return True  # All houses filled successfully

        # Try assigning each attribute to the current house
        for attr, values in self.attributes.items():
            if attr in self.houses[house_index]:  # Skip if already assigned
                continue

            for value in values:
                if self.is_valid_assignment(house_index, attr, value):
                    # Assign the value and move to the next house
                    self.houses[house_index][attr] = value
                    if self.backtracking_solve(house_index + 1):
                        return True
                    # Backtrack if assignment didn't lead to solution
                    del self.houses[house_index][attr]

        return False  # No valid assignment found

    def solve_with_backtracking(self):
        """
        Solve with backtracking and measure time taken.
        :return: Time taken to solve in seconds.
        """
        start_time = time.time()
        success = self.backtracking_solve()
        end_time = time.time()
        if success:
            print("Puzzle solved with backtracking.")
        else:
            print("No solution found with backtracking.")
        return end_time - start_time

    def solve_with_forward_checking(self):
        """
        Solve with forward checking and measure time taken.
        :return: Time taken to solve in seconds.
        """
        # This function can incorporate additional logic if forward-checking differs from backtracking.
        return self.solve_with_backtracking()
class House:
    def __init__(self, number = "",color="", nationality="", beverage="", cigarette="", pet=""):
        self.number = number
        self.color = color
        self.nationality = nationality
        self.beverage = beverage
        self.cigarette = cigarette
        self.pet = pet
    def update(self, attributes):
        self.color = attributes.get('color', self.color)
        self.nationality = attributes.get('nationality', self.nationality)
        self.beverage = attributes.get('beverage', self.beverage)
        self.cigarette = attributes.get('cigarette', self.cigarette)
        self.pet = attributes.get('pet', self.pet)
    def clear(self):
        self.color = ""
        self.nationality = ""
        self.beverage = ""
        self.cigarette = ""
        self.pet = ""
    def __str__(self):
        return (f"House {self.number}:\n"
                f"  Color: {self.color}\n"
                f"  Nationality: {self.nationality}\n"
                f"  Beverage: {self.beverage}\n"
                f"  Cigarette: {self.cigarette}\n"
                f"  Pet: {self.pet}\n")
#Uses clear method to clear all attributes from objects in list
def clear_all(houses):
    """ Clears all attributes of all houses. """
    for house in houses:
        house.clear() 
def house_print(houses):
    #In order to print houses iterate with for loop
    for house in houses:
        print(house)       
#Function to randomly assign attributes to house
def get_random_attr(houses, attributes):
    # Shuffle attributes to ensure randomness and uniqueness
    shuffled_attributes = {
        key: random.sample(values, len(values)) for key, values in attributes.items()
    }
    for i, house in enumerate(houses):
        house.color = shuffled_attributes['color'][i]
        house.nationality = shuffled_attributes['nationality'][i]
        house.beverage = shuffled_attributes['beverage'][i]
        house.cigarette = shuffled_attributes['cigarette'][i]
        house.pet = shuffled_attributes['pet'][i]
def get_original_attr(houses, og_attributes):
    #Assigns original attributes from zebra puzzle for testing
    for i, house in enumerate(houses):
        house.update(og_attributes[i])
def load_clues(clues):
    try:
        with open(clues, 'r') as file:
            return json.load(file)['clues']
    except FileNotFoundError:
        print(f"Error: {clues} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: JSON decoding failed for {clues}.")
        return []
    
def show_clues():
    """Displays all clues in a readable format."""
    print("Zebra Puzzle Clues:")
    for clue in clues:
        print(f"{clue['id']}. {clue['description']}")

def user_assign_attribute(houses, house_number, attribute_type, attribute_value):
    '''Assigns or reassigns an attribute to the specified house, clearing the attribute from any previous assignment.'''
    house = next((h for h in houses if h.number == house_number), None)
    if not house:
        print(f"House {house_number} does not exist.")
        return

    # Clear the attribute value from any other house that has it
    for h in houses:
        if getattr(h, attribute_type) == attribute_value:
            setattr(h, attribute_type, "")
            print(f"Cleared {attribute_type} '{attribute_value}' from House {h.number}.")

    # Assign or reassign the attribute
    setattr(house, attribute_type, attribute_value)
    print(f"Assigned {attribute_type} '{attribute_value}' to House {house_number}.")
    return

    # Assign the attribute
    setattr(house, attribute_type, attribute_value)
    print(f"Assigned {attribute_type} '{attribute_value}' to House {house_number}.")
def check_solution(houses, og_attributes):
    """Calculates and returns the percentage of correct attribute assignments."""
    total_attributes = 5 * 5  # 5 houses with 5 attributes each
    correct_attributes = 0

    for house, og in zip(houses, og_attributes):
        for attribute in ['color', 'nationality', 'beverage', 'cigarette', 'pet']:
            if getattr(house, attribute) == og[attribute]:
                correct_attributes += 1

    accuracy = (correct_attributes / total_attributes) * 100
    return accuracy
def game_loop(houses, attributes, og_attributes, solver):
    print("GAME START")
    clear_all(houses)  # Start with cleared houses
    get_random_attr(houses, attributes)  # Randomly assign initial values
    house_print(houses)  # Show initial random assignments
    
    while True:
        user_input = input("Enter 'clues' to view clues, 'check' to validate your solution, 'compare' to see solver times, or 'quit' to exit: ").strip()

        if user_input.lower() == 'quit':
            print("Exiting the game.")
            break
        elif user_input.lower() == 'clues':
            show_clues(load_clues('clues.json'))
        elif user_input.lower() == 'check':
            accuracy = check_solution(houses, og_attributes)
            if accuracy == 100:
                print("Congratulations! You've solved the puzzle correctly!")
                break
            else:
                print(f"Your solution is {accuracy:.2f}% accurate. Keep trying!")
        elif user_input.lower() == 'compare':
            print("\nSolving puzzle with different methods...")
            time_bt = solver.solve_with_backtracking()
            time_fc = solver.solve_with_forward_checking()
            accuracy = check_solution(houses, og_attributes)
            print(f"\nPlayer's manual progress: {accuracy:.2f}% accurate.")
            print(f"Backtracking time: {time_bt:.4f} seconds.")
            print(f"Forward Checking time: {time_fc:.4f} seconds.\n")
        else:
            try:
                parts = user_input.split()
                if len(parts) < 4 or parts[0].lower() != 'set':
                    print("Invalid input format. Use: set <house_number> <attribute_type> <attribute_value>")
                    continue

                command, house_num, attr = parts[0], parts[1], parts[2]
                value = " ".join(parts[3:])
                if command.lower() == 'set':
                    user_assign_attribute(houses, house_num, attr.lower(), value)
                else:
                    print("Unknown command. Use 'set' to assign attributes.")
            except ValueError:
                print("Invalid input format. Use: set <house_number> <attribute_type> <attribute_value>")
#Read in JSON file
with open('attributes.json', 'r') as file:
    data = json.load(file)
with open('og_attributes.json', 'r') as og_file:
    data1 = json.load(og_file)

#Debug print    
##print(data)
##print(data1)
#Set objects
#attributes = data['attributes']
og_attributes = data1['original_attributes']
clues = load_clues('clues.json')
##Initialize house numbers
houses = [House(str(i + 1)) for i in range(5)]
#Access attributes directly
attributes = {
    'color': ['red', 'green', 'ivory', 'yellow', 'blue'],
    'nationality': ['Englishman', 'Spaniard', 'Ukrainian', 'Norwegian', 'Japanese'],
    'beverage': ['coffee', 'tea', 'milk', 'orange juice', 'water'],
    'cigarette': ['Old Gold', 'Kools', 'Chesterfields', 'Lucky Strike', 'Parliaments'],
    'pet': ['dog', 'snails', 'fox', 'horse', 'zebra']
}
solver = ZebraPuzzleSolver(attributes, clues)
get_random_attr(houses, attributes)

print("Random Puzzle")
#Call house print function
house_print(houses)
#Clear with clear_all function
clear_all(houses)

#Update the original attributes to houses
get_original_attr(houses, og_attributes)
print("Original Puzzle")
# Print the houses with the original attributes
house_print(houses)
##Initialize house numbers
houses = [House(str(i + 1)) for i in range(5)]
clear_all(houses)
house_print(houses)
game_loop(houses, attributes, og_attributes, solver)
