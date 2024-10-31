# zebraPuzzleGame.py
import pygame
import json
import sys
import random
import time
from backTracking import ZebraPuzzleSolver  # Ensure the file name matches

# Initialize Pygame
pygame.init()

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
GRID_COLOR = (0, 0, 0)    # Black grid

# Fonts
FONT_SIZE = 20
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
#Ouput message in output box
output_message = ""
message_time = 0  # Timestamp for when the message was last updated
MESSAGE_DISPLAY_DURATION = 5  # Duration in seconds for the message to stay
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

def get_random_attr(houses, attributes):
    shuffled_attributes = {key: random.sample(values, len(values)) for key, values in attributes.items()}
    for i, house in enumerate(houses):
        house.color = shuffled_attributes['color'][i]
        house.nationality = shuffled_attributes['nationality'][i]
        house.beverage = shuffled_attributes['beverage'][i]
        house.cigarette = shuffled_attributes['cigarette'][i]
        house.pet = shuffled_attributes['pet'][i]

def get_original_attr(houses, og_attributes):
    for i, house in enumerate(houses):
        house.update(og_attributes[i])

def check_solution(houses, og_attributes):
    total_attributes = 5 * 5  # 5 houses with 5 attributes each
    correct_attributes = 0
    for house, og in zip(houses, og_attributes):
        for attribute in ['color', 'nationality', 'beverage', 'cigarette', 'pet']:
            if getattr(house, attribute) == og[attribute]:
                correct_attributes += 1
    return (correct_attributes / total_attributes) * 100

def show_clues(screen):
    screen.fill(WHITE)
    y_offset = 10
    for clue in clues:
        text_surface = FONT.render(f"{clue['id']}. {clue['description']}", True, BLACK)
        screen.blit(text_surface, (10, y_offset))
        y_offset += FONT_SIZE + 5
        if y_offset > HEIGHT - FONT_SIZE:
            y_offset = 10
            pygame.display.flip()
            wait_for_key()
            screen.fill(WHITE)
    pygame.display.flip()
    wait_for_key()

def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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

def update_output_box(screen, message):
    global output_message, message_time
    output_message = message  # Update the global message variable
    message_time = time.time()  # Set the current time as the last update time

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

def main():
    global current_selection, cycle_mode
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zebra Puzzle")
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)
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
                    show_clues(screen)
                elif event.key == pygame.K_s:
                    accuracy = 0
                    try:
                        with open('og_attributes.json', 'r') as og_file:
                            og_attributes = json.load(og_file)['original_attributes']
                        accuracy = check_solution(houses, og_attributes)
                        update_output_box(screen, f"You are {accuracy:.2f}% accurate.")
                        if accuracy == 100:
                            update_output_box(screen, "Congratulations! You've solved the puzzle correctly!")
                        else:
                            update_output_box(screen, f"You are {accuracy:.2f}% accurate.")
                    except (FileNotFoundError, json.JSONDecodeError):
                        update_output_box(screen, "Original attributes not found or invalid.")
                elif event.key == pygame.K_a:  # Press 'a' to solve the puzzle
                    print("AI solving puzzle now ...")
                    # Initialize the solver with debug mode enabled
                    solver = ZebraPuzzleSolver(attributes, clues, debug=True)
                    solution = solver.solve()

                    if solution:
                        update_output_box(screen, "Solution found!")
                        for i, house in enumerate(solution):
                            print(f"House {i + 1}: {house}")
                        # Update the Pygame houses to reflect the solution
                        for i in range(5):
                            houses[i].update(solution[i])
                    else:
                        update_output_box(screen, "No solution found.")
                elif event.key == pygame.K_r:
                    update_output_box(screen, "Houses reset!")
                    clear_all(houses)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
