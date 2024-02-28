from os import listdir
from os.path import isfile, join
import json
import numpy as np

path = 'results/evaluations/'
files_names = [f for f in listdir(path) if isfile(join(path, f))]
h = 0
for file_name in files_names:
    h += 1
    file = open(path + file_name)
    data = json.load(file)
    data_json = json.loads(data)

    # hyperparameters
    policy_type = data_json[0][0]['policy type']
    policy_execution = data_json[0][0]['policy_execution']
    LLM_model = data_json[0][0]['LLM model']
    filter_objects = data_json[0][0]['filter objects']

    # general results
    n_tasks = data_json[-1]['total']
    successes = data_json[-1]['successes']
    success_rate = data_json[-1]['success rate']

    # iterate along tasks
    episode_results_list = []
    k = 0
    if policy_type == 'mcts':
        k = 1
    for i in range(len(data_json) - 1):
        goal = data_json[i][1]['goal']
        successful = data_json[i][-1]['successful']
        n_nodes = data_json[i][2+k]['n nodes']
        n_states_nodes = data_json[i][2+k]['n states nodes']
        n_selected_objects = data_json[i][2+k]['n selected objects']
        episode_results = {'goal': goal,
                           'successful': successful,
                           'n nodes': n_nodes,
                           'n states nodes': n_states_nodes,
                           'n selected objects': n_selected_objects}

        n_edges = []
        #n_states_llm = []
        n_valid_actions = []
        n_filtered_valid_actions = []
        #action_list = []

        # iterate along episodes
        for j in range(len(data_json[i]) - 3 - k):
            n_edges.append(data_json[i][j+2+k]['n edges'])
            #n_states_llm.append(data_json[i][j+2+k]['n states llm'])
            n_valid_actions.append(data_json[i][j+2+k]['n valid actions'])
            n_filtered_valid_actions.append(data_json[i][j+2+k]['n filtered valid actions'])
            #action_list.append(data_json[i][j+2+k]['action'])

        # compute statistics
        average_n_edges = np.mean(n_edges)
        #average_n_states_llm = np.mean(n_states_llm)
        average_n_valid_actions = np.mean(n_valid_actions)
        average_n_filtered_valid_actions = np.mean(n_filtered_valid_actions)
        valid_action_proportion = average_n_filtered_valid_actions / average_n_valid_actions
        selected_objects_proportion = n_selected_objects / n_nodes

        episode_results.update({'goal': goal,
                           'n nodes': n_nodes,
                           'n states nodes': n_states_nodes,
                           'n selected objects': n_selected_objects,
                           'selected_objects_proportion': selected_objects_proportion,
                           'mean n edges': average_n_edges,
                           #'mean n states llm': average_n_states_llm,
                           'mean n valid actions': average_n_valid_actions,
                           'average n filtered valid actions': average_n_filtered_valid_actions,
                           'valid action proportion': valid_action_proportion})

        episode_results_list.append(episode_results)

    # Get average results over episodes
    average_n_nodes_tasks = []
    average_selected_objects_tasks = []
    average_valid_actions_tasks = []
    average_filter_valid_actions_tasks = []
    for result in episode_results_list:
        average_n_nodes_tasks.append(result['n nodes'])
        average_selected_objects_tasks.append(result['n selected objects'])
        average_valid_actions_tasks.append(result['mean n valid actions'])
        average_filter_valid_actions_tasks.append(result['average n filtered valid actions'])

    average_n_nodes_tasks = np.mean(average_n_nodes_tasks)
    average_selected_objects_tasks = np.mean(average_selected_objects_tasks)
    average_valid_actions_tasks = np.mean(average_valid_actions_tasks)
    average_filter_valid_actions_tasks = np.mean(average_filter_valid_actions_tasks)

    print('Experiment', h)
    # Print hyperparameters:
    print('\nHyperparameters:\n')
    print('- Policy type:', policy_type)
    print('- LLM model:', LLM_model)
    print('- Filter objects:', filter_objects)
    print('\n')

    # Print general results
    print('General results:\n')
    print('- N tasks:', n_tasks)
    print('- Success rate:', success_rate)
    print('- Nodes average:', average_n_nodes_tasks)
    print('- Filtered nodes average:', average_selected_objects_tasks,
          '(%.2f %%)' % (100 * average_selected_objects_tasks/average_n_nodes_tasks))
    print('- Valid actions average:', average_valid_actions_tasks)
    print('- Filtered valid actions average:', average_filter_valid_actions_tasks,
          '(%.2f %%)' % (100 * average_filter_valid_actions_tasks/average_valid_actions_tasks))
    print('\n ---------------------------------------------------------------------------------')