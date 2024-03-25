import copy
import numpy as np
import json
from environment.utils_environment import filter_valid_actions
from mcts.vh_env import VhGraphEnv
with open('environment/info/object_info.json') as f:
    object_info = json.load(f)


class MCTSVHEnv:
    def __init__(self, graph, goal_spec, task_goal, selected_objects_id):
        self.vh_pyenv = VhGraphEnv()
        self.goal_spec = goal_spec
        self.task_goal = task_goal
        self.vh_pyenv.pomdp = False
        self.selected_objects_id = selected_objects_id
        self.model = None
        self.history = []
        self.init_history = []
        self.cur_state_graph = graph
        self.cur_state = self.vh_pyenv.get_vh_state(graph)
        self.init_state = copy.deepcopy(self.cur_state)
        self.init_graph = self.init_state.to_dict()
        #self.belief = None

    def filtering_graph(self, graph):
        new_edges = []
        edge_dict = {}
        for edge in graph['edges']:
            key = (edge['from_id'], edge['to_id'])
            if key not in edge_dict:
                edge_dict[key] = [edge['relation_type']]
                new_edges.append(edge)
            else:
                if edge['relation_type'] not in edge_dict[key]:
                    edge_dict[key] += [edge['relation_type']]
                    new_edges.append(edge)

        graph['edges'] = new_edges
        return graph

    # def check_progress(self, state, goal_spec):
    #     """TODO: add more predicate checkers; currently only ON"""
    #     count = 0
    #     for key, value in goal_spec.items():
    #         if key.startswith('off'):
    #             count += value
    #     id2node = {node['id']: node for node in state['nodes']}
    #     for key, value in goal_spec.items():
    #         elements = key.split('_')
    #         for edge in state['edges']:
    #             if elements[0] in ['on', 'inside']:
    #                 if edge['relation_type'].lower() == elements[0] and edge['to_id'] == int(elements[2]) and (
    #                         id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
    #                     count += 1
    #             elif elements[0] == 'offOn':
    #                 if edge['relation_type'].lower() == 'on' and edge['to_id'] == int(elements[2]) and (
    #                         id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
    #                     count -= 1
    #             elif elements[1] == 'offInside':
    #                 if edge['relation_type'].lower() == 'inside' and edge['to_id'] == int(elements[2]) and (
    #                         id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[1]):
    #                     count -= 1
    #             elif elements[0] == 'holds':
    #                 if edge['relation_type'].lower().startswith('holds') and id2node[edge['to_id']]['class_name'] == \
    #                         elements[1] and edge['from_id'] == int(elements[2]):
    #                     count += 1
    #             elif elements[0] == 'sit':
    #                 if edge['relation_type'].lower().startswith('on') and edge['to_id'] == int(elements[2]) and edge['from_id'] == int(elements[1]):
    #                     count += 1
    #         if elements[0] == 'turnOn':
    #             if 'ON' in id2node[int(elements[1])]['states']:
    #                 count += 1
    #     goals = sum([value[0] for key, value in goal_spec.items()])
    #     if count < goals:
    #         reward = 0
    #     else:
    #         reward = 10
    #     return reward

    def check_progress(self, state, goal_spec):
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
                    if edge['relation_type'].lower().startswith('close') and id2node[edge['to_id']]['class_name'] == \
                            elements[1] and edge['from_id'] == int(elements[2]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                        satisfied[key].append(predicate)
                        unsatisfied[key] -= 1
                if elements[0] in ['on', 'inside']:
                    # print(edge)
                    if edge['relation_type'].lower() == elements[0] and edge['to_id'] == int(elements[2]) and (
                            id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[
                        1]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                        satisfied[key].append(predicate)
                        unsatisfied[key] -= 1
                elif elements[0] == 'offOn':
                    if edge['relation_type'].lower() == 'on' and edge['to_id'] == int(elements[2]) and (
                            id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[
                        1]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                        unsatisfied[key] += 1
                elif elements[0] == 'offInside':
                    if edge['relation_type'].lower() == 'inside' and edge['to_id'] == int(elements[2]) and (
                            id2node[edge['from_id']]['class_name'] == elements[1] or str(edge['from_id']) == elements[
                        1]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['from_id'], elements[2])
                        unsatisfied[key] += 1
                elif elements[0] == 'holds':
                    if edge['relation_type'].lower().startswith('holds') and id2node[edge['to_id']]['class_name'] == \
                            elements[1] and edge['from_id'] == int(elements[2]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                        satisfied[key].append(predicate)
                        unsatisfied[key] -= 1
                elif elements[0] == 'sit':
                    if edge['relation_type'].lower().startswith('sit') and edge['to_id'] == int(elements[2]) and edge[
                        'from_id'] == int(elements[1]):
                        predicate = '{}_{}_{}'.format(elements[0], edge['to_id'], elements[2])
                        satisfied[key].append(predicate)
                        unsatisfied[key] -= 1
            if elements[0] == 'turnon':
                if 'ON' in id2node[int(elements[1])]['states']:
                    predicate = '{}_{}_{}'.format(elements[0], elements[1], 1)
                    satisfied[key].append(predicate)
                    unsatisfied[key] -= 1
        return satisfied, unsatisfied

    def get_valid_actions(self, obs, agent_id):
        objects_grab = object_info['objects_grab']
        objects_inside = object_info['objects_inside']
        objects_surface = object_info['objects_surface']
        objects_switchonoff = object_info['objects_switchonoff']

        valid_action_space = {}

        node_id_name_dict = {node['id']: node['class_name'] for node in obs[0]['nodes']}
        for agent_action in ['walk', 'grab', 'putback', 'putin', 'switchon', 'open', 'close']:
            if agent_action == 'walk':
                # room_nodes = [node for node in obs[agent_id]['nodes'] if node['class_name'] in ['kitchen', 'livingroom', 'bathroom', 'bedroom']]
                # if len(room_nodes)!=4:
                #     pdb.set_trace()

                # ignore_objs = ['walllamp', 'doorjamb', 'ceilinglamp', 'door', 'curtains', 'candle', 'wallpictureframe',
                #                'powersocket']
                ignore_objs = []
                ignore_objs_idx = [idx for idx, node in enumerate(obs[agent_id]['nodes']) if
                                   node['class_name'] in ignore_objs]
                # interacted_object_idxs = [tem for tem in list(range(len(obs[agent_id]['nodes']))) if tem not in ignore_objs_idx]
                interacted_object_idxs = [(node["id"], node["class_name"]) for idx, node in
                                          enumerate(obs[agent_id]['nodes']) if idx not in ignore_objs_idx]

            elif agent_action == 'grab':
                agent_edge = [edge for edge in obs[agent_id]['edges'] if
                              edge['from_id'] == agent_id + 1 or edge['to_id'] == agent_id + 1]
                agent_obj_hold_edge = [edge for edge in agent_edge if 'HOLD' in edge['relation_type']]
                if len(agent_obj_hold_edge) > 1:  # Two arms
                    continue
                # if len(agent_obj_hold_edge) > 0:  # One arm
                #     continue

                ignore_objs = ['radio']
                ignore_objs_id = [node['id'] for node in obs[agent_id]['nodes'] if node['class_name'] in ignore_objs]
                grabbable_object_ids = [node['id'] for node in obs[agent_id]['nodes'] if
                                        node['class_name'] in objects_grab]
                grabbable_object_ids = [tem for tem in grabbable_object_ids if tem not in ignore_objs_id]
                agent_obj_edge = [edge for edge in agent_edge if
                                  edge['from_id'] in grabbable_object_ids or edge['to_id'] in grabbable_object_ids]
                agent_obj_close_edge = [edge for edge in agent_obj_edge if edge['relation_type'] == 'CLOSE']

                if len(agent_obj_close_edge) > 0:
                    interacted_object_ids = []
                    interacted_object_ids += [edge['from_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids += [edge['to_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids = list(np.unique(interacted_object_ids))
                    interacted_object_ids.remove(agent_id + 1)
                    # interacted_object_idxs = [idx for idx, node in enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                    interacted_object_idxs = [(node["id"], node["class_name"]) for idx, node in
                                              enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                else:
                    continue

            elif agent_action == 'open':
                agent_edge = [edge for edge in obs[agent_id]['edges'] if
                              edge['from_id'] == agent_id + 1 or edge['to_id'] == agent_id + 1]

                agent_obj_hold_edge = [edge for edge in agent_edge if 'HOLD' in edge['relation_type']]
                if len(agent_obj_hold_edge) > 1:  # Two arms
                    continue
                # if len(agent_obj_hold_edge) > 0:  # One arm
                #     continue

                container_object_nodes = [node for node in obs[agent_id]['nodes'] if
                                          node['class_name'] in objects_inside]
                # container_object_nodes = [node for node in container_object_nodes if 'CLOSED' in node['states']] ## contrainer is closed
                container_object_ids = [node['id'] for node in container_object_nodes]

                agent_obj_edge = [edge for edge in agent_edge if
                                  edge['from_id'] in container_object_ids or edge['to_id'] in container_object_ids]
                agent_obj_close_edge = [edge for edge in agent_obj_edge if edge['relation_type'] == 'CLOSE']

                if len(agent_obj_close_edge) > 0:
                    interacted_object_ids = []
                    interacted_object_ids += [edge['from_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids += [edge['to_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids = list(np.unique(interacted_object_ids))
                    interacted_object_ids.remove(agent_id + 1)
                    # interacted_object_idxs = [idx for idx, node in enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                    interacted_object_idxs = [(node["id"], node["class_name"]) for idx, node in
                                              enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                else:
                    continue

            elif agent_action == 'close':
                agent_edge = [edge for edge in obs[agent_id]['edges'] if
                              edge['from_id'] == agent_id + 1 or edge['to_id'] == agent_id + 1]

                agent_obj_hold_edge = [edge for edge in agent_edge if 'HOLD' in edge['relation_type']]
                if len(agent_obj_hold_edge) > 1:  # Two arms
                    continue
                # if len(agent_obj_hold_edge) > 0:  # One arm
                #     continue

                container_object_nodes = [node for node in obs[agent_id]['nodes'] if
                                          node['class_name'] in objects_inside]
                container_object_nodes = [node for node in container_object_nodes if
                                          'OPEN' in node['states']]  ## contrainer is closed
                container_object_ids = [node['id'] for node in container_object_nodes]

                agent_obj_edge = [edge for edge in agent_edge if
                                  edge['from_id'] in container_object_ids or edge['to_id'] in container_object_ids]
                agent_obj_close_edge = [edge for edge in agent_obj_edge if edge['relation_type'] == 'CLOSE']

                if len(agent_obj_close_edge) > 0:
                    interacted_object_ids = []
                    interacted_object_ids += [edge['from_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids += [edge['to_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids = list(np.unique(interacted_object_ids))
                    interacted_object_ids.remove(agent_id + 1)
                    interacted_object_idxs = [(node["id"], node["class_name"]) for idx, node in
                                              enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                    # interacted_object_idxs = [idx for idx, node in enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                else:
                    continue

            elif agent_action == 'switchon':
                agent_edge = [edge for edge in obs[agent_id]['edges'] if
                              edge['from_id'] == agent_id + 1 or edge['to_id'] == agent_id + 1]

                container_object_nodes = [node for node in obs[agent_id]['nodes'] if
                                          node['class_name'] in objects_switchonoff]
                container_object_nodes = [node for node in container_object_nodes if
                                          ('OFF' in node['states'])]  ## contrainer is closed
                container_object_ids = [node['id'] for node in container_object_nodes]

                agent_obj_edge = [edge for edge in agent_edge if
                                  edge['from_id'] in container_object_ids or edge['to_id'] in container_object_ids]
                agent_obj_close_edge = [edge for edge in agent_obj_edge if edge['relation_type'] == 'CLOSE']

                if len(agent_obj_close_edge) > 0:
                    interacted_object_ids = []
                    interacted_object_ids += [edge['from_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids += [edge['to_id'] for edge in agent_obj_close_edge]
                    interacted_object_ids = list(np.unique(interacted_object_ids))
                    interacted_object_ids.remove(agent_id + 1)
                    interacted_object_idxs = [(node["id"], node["class_name"]) for idx, node in
                                              enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                else:
                    continue

            elif agent_action == 'putin' or agent_action == 'putback':
                agent_edge = [edge for edge in obs[agent_id]['edges'] if
                              edge['from_id'] == agent_id + 1 or edge['to_id'] == agent_id + 1]
                agent_obj_hold_edge = [edge for edge in agent_edge if 'HOLD' in edge['relation_type']]

                # ignore_objs_tars = [('fryingpan', 'kitchencounter'), ('mug', 'sofa'),
                #                     ('pillow', 'kitchencounter'), ('pillow', 'sofa'), ('pillow', 'fridge'),
                #                     ('pillow', 'kitchencabinet'), ('pillow', 'coffeetable'),
                #                     ('pillow', 'bathroomcabinet'),
                #                     ('keyboard', 'coffeetable'), ('keyboard', 'bathroomcabinet'),
                #                     ('keyboard', 'cabinet'), ('keyboard', 'sofa'),
                #                     ('dishbowl', 'bathroomcabinet'), ('hairproduct', 'sofa')]

                ignore_objs_tars = []

                ignore_objs = [tem[0] for tem in ignore_objs_tars]

                if len(agent_obj_hold_edge) == 0:
                    continue
                else:
                    if len(agent_obj_hold_edge) != 1:
                        continue

                    holding_obj_name = node_id_name_dict[agent_obj_hold_edge[0]['to_id']]
                    ignore_tar = [tem[1] for tem in ignore_objs_tars if tem[0] == holding_obj_name]
                    holding_obj_id = agent_obj_hold_edge[0]['to_id']
                    if agent_action == 'putin':
                        container_object_nodes = [node for node in obs[agent_id]['nodes'] if
                                                  node['class_name'] in objects_inside]
                        container_object_nodes = [node for node in container_object_nodes if
                                                  node['class_name'] not in ignore_tar]
                        container_object_nodes = [node for node in container_object_nodes if
                                                  'OPEN' in node['states']]  ## contrainer is open
                        container_object_ids = [node['id'] for node in container_object_nodes]
                    elif agent_action == 'putback':
                        container_object_nodes = [node for node in obs[agent_id]['nodes'] if
                                                  node['class_name'] in objects_surface]
                        container_object_nodes = [node for node in container_object_nodes if
                                                  node['class_name'] not in ignore_tar]
                        container_object_ids = [node['id'] for node in container_object_nodes]

                    agent_obj_edge = [edge for edge in agent_edge if
                                      edge['from_id'] in container_object_ids or edge['to_id'] in container_object_ids]
                    agent_obj_close_edge = [edge for edge in agent_obj_edge if edge['relation_type'] == 'CLOSE']

                    if len(agent_obj_close_edge) > 0:
                        interacted_object_ids = []
                        interacted_object_ids += [edge['from_id'] for edge in agent_obj_close_edge]
                        interacted_object_ids += [edge['to_id'] for edge in agent_obj_close_edge]
                        interacted_object_ids = list(np.unique(interacted_object_ids))
                        interacted_object_ids.remove(agent_id + 1)
                        interacted_object_idxs = [(holding_obj_id, holding_obj_name, node["id"], node["class_name"]) for
                                                  idx, node in enumerate(obs[agent_id]['nodes']) if
                                                  node['id'] in interacted_object_ids]
                        # interacted_object_idxs = [idx for idx, node in enumerate(obs[agent_id]['nodes']) if node['id'] in interacted_object_ids]
                    else:
                        continue

            else:
                continue

            if len(interacted_object_idxs) == 0:
                continue
            else:
                valid_action_space[agent_action] = interacted_object_idxs
        return valid_action_space

    def get_valid_action(self, obs, agent_id=0):
        valid_action_space = []
        valid_action_space_dict = self.get_valid_actions(obs, agent_id)
        for action in valid_action_space_dict:
            interact_item_idxs = valid_action_space_dict[action]
            action = action.replace('walktowards', 'walk')
            if 'put' in action:

                valid_action_space += [
                    f'[{action}] <{grab_name}> ({grab_id}) <{item_name}> ({item_id})'
                    for grab_id, grab_name, item_id, item_name in interact_item_idxs]
            else:
                valid_action_space += [
                    f'[{action}] <{item_name}> ({item_id})'
                    for item_id, item_name in interact_item_idxs if
                    item_name not in ['wall', 'floor', 'ceiling', 'curtain', 'window']]

        return valid_action_space

    def reset(self, obs=None, graph=None, goal_spec=None, task_goal=None):
        if graph is None:
            graph = self.init_graph
        else:
            #self.belief = Belief(graph, agent_id=1)
            #graph = self.sample_belief()
            self.init_graph = graph
        obs = self.vh_pyenv.reset(graph)

        self.cur_state_graph = graph
        self.cur_state = self.vh_pyenv.get_vh_state(graph)
        self.init_state = copy.deepcopy(self.cur_state)
        self.init_graph = copy.deepcopy(graph)
        self.goal_spec = goal_spec if goal_spec is not None else self.goal_spec
        self.task_goal = task_goal if task_goal is not None else self.task_goal

        self.history = []
        self.init_history = []
        return obs

    def copy_env(self):
        self.reset(self.init_graph, self.goal_spec, self.task_goal)
        return self

    def update(self, action, obs):
        self.vh_pyenv.step({0: action})
        self.cur_state = self.vh_pyenv.vh_state
        self.cur_state_graph = self.vh_pyenv.state
        obs = self.vh_pyenv._mask_state(self.cur_state_graph, 0)
        #text_obs = self.graph_to_text(obs)
        if action is not None:
            self.history.append(action)
        #valid_actions = self.get_valid_action([obs])
        #reward = self.check_progress(self.cur_state_graph, self.goal_spec)
        reward = self.reward()
        if reward <= 0:
            done = False
        else:
            done = True
        self.init_graph = copy.deepcopy(self.cur_state_graph)
        self.init_state = copy.deepcopy(self.cur_state)
        return reward, done, self.history#, valid_actions

    # def update_(self, action, obs):
    #     if action is not None:
    #         self.vh_pyenv.step({0: action})
    #     #self.update_and_sample_belief(obs)
    #
    #     #text_obs = self.graph_to_text(obs)
    #     if action is not None:
    #         self.history.append(action)
    #     #valid_actions = self.get_valid_action([obs])
    #     reward = self.check_progress(self.cur_state_graph, self.goal_spec)
    #     if reward <= 0:
    #         done = False
    #     else:
    #         done = True
    #     self.init_graph = copy.deepcopy(self.cur_state_graph)
    #     self.init_state = copy.deepcopy(self.cur_state)
    #     return reward, done, self.history

    def reward(self):
        reward = 0.
        done = True
        #satisfied, unsatisfied = utils.check_progress(self.get_graph(), self.goal_spec[0])
        satisfied, unsatisfied = self.check_progress(self.cur_state_graph, self.goal_spec)
        for key, value in satisfied.items():
            #preds_needed, mandatory, reward_per_pred = self.goal_spec[0][key]
            preds_needed, mandatory, reward_per_pred = self.goal_spec[key]
            # How many predicates achieved
            value_pred = min(len(value), preds_needed)
            reward += value_pred * reward_per_pred
            if mandatory and unsatisfied[key] > 0:
                done = False

        self.prev_reward = reward
        return reward, done, {'satisfied_goals': satisfied}

    def step(self, action):
        #obs = self.vh_pyenv._mask_state(self.cur_state_graph, 0)
        #valid_actions = self.get_valid_action([obs])
        try:
            self.cur_state, succeed = self.vh_pyenv.transition(self.cur_state, {0: action})
        except:
            print(action)
        self.cur_state_graph = self.cur_state.to_dict()
        obs = self.vh_pyenv._mask_state(self.cur_state_graph, 0)
        #plate_ids = []
        # text_obs = self.graph_to_text(obs)
        # print("self.cur_state_graph: ", self.cur_state_graph)
        self.history.append(action)

        valid_actions = self.get_valid_action([obs])
        # Filter valid actions
        if self.selected_objects_id is not None:  # if filter is active
            valid_actions = filter_valid_actions(valid_actions, self.selected_objects_id)
        #reward = self.check_progress(self.cur_state_graph, self.goal_spec)
        reward, done, _ = self.reward()
        # if reward <= 0:
        #     done = False
        # else:
        #     done = True
        return obs, reward, done, self.history, valid_actions