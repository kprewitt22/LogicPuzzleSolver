# zebraPuzzleGame.py
import pygame
import json
import sys
import random
import time
import copy
from backTracking import ZebraPuzzleSolver  #Deals with original constraints
from backtrackingRandom import ZebraRandomSolver #Deals with random dynamically generated constraints
from enum import Enum
# Initialize Pygame
pygame.init()
# **Seed the random number generator with current time**
random.seed(time.time())
# Global variables for timing
game_start_time = None
solver_time = None
total_time_elapsed = None
# Screen dimensions
WIDTH, HEIGHT = 1000, 700
GRID_MARGIN_TOP = 50
GRID_MARGIN_LEFT = 50
OUTPUT_BOX_HEIGHT = 100
ROWS, COLS = 6, 6
CELL_WIDTH = (WIDTH - 2 * GRID_MARGIN_LEFT) // COLS
CELL_HEIGHT = (HEIGHT - OUTPUT_BOX_HEIGHT - GRID_MARGIN_TOP) // ROWS

# Colors
WHITE = (255, 255, 255)  # Cell color
BLACK = (0, 0, 0)        # Text color
GRAY = (200, 200, 200)   # Button color
DARK_GRAY = (150, 150, 150)  # Button hover color
GRID_COLOR = (0, 0, 0)    # Black grid

# Fonts
FONT_SIZE = 20
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
BUTTON_FONT = pygame.font.SysFont('Arial', 30)
#Ouput message in output box
output_message = ""
message_time = 0  # Timestamp for when the message was last updated
MESSAGE_DISPLAY_DURATION = 5  # Duration in seconds for the message to stay
# Load background image
try:
    background_image = pygame.image.load('./albert.png').convert()
    # Scale the image to fit the screen if necessary
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Unable to load background image: {e}")
    background_image = None  # Proceed without background
# Load attributes
with open('attributes.json', 'r') as file:
    attributes_data = json.load(file)
    attributes = attributes_data['attributes']

# Load clues from clues.json
try:
    with open('clues.json', 'r') as clues_file:
        clues = json.load(clues_file)['clues']
except (FileNotFoundError, json.JSONDecodeError) as e:
    print("Error loading clues.json:", e)
    clues = []
#Create game state
class GameState(Enum):
    MAIN_MENU = 1
    GAMEPLAY = 2
    SUBMENU = 3
    CONTROLS_INFO = 4
    CLUE_MENU = 5
    EXIT = 6
# Define House class
class House:
    def __init__(self, number, color="", nationality="", beverage="", cigarette="", pet=""):
        self.number = number
        self.color = color
        self.nationality = nationality
        self.beverage = beverage
        self.cigarette = cigarette
        self.pet = pet
        # Store indexes for rotating display of options
        self.option_indices = {'color': 0, 'nationality': 0, 'beverage': 0, 'cigarette': 0, 'pet': 0}

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
        # Reset option indices
        self.option_indices = {'color': 0, 'nationality': 0, 'beverage': 0, 'cigarette': 0, 'pet': 0}
#Solution class
class Solution:
    def __init__(self):
        # A list of dictionaries to store the attributes for each house
        self.houses = [{ 'color': None, 'nationality': None, 'beverage': None, 'cigarette': None, 'pet': None } for _ in range(5)]

    def set_attributes(self, index, color, nationality, beverage, cigarette, pet):
        # Store attributes for a specific house at the given index
        self.houses[index] = {
            'color': color,
            'nationality': nationality,
            'beverage': beverage,
            'cigarette': cigarette,
            'pet': pet
        }

    def get_attributes(self, index):
        # Return the attributes for a specific house at the given index
        return self.houses[index]

    def display(self):
        # Print the attributes for all houses
        for i, house in enumerate(self.houses):
            print(f"House {i + 1}: {house}")

# Button class for main menu
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.hover_color = DARK_GRAY
        self.callback = callback

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border

        text_surface = BUTTON_FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    self.callback()
                    return True
        return False
# Initialize houses
houses = [House(str(i + 1)) for i in range(5)]

# Mapping attribute types to their corresponding plural forms in attributes.json
# Since attributes.json now uses singular keys, adjust accordingly
attribute_keys = ['color', 'nationality', 'beverage', 'cigarette', 'pet']

# Track the current selection for cycling
current_selection = None
cycle_mode = False

# Functions to manage house attributes
def clear_all(houses):
    for house in houses:
        house.clear()
#Get randomly assigned attributes for the puzle
def get_random_attr(attributes):
    # Create a new Solution instance
    solution = Solution()
    randomized_attributes = {}
    for attr, values in attributes.items():
        randomized_values = copy.deepcopy(values)
        random.shuffle(randomized_values)
        randomized_attributes[attr] = randomized_values
    #Set solution for randomized attributes to confirm choices
    for i in range(5):
        solution.set_attributes(
            i,
            randomized_attributes['color'][i],
            randomized_attributes['nationality'][i],
            randomized_attributes['beverage'][i],
            randomized_attributes['cigarette'][i],
            randomized_attributes['pet'][i]
        )
    return solution
#Generate Constraint dictionary from solution to puzzle. These will be expressed as pairs for later translation into clues
def generate_constraints_from_solution(solution):
    """
    Generate logical constraints based on a complete solution.

    :param solution: A list of dictionaries representing each house's attributes.
    :return: A list of constraints that describe the solution, each with associated house numbers.
    """
    constraints = []
    added_constraints = set()

    # Define attribute types for reference
    attribute_types = ['color', 'nationality', 'beverage', 'cigarette', 'pet']

    # Generate 'same_house' constraints for all unique attribute pairs in each house
    for house_num, house in enumerate(solution, start=1):
        attr_values = list(house.items())
        for i in range(len(attr_values)):
            for j in range(i + 1, len(attr_values)):
                attr1, val1 = attr_values[i]
                attr2, val2 = attr_values[j]

                # Ensure that attributes are of different types
                if attr1 == attr2:
                    continue  # Skip same attribute types

                pair = tuple(sorted([(attr1, val1), (attr2, val2)]))
                if pair not in added_constraints:
                    constraints.append({
                        'same_house': [pair[0], pair[1]],
                        'houses': [house_num]
                    })
                    added_constraints.add(pair)

    # Generate 'left_of' constraints based on house positions
    for i in range(len(solution) - 1):
        current_house = solution[i]
        next_house = solution[i + 1]
        constraints.append({
            'left_of': [('color', current_house['color']), ('color', next_house['color'])],
            'houses': [i + 1, i + 2]
        })

    # Generate 'next_to' constraints based on attribute relationships
    # For demonstration, link 'cigarette' of one house to 'pet' of the adjacent house
    for i in range(len(solution) - 1):
        current_house = solution[i]
        next_house = solution[i + 1]
        constraints.append({
            'next_to': [('cigarette', current_house['cigarette']), ('pet', next_house['pet'])],
            'houses': [i + 1, i + 2]
        })

    return constraints
#Shuffle constraints for uniqueness
def shuffle_constraints_no_consecutive_same_house(constraints):
    """
    Shuffle constraints ensuring that no two consecutive constraints involve the same house.

    :param constraints: List of constraint dictionaries, each with a 'houses' key listing house numbers involved.
    :return: Shuffled list of constraints adhering to the no-consecutive-same-house rule.
    """
    if not constraints:
        return []

    attempts = 0
    max_attempts = 1000  # Prevent infinite loops

    while attempts < max_attempts:
        random.shuffle(constraints)
        conflict = False

        for i in range(len(constraints) - 1):
            houses_current = set(constraints[i].get('houses', []))
            houses_next = set(constraints[i + 1].get('houses', []))
            if houses_current & houses_next:
                conflict = True
                break  # Found a conflict; reshuffle

        if not conflict:
            return constraints

        attempts += 1

    print("Warning: Could not shuffle constraints without consecutive house references after multiple attempts.")
    return constraints  # Return the last shuffled list even if it has conflicts

#Get orignal attributes assigned to houses
def get_original_attr(houses, og_attributes):
    for i, house in enumerate(houses):
        house.update(og_attributes[i])
#Check the solution of either random or original puzzle
def check_solution(houses, solution):
    """
    Check the current houses against the provided solution and calculate accuracy.
    
    :param houses: The current state of the game houses.
    :param solution: The correct solution to compare against.
    :return: The percentage of correctly assigned attributes.
    """
    print("Debug: Comparing solutions...")
    total_attributes = len(houses) * len(attribute_keys)  # Total attributes across all houses
    correct_attributes = 0
    
    # Iterate over each house and compare attributes
    for house_index, (house, correct_house) in enumerate(zip(houses, solution)):
        print(f"House {house_index + 1}:")
        for attribute in attribute_keys:
            house_value = getattr(house, attribute, None)  # Safely get attribute with default None
            correct_value = correct_house.get(attribute)  # Ensure correct_house is a dict
            if house_value == correct_value:
                correct_attributes += 1
                print(f"  {attribute}: {house_value} (Correct)")
            else:
                print(f"  {attribute}: {house_value} (Incorrect, should be {correct_value})")
    
    accuracy = (correct_attributes / total_attributes) * 100
    print(f"Debug: Total accuracy: {accuracy:.2f}%")
    return accuracy
# Main menu function
def main_menu(screen):
    clock = pygame.time.Clock()
    buttons = []
    choice = None  # To store the user's choice

    button_width, button_height = 200, 50
    button_spacing = 20
    total_height = 3 * button_height + 2 * button_spacing
    start_y = (HEIGHT - total_height) // 2
    center_x = WIDTH // 2

    # Callback functions for buttons
    def start_original():
        nonlocal choice
        choice = 'original'
        nonlocal running_menu
        running_menu = False

    def start_random():
        nonlocal choice
        choice = 'random'
        nonlocal running_menu
        running_menu = False

    def quit_game():
        pygame.quit()
        sys.exit()

    # Create buttons for original, random, or quit
    buttons.append(Button("Original Puzzle", center_x - button_width//2, start_y, button_width, button_height, start_original))
    buttons.append(Button("Random Puzzle", center_x - button_width//2, start_y + button_height + button_spacing, button_width, button_height, start_random))
    buttons.append(Button("Quit", center_x - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height, quit_game))

    running_menu = True
    while running_menu:
        #Bug: Attempt to run background image or white if fails
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(WHITE)  # Fallback to white background if image isn't loaded

        # Render the title screen
        title_text = BUTTON_FONT.render("Zebra Puzzle", True, BLACK)
        title_rect = title_text.get_rect(center=(center_x, start_y - 80))
        screen.blit(title_text, title_rect)
        #Draw buttons via for loop
        for button in buttons:
            button.draw(screen)
        #Set loop for game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                if button.is_clicked(event):
                    break  # If a button was clicked, skip checking others

        pygame.display.flip()
        clock.tick(60)

    return choice

# Submenu function triggered by pressing Escape
def sub_menu(screen):
    clock = pygame.time.Clock()
    buttons = []
    choice = None  # To store the user's choice

    button_width, button_height = 250, 50
    button_spacing = 20
    total_height = 3 * button_height + 2 * button_spacing
    start_y = (HEIGHT - total_height) // 2
    center_x = WIDTH // 2

    # Callback functions for submenu buttons
    def return_to_main():
        nonlocal choice
        choice = 'main_menu'
        nonlocal running_submenu
        running_submenu = False
    #Controls information submenu
    def controls_info():
        nonlocal choice
        choice = 'controls_info'
        nonlocal running_submenu
        running_submenu = False
    #Select to quit
    def quit_game():
        pygame.quit()
        sys.exit()
    #Select to unpause
    def unpause_game():
        nonlocal choice
        choice = 'unpause'
        nonlocal running_submenu
        running_submenu = False
    # Create buttons
    buttons.append(Button("Return to Main Menu", center_x - button_width//2, start_y, button_width, button_height, return_to_main))
    buttons.append(Button("Controls Info", center_x - button_width//2, start_y + button_height + button_spacing, button_width, button_height, controls_info))
    buttons.append(Button("Quit", center_x - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height, quit_game))
    buttons.append(Button("Unpause Game", center_x - button_width//2, start_y + 3*(button_height + button_spacing), button_width, button_height, unpause_game))
    running_submenu = True
    while running_submenu:
        screen.fill(WHITE) #Submenu background

        # Render the submenu title
        title_text = BUTTON_FONT.render("Paused", True, BLACK)
        title_rect = title_text.get_rect(center=(center_x, start_y - 80))
        screen.blit(title_text, title_rect)
        # Render solver times if available
        if solver_time is not None and total_time_elapsed is not None:
            time_text = FONT.render(f"Solver Time: {solver_time:.2f}s", True, BLACK)
            total_time_text = FONT.render(f"Total Time Elapsed: {total_time_elapsed:.2f}s", True, BLACK)
            screen.blit(time_text, (center_x - time_text.get_width() // 2, start_y - 40))
            screen.blit(total_time_text, (center_x - total_time_text.get_width() // 2, start_y - 10))

        for button in buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pressing Escape in submenu returns to main menu
                    choice = 'unpause'
                    running_submenu = False
            for button in buttons:
                if button.is_clicked(event):
                    break  # If a button was clicked, skip checking others

        pygame.display.flip()
        clock.tick(60)

    return choice

# Controls info function
def controls_info_screen(screen):
    clock = pygame.time.Clock()
    running_controls = True

    while running_controls:
        screen.fill(WHITE)

        # Render the controls info title
        title_text = BUTTON_FONT.render("Controls Information", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # Define controls info content for users
        controls = [
            "Mouse Click:",
            "  - Click on a cell to cycle through attribute options.",
            "Enter Key:",
            "  - Press Enter to finalize your selection.",
            "C Key:",
            "  - Press C to view the clues.",
            "A Key:",
            "  - Press A to let the AI solve the puzzle.",
            "R Key:",
            "  - Press R to reset the houses.",
            "Escape Key:",
            "  - Press Escape to open the pause menu."
        ]

        # Render each line of controls
        y_offset = 200
        for line in controls:
            text_surface = FONT.render(line, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
            y_offset += FONT_SIZE + 5

        # Instruction to return
        return_text = FONT.render("Press Escape to return to submenu.", True, BLACK)
        screen.blit(return_text, (WIDTH // 2 - return_text.get_width() // 2, HEIGHT - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_controls = False
                    return 'unpause'

        pygame.display.flip()
        clock.tick(60)

    return 'sub_menu'
def show_clues(screen, clues_to_display):
    """
    Displays a list of clues in a separate Clue Menu.

    :param screen: Pygame screen object.
    :param clues_to_display: List of clue strings to display.
    """
    clock = pygame.time.Clock()
    running_clue_menu = True
    back_button = Button("Back to Game", WIDTH//2 - 100, HEIGHT - 150, 200, 50, lambda: None)  # Callback handled below
    
    # Scroll variables
    scroll_y = 0
    scroll_speed = 20
    max_scroll = max(0, len(clues_to_display) * (FONT_SIZE + 5) - (HEIGHT - 200))
    
    while running_clue_menu:
        screen.fill(WHITE)

        # Render the Clue Menu title
        title_text = BUTTON_FONT.render("Clues", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title_text, title_rect)

        # Render clues with scrolling
        y_offset = 120 - scroll_y
        for clue in clues_to_display:
            wrapped_text = wrap_text(clue, FONT, WIDTH - 100)
            for line in wrapped_text:
                text_surface = FONT.render(line, True, BLACK)
                screen.blit(text_surface, (50, y_offset))
                y_offset += FONT_SIZE + 5
                if y_offset > HEIGHT - 200:
                    break  # Prevent overflow
            if y_offset > HEIGHT - 200:
                break

        # Draw the Back button
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if back_button.is_clicked(event):
                running_clue_menu = False
                return 'unpause'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or pygame.K_c:
                    running_clue_menu = False
                    return 'unpause'
                if event.key == pygame.K_UP:
                    scroll_y = max(scroll_y - scroll_speed, 0)
                if event.key == pygame.K_DOWN:
                    scroll_y = min(scroll_y + scroll_speed, max_scroll)

        pygame.display.flip()
        clock.tick(60)

def wrap_text(text, font, max_width):
    """
    Wraps text to fit within a specified width.

    :param text: The text to wrap.
    :param font: Pygame font object.
    :param max_width: Maximum width in pixels.
    :return: List of wrapped text lines.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    return lines


def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
# Define the role of each attribute type
ATTRIBUTE_ROLES = {
    'color': 'house',
    'nationality': 'person',
    'beverage': 'drink',
    'cigarette': 'smoker',
    'pet': 'pet'
}
#Translate contraints into clues 
def translate_constraints(constraints):
    """
    Translates a list of constraint dictionaries into readable English sentences.

    :param constraints: List of constraint dictionaries.
    :return: List of readable English sentences.
    """
    # Helper functions
    def describe_person(nationality):
        #Returns a descriptive phrase for a person based on nationality.
        return f"The {nationality} person"

    def describe_house(color):
        #Returns a descriptive phrase for a house based on its color.
        return f"the {color.lower()} house"

    def describe_drink(beverage):
        #Returns the beverage in lowercase.
        return f"{beverage.lower()}"

    def describe_smoker(cigarette):
        #Returns a descriptive phrase for a smoker based on the cigarette brand.
        return f"{cigarette} smoker"

    def describe_pet(pet):
        #Returns a descriptive phrase for a pet with the correct article.
        return f"a {pet.lower()}"

    def construct_same_house_sentence(attr1, val1, attr2, val2):
        #Constructs a sentence for 'same_house' constraints based on attribute roles.
        role1 = ATTRIBUTE_ROLES.get(attr1)
        role2 = ATTRIBUTE_ROLES.get(attr2)
        
        if role1 == 'person' and role2 == 'house':
            return f"{describe_person(val1)} lives in {describe_house(val2)}."
        elif role2 == 'person' and role1 == 'house':
            return f"{describe_person(val2)} lives in {describe_house(val1)}."
        elif role1 == 'smoker' and role2 == 'pet':
            return f"The {describe_smoker(val1)} has {describe_pet(val2)}."
        elif role2 == 'smoker' and role1 == 'pet':
            return f"The {describe_smoker(val2)} has {describe_pet(val1)}."
        elif role1 == 'person' and role2 == 'drink':
            return f"{describe_person(val1)} drinks {describe_drink(val2)}."
        elif role2 == 'person' and role1 == 'drink':
            return f"{describe_person(val2)} drinks {describe_drink(val1)}."
        elif role1 == 'smoker' and role2 == 'drink':
            return f"The {describe_smoker(val1)} drinks {describe_drink(val2)}."
        elif role2 == 'smoker' and role1 == 'drink':
            return f"The {describe_smoker(val2)} drinks {describe_drink(val1)}."
        elif role1 == 'drink' and role2 == 'house':
            return f"{describe_drink(val1).capitalize()} is drunk in {describe_house(val2)}."
        elif role2 == 'drink' and role1 == 'house':
            return f"{describe_drink(val2).capitalize()} is drunk in {describe_house(val1)}."
        elif role1 == 'person' and role2 == 'pet':
            return f"{describe_person(val1)} has {describe_pet(val2)}."
        elif role2 == 'person' and role1 == 'pet':
            return f"{describe_person(val2)} has {describe_pet(val1)}."
        elif role1 == 'person' and role2 == 'smoker':
            return f"{describe_person(val1)} is a {describe_smoker(val2)}."
        elif role2 == 'person' and role1 == 'smoker':
            return f"{describe_person(val2)} is a {describe_smoker(val1)}."
        elif role1 == 'pet' and role2 == 'house':
            return f"The owner with {describe_pet(val1)} is in {describe_house(val2)}."
        elif role2 == 'pet' and role1 == 'house':
            return f"The owner with {describe_pet(val2)} is in {describe_house(val1)}."
        elif role1 == 'smoker' and role2 == 'house':
            return f"The {describe_smoker(val1)} is in {describe_house(val2)}."
        elif role2 == 'smoker' and role1 == 'house':
            return f"The {describe_smoker(val2)} is in {describe_house(val1)}."
        elif role1 == 'beverage' and role2 == 'pet':
            return f"The house with {describe_pet(val2)} enjoys {describe_drink(val1)}."
        elif role2 == 'beverage' and role1 == 'pet':
            return f"The house with {describe_pet(val1)} enjoys {describe_drink(val2)}."
        else:
            return f"The {val1.lower()} is in the same house as the {val2.lower()}."

    def construct_left_of_sentence(attr1, val1, attr2, val2):
        """Constructs a sentence for 'left_of' constraints based on attribute roles."""
        role1 = ATTRIBUTE_ROLES.get(attr1)
        role2 = ATTRIBUTE_ROLES.get(attr2)
        if role1 == 'house' and role2 == 'house':
            return f"{describe_house(val1)} is immediately to the left of {describe_house(val2)}."
        else:
            return f"The {val1.lower()} {attr1} is immediately to the left of the {val2.lower()} {attr2}."

    def construct_next_to_sentence(attr1, val1, attr2, val2):
        """Constructs a sentence for 'next_to' constraints based on attribute roles."""
        role1 = ATTRIBUTE_ROLES.get(attr1)
        role2 = ATTRIBUTE_ROLES.get(attr2)
        
        if role1 == 'smoker' and role2 == 'pet':
            return f"The {describe_smoker(val1)} is next to the house with {describe_pet(val2)}."
        elif role2 == 'smoker' and role1 == 'pet':
            return f"The {describe_smoker(val2)} is next to the house with {describe_pet(val1)}."
        elif role1 == 'person' and role2 == 'pet':
            return f"The {val1} person is next to the house with {describe_pet(val2)}."
        elif role2 == 'person' and role1 == 'pet':
            return f"The {val2} person is next to the house with {describe_pet(val1)}."
        else:
            return f"The {val1.lower()} {attr1} is next to the {val2.lower()} {attr2}."

    translated = []
    previous_houses = set()  # Track houses referenced in the previous clue

    for constraint in constraints:
        if 'same_house' in constraint:
            (attr1, val1), (attr2, val2) = constraint['same_house']
            sentence = construct_same_house_sentence(attr1, val1, attr2, val2)
            current_houses = set(constraint.get('houses', []))
        elif 'left_of' in constraint:
            (attr1, val1), (attr2, val2) = constraint['left_of']
            sentence = construct_left_of_sentence(attr1, val1, attr2, val2)
            current_houses = set(constraint.get('houses', []))
        elif 'next_to' in constraint:
            (attr1, val1), (attr2, val2) = constraint['next_to']
            sentence = construct_next_to_sentence(attr1, val1, attr2, val2)
            current_houses = set(constraint.get('houses', []))
        else:
            continue  # Handle other constraint types if any
        
        # Check if current houses overlap with previous houses
        if current_houses & previous_houses:
            # If overlap exists, skip adding this clue to avoid consecutive mentions
            continue
        
        if sentence not in translated:
            translated.append(sentence)
            previous_houses = current_houses  # Update previous houses
        else:
            # If the sentence is already in translated, skip to avoid duplicates
            continue

    return translated




# Draw grid and houses
def draw_grid(screen):
    # Drawing the grid with margins for space around it
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(
                GRID_MARGIN_LEFT + col * CELL_WIDTH, 
                GRID_MARGIN_TOP + row * CELL_HEIGHT, 
                CELL_WIDTH, 
                CELL_HEIGHT
            )
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)
#Draw house headers for grid
def draw_houses(screen, houses):
    # Draw header labels in the top row
    headers = ['House', 'Color', 'Nationality', 'Beverage', 'Cigarette', 'Pet']
    for col, header in enumerate(headers):
        text_surface = FONT.render(header, True, BLACK)
        text_x = GRID_MARGIN_LEFT + col * CELL_WIDTH + (CELL_WIDTH - text_surface.get_width()) // 2
        text_y = GRID_MARGIN_TOP + (CELL_HEIGHT - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    # Draw house number labels in the first column
    for row, house in enumerate(houses):
        text_surface = FONT.render(f"House {house.number}", True, BLACK)
        text_x = GRID_MARGIN_LEFT + (CELL_WIDTH - text_surface.get_width()) // 2
        text_y = GRID_MARGIN_TOP + (row + 1) * CELL_HEIGHT + (CELL_HEIGHT - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    # Populate house attributes in the respective cells
    for row, house in enumerate(houses, start=1):  # Rows start from 1 to leave space for headers
        attributes = [house.color, house.nationality, house.beverage, house.cigarette, house.pet]
        for col, attr in enumerate(attributes, start=1):  # Columns start from 1 for the headers
            text = attr if attr else ""
            text_surface = FONT.render(text, True, BLACK)
            text_x = GRID_MARGIN_LEFT + col * CELL_WIDTH + (CELL_WIDTH - text_surface.get_width()) // 2
            text_y = GRID_MARGIN_TOP + row * CELL_HEIGHT + (CELL_HEIGHT - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
#Update the output box below(think of as print to console)
def update_output_box(screen, message):
    global output_message, message_time
    output_message = message  # Update the global message variable
    message_time = time.time()  # Set the current time as the last update time
#Draw the output box
def draw_output_box(screen):
    global output_message
    current_time = time.time()

    # Check if the duration for the message display has expired
    if current_time - message_time > MESSAGE_DISPLAY_DURATION:
        output_message = ""  # Clear the message after the delay

    # Draw the output box area below the grid
    output_box_rect = pygame.Rect(
        0, HEIGHT - OUTPUT_BOX_HEIGHT, WIDTH, OUTPUT_BOX_HEIGHT
    )
    pygame.draw.rect(screen, WHITE, output_box_rect)  # Clear the output box area
    pygame.draw.rect(screen, BLACK, output_box_rect, 2)  # Draw border

    # Render and display the current message
    text_surface = FONT.render(output_message, True, BLACK)
    screen.blit(text_surface, (10, HEIGHT - OUTPUT_BOX_HEIGHT + 10))

# Handle attribute assignments with rotating options
def handle_click(pos, houses, attributes, screen):
    global current_selection, cycle_mode

    x, y = pos

    # Adjust for grid margin offsets
    if x < GRID_MARGIN_LEFT or y < GRID_MARGIN_TOP:
        return  # Click is outside the grid area

    # Calculate column and row based on the adjusted positions
    col = (x - GRID_MARGIN_LEFT) // CELL_WIDTH
    row = (y - GRID_MARGIN_TOP) // CELL_HEIGHT

    # Ensure we are within grid bounds
    if not (0 <= col < COLS and 1 <= row < ROWS):  # Row 0 is reserved for headers
        return  # Click is outside the valid cell area

    # Adjust the row to ignore the header row (row 0)
    row -= 1

    # Handle cycling attribute values within the clicked cell
    if cycle_mode and current_selection:
        # Only allow cycling within the currently selected cell
        if current_selection[0] == houses[row] and current_selection[1] in attributes:
            house, attr_type, index = current_selection
            next_index = (index + 1) % len(attributes[current_selection[1]])
            current_selection = (house, attr_type, next_index)
            setattr(current_selection[0], attr_type, attributes[current_selection[1]][next_index])
    else:
        # Start cycling in the newly clicked cell if not already in cycle mode
        house = houses[row]
        attribute_types = ['color', 'nationality', 'beverage', 'cigarette', 'pet']
        if 1 <= col < COLS:  # Ensure col corresponds to a valid attribute column
            attr_type = attribute_types[col - 1]  # Adjust col to skip "House" column
            current_selection = (house, attr_type, 0)
            cycle_mode = True
            setattr(house, attr_type, attributes[attr_type][0])

#Finalize choice after clicking through options and prevents duplicate answers
def finalize_selection(screen):
    global current_selection, cycle_mode

    if current_selection:
        house, attr_type, _ = current_selection
        selected_value = getattr(house, attr_type)
        duplicate_house = next((h for h in houses if h is not house and getattr(h, attr_type) == selected_value), None)
        if duplicate_house:
            response = prompt_clear_or_cancel(screen, selected_value)
            if response == "clear":
                setattr(duplicate_house, attr_type, "")
            elif response == "cancel":
                setattr(house, attr_type, "")
        current_selection = None
        cycle_mode = False

def prompt_clear_or_cancel(screen, selected_value):
    prompt_width, prompt_height = 400, 200
    prompt_x = (WIDTH - prompt_width) // 2
    prompt_y = (HEIGHT - prompt_height) // 2
    prompt_rect = pygame.Rect(prompt_x, prompt_y, prompt_width, prompt_height)

    pygame.draw.rect(screen, WHITE, prompt_rect)
    pygame.draw.rect(screen, BLACK, prompt_rect, 2)

    prompt_text = FONT.render(f"'{selected_value}' is already assigned.", True, BLACK)
    screen.blit(prompt_text, (prompt_x + 20, prompt_y + 30))
    clear_text = FONT.render("Press C to Clear", True, BLACK)
    cancel_text = FONT.render("Press X to Cancel", True, BLACK)
    screen.blit(clear_text, (prompt_x + 20, prompt_y + 80))
    screen.blit(cancel_text, (prompt_x + 20, prompt_y + 120))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    return "clear"
                elif event.key == pygame.K_x:
                    return "cancel"
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Draw solution visualization (optional). This function displays the solution given by the backtracking w/forward checking heuristic in the game's puzzle
def visualize_solution(screen, houses, solver):
    def backtrack_visual(house_index=0):
        if house_index == 5:
            return True

        for attribute in solver.attributes:
            for value in solver.attributes[attribute]:
                if solver.is_valid_assignment(house_index, attribute, value):
                    houses[house_index].__dict__[attribute] = value
                    solver.houses[house_index][attribute] = value

                    # Draw updated houses
                    screen.fill(WHITE)
                    draw_grid(screen)
                    draw_houses(screen, houses)
                    pygame.display.flip()
                    pygame.time.delay(200)  # Delay to visualize solving

                    if backtrack_visual(house_index + 1):
                        return True

                    # Undo the assignment if it leads to a dead end
                    houses[house_index].__dict__[attribute] = None
                    solver.houses[house_index][attribute] = None

        return False

    backtrack_visual()
#Solver test for randomly assigned attributes
def run_solver_test(screen, houses, solver):
    """
    Run the Zebra puzzle solver and show the solution for the current attribute setup.
    
    :param screen: Pygame screen object.
    :param houses: List of house objects to assign and display attributes.
    :param solver: ZebraRandomSolver instance for solving.
    """
    # Start the solver with forward checking enabled
    start_time = time.time()
    solution = solver.solve()  # Use the forward-checking backtracking solver
    elapsed_time = time.time() - start_time

    if solution:
        # Update the houses in the game to display the solution
        for i, house_solution in enumerate(solution):
            houses[i].update(house_solution)

        # Display that the solver has completed and the time taken
        update_output_box(screen, f"Solver completed in {elapsed_time:.9f}s.")
    else:
        update_output_box(screen, "No solution found by the solver.")

def main():
    global current_selection, cycle_mode #sets current selection between options
    game_state = GameState.MAIN_MENU  # Initialize game state
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #game screen
    pygame.display.set_caption("Zebra Puzzle")
    clock = pygame.time.Clock()
    running = True #flag for game running
    random_solution = None #store a blank random solution



    while running:
        if game_state == GameState.MAIN_MENU:
            choice = main_menu(screen)
            if choice == 'original':
                use_original = True
                try:
                    with open('og_attributes.json', 'r') as og_file:
                        og_attributes = json.load(og_file)['original_attributes']
                    #get_original_attr(houses, og_attributes)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    update_output_box(screen, "Original attributes not found or invalid.")
                    print("Error loading og_attributes.json:", e)
                game_start_time = time.time()  # Set the start time
                game_state = GameState.GAMEPLAY
            elif choice == 'random':
                use_original = False
                random_solution_instance = get_random_attr(attributes)
                random_solution = random_solution_instance.houses
                generated_constraints = generate_constraints_from_solution(random_solution)
                shuffled_constraints = shuffle_constraints_no_consecutive_same_house(generated_constraints)
                translated_clues = translate_constraints(shuffled_constraints)
                # Print generated constraints for debugging
                print("\nGenerated Constraints:")
                for constraint in generated_constraints:
                    print(constraint)
                update_output_box(screen, "Using randomly assigned attributes.")
                game_start_time = time.time()  # Set the start time
                game_state = GameState.GAMEPLAY
            elif choice == 'quit':
                game_state = GameState.EXIT

        elif game_state == GameState.GAMEPLAY:
            # Blit the background image first
            if background_image:
                screen.blit(background_image, (0, 0))
            else:
                screen.fill(WHITE)  # Fallback to white background if image isn't loaded
            draw_grid(screen)
            draw_houses(screen, houses)
            draw_output_box(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    handle_click(pos, houses, attributes, screen)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        finalize_selection(screen)
                    elif event.key == pygame.K_c and not cycle_mode:
                        # Transition to Clue Menu
                        if use_original:
                            # Load clues from og_attributes or another source
                            # For simplicity, assuming clues are in clues.json
                            translated_clues = [clue['description'] for clue in clues]
                        else:
                            translated_clues = translate_constraints(generated_constraints)
                        game_state = GameState.CLUE_MENU
                    elif event.key == pygame.K_s:
                        accuracy = 0
                        try:
                            with open('og_attributes.json', 'r') as og_file:
                                og_attributes = json.load(og_file)['original_attributes']
                            if use_original:
                                accuracy = check_solution(houses, og_attributes)
                                update_output_box(screen, f"You are {accuracy:.2f}% accurate.")
                                if accuracy == 100:
                                    update_output_box(screen, "Congratulations! You've solved the puzzle correctly!")
                                else:
                                    update_output_box(screen, f"You are {accuracy:.2f}% accurate.")
                            else:
                                accuracy = check_solution(houses, random_solution)
                                if accuracy == 100:
                                    update_output_box(screen, "Congratulations! You've solved the puzzle correctly!")
                                else:
                                    update_output_box(screen, f"You are {accuracy:.2f}% accurate.")
                        except (FileNotFoundError, json.JSONDecodeError):
                            update_output_box(screen, "Original attributes not found or invalid.")
                    elif event.key == pygame.K_a:  # Press 'a' to solve the puzzle
                        print("AI solving puzzle now ...")
                        
                        if use_original:
                            # Solve using the original attributes
                            solver = ZebraPuzzleSolver(attributes, clues, debug=True)
                        else:
                            # Solve using the randomly assigned attributes
                            solver = ZebraRandomSolver(attributes, constraints=generated_constraints)

                        # Run the solver and display the result
                        start_solver = time.time()
                        solution = solver.solve()
                        end_solver = time.time()
                        solver_time = end_solver - start_solver
                        if game_start_time:
                            total_time_elapsed = end_solver - game_start_time
                        else:
                            total_time_elapsed = solver_time  # Fallback if game_start_time is not set
                        if solution:  # Ensure solution is a list or valid iterable
                            update_output_box(screen, f"Solver completed in {solver_time:.9f}s. Total time elapsed: {total_time_elapsed:.9f}s.")
                            for i, house in enumerate(solution):
                                print(f"House {i + 1}: {house}")
                            for i in range(5):
                                houses[i].update(solution[i])
                        else:
                            update_output_box(screen, f"No solution found. Solver time: {solver_time:.9f}s. Total time elapsed: {total_time_elapsed:.9f}s.")

                    elif event.key == pygame.K_r:
                        update_output_box(screen, "Houses reset!")
                        clear_all(houses)
                    elif event.key ==pygame.K_ESCAPE:
                        # Trigger the submenu when Escape is pressed
                        game_state = GameState.SUBMENU
            pygame.display.flip()
            clock.tick(60)
        elif game_state == GameState.SUBMENU:
            submenu_choice = sub_menu(screen)
            if submenu_choice == 'main_menu':
                clear_all(houses)
                game_state = GameState.MAIN_MENU
            elif submenu_choice == 'controls_info':
                game_state = GameState.CONTROLS_INFO
            elif submenu_choice == 'quit':
                game_state = GameState.EXIT
            elif submenu_choice == 'unpause':
                game_state = GameState.GAMEPLAY

        elif game_state == GameState.CONTROLS_INFO:
            submenu_choice = controls_info_screen(screen)
            if submenu_choice == 'submenu':
                game_state = GameState.SUBMENU
            elif submenu_choice == 'unpause':
                game_state = GameState.SUBMENU
        elif game_state == GameState.CLUE_MENU:
            clue_choice = show_clues(screen, translated_clues)
            if clue_choice == 'unpause':
                game_state = GameState.GAMEPLAY
        elif game_state == GameState.EXIT:
            running = False

    pygame.quit()
if __name__ == "__main__":
    main()
