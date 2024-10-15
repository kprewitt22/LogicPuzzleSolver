import numpy as np
##from backTracking import *
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
def get_random_attr(house, attributes):
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
def get_original_attr(house, og_attributes):
    #Assigns original attributes from zebra puzzle for testing
    for i, house in enumerate(houses):
        house.update(og_attributes[i])
#Read in JSON file
with open('attributes.json', 'r') as file:
    data = json.load(file)
with open('og_attributes.json', 'r') as og_file:
    data1 = json.load(og_file)

#Debug print    
print(data)
print(data1)
#Set objects
attributes = data['attributes']
og_attributes = data1['original_attributes']
# Convert the loaded 'houses' from the JSON file into House objects
houses = [House(house_data['number']) for house_data in data['houses']]
#Access attributes directly
print("Nationalities: ", attributes['nationalities'])
get_random_attr(houses, attributes)


#Call house print function
house_print(houses)
#Clear with clear_all function
clear_all(houses)

#Update the original attributes to houses
get_original_attr(houses, og_attributes)

# Print the houses with the original attributes
house_print(houses)