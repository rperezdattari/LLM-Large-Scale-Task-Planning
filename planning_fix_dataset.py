from environment.unity_environment import UnityEnvironment
from environment.utils_environment import get_goal_language, filter_valid_actions, parse_language_from_goal_script_output_object
from utils import get_total_states
from llm_policy import LLMPolicy
from language_filter import LanguageFilter
import time
import argparse
import pickle
import json
from mcts.mcts import MCTSAgent
# from experiments_info.tasks import tasks
import os
from experiments_info.experiments_parameters import experiments

from test_mcts_agents import MCTS_agent

from utils import find_edges_from, find_edges_to


import ipdb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='full', type=str)

    # MCTC
    parser.add_argument('--exploration_constant', default=0.5, type=int)
    parser.add_argument('--bonus_constant', default=1, type=int)
    parser.add_argument('--max_depth', default=199, type=int)
    parser.add_argument('--round', default=0, type=int)
    parser.add_argument('--simulation_per_act', default=2, type=int)
    parser.add_argument('--discount_factor', default=0.99, type=float)
    parser.add_argument('--simulation_num', default=600, type=int)
    parser.add_argument('--uct_type', default='PUCT', type=str)
    return parser.parse_args()


def get_filtered_objects(graph, goal_language, LLM_model):
    # file_name = 'results/filtered_objects/' + goal_language.replace(' ', '_') + '_' + LLM_model + '.pk'
    file_name = 'results_exp/filtered_objects/' + goal_language.replace(' ', '_') + '_' + LLM_model + '.pk'
    # Check if file exists
    if os.path.isfile(file_name):
        # Load if exists
        with open(file_name, 'rb') as file:
            loaded_dict = pickle.load(file)
        selected_objects_id = loaded_dict['selected objects id']
        selected_objects_names = loaded_dict['selected objects names']
        failure_count = None
        print('Filtered objects file existed and loaded!')
    else:
        # Filter objects and save them
        language_filter = LanguageFilter(graph, goal_language, LLM_model)
        selected_objects_id, selected_objects_names, failure_count = language_filter.filter_graph()  # get ids objects used for planning
        save_dict = {'selected objects id': selected_objects_id,
                     'selected objects names': selected_objects_names}
        try:
            with open(file_name, 'wb') as file:  # save filtered objects
                pickle.dump(save_dict, file)
            print('Objects filtered and saved!')
        except OSError as e:
            if e.errno == 36:
                print(f"Error: File name too long: '{file_name}'")
                # Handle the long file name error (e.g., log it, truncate it, etc.)
            else:
                raise  # Re-raise the exception if it's not the specific OSError we expect
    return selected_objects_id, selected_objects_names, failure_count



def parse_language_from_goal_script(goal_script, goal_num, init_graph, template=0):
    goal_script_split = goal_script.split('_')

    if 'closed' in goal_script.lower():
        obj = goal_script_split[1]
        tar_node = [node for node in init_graph['nodes'] if node['id'] == int(obj)]

        assert len(tar_node) == 1

        if template == 1:
            goal_language = 'could you please close the %s' % (tar_node[0]['class_name'])
        elif template == 2:
            goal_language = 'please close the %s' % (tar_node[0]['class_name'])
        else:
            goal_language = 'close %s' % (tar_node[0]['class_name'])

    elif 'turnon' in goal_script.lower():
        obj = goal_script_split[1]
        tar_node = [node for node in init_graph['nodes'] if node['id'] == int(obj)]
        assert len(tar_node) == 1

        if template == 1:
            goal_language = 'could you please turn on the %s' % (tar_node[0]['class_name'])
        elif template == 2:
            goal_language = 'next turn on the %s' % (tar_node[0]['class_name'])
        else:
            goal_language = 'turn on %s' % (tar_node[0]['class_name'])

    elif 'on_' in goal_script.lower() or 'inside_' in goal_script.lower():
        # print(goal_script)
        rel = goal_script_split[0]
        obj = goal_script_split[1]
        tar = goal_script_split[2]
        tar_node = [node for node in init_graph['nodes'] if node['id'] == int(tar)]
        assert len(tar_node) == 1

        if template == 1:
            goal_language = 'could you please place %d %s %s the %s' % (
            goal_num, obj, rel, tar_node[0]['class_name'])
        elif template == 2:
            goal_language = 'get %d %s and put it %s the %s' % (goal_num, obj, rel, tar_node[0]['class_name'])
        else:
            goal_language = 'put %d %s %s the %s' % (goal_num, obj, rel, tar_node[0]['class_name'])
    else:
        ipdb.set_trace()
    goal_language = goal_language.lower()
    return goal_language
    

if __name__ == "__main__":
    # Iterate through every experiment


   
    for experiment in experiments:
         # Initialize the log dictionary
        log_data = {
            "experiment_results": []
        }


        # Get experiment parameters
        policy_type = experiment['policy type']
        policy_execution = experiment['policy execution']
        LLM_model = experiment['LLM model']
        filter_objects = experiment['filter objects']
        dataset_type = experiment['Dataset']
        
        if dataset_type == '1task':
            from experiments_info.tasks_dataset_1task import tasks
        elif dataset_type == '2task':
            from experiments_info.tasks_dataset_2task import tasks
        elif dataset_type == '3task':
            from experiments_info.tasks_dataset_3task import tasks
        elif dataset_type == '4task':
            from experiments_info.tasks_dataset_4task import tasks
        elif dataset_type == '5task':
            from experiments_info.tasks_dataset_5task import tasks
        else:
            tasks = None

        args = parse_args()

        # Following lines currently not used
        file_path = f'../llm-mcts/vh/dataset/env_task_set_500_{args.mode}.pik'  
        # env_task_set = pickle.load(open(file_path, 'rb'))
        executable_args = {
            'file_name': "/home/zhaoting/miniconda3/envs/llm_filter_planning/lib/python3.8/site-packages/virtualhome/simulation/unity_simulator/linux_exec/linux_exec.v2.3.0.x86_64",
            'x_display': "1",
            'no_graphics': False
        }
        
        results = []
        succ, total = 0, 0

        # Iterate through every evaluation task
        for task in tasks:
            # Get task goal
            task_goal = task['goal'][0]
            env_id = task['id']
            print("---------------------------------------------")
            print("task goal: ", task_goal, "env id: ", env_id)

            from utils import find_nodes

            # Init virtualhome env
            vhenv = UnityEnvironment(num_agents=1,
                                    max_episode_length=300,
                                    port_id=2,
                                    env_task_set=None,  
                                    observation_types=['full'],
                                    use_editor=True,
                                    task_goal=[task_goal],
                                    executable_args=executable_args,
                                    base_port=8080,
                                    seed=1)

            vhenv.reset(task_goal=task_goal,env_id=env_id)

            # Add beers and restart again TODO: this should not be done, or at least not here
            graph = vhenv.add_beers()

            obs = vhenv.reset(task_goal=task_goal, environment_graph=graph, env_id=env_id, add_character=False)
            # Get valid actions
            valid_actions = vhenv.get_valid_action(obs)

            goal_language = get_goal_language(task_goal, graph)
            print('Goal language:', goal_language) 

            obs_list = [parse_language_from_goal_script_output_object(subgoal, subgoal_count, graph, template=0) for subgoal, subgoal_count in task_goal.items()]
            print("obs_list: ", obs_list)
            # Flatten the list and remove duplicates
            seen = set()
            flattened_obs__list = []
            for sublist in obs_list:
                for item in sublist:
                    if item not in seen:
                        flattened_obs__list.append(item)
                        seen.add(item)

            print("obs_list: ",flattened_obs__list)

            objects_name = []
            targets_id = []  # such as the id of table or fridge

            # Iterate through the list and classify each item
            for item in flattened_obs__list:
                if item is None:
                    continue
                elif item.isdigit():
                    targets_id.append(int(item))
                else:
                    objects_name.append(item)
            
            groundtruth_object_ids = []
            groundtruth_object_ids_with_indirect_objects = []
            for object_name in objects_name:
                object_nodes = find_nodes(graph,class_name= object_name)
                # print("object_nodes", object_nodes)
                object_ids = [object_nodes[i]['id'] for i in range(0,  len(object_nodes))]

                # print("find_edges_from: ", find_edges_from(graph, object_ids[0]))
                # print("find_edges_to: ", find_edges_to(graph, object_ids[0]))
                for obj_id in object_ids:
                    edges_from = find_edges_from(graph, obj_id)
                    # print("find_edges_from: ", edges_from)

                    for edge in edges_from:
                        relation, obj = edge
                        if relation == 'INSIDE' and obj['category'] != 'Rooms':
                            groundtruth_object_ids_with_indirect_objects.append(obj['id'])

                groundtruth_object_ids = groundtruth_object_ids + object_ids
                print("find nodes of initial graph apple: ", len(object_nodes), object_ids)
            groundtruth_object_ids = groundtruth_object_ids + targets_id
            groundtruth_object_ids_with_indirect_objects = groundtruth_object_ids_with_indirect_objects + groundtruth_object_ids
            print("groundtruth_object_ids: ", groundtruth_object_ids)
            

            failure_counts = None
            if filter_objects:
                selected_objects_id, selected_objects_names, failure_counts = get_filtered_objects(obs, goal_language, LLM_model)
                filtered_valid_actions = filter_valid_actions(valid_actions, selected_objects_id)
                print("selected_objects_names: ", selected_objects_names)
                print("selected_objects_id: ", selected_objects_id)
                print("failure_counts: ", failure_counts)
            else:
                selected_objects_id = []
                filtered_valid_actions = []
                selected_objects_names = []

            # Analyse the difference between groundtruth list and LLM-generated list
            difference_log = {
                "task_goal": task_goal,
                "env_id": env_id,
                "groundtruth_object_ids": groundtruth_object_ids,
                "groundtruth_object_ids_with_indirect_objects": groundtruth_object_ids_with_indirect_objects,
                "selected_objects_id": selected_objects_id,
                "selected_objects_names": selected_objects_names
            }
            
            difference_log["failure_counts"] = str(failure_counts)

            if groundtruth_object_ids == selected_objects_id:
                print("The lists are the same.")
                difference_log["difference groundtruth_object_ids"] = str(False)
            else:
                groundtruth_not_in_selected = list(set(groundtruth_object_ids) - set(selected_objects_id))
                selected_not_in_groundtruth = list(set(selected_objects_id) - set(groundtruth_object_ids))

                def find_corresponding_name_via_ID(id):
                    for node in graph['nodes']:
                        if node['id'] == int(id):
                            return node['class_name']
                    
                groundtruth_not_in_selected_objName = [find_corresponding_name_via_ID(one_id) for one_id in groundtruth_not_in_selected]
                selected_not_in_groundtruth_objName = [find_corresponding_name_via_ID(one_id) for one_id in selected_not_in_groundtruth]
                
                print("The lists are different.")
                difference_log["difference groundtruth_object_ids"] = str(True)
                if groundtruth_not_in_selected:
                    print("Items in groundtruth_object_ids but not in selected_objects_id:", groundtruth_not_in_selected, " name: ", groundtruth_not_in_selected_objName)
                    difference_log["groundtruth_not_in_selected"] = {
                        "ids": groundtruth_not_in_selected,
                        "names": groundtruth_not_in_selected_objName
                    }
                if selected_not_in_groundtruth:
                    print("Items in selected_objects_id but not in groundtruth_object_ids:", selected_not_in_groundtruth, " name: ", selected_not_in_groundtruth_objName)
                    difference_log["selected_not_in_groundtruth"] = {
                        "ids": selected_not_in_groundtruth,
                        "names": selected_not_in_groundtruth_objName
                    }

            if groundtruth_object_ids_with_indirect_objects != groundtruth_not_in_selected:
                if groundtruth_object_ids_with_indirect_objects == selected_objects_id:
                    print("The lists are the same. groundtruth_object_ids_with_indirect_objects")
                    difference_log["difference groundtruth_object_ids"] = str(False)
                else:
                    groundtruth_not_in_selected = list(set(groundtruth_object_ids_with_indirect_objects) - set(selected_objects_id))
                    selected_not_in_groundtruth = list(set(selected_objects_id) - set(groundtruth_object_ids_with_indirect_objects))

                    def find_corresponding_name_via_ID(id):
                        for node in graph['nodes']:
                            if node['id'] == int(id):
                                return node['class_name']
                        
                    groundtruth_not_in_selected_objName = [find_corresponding_name_via_ID(one_id) for one_id in groundtruth_not_in_selected]
                    selected_not_in_groundtruth_objName = [find_corresponding_name_via_ID(one_id) for one_id in selected_not_in_groundtruth]
                    
                    print("The lists are different. groundtruth_object_ids_with_indirect_objects")
                    difference_log["difference groundtruth_object_ids_with_indirect_objects"] = str(True)
                    if groundtruth_not_in_selected:
                        print("Items in groundtruth_object_ids_with_indirect_objects but not in selected_objects_id:", groundtruth_not_in_selected, " name: ", groundtruth_not_in_selected_objName)
                        difference_log["groundtruth_with_indirect_objects_not_in_selected"] = {
                            "ids": groundtruth_not_in_selected,
                            "names": groundtruth_not_in_selected_objName
                        }
                    if selected_not_in_groundtruth:
                        print("Items in selected_objects_id but not in groundtruth_object_ids_with_indirect_objects:", selected_not_in_groundtruth, " name: ", selected_not_in_groundtruth_objName)
                        difference_log["selected_not_in_groundtruth_with_indirect_objects"] = {
                            "ids": selected_not_in_groundtruth,
                            "names": selected_not_in_groundtruth_objName
                        }

            # Append the result to the log dictionary
            log_data["experiment_results"].append(difference_log)

        # Write the log data to a JSON file
        log_file_path = "results_exp/filtered_objects_evaluation/" + "results_FilterObject_policy_type_dataSet_%s_LLM_%s.json" \
                            % (dataset_type, LLM_model)
        with open(log_file_path, 'w') as log_file:
            json.dump(log_data, log_file, indent=4)

        print(f"Experiment log saved to {log_file_path}")

                