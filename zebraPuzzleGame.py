import pygame
import json
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 6, 6
CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (200, 200, 200)

# Fonts
FONT_SIZE = 20
FONT = pygame.font.SysFont('Arial', FONT_SIZE)

# Load attributes
with open('attributes.json', 'r') as file:
    attributes = json.load(file)['attributes']
with open('og_attributes.json', 'r') as og_file:
    og_attributes = json.load(og_file)['original_attributes']

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

# Correct mapping for each attribute type to the plural form used in the attributes dictionary
attribute_plural_keys = {
    'color': 'colors',
    'nationality': 'nationalities',
    'beverage': 'beverages',
    'cigarette': 'cigarettes',
    'pet': 'pets'
}

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
        house.color = shuffled_attributes['colors'][i]
        house.nationality = shuffled_attributes['nationalities'][i]
        house.beverage = shuffled_attributes['beverages'][i]
        house.cigarette = shuffled_attributes['cigarettes'][i]
        house.pet = shuffled_attributes['pets'][i]

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
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_WIDTH, row * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def draw_houses(screen, houses):
    # Header label for the top-left cell
    text_surface = FONT.render("House", True, BLACK)
    screen.blit(text_surface, (5, 5))  # Place "House" label in the top-left cell

    # Header labels for the first row (attribute names)
    headers = ['Color', 'Nationality', 'Beverage', 'Cigarette', 'Pet']
    for col, header in enumerate(headers, start=1):
        text_surface = FONT.render(header, True, BLACK)
        screen.blit(text_surface, (col * CELL_WIDTH + 5, 5))  # Top row headers

    # House number labels in the first column, starting from the second row
    for row, house in enumerate(houses, start=1):
        text_surface = FONT.render(f"House {house.number}", True, BLACK)
        screen.blit(text_surface, (5, row * CELL_HEIGHT + 5))  # Left column headers
    
    # Populate house attributes in the respective cells
    for row, house in enumerate(houses, start=1):  # Rows start from 1 to leave space for headers
        attributes = [house.color, house.nationality, house.beverage, house.cigarette, house.pet]
        for col, attr in enumerate(attributes, start=1):  # Columns start from 1 for the headers
            text = attr if attr else ""
            text_surface = FONT.render(text, True, BLACK)
            screen.blit(text_surface, (col * CELL_WIDTH + 5, row * CELL_HEIGHT + 5))

# Handle attribute assignments with rotating options
def handle_click(pos, houses, attributes, screen):
    global current_selection, cycle_mode

    x, y = pos
    col = x // CELL_WIDTH
    row = y // CELL_HEIGHT

    # Ensure we are within the bounds of attribute cells (not header or label cells)
    if cycle_mode:
        # Only allow clicks within the currently selected cell
        if current_selection and (houses.index(current_selection[0]) + 1 == row) and (attribute_plural_keys[current_selection[1]] == list(attribute_plural_keys.values())[col - 1]):
            _, attr_type, index = current_selection
            next_index = (index + 1) % len(attributes[attribute_plural_keys[attr_type]])
            current_selection = (current_selection[0], attr_type, next_index)
            setattr(current_selection[0], attr_type, attributes[attribute_plural_keys[attr_type]][next_index])
    elif 1 <= col < COLS and 1 <= row < ROWS:
        # Start cycling in the newly clicked cell if not already in cycle mode
        house = houses[row - 1]
        attribute_types = ['color', 'nationality', 'beverage', 'cigarette', 'pet']
        attr_type = attribute_types[col - 1]
        current_selection = (house, attr_type, 0)
        cycle_mode = True
        setattr(house, attr_type, attributes[attribute_plural_keys[attr_type]][0])

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
                    accuracy = check_solution(houses, og_attributes)
                    print(f"Your solution is {accuracy:.2f}% accurate.")
                    if accuracy == 100:
                        print("Congratulations! You've solved the puzzle correctly!")
                elif event.key == pygame.K_r:
                    clear_all(houses)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
