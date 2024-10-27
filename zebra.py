import numpy as np
from backTracking import *
import random
import json

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
        house.color = shuffled_attributes['colors'][i]
        house.nationality = shuffled_attributes['nationalities'][i]
        house.beverage = shuffled_attributes['beverages'][i]
        house.cigarette = shuffled_attributes['cigarettes'][i]
        house.pet = shuffled_attributes['pets'][i]
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
def game_loop(houses, attributes, solver):
    print("GAME START")
    clear_all(houses)
    while True:
        house_print(houses)
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
            print(f"\nPlayer's manual progress: {accuracy:.2f}% accurate.")
            print(f"Backtracking time: {time_bt:.4f} seconds.")
            print(f"Forward Checking time: {time_fc:.4f} seconds.\n")
        else:
            try:
                # Split user input and handle multi-word values
                parts = user_input.split()
                if len(parts) < 4 or parts[0].lower() != 'set':
                    print("Invalid input format. Use: set <house_number> <attribute_type> <attribute_value>")
                    continue
                
                command, house_num, attr = parts[0], parts[1], parts[2]
                value = " ".join(parts[3:])  # Join all remaining parts as the value

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
attributes = data['attributes']
og_attributes = data1['original_attributes']
clues = load_clues('clues.json')
# Convert the loaded 'houses' from the JSON file into House objects
houses = [House(house_data['number']) for house_data in data['houses']]
#Access attributes directly
domains = {
    'color': ['red', 'green', 'ivory', 'yellow', 'blue'],
    'nationality': ['Englishman', 'Spaniard', 'Ukrainian', 'Norwegian', 'Japanese'],
    'beverage': ['coffee', 'tea', 'milk', 'orange juice', 'water'],
    'cigarette': ['Old Gold', 'Kools', 'Chesterfields', 'Lucky Strike', 'Parliaments'],
    'pet': ['dog', 'snails', 'fox', 'horse', 'zebra']
}
solver = ZebraPuzzleSolver(domains, clues)
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
game_loop(houses, og_attributes, solver)
