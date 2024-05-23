# adapted from https://github.com/jys5609/MC-LAVE-RL.git

import numpy as np
from tqdm import tqdm
import mcts.mcts_utils as utils
from collections import defaultdict
from mcts.mcts_vh_env import MCTSVHEnv
from environment.utils_environment import filter_valid_actions

import ipdb 

import random
import copy
DISCOUNT_FACTOR = 0.95

####################################### Heuristic ##################################################

def find_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, object_target):
    # observations = simulator.get_observations(env_graph, char_index=char_index)
    observations = simulator.get_observations()

    id2node = {node['id']: node for node in env_graph['nodes']}
    containerdict = {edge['from_id']: edge['to_id'] for edge in env_graph['edges'] if edge['relation_type'] == 'INSIDE'}
    target = int(object_target.split('_')[-1])
    observation_ids = [x['id'] for x in observations['nodes']]
    try:
        room_char = [edge['to_id'] for edge in env_graph['edges'] if edge['from_id'] == agent_id and edge['relation_type'] == 'INSIDE'][0]
    except:
        print('Error')
        #ipdb.set_trace()

    action_list = []
    cost_list = []
    # if target == 478:
    #     ipdb.set_trace()
    while target not in observation_ids:
        try:
            container = containerdict[target]
        except:
            print(id2node[target])
            #ipdb.set_trace()
        # If the object is a room, we have to walk to what is insde

        if id2node[container]['category'] == 'Rooms':
            action_list = [('walk', (id2node[target]['class_name'], target), None)] + action_list 
            cost_list = [0.5] + cost_list
        
        elif 'CLOSED' in id2node[container]['states'] or ('OPEN' not in id2node[container]['states']):
            action = ('open', (id2node[container]['class_name'], container), None)
            action_list = [action] + action_list
            cost_list = [0.05] + cost_list

        target = container
    
    ids_character = [x['to_id'] for x in observations['edges'] if
                     x['from_id'] == agent_id and x['relation_type'] == 'CLOSE'] + \
                    [x['from_id'] for x in observations['edges'] if
                     x['to_id'] == agent_id and x['relation_type'] == 'CLOSE']

    if target not in ids_character:
        # If character is not next to the object, walk there
        action_list = [('walk', (id2node[target]['class_name'], target), None)]+ action_list
        cost_list = [1] + cost_list

    return action_list, cost_list

def grab_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, object_target):
    # observations = simulator.get_observations(env_graph, char_index=char_index)
    observations = simulator.get_observations()
    target_id = int(object_target.split('_')[-1])

    observed_ids = [node['id'] for node in observations['nodes']]
    agent_close = [edge for edge in env_graph['edges'] if ((edge['from_id'] == agent_id and edge['to_id'] == target_id) or (edge['from_id'] == target_id and edge['to_id'] == agent_id) and edge['relation_type'] == 'CLOSE')]
    grabbed_obj_ids = [edge['to_id'] for edge in env_graph['edges'] if (edge['from_id'] == agent_id and 'HOLDS' in edge['relation_type'])]

    target_node = [node for node in env_graph['nodes'] if node['id'] == target_id][0]

    if target_id not in grabbed_obj_ids:
        target_action = [('grab', (target_node['class_name'], target_id), None)]
        cost = [0.05]
    else:
        target_action = []
        cost = []

    if len(agent_close) > 0 and target_id in observed_ids:
        return target_action, cost
    else:
        find_actions, find_costs = find_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, object_target)
        return find_actions + target_action, find_costs + cost

def put_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, target):
    # observations = simulator.get_observations(env_graph, char_index=char_index)
    observations = simulator.get_observations()

    target_grab, target_put = [int(x) for x in target.split('_')[-2:]]

    if sum([1 for edge in observations['edges'] if edge['from_id'] == target_grab and edge['to_id'] == target_put and edge['relation_type'] == 'ON']) > 0:
        # Object has been placed
        return [], []

    if sum([1 for edge in observations['edges'] if edge['to_id'] == target_grab and edge['from_id'] != agent_id and 'HOLD' in edge['relation_type']]) > 0:
        # Object has been placed
        return None, None

    target_node = [node for node in env_graph['nodes'] if node['id'] == target_grab][0]
    target_node2 = [node for node in env_graph['nodes'] if node['id'] == target_put][0]
    id2node = {node['id']: node for node in env_graph['nodes']}
    target_grabbed = len([edge for edge in env_graph['edges'] if edge['from_id'] == agent_id and 'HOLDS' in edge['relation_type'] and edge['to_id'] == target_grab]) > 0


    object_diff_room = None
    if not target_grabbed:
        grab_obj1, cost_grab_obj1 = grab_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, 'grab_' + str(target_node['id']))
        if len(grab_obj1) > 0:
            if grab_obj1[0][0] == 'walk':
                id_room = grab_obj1[0][1][1]
                if id2node[id_room]['category'] == 'Rooms':
                    object_diff_room = id_room
        
        env_graph_new = copy.deepcopy(env_graph)
        
        if object_diff_room:
            env_graph_new['edges'] = [edge for edge in env_graph_new['edges'] if edge['to_id'] != agent_id and edge['from_id'] != agent_id]
            env_graph_new['edges'].append({'from_id': agent_id, 'to_id': object_diff_room, 'relation_type': 'INSIDE'})
        
        else:
            env_graph_new['edges'] = [edge for edge in env_graph_new['edges'] if (edge['to_id'] != agent_id and edge['from_id'] != agent_id) or edge['relation_type'] == 'INSIDE']
    else:
        env_graph_new = env_graph
        grab_obj1 = []
        cost_grab_obj1 = []
    find_obj2, cost_find_obj2 = find_heuristic(agent_id, char_index, unsatisfied, env_graph_new, simulator, 'find_' + str(target_node2['id']))
    action = [('putback', (target_node['class_name'], target_grab), (target_node2['class_name'], target_put))]
    cost = [0.05]
    res = grab_obj1 + find_obj2 + action
    cost_list = cost_grab_obj1 + cost_find_obj2 + cost

    #print(res, target)
    return res, cost_list

def putIn_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, target):
    observations = simulator.get_observations(env_graph, char_index=char_index)

    target_grab, target_put = [int(x) for x in target.split('_')[-2:]]

    if sum([1 for edge in observations['edges'] if edge['from_id'] == target_grab and edge['to_id'] == target_put and edge['relation_type'] == 'ON']) > 0:
        # Object has been placed
        return [], []

    if sum([1 for edge in observations['edges'] if edge['to_id'] == target_grab and edge['from_id'] != agent_id and 'HOLD' in edge['relation_type']]) > 0:
        # Object has been placed
        return None, None

    target_node = [node for node in env_graph['nodes'] if node['id'] == target_grab][0]
    target_node2 = [node for node in env_graph['nodes'] if node['id'] == target_put][0]
    id2node = {node['id']: node for node in env_graph['nodes']}
    target_grabbed = len([edge for edge in env_graph['edges'] if edge['from_id'] == agent_id and 'HOLDS' in edge['relation_type'] and edge['to_id'] == target_grab]) > 0


    object_diff_room = None
    if not target_grabbed:
        grab_obj1, cost_grab_obj1 = grab_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, 'grab_' + str(target_node['id']))
        if len(grab_obj1) > 0:
            if grab_obj1[0][0] == 'walk':
                id_room = grab_obj1[0][1][1]
                if id2node[id_room]['category'] == 'Rooms':
                    object_diff_room = id_room
        
        env_graph_new = copy.deepcopy(env_graph)
        
        if object_diff_room:
            env_graph_new['edges'] = [edge for edge in env_graph_new['edges'] if edge['to_id'] != agent_id and edge['from_id'] != agent_id]
            env_graph_new['edges'].append({'from_id': agent_id, 'to_id': object_diff_room, 'relation_type': 'INSIDE'})
        
        else:
            env_graph_new['edges'] = [edge for edge in env_graph_new['edges'] if (edge['to_id'] != agent_id and edge['from_id'] != agent_id) or edge['relation_type'] == 'INSIDE']
    else:
        env_graph_new = env_graph
        grab_obj1 = []
        cost_grab_obj1 = []
    find_obj2, cost_find_obj2 = find_heuristic(agent_id, char_index, unsatisfied, env_graph_new, simulator, 'find_' + str(target_node2['id']))
    target_put_state = target_node2['states']
    action_open = [('open', (target_node2['class_name'], target_put))]
    action_put = [('putin', (target_node['class_name'], target_grab), (target_node2['class_name'], target_put))]
    cost_open = [0.05]
    cost_put = [0.05]
    

    remained_to_put = 0
    for predicate, count in unsatisfied.items():
        if predicate.startswith('inside'):
            remained_to_put += count
    if remained_to_put == 1: # or agent_id > 1:
        action_close= []
        cost_close = []
    else:
        action_close = [('close', (target_node2['class_name'], target_put))]
        cost_close = [0.05]

    if 'CLOSED' in target_put_state or 'OPEN' not in target_put_state:
        res = grab_obj1 + find_obj2 + action_open + action_put + action_close
        cost_list = cost_grab_obj1 + cost_find_obj2 + cost_open + cost_put + cost_close
    else:
        res = grab_obj1 + find_obj2 + action_put + action_close
        cost_list = cost_grab_obj1 + cost_find_obj2 + cost_put + cost_close

    #print(res, target)
    return res, cost_list


def turnOn_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, object_target):
    observations = simulator.get_observations(env_graph, char_index=char_index)
    target_id = int(object_target.split('_')[-1])

    observed_ids = [node['id'] for node in observations['nodes']]
    agent_close = [edge for edge in env_graph['edges'] if ((edge['from_id'] == agent_id and edge['to_id'] == target_id) or (edge['from_id'] == target_id and edge['to_id'] == agent_id) and edge['relation_type'] == 'CLOSE')]
    grabbed_obj_ids = [edge['to_id'] for edge in env_graph['edges'] if (edge['from_id'] == agent_id and 'HOLDS' in edge['relation_type'])]

    target_node = [node for node in env_graph['nodes'] if node['id'] == target_id][0]

    if target_id not in grabbed_obj_ids:
        target_action = [('switchon', (target_node['class_name'], target_id), None)]
        cost = [0.05]
    else:
        target_action = []
        cost = []

    if len(agent_close) > 0 and target_id in observed_ids:
        return target_action, cost
    else:
        find_actions, find_costs = find_heuristic(agent_id, char_index, unsatisfied, env_graph, simulator, object_target)
        return find_actions + target_action, find_costs + cost

heuristic_dict = {
        'find': find_heuristic,
        'grab': grab_heuristic,
        'put': put_heuristic,
        'putIn': putIn_heuristic,
        # 'sit': sit_heuristic,
        'turnOn': turnOn_heuristic
    }

class StateNode:
    def __init__(self, reward=0, done=False):
        self.ob = None
        self.look = None
        self.inv = None
        self.state = None
        self.prev_action = None
        self.id = None
        self.valid_actions = None
        self.history = []
        self.parent = None
        self.parent_action_id = None
        self.best_action_node = None
        

        self.N = 0
        self.children = []
        self.children_probs = []
        self.reward = reward/(1-DISCOUNT_FACTOR)
        self.score = 0
        self.done = done
        self.predicted_reward = 0
        self.use_llm = False
        self.expand_node = False

    # def find_state_in_tree(self, target_obs):
    #     """
    #     Searches the entire tree for a state with the given observation.
    #     Utilizes DFS to traverse through all state nodes in the tree.
    #     """
    #     # Check the current state node first
    #     if self.ob == target_obs:
    #         print("-----------------------same state before !!! -------------------------")
    #         return True, self

    #     # If not found, recursively search through the children of the state node
    #     for action_node in self.children:
    #         if action_node.children:  # Ensure the action node has a child state
    #             found, state_node = action_node.children.find_state_in_tree(target_obs)
    #             if found:
    #                 print("-----------------------same state before !!! -------------------------")
    #                 return True, state_node

    #     # If the state was not found in any children, return False
    #     return False, None
    
    def find_state_in_tree(self, target_obs, visited=None):
        if visited is None:
            visited = set()

        # Mark the current node as visited
        if self.id in visited:
            return False, None
        visited.add(self.id)

        # Check if the current node matches the target observation
        if self.ob == target_obs:
            print("-----------------------same state before !!! -------------------------")
            return True, self

        # Recursively search in children nodes
        for action_node in self.children:
            if action_node.children:
                # Ensure that the child node is not already visited
                if action_node.children not in visited:
                    found, state_node = action_node.children.find_state_in_tree(target_obs, visited)
                    if found:
                        # print("-----------------------same state before !!! -------------------------")
                        return True, state_node

        # If not found in any children, return False
        return False, None








class ActionNode:
    def __init__(self, action):
        self.action = action
        self.N = 0
        self.Q = 0
        self.Q_hat = 0
        self.Rs = []
        self.children = None
        self.children_id = None


class MCTSAgent:
    def __init__(self, args, vhenv, selected_objects_id, policy=None, name='MCTS',
                uct_type='PUCT', valid_action_dict=None, actions_info=None,
                  log_dir=None, visited_transitions=None, replay_file=None):

        goal_spec = vhenv.get_goal(vhenv.task_goal[0], vhenv.agent_goals[0])
        graph = vhenv.get_graph()
        self.env = MCTSVHEnv(graph, goal_spec, vhenv.task_goal, selected_objects_id)
        print('goal spec MCTSVHEnv:', self.env.goal_spec)
        print('task goal MCTSVHEnv:', self.env.task_goal)
        self.name = name
        self.best_action_node = None
        self.uct_type = uct_type
        self.seed = 10#args.seed
        self.round = args.round
        self.root = None
        self.last_history = []
        self.selected_objects_id = selected_objects_id
        self.done = False

        self.exploration_constant = args.exploration_constant
        self.bonus_constant = args.bonus_constant
        self.max_depth = args.max_depth
        # self.max_depth_rollout = 30
        self.max_depth_rollout = 50
        self.simulation_per_act = args.simulation_per_act
        self.discount_factor = args.discount_factor
        self.visited_transitions = visited_transitions

        self.action_selection_temp = 0.1 / (self.round + 1)

        self.policy = policy
        self.actions = [] if actions_info is None else actions_info[0]
        self.actions_e = [] if actions_info is None else actions_info[1]

        self.action_values = defaultdict(set)   # Ex: {north: [3.01, 2.00, 5.01]}

        self.maxlen_obs = 150
        self.maxlen_look = 150
        self.maxlen_inv = 50
        self.maxlen_action = 12
        self.simulation_num = args.simulation_num
        self.q_network = None
        self.valid_action_dict = {} if valid_action_dict is None else valid_action_dict
        self.state_dict = {}
        self.action_embedding = {}
        self.replay_file = replay_file

        self.states_created_id = 1
        self.states_id_history = []

    def search(self, valid_actions, done=False):
        '''
        Search the best action with probs
        :return: best action
        '''
        #init_history = history.copy()
        obs = self.env.reset()
        self.root = self.build_state(obs, valid_actions, done)
        sim_steps = 0
        for _ in tqdm(range(self.simulation_num)):
            self.env.reset()
            self.last_history = []
            self.states_id_history = []
            #self.env.history = init_history.copy()
            R, root, history  = self.simulate(self.root, 0)
            sim_steps += 1
            # if self.done:  # if success, the action returned is the history
            #     return self.env.history, sim_steps
            # self.root = root
        # select best action by Q-value
        # best_action_node_idx = self.greedy_action_node(self.root, 0, 0, if_print=True)
        # # select best action by Count
        # best_action_node = self.root.children[best_action_node_idx]
        # print("best action node: ", best_action_node)
        # self.root.best_action_node = best_action_node

        # ipdb.set_trace()
        self.env.reset()
        self.last_history = []
        #self.env.history = init_history.copy()
        self.exploration_constant = 0.0
        R, root, history  = self.simulate(self.root, 0)  # the history returned here can be wrong
        
        return self.env.history, sim_steps #self.root.best_action_node.action

    @staticmethod
    def state_id(history: list):
        return ' '.join(history)

    # expand node by taking all the possible actions
    def expand_node(self, current_state_node, valid_actions, done, reward=0, prev_action='<s>'):
        current_state_node.is_expanded = True

        state = StateNode()
        # state.ob = ob
        # state.state = ob
        state.done = done
        state.reward = reward
        state.prev_action = prev_action
        # state.history = history
        # state.id = self.state_id(history)
        state.valid_actions = valid_actions

        state.children_probs = np.ones((len(state.valid_actions),)) / len(state.valid_actions)
            
        self.state_dict[state.id] = state
        for valid_action in state.valid_actions:
            if isinstance(state.valid_actions, dict):
                state.children.append(ActionNode(state.valid_actions[valid_action]))
            else:
                state.children.append(ActionNode(valid_action))

        return state

    def build_state(self, obs, valid_actions, done, reward=0, prev_action='<s>'):
        state = StateNode()
        state.ob = obs
        # state.state = ob
        state.done = done
        state.reward = reward
        state.prev_action = prev_action
        # state.history = history
        state.id = self.states_created_id
        self.states_created_id = self.states_created_id + 1
        state.valid_actions = valid_actions

        state.children_probs = np.ones((len(state.valid_actions),)) / len(state.valid_actions)
            
        self.state_dict[state.id] = state
        for valid_action in state.valid_actions:
            if isinstance(state.valid_actions, dict):
                state.children.append(ActionNode(state.valid_actions[valid_action]))
            else:
                state.children.append(ActionNode(valid_action))

        return state

    def check_wether_already_in_tree(self, new_obs, state_node):
        # only check current branch
        check_number = 0
        while state_node.parent is not None:
            check_number = check_number + 1
            print("check_wether_already_in_tree ")
            state_obs = state_node.ob
            # print(state_obs)
            if state_obs == new_obs:
                print("-----------------------same state before !!! -------------------------")
                return True, state_node
            state_node = state_node.parent
            if check_number > 100:
                return False, None
            
        
        return False, None


    def simulate(self, state_node, depth):
        if state_node.done or depth == self.max_depth:
            return 0, state_node, self.last_history

        if len(state_node.children) == 0:
            state_node.N += 1
            return 0, state_node, self.last_history

        print("SIMULATE: state_node:  child number: ", len(state_node.children), " action: ", state_node.valid_actions)
        best_action_node_idx = self.greedy_action_node(state_node, self.exploration_constant, self.bonus_constant)
        best_action_node = state_node.children[best_action_node_idx]
        rollout_next = False
        print("best action node.action: ", best_action_node.action)
        obs, reward, done, history, valid_actions = self.env.step(best_action_node.action)
        if done:
            print("done!")
            self.last_history = history
            self.done = True
            # return 0, state_node, self.last_history
            return reward, state_node, self.last_history
        print('len of self.last_history: ', len(self.last_history), 'len of history: ', len(history))
        print("valid_actions: ", valid_actions)
        # print("history: ", history)
        if len(history) > self.max_depth:
            return 0, state_node, self.last_history
        next_state_id = self.state_id(history)
        self.states_id_history.append(state_node.id)

        if best_action_node.children is not None: 
            # [To do] check whether the state is in the current tree
            #next_state_node = best_action_node.children
            # next_state_node = self.build_state(obs, valid_actions, done, reward, prev_action=best_action_node.action)
            next_state_node = best_action_node.children
            next_state_node.parent = state_node
            rollout_next = False
        else: 
            next_state_node = self.build_state(obs, valid_actions, done, reward, prev_action=best_action_node.action)
            next_state_node.parent = state_node
            state_node.children[best_action_node_idx].children = next_state_node
            state_node.children[best_action_node_idx].children_id = next_state_node.id
            rollout_next = True

        print("rollout_next: ", rollout_next)

        if rollout_next and self.exploration_constant == 0.0:
            return 0, state_node, self.last_history

        if rollout_next:
            rollout_r = []
            for _ in range(1):
                random_r = reward + self.discount_factor * self.rollout(next_state_node, 0, len(history))
                rollout_r.append(random_r)
            R = sum(rollout_r)/len(rollout_r)
        else:
            # r, next_state_node = self.simulate(next_state_node, depth+1)
            r, next_state_node, _ = self.simulate(next_state_node, 0)
            R = reward + self.discount_factor * r

        # [To do]backprogration, also change N and Q for all the parents node
        print("total reward: ", R, " reward ", reward, " len(history): ", len(history) )
        # print("reward: ", R, " state_node.N: ", state_node.N, ' state id: ', state_node.id , " best_action_node.action:",best_action_node.action )
        # print("best_action_node_idx: ", best_action_node_idx, "state_node.children[best_action_node_idx].Rs: ", state_node.children[best_action_node_idx].Rs, ' N: ',  state_node.children[best_action_node_idx].N)
        state_node.N += 1
        state_node.children[best_action_node_idx].N += 1
        state_node.children[best_action_node_idx].children = next_state_node
        state_node.children[best_action_node_idx].Rs.append(R)
        state_node.children[best_action_node_idx].Q = np.sum(np.array(state_node.children[best_action_node_idx].Rs) * utils.softmax(state_node.children[best_action_node_idx].Rs, T=10))
        state_node.best_action_node = best_action_node
        return R, state_node, self.last_history

    def max_visit_action_node(self, state_node):
        children_count = []

        for i in range(len(state_node.children)):
            child = state_node.children[i]
            children_count.append(child.N)

        children_count = children_count / np.max(children_count)
        count_based_probs = children_count ** (1/self.action_selection_temp) / (np.sum(children_count ** (1/self.action_selection_temp)))
        return np.random.choice(state_node.children, p=count_based_probs)

    def greedy_action_node(self, state_node, exploration_constant, bonus_constant, if_print=True):
        best_value = -np.inf
        best_children = []
        best_children_prob = []
        for i in range(len(state_node.children)):
            child = state_node.children[i]
            # print("i: ", i, " child node: ", state_node.children_probs)
            assert len(state_node.children_probs) == len(state_node.children), print(state_node.children_probs)
            child_prob = state_node.children_probs[i]
            
            if exploration_constant == 0:
                ucb_value = child.Q
            elif self.uct_type == 'UCT':
                ucb_value = child.Q + exploration_constant * np.sqrt(np.log(state_node.N + 1) / (child.N + 1))
                # print(child.Q, exploration_constant * np.sqrt(np.log(state_node.N + 1) / (child.N + 1)))
            elif self.uct_type == 'PUCT':
                # print(child_prob)
                ucb_value = child.Q + exploration_constant * child_prob * np.sqrt(state_node.N) / (child.N + 1)
            elif self.uct_type == 'MC-LAVE':
                if child.action in self.action_embedding.keys():
                    action_e = self.action_embedding[child.action]
                else:
                    action_e = utils.vectorize(child.action)
                    self.action_embedding[child.action] = action_e

                actions = list(self.action_values.keys())
                if child.action in actions:
                    actions.pop(actions.index(child.action))

                actions_e = []
                for a in actions:
                    actions_e.append(self.action_embedding[a])

                near_act, near_idx = utils.find_near_actions(action_e, actions, np.array(actions_e), threshold=0.8)
                if len(near_idx) == 0:
                    child.Q_hat = 0
                else:
                    near_Qs = set()
                    for a in near_act:
                        near_Qs.add(np.mean(list(self.action_values[a])))
                    near_Qs = list(near_Qs)
                    child.Q_hat = utils.softmax_value(near_Qs)

                ucb_value = child.Q \
                            + exploration_constant * np.sqrt(state_node.N + 1) / (child.N + 1) * child_prob \
                            + bonus_constant * np.sqrt(state_node.N + 1) / (child.N + 1) * child.Q_hat

            else:
                raise NotImplementedError

            if ucb_value == best_value:
                best_children.append(i)
                best_children_prob.append(child_prob)
            elif ucb_value > best_value:
                best_value = ucb_value
                best_children = [i]
                best_children_prob = [child_prob]
        if if_print:
            for c in state_node.children:
                if c.N > 0:
                    print(c.action, c.Q, c.N)
        best_children_prob = np.array(best_children_prob) / np.sum(best_children_prob)
        # [To do] if multiple has same argmax, randomly choose one
        # output_action_index = np.argmax(best_children_prob)
        # return best_children[output_action_index]
        # print("best_children_prob: ", best_children_prob)
        max_prob_indices = np.flatnonzero(best_children_prob == best_children_prob.max())
        # Randomly choose one of the indices with the maximum value
        output_action_index = np.random.choice(max_prob_indices)
        # Use the randomly chosen index to select the corresponding action
        return best_children[output_action_index]

    def rollout(self, state_node, depth, depth_traj):
        if state_node.done or depth == self.max_depth_rollout or depth_traj == self.max_depth or len(state_node.children) == 0:
            return 0

        # action_node = np.random.choice(state_node.children, 1)[0]

        # action = action_node.action
        action_index = np.random.choice(range(len(state_node.children)), 1)[0]

        action_node = state_node.children[action_index]
        action = action_node.action


        # print("possible action: ", len(state_node.children),  "rollout action: ", action)

        obs, reward, done, history, valid_actions = self.env.step(action)
        self.last_history = history

        # if self.selected_objects_id is not None:  # this means filter objects is False
        #     print("self.selected_objects_id: ", self.selected_objects_id)
        #     valid_actions = filter_valid_actions(valid_actions, self.selected_objects_id)

        if done:
            print("Done!")
            self.done = True
        next_state_id = self.state_id(history)

        if next_state_id == action_node.children_id:
            next_state_node = action_node.children
        # flag_same_state, same_state_previous = self.root.find_state_in_tree(obs)
        # if flag_same_state:
            # next_state_node = same_state_previous
        else:
            next_state_node = self.build_state(obs, valid_actions, done, reward, prev_action=action)
            next_state_node.parent = state_node
            action_node.children = next_state_node
            action_node.children_id = next_state_node.id
        
        r = reward + self.discount_factor * self.rollout(next_state_node, depth+1, depth_traj+1)

        state_node.N += 1
        state_node.children[action_index].N += 1
        state_node.children[action_index].children = next_state_node
        state_node.children[action_index].Rs.append(r)
        state_node.children[action_index].Q = np.sum(np.array(state_node.children[action_index].Rs) * utils.softmax(state_node.children[action_index].Rs, T=10))

        return r
    
    def get_action_str(self, action_tuple):
        obj_args = [x for x in list(action_tuple)[1:] if x is not None]
        objects_str = ' '.join(['<{}> ({})'.format(x[0], x[1]) for x in obj_args])
        return '[{}] {}'.format(action_tuple[0], objects_str)
    
    def get_subgoal_space(self, state, satisfied, unsatisfied, opponent_subgoal=None, verbose=0):
        """
        Get subgoal space
        Args:
            state: current state
            satisfied: satisfied predicates
            unsatisfied: # of unstatisified predicates
        Returns:
            subgoal space
        """
        """TODO: add more subgoal heuristics; currently only have (put x y)"""
        # print('get subgoal space, state:\n', state['nodes'])
        char_index = 0
        agent_id = 0
        obs = self.env.vh_pyenv._mask_state(state, char_index)
        obsed_objs = [node["id"] for node in obs["nodes"]]

        inhand_objects = []
        for edge in state['edges']:
            if edge['relation_type'].startswith('HOLDS') and \
                edge['from_id'] == agent_id:
                inhand_objects.append(edge['to_id'])
        inhand_objects_opponent = []
        for edge in state['edges']:
            if edge['relation_type'].startswith('HOLDS') and \
                edge['from_id'] == 3 - agent_id:
                inhand_objects_opponent.append(edge['to_id'])

        # if verbose:
        #     print('inhand_objects:', inhand_objects)
        #     print(state['edges'])

        id2node = {node['id']: node for node in state['nodes']}

        opponent_predicate_1 = None
        opponent_predicate_2 = None
        if opponent_subgoal is not None:
            elements = opponent_subgoal.split('_')
            if elements[0] in ['put', 'putIn']:
                obj1_class = None
                for node in state['nodes']:
                    if node['id'] == int(elements[1]):
                        obj1_class = node['class_name']
                        break
                # if obj1_class is None:
                #     opponent_subgoal = None
                # else:
                opponent_predicate_1 = '{}_{}_{}'.format('on' if elements[0] == 'put' else 'inside', obj1_class, elements[2])
                opponent_predicate_2 = '{}_{}_{}'.format('on' if elements[0] == 'put' else 'inside', elements[1], elements[2])

        subgoal_space, obsed_subgoal_space, overlapped_subgoal_space = [], [], []
        for predicate, count in unsatisfied.items():
            if count > 1 or count > 0 and predicate not in [opponent_predicate_1, opponent_predicate_2]:
                elements = predicate.split('_')
                # print(elements)
                if elements[0] == 'on':
                    subgoal_type = 'put'
                    obj = elements[1]
                    surface = elements[2] # assuming it is a graph node id
                    print("obj: ", obj, " surface: ", surface)
                    for node in state['nodes']:
                        if node['class_name'] == obj or str(node['id']) == obj:
                            print(node)
                            # if verbose:
                            #     print(node)
                            tmp_predicate = 'on_{}_{}'.format(node['id'], surface) 
                            print("tmp_predicate: ", tmp_predicate)
                            # ipdb.set_trace()
                            if tmp_predicate not in satisfied[predicate]:
                            # if True:
                                tmp_subgoal = '{}_{}_{}'.format(subgoal_type, node['id'], surface)
                                if tmp_subgoal != opponent_subgoal:
                                    subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])
                                    if node['id'] in obsed_objs:
                                        obsed_subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])
                                    if node['id'] in inhand_objects:
                                        return [subgoal_space[-1]]
                elif elements[0] == 'inside':
                    subgoal_type = 'putIn'
                    obj = elements[1]
                    surface = elements[2] # assuming it is a graph node id
                    for node in state['nodes']:
                        if node['class_name'] == obj or str(node['id']) == obj:
                            # if verbose:
                            #     print(node)
                            tmp_predicate = 'inside_{}_{}'.format(node['id'], surface) 
                            if tmp_predicate not in satisfied[predicate]:
                                tmp_subgoal = '{}_{}_{}'.format(subgoal_type, node['id'], surface)
                                if tmp_subgoal != opponent_subgoal:
                                    subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])
                                    if node['id'] in obsed_objs:
                                        obsed_subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])
                                    if node['id'] in inhand_objects:
                                        return [subgoal_space[-1]]
                elif elements[0] == 'offOn':
                    if id2node[elements[2]]['class_name'] in ['dishwasher', 'kitchentable']:
                        containers = [[node['id'], node['class_name']] for node in state['nodes'] if node['class_name'] in ['kitchencabinets', 'kitchencounterdrawer', 'kitchencounter']]
                    else:
                        containers = [[node['id'], node['class_name']] for node in state['nodes'] if node['class_name'] == 'coffetable']
                    for edge in state['edges']:
                        if edge['relation_type'] == 'ON' and edge['to_id'] == int(elements[2]) and id2node[edge['from_id']]['class_name'] == elements[1]:
                            container = random.choice(containers)
                            predicate = '{}_{}_{}'.format('on' if container[1] == 'kitchencounter' else 'inside', edge['from_id'], container[0])
                            goals[predicate] = 1
                elif elements[0] == 'offInside':
                    if id2node[elements[2]]['class_name'] in ['dishwasher', 'kitchentable']:
                        containers = [[node['id'], node['class_name']] for node in state['nodes'] if node['class_name'] in ['kitchencabinets', 'kitchencounterdrawer', 'kitchencounter']]
                    else:
                        containers = [[node['id'], node['class_name']] for node in state['nodes'] if node['class_name'] == 'coffetable']
                    for edge in state['edges']:
                        if edge['relation_type'] == 'INSIDE' and edge['to_id'] == int(elements[2]) and id2node[edge['from_id']]['class_name'] == elements[1]:
                            container = random.choice(containers)
                            predicate = '{}_{}_{}'.format('on' if container[1] == 'kitchencounter' else 'inside', edge['from_id'], container[0])
                            goals[predicate] = 1
            elif predicate in [opponent_predicate_1, opponent_predicate_2] and len(inhand_objects_opponent) == 0:
                elements = predicate.split('_')
                # print(elements)
                if elements[0] == 'on':
                    subgoal_type = 'put'
                    obj = elements[1]
                    surface = elements[2] # assuming it is a graph node id
                    for node in state['nodes']:
                        if node['class_name'] == obj or str(node['id']) == obj:
                            tmp_predicate = 'on_{}_{}'.format(node['id'], surface) 
                            if tmp_predicate not in satisfied[predicate]:
                                tmp_subgoal = '{}_{}_{}'.format(subgoal_type, node['id'], surface)
                                overlapped_subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])                        
                elif elements[0] == 'inside':
                    subgoal_type = 'putIn'
                    obj = elements[1]
                    surface = elements[2] # assuming it is a graph node id
                    for node in state['nodes']:
                        if node['class_name'] == obj or str(node['id']) == obj:
                            tmp_predicate = 'inside_{}_{}'.format(node['id'], surface) 
                            if tmp_predicate not in satisfied[predicate]:
                                tmp_subgoal = '{}_{}_{}'.format(subgoal_type, node['id'], surface)
                                overlapped_subgoal_space.append(['{}_{}_{}'.format(subgoal_type, node['id'], surface), predicate, tmp_predicate])
                                    
        if len(obsed_subgoal_space) > 0:
            return obsed_subgoal_space
        if len(subgoal_space) == 0:
            # if agent_id == 2 and verbose == 1:
            #     ipdb.set_trace()
            if len(overlapped_subgoal_space) > 0:
                return overlapped_subgoal_space
            for predicate, count in unsatisfied.items():
                if count == 1:
                    elements = predicate.split('_')
                    # print(elements)
                    if elements[0] == 'turnOn':
                        subgoal_type = 'turnOn'
                        obj = elements[1]
                        for node in state['nodes']:
                            if node['class_name'] == obj or str(node['id']) == obj:
                                # print(node)
                                # if verbose:
                                #     print(node)
                                tmp_predicate = 'turnOn{}_{}'.format(node['id'], 1) 
                                if tmp_predicate not in satisfied[predicate]:
                                    subgoal_space.append(['{}_{}'.format(subgoal_type, node['id']), predicate, tmp_predicate])
        if len(subgoal_space) == 0:
            for predicate, count in unsatisfied.items():
                if count == 1:
                    elements = predicate.split('_')
                    # print(elements)
                    if elements[0] == 'holds' and int(elements[2]) == agent_id:
                        subgoal_type = 'grab'
                        obj = elements[1]
                        for node in state['nodes']:
                            if node['class_name'] == obj or str(node['id']) == obj:
                                # print(node)
                                # if verbose:
                                #     print(node)
                                tmp_predicate = 'holds_{}_{}'.format(node['id'], 1) 
                                if tmp_predicate not in satisfied[predicate]:
                                    subgoal_space.append(['{}_{}'.format(subgoal_type, node['id']), predicate, tmp_predicate])
        if len(subgoal_space) == 0:
            for predicate, count in unsatisfied.items():
                if count == 1:
                    elements = predicate.split('_')
                    # print(elements)
                    if elements[0] == 'sit' and int(elements[1]) == agent_id:
                        subgoal_type = 'sit'
                        obj = elements[2]
                        for node in state['nodes']:
                            if node['class_name'] == obj or str(node['id']) == obj:
                                # print(node)
                                # if verbose:
                                #     print(node)
                                tmp_predicate = 'sit_{}_{}'.format(1, node['id']) 
                                if tmp_predicate not in satisfied[predicate]:
                                    subgoal_space.append(['{}_{}'.format(subgoal_type, node['id']), predicate, tmp_predicate])

        return subgoal_space
