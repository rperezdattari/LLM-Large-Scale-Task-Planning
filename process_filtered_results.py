import json
import os
import numpy as np
# Define the directory containing the JSON files
# directory_path = "results_exp/filtered_objects_evaluation"
directory_path = "results_exp/filtered_objects_evaluation_removewalls"

# List all JSON files in the directory
json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
# json_files = ['results_FilterObject_policy_type_dataSet_1task_LLM_gpt-4o.json']

# Function to read and print keys from a JSON file
def read_json_file_keys(file_path):
    with open(file_path, 'r') as log_file:
        log_data = json.load(log_file)
    return log_data

# Recursive function to print all keys in a nested dictionary
def print_keys(d, parent_key=''):
    if isinstance(d, dict):
        for key in d:
            full_key = f"{parent_key}.{key}" if parent_key else key
            print(full_key)
            print_keys(d[key], full_key)
    elif isinstance(d, list):
        for i, item in enumerate(d):
            full_key = f"{parent_key}[{i}]"
            print_keys(item, full_key)


def caculate_mean_var(numbers):
        # Calculate the mean
    mean_value = sum(numbers) / len(numbers)
    # print(f"Mean: {mean_value}")

    # Calculate the variance
    variance_value = np.sqrt(sum((x - mean_value) ** 2 for x in numbers) / (len(numbers) - 1))
    # print(f"Variance: {variance_value}")
    return mean_value, variance_value

# Process each JSON file
for json_file in json_files:
    file_path = os.path.join(directory_path, json_file)
    log_data = read_json_file_keys(file_path)
    
    # print(f"Keys in {json_file}:")
    # print_keys(log_data)
    # print("\n")

    # # Access specific parts of the data if needed
    experiment_results = log_data.get("experiment_results", [])
    list_of_node_num = log_data.get("list_of_node_num", [])
    list_of_node_num_filtered = []
    count_groundtruth_not_in_selected = 0

    num_selected_objects = []
    num_groundtruth_objects = []
    print("----------------------------------------------")
    print("json_file: ", json_file)

    results_i = 0
    for result in experiment_results:
        # print_keys(result)

        if not ('groundtruth_not_in_selected' in result):
            # # number of selected objects:
            # print("number of selected objects :", len(result['selected_objects_id']))
            num_selected_objects.append(len(result['selected_objects_id']))
            num_groundtruth_objects.append(len(result['groundtruth_object_ids']))
            list_of_node_num_filtered.append(list_of_node_num[results_i])
            # # number of groundtruth: 
            # print("number of groundtruth objects :", len(result['groundtruth_object_ids']))

        results_i = results_i + 1

        if 'groundtruth_not_in_selected' in result:
            # print("groundtruth_not_in_selected: ", result['groundtruth_not_in_selected']['names'])
            count_groundtruth_not_in_selected = count_groundtruth_not_in_selected+1

        # if 'groundtruth_with_indirect_objects_not_in_selected' in result:
        #     print("groundtruth_with_indirect_objects_not_in_selected: ", result['groundtruth_with_indirect_objects_not_in_selected']['names'])
    
    mean_value, variance_value = caculate_mean_var(num_selected_objects)
    print("num_selected_objects mean: ", mean_value, " std: ", variance_value)

    mean_value, variance_value = caculate_mean_var(num_groundtruth_objects)
    print("num_groundtruth_objects mean: ", mean_value, " std: ", variance_value)

    mean_value, variance_value = caculate_mean_var(list_of_node_num_filtered)
    print("list_of_node_num mean: ", mean_value, " std: ", variance_value)

    # print("count_groundtruth_not_in_selected: ", count_groundtruth_not_in_selected)


print(json_files)