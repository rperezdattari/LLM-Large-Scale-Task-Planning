import ipdb
import copy
import random
import pdb


def inside_not_trans(graph):
    #print([{'from_id': 425, 'to_id': 396, 'relation_type': 'ON'}, {'from_id': 425, 'to_id': 396, 'relation_type': 'INSIDE'}])
    id2node = {node['id']: node for node in graph['nodes']}
    parents = {}
    grabbed_objs = []
    for edge in graph['edges']:
        if edge['relation_type'] == 'INSIDE':

            if edge['from_id'] not in parents:
                parents[edge['from_id']] = [edge['to_id']]
            else:
                parents[edge['from_id']] += [edge['to_id']]

        elif edge['relation_type'].startswith('HOLDS'):
            grabbed_objs.append(edge['to_id'])

    edges = []
    for edge in graph['edges']:
        if edge['relation_type'] == 'INSIDE' and id2node[edge['to_id']]['category'] == 'Rooms':
            if len(parents[edge['from_id']]) == 1:
                edges.append(edge)
            
        else:
            edges.append(edge)
    graph['edges'] = edges

    # # add missed edges
    # missed_edges = []
    # for obj_id, action in self.obj2action.items():
    #     elements = action.split(' ')
    #     if elements[0] == '[putback]':
    #         surface_id = int(elements[-1][1:-1])
    #         found = False
    #         for edge in edges:
    #             if edge['relation_type'] == 'ON' and edge['from_id'] == obj_id and edge['to_id'] == surface_id:
    #                 found = True
    #                 break
    #         if not found:
    #             missed_edges.append({'from_id': obj_id, 'relation_type': 'ON', 'to_id': surface_id})
    # graph['edges'] += missed_edges

    parent_for_node = {}

    char_close = {1: [], 2: []}
    for char_id in range(1, 3):
        for edge in graph['edges']:
            if edge['relation_type'] == 'CLOSE':
                if edge['from_id'] == char_id and edge['to_id'] not in char_close[char_id]:
                    char_close[char_id].append(edge['to_id'])
                elif edge['to_id'] == char_id and edge['from_id'] not in char_close[char_id]:
                    char_close[char_id].append(edge['from_id'])
    ## Check that each node has at most one parent
    objects_to_check = []
    for edge in graph['edges']:
        if edge['relation_type'] == 'INSIDE':
            if edge['from_id'] in parent_for_node and not id2node[edge['from_id']]['class_name'].startswith('closet'):
                print('{} has > 1 parent'.format(edge['from_id']))
                ipdb.set_trace()
                raise Exception
            parent_for_node[edge['from_id']] = edge['to_id']
            # add close edge between objects in a container and the character
            if id2node[edge['to_id']]['class_name'] in ['fridge', 'kitchencabinet', 'cabinet', 'microwave',
                                                        'dishwasher', 'stove']:
                objects_to_check.append(edge['from_id'])
                for char_id in range(1, 3):
                    if edge['to_id'] in char_close[char_id] and edge['from_id'] not in char_close[char_id]:
                        graph['edges'].append({
                            'from_id': edge['from_id'],
                            'relation_type': 'CLOSE',
                            'to_id': char_id
                        })
                        graph['edges'].append({
                            'from_id': char_id,
                            'relation_type': 'CLOSE',
                            'to_id': edge['from_id']
                        })

    ## Check that all nodes except rooms have one parent
    nodes_not_rooms = [node['id'] for node in graph['nodes'] if node['category'] not in ['Rooms', 'Doors']]
    nodes_without_parent = list(set(nodes_not_rooms) - set(parent_for_node.keys()))
    nodes_without_parent = [node for node in nodes_without_parent if node not in grabbed_objs]
    graph['edges'] = [edge for edge in graph['edges'] if not (edge['from_id'] in objects_to_check and edge['relation_type'] == 'ON')]
    # if len(nodes_without_parent) > 0:
    #     for nd in nodes_without_parent:
    #         print(id2node[nd])
    #     ipdb.set_trace()
    #     raise Exception
    return graph


def convert_action(action_dict):
    agent_do = [item for item, action in action_dict.items() if action is not None]
    # Make sure only one agent interact with the same object
    if len(action_dict.keys()) > 1:
        if None not in list(action_dict.values()) and sum(['walk' in x for x in action_dict.values()]) < 2:
            # continue
            objects_interaction = [x.split('(')[1].split(')')[0] for x in action_dict.values()]
            if len(set(objects_interaction)) == 1:
                agent_do = [random.choice([0,1])]

    script_list = ['']

    for agent_id in agent_do:
        script = action_dict[agent_id]
        if script is None:
            continue
        current_script = ['<char{}> {}'.format(agent_id, script)]

        script_list = [x + '|' + y if len(x) > 0 else y for x, y in zip(script_list, current_script)]

    # if self.follow:
    #script_list = [x.replace('[walk]', '[walktowards]') for x in script_list]
    # script_all = script_list
    return script_list


def separate_new_ids_graph(graph, max_id):
    new_graph = copy.deepcopy(graph)
    for node in new_graph['nodes']:
        if node['id'] > max_id:
            node['id'] = node['id'] - max_id + 1000
    for edge in new_graph['edges']:
        if edge['from_id'] > max_id:
            edge['from_id'] = edge['from_id'] - max_id + 1000
        if edge['to_id'] > max_id:
            edge['to_id'] = edge['to_id'] - max_id + 1000
    return new_graph

def check_progress(state, goal_spec):
    """TODO: add more predicate checkers; currently only ON"""
    unsatisfied = {}
    satisfied = {}
    reward = 0.
    id2node = {node['id']: node for node in state['nodes']}

    for key, value in goal_spec.items():

        elements = key.split('_')
        unsatisfied[key] = value[0] if elements[0] not in ['offOn', 'offInside'] else 0
        satisfied[key] = [None] * 2
        satisfied[key]
        satisfied[key] = []
        for edge in state['edges']:
            if elements[0] in 'close':
                if edge['relation_type'].lower().startswith('close') and id2node[edge['to_id']]['class_name'] == elements[1] and edge['from_id'] == int(elements[2]):
                    predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                    satisfied[key].append(predicate)
                    unsatisfied[key] -= 1
            if elements[0] in ['on', 'inside']:
                # print(edge)
                if edge['relation_type'].lower() == elements[0] and edge['to_id'] == int(elements[2]):
                    if (id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                        satisfied[key].append(predicate)
                        unsatisfied[key] -= 1
            elif elements[0] == 'offOn':
                if edge['relation_type'].lower() == 'on' and edge['to_id'] == int(elements[2]) and (id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
                    predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                    unsatisfied[key] += 1
            elif elements[0] == 'offInside':
                if edge['relation_type'].lower() == 'inside' and edge['to_id'] == int(elements[2]) and (id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
                    predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                    unsatisfied[key] += 1
            elif elements[0] == 'holds':
                if edge['relation_type'].lower().startswith('holds') and id2node[edge['to_id']]['class_name'] == elements[1] and edge['from_id'] == int(elements[2]):
                    predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                    satisfied[key].append(predicate)
                    unsatisfied[key] -= 1
            elif elements[0] == 'sit':
                if edge['relation_type'].lower().startswith('sit') and edge['to_id'] == int(elements[2]) and edge['from_id'] == int(elements[1]):
                    predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                    satisfied[key].append(predicate)
                    unsatisfied[key] -= 1
        if elements[0] == 'turnon':
            if 'ON' in id2node[int(elements[1])]['states']:
                predicate = '{}_{}_{}'.format(elements[0], elements[1], 1)
                satisfied[key].append(predicate)
                unsatisfied[key] -= 1
    return satisfied, unsatisfied


def parse_language_from_goal_script(goal_script, goal_num, init_graph, template=0):
    goal_script_split = goal_script.split('_')

    if 'closed' in goal_script.lower():
        obj = goal_script_split[1]

        for node in init_graph['nodes']:
            if node['id'] == int(obj):
                tar_node = node
                tar_id = node['id']

        if template == 1:
            goal_language = 'could you please close the %s' % (tar_node['class_name'])
        elif template == 2:
            goal_language = 'please close the %s' % (tar_node['class_name'])
        else:
            goal_language = 'close %s (%i)' % (tar_node['class_name'], tar_id)

    elif 'turnon' in goal_script.lower():
        obj = goal_script_split[1]
        for node in init_graph['nodes']:
            if node['id'] == int(obj):
                tar_node = node
                tar_id = node['id']

        if template == 1:
            goal_language = 'could you please turn on the %s' % (tar_node['class_name'])
        elif template == 2:
            goal_language = 'next turn on the %s' % (tar_node['class_name'])
        else:
            goal_language = 'turn on %s (%i)' % (tar_node['class_name'], tar_id)

    elif 'on_' in goal_script.lower() or 'inside_' in goal_script.lower():
        numbers = {'1': 'one',
                   '2': 'two',
                   '3': 'three'}

        rel = goal_script_split[0]
        obj = goal_script_split[1]
        tar = goal_script_split[2]
        for node in init_graph['nodes']:
            if node['id'] == int(tar):
                tar_node = node
                tar_id = node['id']

        plural = ''
        if goal_num > 1:
            plural = 's'

        if template == 1:
            goal_language = 'could you please place %d %s %s the %s' % (goal_num, obj, rel, tar_node['class_name'])
        elif template == 2:
            goal_language = 'get %d %s and put it %s the %s' % (goal_num, obj, rel, tar_node['class_name'])
        else:
            goal_language = 'put %s %s%s %s the %s (%i)' % (numbers[str(goal_num)], obj, plural, rel, tar_node['class_name'], tar_id)
    else:
        pdb.set_trace()
    goal_language = goal_language.lower()
    return goal_language


def get_goal_language(task_goal, init_graph, template=0):
    goals_list = [parse_language_from_goal_script(subgoal, subgoal_count, init_graph, template=template) for subgoal, subgoal_count in task_goal.items()]

    goal_language = goals_list[0]
    if len(goals_list) > 1:
        for i in range(len(goals_list) - 1):
            goal_language += ' and ' + goals_list[i + 1]

    return goal_language


def filter_valid_actions(valid_actions, selected_objects):
    filtered_valid_actions = []
    for valid_action in valid_actions:
        valid_action_id = int(valid_action.split(' ')[2][1:-1])
        if valid_action_id in selected_objects:
            filtered_valid_actions.append(valid_action)

    return filtered_valid_actions