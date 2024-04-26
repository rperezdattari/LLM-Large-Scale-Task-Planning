from environment.unity_environment import UnityEnvironment
from environment.utils_environment import get_goal_language, filter_valid_actions
from utils import get_total_states
from llm_policy import LLMPolicy
from language_filter import LanguageFilter
import time
import argparse
import pickle
import json
from mcts.mcts import MCTSAgent
from experiments_info.tasks import tasks
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


if __name__ == "__main__":
    # Iterate through every experiment
    for experiment in experiments:
        # Get experiment parameters
        policy_type = experiment['policy type']
        policy_execution = experiment['policy execution']
        LLM_model = experiment['LLM model']
        filter_objects = experiment['filter objects']

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
        
        filename = 'gen_data/dataset/train_env_set_help.pik'
        with open(filename, 'rb') as file:
            # Load the object from the file
            dataset_list = pickle.load(file)

        # 'env_id', 'init_graph'
        

        results = []
        succ, total = 0, 0

        # Iterate through every evaluation task
        for task in tasks:
            # Get task goal
            # task_goal = task['goal'][0]
            # env_id = task['id']

            test_data_id = 98
            env_id = dataset_list[test_data_id]['env_id']
            task_goal = dataset_list[test_data_id]['task_goal'][0]
            graph = dataset_list[test_data_id]['init_graph']
            # print("graph: ", graph.)
            print("init_rooms: ", dataset_list[test_data_id]['init_rooms'])

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
            # vhenv.reset(task_goal=task_goal,env_id=env_id)

            # Add beers and restart again TODO: this should not be done, or at least not here
            # graph = vhenv.add_beers()

            obs = vhenv.reset(task_goal=task_goal, init_graph=graph, env_id=env_id, add_character=True)
            # obs = vhenv.reset(task_goal=task_goal, environment_graph=graph, env_id=env_id, add_character=False)

            # Get valid actions
            valid_actions = vhenv.get_valid_action(obs)

            # Get goal language
            goal_language = get_goal_language(task_goal, graph)
            print('Goal:', goal_language)

            # Get filtered objects and filtered valid actions actions from graph and goal
            if filter_objects:
                selected_objects_id, selected_objects_names = get_filtered_objects(obs, goal_language, LLM_model)
                filtered_valid_actions = filter_valid_actions(valid_actions, selected_objects_id)
            else:
                selected_objects_id = []
                filtered_valid_actions = []
                selected_objects_names = []

            # Initialize episode info list
            init_step = {'step': 0,
                         'n nodes': len(obs[0]['nodes']),
                         'n states nodes': get_total_states(obs),
                         'n edges': len(obs[0]['edges']),
                         'n selected objects': len(selected_objects_id),
                         'n valid actions': len(valid_actions),
                         'n filtered valid actions': len(filtered_valid_actions)}

            episode_info = [experiment, {'goal': goal_language}, init_step]

            # Run MCTS or start LLM policy
            if policy_type == 'mcts':
                # Init MCTS and time counter
                mcts_agent = MCTSAgent(args, vhenv, selected_objects_id, uct_type=args.uct_type)
                mcts_init_time = time.time()
                if filter_objects:
                    mcts_actions, sim_steps = mcts_agent.search(filtered_valid_actions)
                else:
                    mcts_actions, sim_steps = mcts_agent.search(valid_actions)

                # Compute total time and add info to episode info
                mcts_delta_time = time.time() - mcts_init_time
                episode_info.append({'simulation steps': sim_steps,
                                     'simulation time': mcts_delta_time})
            elif policy_type == 'LLM':
                # Init LLM policy
                llm_policy = LLMPolicy(goal_language)
            elif policy_type == 'mcts_2': # not done yet
                args_common = dict(recursive=False,
                         max_episode_length=5,
                         num_simulation=200,
                         max_rollout_steps=5,
                         c_init=0.1,
                         c_base=1000000,
                         num_samples=1,
                         num_processes=1,
                         logging=True,
                         logging_graphs=True)

                args_agent1 = {'agent_id': 0, 'char_index': 0}
                args_agent1.update(args_common)
                mcts_agent2 = MCTS_agent(**args_agent1)
                # print("obs: ", obs)
                mcts_agent2.reset(obs[0], graph, task_goal)
                mcts_agent2.get_action(obs[0],  vhenv.get_goal(task_goal, 'full'), None)
            else:
                raise NameError('Policy type %s does not exist' % policy_type)

            actions = []
            done = False
            # Iterate over episode
            for j in range(args.max_depth + 1):  # TODO: check this, currently being set w.r.t. MCTS, but it could be different in the case of LLM
                print(" ---------------------- Step: ", j, " ---------------------- ")

                # Get action from LLM or MCTS
                if policy_type == 'mcts':
                    state_llm = []
                    # If no actions, MCTS failed
                    if mcts_actions is None:
                        print('MCTS failed.')
                        break
                    # Make sure the current index is valid in action list from MCTS
                    if j < len(mcts_actions):
                        action = mcts_actions[j]
                    else:
                        action = valid_actions[0]
                elif policy_type == 'LLM':
                    # Get LLM state and get action
                    state_llm = llm_policy.get_llm_state(obs, selected_objects_id, selected_objects_names)
                    action, response_message = llm_policy.act(state_llm, filtered_valid_actions, LLM_model)
                elif policy_type == 'mcts_2':
                    print("not done yet")
                else:
                    raise NameError('Policy type %s does not exist' % policy_type)

                # Do environment step
                obs, reward, done, info, success = vhenv.step({0: action})
                print("done: ", done)

                # Get valid actions and filtered actions (if filter activated)
                valid_actions = vhenv.get_valid_action(obs)
                if filter_objects:
                    filtered_valid_actions = filter_valid_actions(valid_actions, selected_objects_id)

                # Collect step info
                total_states = get_total_states(obs)  # get total states

                step = {'step': j + 1,
                        'n nodes': len(obs[0]['nodes']),
                        'n states nodes': total_states,
                        'n edges': len(obs[0]['edges']),
                        'n selected objects': len(selected_objects_id),
                        'n states llm': len(state_llm),
                        'n valid actions': len(valid_actions),
                        'n filtered valid actions': len(filtered_valid_actions),
                        'action (t-1)': action}

                # Append step and action
                episode_info.append(step)
                actions.append(action)
                print('Actions:\n', actions)

                if done:
                    succ += 1
                    break

                if action == 'Finished!':
                    print('llm response:', response_message)
                    print('\nValid actions:', filtered_valid_actions)
                    break

            total += 1
            # ipdb.set_trace()
            episode_info.append({'successful': done})
            results.append(episode_info)

            time.sleep(1)
            print('succ rate: ', succ / total)

        results.append({'successes': succ,
                        'total': total,
                        'success rate': succ / total})
        results_json = json.dumps(results)

        # Save results
        json_file_name = "results_filter_%s_policy_type_%s_policy_execution_%s_LLM_%s.json" \
                         % (str(filter_objects), policy_type, policy_execution, LLM_model)
        with open('results/evaluations/' + json_file_name, 'w', encoding='utf-8') as file:
            json.dump(results_json, file, ensure_ascii=False, indent=4)