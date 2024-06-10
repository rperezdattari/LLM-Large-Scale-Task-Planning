import itertools

def extract_individual_subtasks(tasks):
    subtasks = []
    for task in tasks:
        for subtask, count in task['goal'][0].items():
            subtasks.extend([(subtask, 1)] * count)
    return subtasks

def create_task_combinations(subtasks, num_subtasks):
    combinations = list(itertools.combinations(subtasks, num_subtasks))
    unique_combinations = set()

    for combination in combinations:
        new_goal = {}
        for subtask, count in combination:
            if subtask in new_goal:
                new_goal[subtask] += count
            else:
                new_goal[subtask] = count
        # Convert the goal dictionary to a tuple of sorted items to ensure uniqueness
        unique_combinations.add(tuple(sorted(new_goal.items())))

    # Convert back to the original dictionary format
    new_tasks = [{'goal': {0: dict(goal)}, 'id': 0} for goal in unique_combinations]
    return new_tasks

# Example usage:
tasks = [
    {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
    {'goal': {0: {'on_book_111': 2}}, 'id': 0},
    {'goal': {0: {'on_mug_111': 2}}, 'id': 0},
    {'goal': {0: {'on_cutleryfork_238': 2}}, 'id': 0},
    {'goal': {0: {'on_wineglass_231': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'inside_pie_305': 1}}, 'id': 0},
    {'goal': {0: {'inside_creamybuns_305': 1}}, 'id': 0}
]

num_subtasks = 5

# Extract all individual subtasks
individual_subtasks = extract_individual_subtasks(tasks)

# Create new tasks with the specified number of subtasks
new_tasks = create_task_combinations(individual_subtasks, num_subtasks)

# Output the new tasks
for task in new_tasks:
    print(task)
