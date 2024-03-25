import pickle
import ipdb
# Replace 'yourfile.pik' with the actual file path
# filename = 'gen_data/dataset/train_env_set_help.pik'
filename = 'gen_data/dataset/test_env_set_help.pik'

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
    print(i, " task name: ", dataset_list[i]['task_name'],  " task_goal: ", dataset_list[i]['task_goal'], " level: ", dataset_list[i]['level'])
