# Zebra Puzzle Solver

A Python-based AI solver for the classic Zebra Puzzle (also known as Einstein's Riddle) using constraint satisfaction with an interactive Pygame-based UI for user engagement. This project explores and benchmarks constraint satisfaction solutions, specifically using backtracking with forward checking, and enables users to interact with the puzzle themselves.

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Game Instructions](#game-instructions)
- [Project Structure](#project-structure)
- [Benchmarking](#benchmarking)

## Project Overview

### Project Members
- **Sarah Burge**
- **CJ Parker**
- **Kyle Prewitt**

### Puzzle Background

The Zebra Puzzle, a famous logic puzzle first published in *Life* magazine in 1962, has been a popular benchmark in constraint satisfaction problems (CSPs). The puzzle has a large number of possible permutations—297,070,617,187,575,000—and 24,883,200,000 valid combinations. The puzzle’s goal is to answer two questions based on fifteen clues:

1. Who owns the zebra?
2. Who drinks water?

The original fifteen clues include conditions about the colors of five houses, nationalities, pets, drinks, and cigarette brands of the residents. 
#### Clues:
- There are five houses.
- The Englishman lives in the red house.
- The Spaniard owns the dog.
- Coffee is drunk in the green house.
- The Ukrainian drinks tea.
- The green house is immediately to the right of the ivory house.
- The Old Gold smoker owns snails.
- Kools are smoked in the yellow house.
- Milk is drunk in the middle house.
- The Norwegian lives in the first house.
- The man who smokes Chesterfields lives in the house next to the man with the fox.
- Kools are smoked in the house next to the house where the horse is kept.
- The Lucky Strike smoker drinks orange juice.
- The Japanese smokes Parliaments.
- The Norwegian lives next to the blue house.

Our project solves this puzzle by implementing a backtracking algorithm with forward checking, and by using constraint satisfaction principles with the Python Constraint library.

### Project Goals

This project allows users to:
- Solve the original and random Zebra Puzzle interactively.
- Solve randomly generated puzzles with dynamically created constraints.
- Benchmark the AI solver's performance between randomly generated and the original puzzle.

Additionally, the project features an AI solver implemented with Python Constraint library and an interactive mini-game with a user-friendly Pygame UI. The AI automatically applies constraints based on clues, uses backtracking with forward checking to increase efficiency, and tracks the time taken to solve each puzzle. Users can test the AI’s capabilities against their own attempts in real-time.

### Key Features

- **Interactive Gameplay**: Visual interface for users to solve the Zebra Puzzle and test their solution accuracy.
- **Original and Randomized Puzzle Options**: Play the traditional Zebra Puzzle or a randomized version with reshuffled attributes and clues.
- **AI Solver with Forward Checking**: Backtracking solver with forward checking to optimize solution speed.
- **Benchmarking Performance**: Track and display the time taken by the solver for different solving methods.

## Installation

### Prerequisites

- Python 3.8+
- [Pygame](https://www.pygame.org/news) (for the graphical user interface)
- [Python Constraint](https://pypi.org/project/python-constraint/) library (for constraint satisfaction)

### Clone the Repository

```bash
git clone https://github.com/yourusername/zebra-puzzle-solver.git
cd zebra-puzzle-solver
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Requirements File (`requirements.txt`)

```
pygame==2.1.0
python-constraint==1.4.0
```

## Usage

To start the game, run the main script `zebraPuzzleGame.py`:

```bash
python zebraPuzzleGame.py
```

## Game Instructions

1. **Choose Puzzle Type**: At the main menu, choose either the Original Puzzle or the Random Puzzle.
2. **Interactive Grid**:
   - **Cycle through Options**: Click on cells to cycle through attribute options (e.g., colors, nationalities).
   - **Finalize Selections**: Press `Enter` to lock in selections.
3. **View Clues**: Press `C` to view clues for the current puzzle.
4. **Use AI Solver**:
   - Press `A` to let the AI solve the puzzle.
   - Solution timing and accuracy will display in the output box.
5. **Check Solution**: Press `S` to check how accurate your solution is against the correct one.
6. **Reset Puzzle**: Press `R` to reset all selections.
7. **Pause/Resume**: Press `Escape` to access the pause menu or resume the game.

## Project Structure

- `zebraPuzzleGame.py`: Main game file, initializes Pygame and manages the game loop, rendering, and user interactions.
- `backtracking.py`: Solver for the original Zebra Puzzle with pre-set constraints.
- `backtrackingRandom.py`: Solver for randomized puzzles with dynamic constraints.
- `requirements.txt`: Lists required libraries for installation.
- `attributes.json`: Stores lists of all possible attributes (colors, nationalities, etc.).
- `clues.json`: Contains clues for the original Zebra Puzzle.
- `og_attributes.json`: Holds the solution for the original Zebra Puzzle, used for accuracy checking.

## Benchmarking

The project also benchmarks solver performance via *Backtracking with Forward Checking* as the heuristic. This is usually within ms or even smaller, due to the library pruning

### Results

Our benchmarking results show that both methods successfully solve the puzzle. The benchmarking tool tracks and displays solver performance for each solving method, allowing comparison of execution times. The random puzzles were difficult to gauge due to constraints being random and structured to avoid duplicate or similar clues, as some generated were faster to solve than others. Generally, our random clues were not too difficult because it would usually result in an insolvable puzzle. Focusing heavily on positional attributes of being next to and in the same house, it increased in solver accuracy as it balanced between too strict and too easy of clues. 







