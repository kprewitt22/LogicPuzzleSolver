import json
from backTracking import ZebraPuzzleSolver

def load_clues(file_path):
    """Loads clues from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)['clues']
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: JSON decoding failed for {file_path}.")
        return []

def benchmark_solvers():
    """Benchmarks and compares solver execution times for the Zebra Puzzle."""

    # Define the puzzle's domains (attributes and their possible values)
    domains = {
        'color': ['red', 'green', 'ivory', 'yellow', 'blue'],
        'nationality': ['Englishman', 'Spaniard', 'Ukrainian', 'Norwegian', 'Japanese'],
        'beverage': ['coffee', 'tea', 'milk', 'orange juice', 'water'],
        'cigarette': ['Old Gold', 'Kools', 'Chesterfields', 'Lucky Strike', 'Parliaments'],
        'pet': ['dog', 'snails', 'fox', 'horse', 'zebra']
    }
    
    # Load clues from a JSON file
    clues = load_clues('clues.json')

    # Initialize the Zebra Puzzle Solver with domains and clues
    solver = ZebraPuzzleSolver(domains, clues)

    # Solve using standard backtracking and measure time
    print("\nRunning Backtracking Solver...")
    time_bt = solver.solve_with_backtracking()
    print(f"Backtracking completed in {time_bt:.4f} seconds.\n")

    # Solve using backtracking with forward checking and measure time
    print("Running Forward Checking Solver...")
    time_fc = solver.solve_with_forward_checking()
    print(f"Forward Checking completed in {time_fc:.4f} seconds.\n")

if __name__ == "__main__":
    benchmark_solvers()