import itertools
import json
import random
def is_valid(house):
    # Example constraints (you can add more based on the Zebra puzzle)
    
    for house in houses:
        # Example: The Englishman lives in the red house
        if house['nationality'] == 'Englishman' and house['color'] != 'red':
            return False
        if house['color'] == 'red' and house['nationality'] != 'Englishman':
            return False

        # The Spaniard owns the dog
        if house['nationality'] == 'Spaniard' and house['pet'] != 'dog':
            return False
        if house['pet'] == 'dog' and house['nationality'] != 'Spaniard':
            return False

        # The Norwegian lives in the first house
        if house['number'] == 1 and house['nationality'] != 'Norwegian':
            return False
        if house['nationality'] == 'Norwegian' and house['number'] != 1:
            return False

        # Milk is drunk in the middle house
        if house['number'] == 3 and house['beverage'] != 'milk':
            return False
        if house['beverage'] == 'milk' and house['number'] != 3:
            return False

    return True

def backtracking(houses, attributes, index):
    
    if index == len(houses):
        if is_valid(houses):
            return houses
        else:
            return None

    current_house = houses[index]
    
    # Try all possible combinations of attributes for this house
    for color in attributes['colors']:
        current_house['color'] = color
        for nationality in attributes['nationalities']:
            current_house['nationality'] = nationality
            for beverage in attributes['beverages']:
                current_house['beverage'] = beverage
                for cigarette in attributes['cigarettes']:
                    current_house['cigarette'] = cigarette
                    for pet in attributes['pets']:
                        current_house['pet'] = pet
                        
                        # Recursively assign attributes to the next house
                        result = backtracking(houses, attributes, index + 1)
                        if result:
                            return result
                        
                        # Reset attributes for backtracking
                        current_house['color'] = None
                        current_house['nationality'] = None
                        current_house['beverage'] = None
                        current_house['cigarette'] = None
                        current_house['pet'] = None

    return None
# Read in JSON file
with open('attributes.json', 'r') as file:
    data = json.load(file)

# Set objects
houses = data['houses']
attributes = data['attributes']

# Initialize houses with empty attributes
for house in houses:
    house.update({
        'color': None,
        'nationality': None,
        'beverage': None,
        'cigarette': None,
        'pet': None
    })

# Solve using backtracking
solution = backtracking(houses, attributes, 0)

# Print the solution if found
if solution:
    for house in solution:
        print(f"House {house['number']}:")
        print(f"  Color: {house['color']}")
        print(f"  Nationality: {house['nationality']}")
        print(f"  Beverage: {house['beverage']}")
        print(f"  Cigarette: {house['cigarette']}")
        print(f"  Pet: {house['pet']}")
        print()
else:
    print("No solution found.")