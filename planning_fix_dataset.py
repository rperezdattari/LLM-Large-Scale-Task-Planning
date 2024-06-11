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
    file_name = 'results/filtered_objects/' + goal_language.replace(' ', '_') + '_' + LLM_model + '.pk'
    # Check if file exists
    if os.path.isfile(file_name):
        # Load if exists
        with open(file_name, 'rb') as file:
            loaded_dict = pickle.load(file)
        selected_objects_id = loaded_dict['selected objects id']
        selected_objects_names = loaded_dict['selected objects names']
        print('Filtered objects file existed and loaded!')
    else:
        # Filter objects and save them
        language_filter = LanguageFilter(graph, goal_language, LLM_model)
        selected_objects_id, selected_objects_names = language_filter.filter_graph()  # get ids objects used for planning
        save_dict = {'selected objects id': selected_objects_id,
                     'selected objects names': selected_objects_names}
        with open(file_name, 'wb') as file:  # save filtered objects
            pickle.dump(save_dict, file)
        print('Objects filtered and saved!')

    return selected_objects_id, selected_objects_names



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

        #### Following lines currently not used
        file_path = f'../llm-mcts/vh/dataset/env_task_set_500_{args.mode}.pik'  # f'../llm-mcts/vh/dataset/env_task_set_10_simple_seen.pik'
        # env_task_set = pickle.load(open(file_path, 'rb'))
        executable_args = {
            'file_name': "/home/zhaoting/miniconda3/envs/llm_filter_planning/lib/python3.8/site-packages/virtualhome/simulation/unity_simulator/linux_exec/linux_exec.v2.3.0.x86_64",
            'x_display': "1",
            'no_graphics': False
        }
        ####
        # filename = 'gen_data/dataset/test_env_set_help.pik'
        
        # filename = 'gen_data/dataset/new_train_set_2_subtasks.pik'
        # with open(filename, 'rb') as file:
        #     # Load the object from the file
        #     dataset_list = pickle.load(file)

        # # 'env_id', 'init_graph'
        
        # for env in dataset_list:
        #     g = env['init_graph']
        #     id2node = {node['id']: node['class_name'] for node in g['nodes']}
        #     cloth_ids = [node['id'] for node in g['nodes'] if node['class_name'] in ["clothespile"]]
        #     g['nodes'] = [node for node in g['nodes'] if node['id'] not in cloth_ids]
        #     g['edges'] = [edge for edge in g['edges'] if edge['from_id'] not in cloth_ids and edge['to_id'] not in cloth_ids]

        results = []
        succ, total = 0, 0

        # Iterate through every evaluation task
        for task in tasks:
        # new_train_set_2_subtasks: 2 is not able to be used because the 'holds' action is not considered in parse_language_from_goal_script
        # for test_data_id in range(3, 13):
        # for test_data_id in range(44, 45):
            # Get task goal
            task_goal = task['goal'][0]
            env_id = task['id']
            print("---------------------------------------------")
            print("task goal: ", task_goal, "env id: ", env_id)
            # env_id = dataset_list[test_data_id]['env_id']
            # task_goal = dataset_list[test_data_id]['task_goal'][0]
            # # graph = dataset_list[test_data_id]['init_graph']
            # graph = dataset_list[test_data_id]['init_graph']
            from utils import find_nodes
            # print("find nodes of initial graph apple: ", find_nodes(graph,class_name= 'bellpepper'))
            # print("graph nodes: ", len(graph['nodes']), len(graph['edges']))
            # print("graph: ", graph.)
            # print("init_rooms: ", dataset_list[test_data_id]['init_rooms'])

            # Init virtualhome env
            vhenv = UnityEnvironment(num_agents=1,
                                     max_episode_length=300,
                                     port_id=2,
                                     env_task_set=None,  # env_task_set,#[env_task_set[0]],
                                     observation_types=['full'],
                                     use_editor=True,
                                     task_goal=[task_goal],
                                     executable_args=executable_args,
                                     base_port=8080,
                                     seed=1)
            # Restart env
            
            # vhenv.reset(task_goal=task_goal, init_graph=graph,env_id=env_id)
            vhenv.reset(task_goal=task_goal,env_id=env_id)

            # Add beers and restart again TODO: this should not be done, or at least not here
            graph = vhenv.add_beers()

            # obs = vhenv.reset(task_goal=task_goal, init_graph=graph, env_id=env_id, add_character=True)

            # to do, needs to find the map from the task in the dataset to the task that is consistent with the obs
            # 1. target (such as dishwasher) has different id
            # 2. missing objects, try to see whether we can add the missing objects into the environment

            # interested_item_list = ['fridge', 'tv', 'apple', 'chips', 'cupcake', 'pudding', 'whippedcream', 'pie', 'candybar', 'crackers', 'breadslice', 'bananas', 'lime', 'peach', 'plum',
            #                         'cereal', 'juice', 'milk', 'carrot', 'salad', 'mincedmeat', 'bellpepper', 'poundcake', 'chocolatesyrup', 'creamybuns', 'salmon', 'book', 'bookshelf']
            # interested_item_list_clean_kicten = ['kitchencounter', 'dishwasher', "coffeetable", 'kitchentable', 'fridge', 'mug', 'plate', 'dishbowl', 'wineglass', 'condimentbottle', 'fryingpan', 'cutleryknife', 'cutleryfork']
            # for item in interested_item_list:
            #     print(item, " find nodes of obs: ", find_nodes(graph,class_name= item))
            goal_language = get_goal_language(task_goal, graph)
            print('Goal language:', goal_language) 

            obs_list = [parse_language_from_goal_script_output_object(subgoal, subgoal_count, graph, template=0) for subgoal, subgoal_count in task_goal.items()]
            
            # Flatten the list and remove duplicates
            seen = set()
            flattened_obs__list = []
            for sublist in obs_list:
                for item in sublist:
                    if item not in seen:
                        flattened_obs__list.append(item)
                        seen.add(item)
            # obs_list = [item for sublist in obs_list for item in sublist]
            # obs_list = [item for subgoal, subgoal_count in task_goal.items() for item in parse_language_from_goal_script_output_object(subgoal, subgoal_count, graph, template=0)]

            print("obs_list: ",flattened_obs__list)
            
            groundtruth_object_ids = []
            for object_name in flattened_obs__list:
                object_nodes = find_nodes(graph,class_name= object_name)
                object_ids = [object_nodes[i]['id'] for i in range(0,  len(object_nodes))]
                groundtruth_object_ids = groundtruth_object_ids + object_ids
                print("find nodes of initial graph apple: ", len(object_nodes), object_ids)
            print("groundtruth_object_ids: ", groundtruth_object_ids)

            