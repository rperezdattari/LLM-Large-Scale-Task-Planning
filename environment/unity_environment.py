import environment.utils_environment as utils
from virtualhome.simulation.environment.unity_environment import UnityEnvironment as BaseUnityEnvironment
from virtualhome.simulation.evolving_graph import utils as utils_env
import pdb
import ipdb
import numpy as np
import json
import copy
from utils import add_beer

with open('environment/info/object_info.json') as f:
    object_info = json.load(f)


class UnityEnvironment(BaseUnityEnvironment):
    def __init__(self,
                 num_agents=2,
                 max_episode_length=300,
                 env_task_set=None,
                 observation_types=None,
                 agent_goals=None,
                 use_editor=False,
                 base_port=8080,
                 port_id=0,
                 task_goal=None,
                 executable_args={},
                 recording_options={'recording': True,
                    'output_folder': 'Output/',
                    'file_name_prefix': 'data',
                    'cameras': 'PERSON_FROM_BACK',
                    'modality': 'normal'},
                 seed=13):

        if agent_goals is not None:
            self.agent_goals = agent_goals
        else:
            self.agent_goals = ['full' for _ in range(num_agents)]
        
        self.task_goal = task_goal
        self.goal_spec = {0: {}}
        self.env_task_set = env_task_set
        super(UnityEnvironment, self).__init__(
            num_agents=num_agents,
            max_episode_length=max_episode_length,
            observation_types=observation_types,
            use_editor=use_editor,
            base_port=base_port,
            port_id=port_id,
            executable_args=executable_args,
            recording_options=recording_options,
            seed=seed
            )
        self.recording_options = recording_options
        self.full_graph = None

        self.rewarded_counts = {}  # Initialize in your environment's constructor

    def get_graph(self):
        graph = super().get_graph()
        return graph

    def add_beers(self):
        graph = super().get_graph()
        graph = add_beer(graph, id=1001)
        graph = add_beer(graph, id=1002)
        return graph

    # def reward(self):
    #     reward = 0.
    #     done = True
    #     #satisfied, unsatisfied = utils.check_progress(self.get_graph(), self.goal_spec[0])
    #     satisfied, unsatisfied = utils.check_progress(self.get_graph(), self.goal_spec)
    #     for key, value in satisfied.items():
    #         #preds_needed, mandatory, reward_per_pred = self.goal_spec[0][key]
    #         preds_needed, mandatory, reward_per_pred = self.goal_spec[key]
    #         # How many predicates achieved
    #         value_pred = min(len(value), preds_needed)
    #         reward += value_pred * reward_per_pred
    #         if mandatory and unsatisfied[key] > 0:
    #             done = False

    #     self.prev_reward = reward
    #     return reward, done, {'satisfied_goals': satisfied}

    def reward(self):
        reward = 0.0
        done = True  # Start by assuming the task is completed.

        # Fetch progress towards the goal specification.
        satisfied, unsatisfied = utils.check_progress(self.get_graph(), self.goal_spec)
        
        # Iterate through each goal in the specification.
        for key, values in satisfied.items():
            preds_needed, mandatory, reward_per_pred = self.goal_spec[key]

            # Initialize the count for this predicate if not already tracked
            if key not in self.rewarded_counts:
                self.rewarded_counts[key] = 0

            # Determine the number of new predicate achievements to reward
            current_count = len(values)
            already_rewarded = self.rewarded_counts[key]
            rewardable = min(current_count, preds_needed) - already_rewarded
            print("key: ", key, " already_rewarded: ", already_rewarded, " rewardable: ", rewardable)

            if rewardable > 0:
                reward += rewardable * reward_per_pred
                # Update the count of rewarded instances for this predicate
                self.rewarded_counts[key] += rewardable

            # If there are mandatory predicates that are unsatisfied, the task is not done.
            if mandatory and unsatisfied[key] > 0:
                done = False

        self.prev_reward = reward  # Store the current reward.
        print("reward: ", reward)
        # Return the reward, the done status, and a dictionary detailing the satisfied goals.
        return reward, done, {'satisfied_goals': satisfied}


    def get_goal(self, task_spec, agent_goal):
        if agent_goal == 'full':
            pred = [x for x, y in task_spec.items() if y > 0 and x.split('_')[0] in ['on', 'inside']]
            # object_grab = [pr.split('_')[1] for pr in pred]
            # predicates_grab = {'holds_{}_1'.format(obj_gr): [1, False, 2] for obj_gr in object_grab}
            res_dict = {goal_k: [goal_c, True, 2] for goal_k, goal_c in task_spec.items()}
            # res_dict.update(predicates_grab)
            # print(res_dict)
            return res_dict
        elif agent_goal == 'grab':
            candidates = [x.split('_')[1] for x,y in task_spec.items() if y > 0 and x.split('_')[0] in ['on', 'inside']]
            object_grab = self.rnd.choice(candidates)
            # print('GOAL', candidates, object_grab)
            return {'holds_'+object_grab+'_'+'1': [1, True, 10], 'close_'+object_grab+'_'+'1': [1, False, 0.1]}
        elif agent_goal == 'put':
            pred = self.rnd.choice([x for x, y in task_spec.items() if y > 0 and x.split('_')[0] in ['on', 'inside']])
            object_grab = pred.split('_')[1]
            return {
                pred: [1, True, 60],
                'holds_' + object_grab + '_' + '1': [1, False, 2],
                'close_' + object_grab + '_' + '1': [1, False, 0.05]

            }
        else:
            raise NotImplementedError

    def reset(self, environment_graph=None, env_id=None, add_character=True, init_graph=None, task_id=None, task_goal=None):

        # Make sure that characters are out of graph, and ids are ok
        # ipdb.set_trace()
        # if task_id is None:
        #     # task_id = random.choice(list(range(len(self.env_task_set))))
        #     task_id = self.rnd.choice(list(range(len(self.env_task_set))))
        # env_task = self.env_task_set[task_id]

        self.rewarded_counts = {}  # Initialize in your environment's constructor

        self.task_id = task_id
        self.init_graph = copy.deepcopy(init_graph)
        self.init_rooms = ['bedroom', 'kitchen']
        # if task_goal is None:
        #     self.task_goal = env_task['task_goal']
        # else:
        #     self.task_goal = task_goal
        #self.task_goal = task_goal
        # print(self.task_goal)

        #self.task_name = env_task['task_name']

        old_env_id = self.env_id
        self.env_id = env_id#env_task['env_id']
        #print("Resetting... Envid: {}. Taskid: {}. Index: {}".format(self.env_id, self.task_id, task_id))

        # TODO: in the future we may want different goals
        self.goal_spec = self.get_goal(self.task_goal[0], self.agent_goals[0])
        # self.goal_spec = {agent_id: self.get_goal(self.task_goal, self.agent_goals[agent_id])
        #                   for agent_id in range(self.num_agents)}
        # self.goal_spec = {agent_id: self.get_goal(self.task_goal[agent_id], self.agent_goals[agent_id])
        #                   for agent_id in range(self.num_agents)}
        
        #if False: # old_env_id == self.env_id:
        if env_id is not None:
            #print("Fast reset")
            self.comm.reset(env_id)
            #self.comm.fast_reset()
        else:
            #self.comm.reset(self.env_id)
            self.comm.reset(0)

        s,g = self.comm.environment_graph()
        edge_ids = set([edge['to_id'] for edge in g['edges']] + [edge['from_id'] for edge in g['edges']])
        node_ids = set([node['id'] for node in g['nodes']])
        if len(edge_ids - node_ids) > 0:
            pdb.set_trace()

        if self.env_id not in self.max_ids.keys():
            max_id = max([node['id'] for node in g['nodes']])
            self.max_ids[self.env_id] = max_id

        max_id = self.max_ids[self.env_id]

        if environment_graph is not None:
            updated_graph = environment_graph
            s, g = self.comm.environment_graph()
            updated_graph = utils.separate_new_ids_graph(updated_graph, max_id)
            success, m = self.comm.expand_scene(updated_graph)
        else:
            success = True

        if not success:
            ipdb.set_trace()
            print("Error expanding scene")
            ipdb.set_trace()
            return None
        
        self.offset_cameras = self.comm.camera_count()[1]
        # if self.init_rooms[0] not in ['kitchen', 'bedroom', 'livingroom', 'bathroom']:
        #     rooms = self.rnd.sample(['kitchen', 'bedroom', 'livingroom', 'bathroom'], 2)
        # else:
        #     rooms = list(self.init_rooms)

        rooms = ['kitchen', 'bedroom', 'livingroom', 'bathroom']
        if add_character:
            for i in range(self.num_agents):
                if i in self.agent_info:
                    self.comm.add_character(self.agent_info[i], initial_room=rooms[i])
                else:
                    self.comm.add_character()

        _, self.init_unity_graph = self.comm.environment_graph()

        self.changed_graph = True
        graph = self.get_graph()

        self.rooms = [(node['class_name'], node['id']) for node in graph['nodes'] if node['category'] == 'Rooms']
        self.id2node = {node['id']: node for node in graph['nodes']}

        obs = self.get_observations()
        self.steps = 0
        self.prev_reward = 0.
        return obs

    def step(self, action_dict):
        script_list = utils.convert_action(action_dict)
        failed_execution = False
        success, message = self.comm.render_script(script_list, recording=True, frame_rate=10)

        if not success:
            print("NO SUCCESS")
            print(message, script_list)
            failed_execution = True
        else:
            self.changed_graph = True

        # Obtain reward
        reward, done, info = self.reward()

        graph = self.get_graph()
        self.steps += 1
        
        obs = self.get_observations()

        info['finished'] = done
        info['graph'] = graph
        info['failed_exec'] = failed_execution
        if self.steps == self.max_episode_length:
            done = True
        return obs, reward, done, info, success

    def get_observation(self, agent_id, info={}):
        if self.observation_types[0] == 'partial':
            # agent 0 has id (0 + 1)
            curr_graph = self.get_graph()
            curr_graph = utils.inside_not_trans(curr_graph)
            self.full_graph = curr_graph
            obs = utils_env.get_visible_nodes(curr_graph, agent_id=(agent_id+1))
            return obs

        elif self.observation_types[0] == 'full':
            # curr_graph = self.get_graph()
            # curr_graph = utils.inside_not_trans(curr_graph)
            # self.full_graph = curr_graph
            self.full_graph = self.get_graph()
	
            return self.full_graph

        elif self.observation_types[0] == 'visible':
            # Only objects in the field of view of the agent
            raise NotImplementedError

        elif self.observation_types[0] == 'image':
            camera_ids = [self.num_static_cameras + agent_id * self.num_camera_per_agent + self.CAMERA_NUM]
            if 'image_width' in info:
                image_width = info['image_width']
                image_height = info['image_height']
            else:
                image_width, image_height = self.default_image_width, self.default_image_height

            s, images = self.comm.camera_image(camera_ids, mode=self.observation_types[0], image_width=image_width, image_height=image_height)
            if not s:
                pdb.set_trace()
            return images[0]
        else:
            raise NotImplementedError

        return updated_graph

    def parse_language_from_goal_script(self, goal_script, goal_num, init_graph, template=0):
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
            pdb.set_trace()
        goal_language = goal_language.lower()
        return goal_language

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

    def get_goal_language(self):
        goal = self.task_goal[0]
        task_goal_languages = [self.parse_language_from_goal_script(subgoal, subgoal_count, self.init_graph, template=0) for subgoal, subgoal_count in goal.items()]
        task_goal = 'Goal: ' + ', '.join(task_goal_languages) + '.'
        return task_goal
