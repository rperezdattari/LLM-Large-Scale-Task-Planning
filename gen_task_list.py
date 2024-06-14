import itertools
import random
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
# tasks = [
#     {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
#     {'goal': {0: {'on_book_111': 2}}, 'id': 0},
#     {'goal': {0: {'on_mug_111': 2}}, 'id': 0},
#     {'goal': {0: {'on_cutleryfork_238': 2}}, 'id': 0},
#     {'goal': {0: {'on_wineglass_231': 2}}, 'id': 0},
#     {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
#     {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
#     {'goal': {0: {'inside_pie_305': 1}}, 'id': 0},
#     {'goal': {0: {'inside_creamybuns_305': 1}}, 'id': 0}
# ]

tasks_env_0 = [
    {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
    {'goal': {0: {'on_book_111': 2}}, 'id': 0},
    {'goal': {0: {'on_mug_111': 2}}, 'id': 0},
    {'goal': {0: {'on_cutleryfork_238': 2}}, 'id': 0},
    {'goal': {0: {'on_wineglass_231': 2}}, 'id': 0},
    {'goal': {0: {'on_cutleryfork_111': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'inside_pie_305': 1}}, 'id': 0},
    {'goal': {0: {'inside_creamybuns_305': 1}}, 'id': 0}
]

tasks_env_1 = [
    {'goal': {0: {'on_plate_210': 2}}, 'id': 1},
    {'goal': {0: {'on_mug_199': 1}}, 'id': 1},
    {'goal': {0: {'inside_fryingpan_228': 1}}, 'id': 1},
    {'goal': {0: {'inside_cutleryknife_228': 1}}, 'id': 1},
    {'goal': {0: {'on_dishbowl_199': 1}}, 'id': 1},
    {'goal': {0: {'on_poundcake_86': 1}}, 'id': 1},
    {'goal': {0: {'on_breadslice_86': 2}}, 'id': 1},
    {'goal': {0: {'on_apple_210': 1}}, 'id': 1},
    {'goal': {0: {'on_creamybuns_210': 2}}, 'id': 1},
    {'goal': {0: {'inside_book_83': 2}}, 'id': 1}
]
tasks_env_2 = [
    {'goal': {0: {'turnon_163': 1}}, 'id': 2},
    {'goal': {0: {'inside_book_158': 2}}, 'id': 2},
    {'goal': {0: {'inside_plate_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_cutleryfork_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_cutleryknife_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_milk_162': 2}}, 'id': 2},
    {'goal': {0: {'inside_salmon_162': 1}}, 'id': 2},
    {'goal': {0: {'on_cupcake_215': 1}}, 'id': 2}
]
tasks_env_3 = [
    {'goal': {0: {'inside_plate_104': 1}}, 'id': 3},
    {'goal': {0: {'inside_waterglass_104': 2}}, 'id': 3},
    {'goal': {0: {'inside_wineglass_104': 1}}, 'id': 3},
    {'goal': {0: {'inside_cutleryfork_104': 2}}, 'id': 3},
    {'goal': {0: {'inside_apple_103': 2}}, 'id': 3},
    # {'goal': {0: {'on_book_269': 3}}, 'id': 3},
    {'goal': {0: {'on_crackers_72': 1}}, 'id': 3},
    {'goal': {0: {'on_peach_72': 1}}, 'id': 3}
]
tasks_env_4 = [
    {'goal': {0: {'inside_cupcake_157': 2}}, 'id': 4},
    {'goal': {0: {'inside_pudding_157': 1, 'inside_pie_157': 1}}, 'id': 4},
    {'goal': {0: {'on_cereal_138': 1}}, 'id': 4},
    {'goal': {0: {'on_chocolatesyrup_138': 1}}, 'id': 4},
    {'goal': {0: {'on_mincedmeat_138': 1}}, 'id': 4},
    {'goal': {0: {'inside_mincedmeat_157': 1}}, 'id': 4},
    {'goal': {0: {'on_breadslice_138': 2}}, 'id': 4},
    {'goal': {0: {'inside_mug_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_plate_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_plate_156': 2, 'inside_mug_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_wineglass_156': 2}}, 'id': 4},
    {'goal': {0: {'on_condimentbottle_138': 2}}, 'id': 4}
]

tasks_env_5 = [
    {'goal': {0: {'on_beer_186': 2}}, 'id': 5},
    {'goal': {0: {'on_mug_106': 1}}, 'id': 5},
    {'goal': {0: {'on_plate_106': 2}}, 'id': 5},
    {'goal': {0: {'on_cutleryfork_189': 2}}, 'id': 5},
    {'goal': {0: {'on_cutleryknife_189': 2}}, 'id': 5},
    {'goal': {0: {'on_cutleryknife_189': 2}}, 'id': 5},
    {'goal': {0: {'on_whippedcream_189': 1}}, 'id': 5},
    {'goal': {0: {'on_milk_189': 1}}, 'id': 5},
    {'goal': {0: {'on_carrot_186': 1}}, 'id': 5}
]

all_tasks_env = [
    (0, tasks_env_0),
    (1, tasks_env_1),
    (2, tasks_env_2),
    (3, tasks_env_3),
    (4, tasks_env_4),
    (5, tasks_env_5)
]

num_subtasks = 5

total_task_number = 30
tasks_per_env = total_task_number // len(all_tasks_env)
# new_tasks_total = []
# for env_i in range(0, 5):
#     # Extract all individual subtasks
#     individual_subtasks = extract_individual_subtasks(tasks)

#     # Create new tasks with the specified number of subtasks
#     new_tasks = create_task_combinations(individual_subtasks, num_subtasks)
#     new_tasks_total = new_tasks_total + new_tasks

# # Output the new tasks
# for task in new_tasks_total:
#     print(new_tasks_total)

new_tasks_total = []

for env_id, tasks in all_tasks_env:
    individual_subtasks = extract_individual_subtasks(tasks)
    new_tasks = create_task_combinations(individual_subtasks, num_subtasks)
    # sample tasks_per_env from the new_tasks list
    new_tasks = random.sample(new_tasks, tasks_per_env)

    
    for task in new_tasks:
        task['id'] = env_id
        new_tasks_total.append(task)

# Output the new tasks
for task in new_tasks_total:
    print(task, ",")


