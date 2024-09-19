import itertools
import random
import time
from datetime import datetime
#Seed random with time
random.seed(datetime.now().timestamp())
#God Class with atrributes name and behavior. Answer is dependent on God's behavior. Random will choose between true and false. Each behavior will be randomized, while gods will stay in sequential order. 
class God:

    def __init__(self, name, behavior):
        self.name = name
        self.behavior = behavior
    
    def answer(self, question):
        if self.behavior == 'true':
            return question == True
        elif self.behavior == 'false':
            return question == False
        elif self.behavior == 'random':
            return random.choice([True, False])

#First we must establish lists of gods behaviors, words, and names
names = ['A','B','C']
behaviors = ['true', 'false', 'random']
godWords = ['ja', 'da']
#initialize the gods with no behaviors
gods = [God(name, None) for name in names]
# Assign random god attributes
def assignGods(gods, behaviors):
    random.shuffle(behaviors)
    for god, behavior in zip(gods, behaviors):
        god.behavior = behavior
#Randomize meaning of 'ja' and 'da'
def randomMeaning(godWords):
    #List of possible meanings
    meanings = ['true', 'false']
    #Shuffle list
    random.shuffle(meanings)
    #Return a dictionary of 'ja' and 'da' 's meanings
    return dict(zip(godWords, meanings))
'''
When generating the cases, it is important to consider the possible combinations of behaviors and god word's english meanings. There are 2! meanings to 'ja' and 'da' and 6! combinations of True, False, and Random for the three gods.
Making for a total of 12 unique cases... or 3!*2! = 12. 
'''
def generate_cases(gods, godWords):
    cases = []
    
    # Generate all permutations of behaviors
    behavior_permutations = list(itertools.permutations(behaviors))
    
    # Generate all permutations of meanings
    meaning_permutations = list(itertools.permutations(['true', 'false']))
    
    for behavior_perm in behavior_permutations:
        for meaning_perm in meaning_permutations:
            # Create a case
            case = {
                'behaviors': dict(zip(names, behavior_perm)),
                'meanings': dict(zip(godWords, meaning_perm)),
            }
            cases.append(case)
    
    return cases
# Helper function to ask a question from God object
def ask_question(god, question, meanings):
    answer = god.answer(question)
    return 'ja' if answer == (meanings['ja'] == 'true') else 'da'
#Constraint satisfaction
def is_valid_case(case):
    behaviors = case['behaviors']
    meanings = case['meanings']
    
    gods = {name: God(name, behavior) for name, behavior in behaviors.items()}

    # Question 1: Ask God B, "If I asked you 'Is A Random?', would you say ja?"
    q1_answer = ask_question(gods['B'], gods['A'].behavior == 'random', meanings)
    print(f"Q1: Asked God B if A is Random; Answer: {q1_answer}")
    
    # Determine which god is not Random based on the answer to Question 1
    if q1_answer == 'ja':
        non_random_god = gods['C']
    else:
        non_random_god = gods['A']
    
    print(f"Determined non-random god: {non_random_god.name}")

    # Question 2: Ask the non-random god "If I asked you 'Are you False?', would you say ja?"
    q2_answer = ask_question(non_random_god, non_random_god.behavior == 'false', meanings)
    print(f"Q2: Asked God {non_random_god.name} if they are False; Answer: {q2_answer}")

    # Determine the truthfulness of the non-random god
    if q2_answer == 'ja':
        non_random_god_truth = 'false'
    else:
        non_random_god_truth = 'true'

    # Set the non-random god's behavior
    non_random_god.behavior = non_random_god_truth
    print(f"Updated non-random god {non_random_god.name} to be {non_random_god.behavior}")

    # Question 3: Ask the same non-random god "If I asked you 'Is B Random?', would you say ja?"
    q3_answer = ask_question(non_random_god, gods['B'].behavior == 'random', meanings)
    print(f"Q3: Asked God {non_random_god.name} if B is Random; Answer: {q3_answer}")

    # Determine if B is Random or not
    if q3_answer == 'ja':
        gods['B'].behavior = 'random'
        remaining_god = gods['A'] if non_random_god == gods['C'] else gods['C']
    else:
        remaining_god = gods['A'] if gods['B'] == gods['C'] else gods['C']

    # Set the remaining god's behavior by elimination
    remaining_god.behavior = 'false' if non_random_god.behavior == 'true' else 'true'

    # Print the answer for debugging
    print(f"God A: {gods['A'].behavior}, God B: {gods['B'].behavior}, God C: {gods['C'].behavior}")

    # Confirm if we correctly identified True, False, and Random gods
    identified_behaviors = {god.name: god.behavior for god in gods.values()}
    return identified_behaviors == behaviors


def dfs(cases, index=0):
    if index >= len(cases):
        return None

    case = cases[index]

    print(f"\nEvaluating Case {index + 1}:")
    print(f"Behaviors: {case['behaviors']}")
    print(f"Meanings: {case['meanings']}")
    print("-------------------------------------------------")

    if is_valid_case(case):
        print("\nValid solution found for Case:")
        print(f"Behaviors: {case['behaviors']}")
        print(f"Meanings: {case['meanings']}\n")
        return case

    print(f"End of Case {index + 1} Evaluation. Moving to the next case.\n")
    return dfs(cases, index + 1)

#Call functions
assignGods(gods, behaviors)
godWords = randomMeaning(godWords)
# Run the generator to produce the case table
generate_cases(gods, godWords) 
# Run the generator to produce the case table
cases = generate_cases(gods, godWords)
#Set timer 
start_time = time.time()

#Solution from backtracking
solution = dfs(cases)
#End timer
end_time = time.time()
#calculate elapsed time for solution and print
elapsed_time = end_time-start_time
print(f"Took a total of {elapsed_time:.4f} seconds")
#!!!Debugging section!!!
# Print the assigned behaviors and god word meanings for debugging
print("God Assignments: \n")
for god in gods:
    print(f"{god.name}: {god.behavior}")
print("God words meanings:")
for word, meaning in godWords.items():
    print(f"{word}: {meaning}")
# Print the generated cases with numbers
print("Generated cases:")
for i, case in enumerate(cases, start=1):
    print(f"Case {i}:")
    print(f"Behaviors: {case['behaviors']}")
    print(f"Meanings: {case['meanings']}")
    print()

# Print the solution or an error message if not
if solution:
    print("Solution found:")
    print(f"Behaviors: {solution['behaviors']}")
    print(f"Meanings: {solution['meanings']}")
else:
    print("No valid solution found.")