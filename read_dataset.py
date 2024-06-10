import pickle
import ipdb
import copy
import random

from environment.unity_environment import UnityEnvironment
from environment.utils_environment import get_goal_language, filter_valid_actions
import environment.utils_environment as utils
executable_args = {
            'file_name': "/home/zhaoting/miniconda3/envs/llm_filter_planning/lib/python3.8/site-packages/virtualhome/simulation/unity_simulator/linux_exec/linux_exec.v2.3.0.x86_64",
            'x_display': "1",
            'no_graphics': False
        }


def get_goal(task_spec, agent_goal = 'full'):
    if agent_goal == 'full':
        pred = [x for x, y in task_spec.items() if y > 0 and x.split('_')[0] in ['on', 'inside']]
        # object_grab = [pr.split('_')[1] for pr in pred]
        # predicates_grab = {'holds_{}_1'.format(obj_gr): [1, False, 2] for obj_gr in object_grab}
        res_dict = {goal_k: [goal_c, True, 2] for goal_k, goal_c in task_spec.items()}
        # res_dict.update(predicates_grab)
        # print(res_dict)
        return res_dict
    
# check whethter the init-graph includes some sub-task that has already been satisfied
def is_task_completed(satisfied):
    return not all(value == [] for value in satisfied.values())


# [TO DO]
# NOT VERY easy to do it for the general case
# so, for single num_subtasks, only take one
def generate_subset_tasks(original_item, num_subtasks):
    new_item = copy.deepcopy(original_item)  # Deep copy to avoid modifying the original

    # Adjust the task_goal to contain only a selected number of subtasks
    if 'task_goal' in new_item:
        # Filter out sub-tasks with zero value, as these are not required
        active_tasks = {key: value for key, value in new_item['task_goal'][0].items() if value != 0}

        # split active_tasks such as {'on_plate_232': 2} to {'on_plate_232': 1, {'on_plate_232': 1} } 
        active_tasks = extract_subtasks(active_tasks, num_subtasks)
        
        # # If active_tasks is smaller than the requested subtasks, add necessary tasks with zero values
        # necessary_zero_tasks = {key: value for key, value in new_item['task_goal'][0].items() if value == 0}
        
        # # Choose from active tasks first
        # task_keys = list(active_tasks.keys())
        # if len(task_keys) >= num_subtasks:
        #     selected_keys = random.sample(task_keys, num_subtasks)
        # else:
        #     selected_keys = task_keys
        #     # If not enough active tasks, add from the zero-value tasks
        #     additional_keys_needed = num_subtasks - len(selected_keys)
        #     if additional_keys_needed > 0 and necessary_zero_tasks:
        #         selected_keys += random.sample(list(necessary_zero_tasks.keys()), additional_keys_needed)

        # Construct the new task_goal with the selected keys
        # new_item['task_goal'][0] = {key: new_item['task_goal'][0][key] for key in selected_keys}
        if active_tasks is None:
            return None
        new_item['task_goal'][0] = active_tasks

    return new_item

def extract_subtasks(original_tasks, num_subtasks):
    # Flatten the task dictionary into a list of tasks
    task_list = []
    for task, count in original_tasks.items():
        task_list.extend([task] * count)

    # Ensure not to sample more than the population
    if num_subtasks > len(task_list):
        # Option 1: Return the whole list as a dictionary if more subtasks are requested than available
        return None
    
    # Randomly select the desired number of subtasks
    selected_tasks = random.sample(task_list, num_subtasks)

    # Create a new dictionary to store the extracted subtasks with their counts
    new_task_dict = {}
    for task in selected_tasks:
        if task in new_task_dict:
            new_task_dict[task] += 1
        else:
            new_task_dict[task] = 1

    return new_task_dict


# Replace 'yourfile.pik' with the actual file path
# filename = 'gen_data/dataset/train_env_set_help.pik'
# filename = 'gen_data/dataset/test_env_set_help.pik'

filename = 'gen_data/dataset/new_train_set_2_subtasks.pik'

# Open the file in binary read mode
with open(filename, 'rb') as file:
    # Load the object from the file
    dataset_list = pickle.load(file)

# list_data = [20, 21, 23, 25, 26, 30, 31, 32, 33, 34, 35, 39, 83, 84, 88, 90, 92, 94, 96, 99] # testing
list_data = [6, 9, 17, 27, 32, 44, 57, 66, 71, 78, 82, 91]
for i in list_data:
# for i in range(0, len(dataset_list)):
   
    graph = dataset_list[i]['init_graph'] 
    # print("graph nodes: ", len(graph['nodes']), len(graph['edges']))

    test_data_id = i
    env_id = dataset_list[test_data_id]['env_id']
    task_goal = dataset_list[test_data_id]['task_goal'][0]
    graph = dataset_list[test_data_id]['init_graph']
    print(i, " task name: ", dataset_list[i]['task_name'],  " task_goal: ", dataset_list[i]['task_goal'][0], " env_id: ", dataset_list[i]['env_id'])


# dataset_list contains many dicts
    # each dict contains the following keys: dict_keys(['task_id', 'task_name', 'env_id', 'init_graph', 'task_goal', 'goal_class', 'level', 'init_rooms', 'pred_str'])dict_keys(['task_id', 'task_name', 'env_id', 'init_graph', 'task_goal', 'goal_class', 'level', 'init_rooms', 'pred_str'])


# ipdb.set_trace() # used for debuggingg 
# your_object is now the deserialized object that was stored in the file

'''Process the dataset'''

number_subtask = 6
new_dataset = []
for i in range(0, len(dataset_list)):
   
    graph = dataset_list[i]['init_graph'] 
    # print("graph nodes: ", len(graph['nodes']), len(graph['edges']))

    test_data_id = i
    env_id = dataset_list[test_data_id]['env_id']
    task_goal = dataset_list[test_data_id]['task_goal'][0]
    graph = dataset_list[test_data_id]['init_graph']
    # print("graph: ", graph.)
    # print("init_rooms: ", dataset_list[test_data_id]['init_rooms'])

    task_goal_env = get_goal(task_goal)
    satisfied, unsatisfied  = utils.check_progress(graph, task_goal_env)
    if is_task_completed(satisfied):
        print("--------------------------------------------------------------------------")
        print("satisfied: ", satisfied, " is_task_completed: ", is_task_completed(satisfied))
        print("unsatisfied: ", unsatisfied)

        print(i, " task name: ", dataset_list[i]['task_name'],  " task_goal: ", dataset_list[i]['task_goal'][0], " level: ", dataset_list[i]['level'])
    else:
        new_item = generate_subset_tasks(dataset_list[i], number_subtask)
        if new_item is not None:
            new_dataset.append(new_item)
            print(i, "new_item task name: ", new_item['task_name'],  " task_goal: ", new_item['task_goal'], " level: ", new_item['level'])
        else:
            print(i," None")
    print(i, " task name: ", dataset_list[i]['task_name'],  " task_goal: ", dataset_list[i]['task_goal'][0], " level: ", dataset_list[i]['level'])

# with open(f'gen_data/dataset/new_train_set_{number_subtask}_subtasks.pik', 'wb') as new_file:
#     pickle.dump(new_dataset, new_file)


# dataset decomposition 
# first check whether the dataset's initial graph is consistent with the task_goal (check whether the sub-goals are satisfied)
