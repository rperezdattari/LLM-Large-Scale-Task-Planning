import json
from experiments_info.experiments_parameters import *

# experiments_list = [exp_1_3]
experiments_list = [exp_2_3]
for experiment_i in experiments_list:
    # Get experiment parameters
    policy_type = experiment_i['policy type']
    policy_execution = experiment_i['policy execution']
    LLM_model = experiment_i['LLM model']
    filter_objects = experiment_i['filter objects']
    dataset_type = experiment_i['Dataset']
    # Load JSON data from a local file
    json_file_name = "results_filter_%s_policy_type_%s_policy_execution_%s_dataSet_%s_LLM_%s.json" \
                            % (str(filter_objects), policy_type, policy_execution, dataset_type, LLM_model)
    

    # with open('results_exp/evaluations/' + json_file_name, 'r', encoding='utf-8') as file:
    with open('results_exp raw2/evaluations/' + json_file_name, 'r', encoding='utf-8') as file:
    # with open('results/evaluations/' + json_file_name, 'r', encoding='utf-8') as file:
        experiment_data = json.load(file)

    # Initialize variables to store the results
    tasks = []
    steps = []
    success_rate = None

    experiment_data = json.loads(experiment_data)
    print("experiment_data: ", type(experiment_data))
    print("experiment_data: ", len(experiment_data))
    # Extract task, steps, and success rate information

    success_count = 0
    step_length_average = 0
    i = 0
    for experiment in experiment_data:
        print("i: ", i)
        i = i + 0.5
        if len(experiment) == 3:
            print("success rate: ", experiment)
        else:
            # print("experiment: ", (experiment))
            # print("experiment[0]", experiment[0])
            # print("experiment[1]", experiment[-1])
            task = experiment[1]['goal']
            print("task: ", task)
            steps_info = [step for step in experiment if 'step' in step]
            tasks.append(task)
            steps.append(steps_info)

            step_length = len(steps_info)
            print("len of steps: ", step_length)

            success_this_exp = experiment[-1]['successful']
            print("success: ", success_this_exp)
            if success_this_exp:
                success_count = success_count + 1
                step_length_average = step_length_average + step_length
    step_length_average = step_length_average / (1.0 * success_count)
    print("successful step_length_average: ", step_length_average)

    # # Display results
    # print(f"Tasks:")
    # for i, task in enumerate(tasks):
    #     print(f"\nTask {i + 1}: {task}")
    #     print("Steps:")
    #     for step in steps[i]:
    #         print(step)

    # print(f"\nOverall Success Rate: {success_rate * 100}%")
