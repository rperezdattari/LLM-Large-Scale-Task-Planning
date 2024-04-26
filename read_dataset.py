import pickle
import ipdb



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

# Replace 'yourfile.pik' with the actual file path
filename = 'gen_data/dataset/train_env_set_help.pik'
# filename = 'gen_data/dataset/test_env_set_help.pik'

# Open the file in binary read mode
with open(filename, 'rb') as file:
    # Load the object from the file
    dataset_list = pickle.load(file)

# dataset_list contains many dicts
    # each dict contains the following keys: dict_keys(['task_id', 'task_name', 'env_id', 'init_graph', 'task_goal', 'goal_class', 'level', 'init_rooms', 'pred_str'])dict_keys(['task_id', 'task_name', 'env_id', 'init_graph', 'task_goal', 'goal_class', 'level', 'init_rooms', 'pred_str'])


# ipdb.set_trace() # used for debuggingg 
# your_object is now the deserialized object that was stored in the file
print('len of the data set: ', len(dataset_list))

for i in range(0, len(dataset_list)):
    print(i, " task name: ", dataset_list[i]['task_name'],  " task_goal: ", dataset_list[i]['task_goal'][0], " level: ", dataset_list[i]['level'])
    graph = dataset_list[i]['init_graph'] 
    print("graph nodes: ", len(graph['nodes']), len(graph['edges']))

    test_data_id = i
    env_id = dataset_list[test_data_id]['env_id']
    task_goal = dataset_list[test_data_id]['task_goal'][0]
    graph = dataset_list[test_data_id]['init_graph']
    # print("graph: ", graph.)
    print("init_rooms: ", dataset_list[test_data_id]['init_rooms'])

    # # Init virtualhome env
    # vhenv = UnityEnvironment(num_agents=1,
    #                             max_episode_length=300,
    #                             port_id=2,
    #                             env_task_set=None,  # env_task_set,#[env_task_set[0]],
    #                             observation_types=['full'],
    #                             use_editor=True,
    #                             task_goal=[task_goal],
    #                             executable_args=executable_args,
    #                             base_port=8080,
    #                             seed=1)
    # # Restart env
    
    # # vhenv.reset(task_goal=task_goal, init_graph=graph,env_id=env_id)
    # # vhenv.reset(task_goal=task_goal,env_id=env_id)

    # # Add beers and restart again TODO: this should not be done, or at least not here
    # # graph = vhenv.add_beers()

    # obs = vhenv.reset(task_goal=task_goal, init_graph=graph, env_id=env_id, add_character=True)

    task_goal_env = get_goal(task_goal)
    satisfied, unsatisfied  = utils.check_progress(graph, task_goal_env)
    print("satisfied: ", satisfied)
    print("unsatisfied: ", unsatisfied)


# dataset decomposition 
# first check whether the dataset's initial graph is consistent with the task_goal (check whether the sub-goals are satisfied)
