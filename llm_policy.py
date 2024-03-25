import json
from openai import OpenAI
client = OpenAI()  # loads api key from environment variable

# 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

class LLMPolicy:
    def __init__(self, goal_language, perturbations=False):
        self.role_system_content = """
        Your job is to solve a high-level decision-making problem. To do this, a goal is going to be given to you. This
        goal represents the state of the environment that must be reached in order to successfully solve the task. 
        You will do this step-by-step, which means that at every interaction with the user you are going to be given 
        the current state of the environment, the previously taken actions, and the set of valid actions that you can 
        take for that state. Note that in the state representation, objects have a number in the form '(id)' next to 
        their names. This number is an id that identifies each object. Hence, if there are, for example, multiple 
        glasses, each different glass is going to have a different id. 
        
        At each time step, you must select the action (one) that you believe will make the environment transition to a 
        state closer to that of the goal.
        
        You will receive a list of valid actions with a specific format, you must keep that format when you select an
        action, i.e., '[action] <object> (id)'. Moreover, the action that you select must be available in list of valid 
        actions you receive.
        
        The previously taken action describe the actions you have already executed in previous time steps. Hence, they
        describe the progress you've made so far, and you must consider it when making decisions.
        
        Do a bit of reasoning before generating an action.
        
        Once you are done, you are allowed to, and must, generate the action 'Finished!', instead of using an action 
        from the valid actions list.
        
        IMPORTANT 1: Do not generate an action that is not contained in the list of valid actions. Otherwise, the agent
        will fail.
        
        IMPORTANT 2: Follow your instructions carefully.
        """

        if perturbations:
            important_3 = """IMPORTANT 3: there are external agents that you can't control that are able to modify the 
            environment as well. Be aware of the external agent's perturbations, as you need to take them into account to 
            analyze how its actions influence your progress towards finishing the task. You might need to replan according 
            to these perturbations.
            """

            self.role_system_content += important_3

        # Append goal to content
        self.role_system_content += '\n' + goal_language + '\n'

        # Init variables
        self.messages = [{"role": "system", "content": self.role_system_content}]
        self.previously_taken_actions = []
        self.action_count = 0
        self.temperature = 0.01

    def get_llm_state(self, obs, selected_objects_id, selected_objects_names):
        state_llm = []

        # Get edges, i.e., relationships between objects
        for edge in obs[0]['edges']:
            from_id = edge['from_id']
            to_id = edge['to_id']

            # Get relationships between inanimate selected objects
            if from_id in selected_objects_id and to_id in selected_objects_id:
                index_from_id = selected_objects_id.index(from_id)
                index_to_id = selected_objects_id.index(to_id)
                edge_with_names = selected_objects_names[index_from_id] + ' (%i) ' % from_id + \
                                  edge['relation_type'].lower() + ' ' + selected_objects_names[
                                      index_to_id] + ' (%i) ' % to_id
                state_llm.append(edge_with_names)

            # Get relationships between selected objects and agent
            if from_id == 1:
                for node in obs[0]['nodes']:
                    if node['id'] == to_id:
                        name = node['class_name']
                        break

                edge_with_names = 'agent ' + edge['relation_type'].lower() + ' ' + name + ' (%i) ' % to_id
                state_llm.append(edge_with_names)

        # Get states of nodes, i.e., features of independent objects
        for node in obs[0]['nodes']:
            if node['id'] in selected_objects_id:
                state_independent = node['states']
                for state in state_independent:
                    state_language = node['class_name'] + ' (%i) is ' % node['id'] + state.lower()
                    state_llm.append(state_language)

        # Create string and postprocess a bit
        state_llm = json.dumps(state_llm)
        state_llm = state_llm.replace('"', '').replace('[', '')  # remove unnecessary characters
        state_llm = state_llm.replace('close ', 'is close to the ').replace('inside', 'is inside the').replace(' on ', ' is on the ')
        return state_llm

    def act(self, observation, valid_actions, LLM_model, use_chat_history=False, max_trials=4):
        # Create language state
        state_llm = 'State: ' + observation

        # Create language actions
        valid_actions_llm = 'Valid actions (you must select an action from this list!) Only exception is to output ' \
                            'Finished! when you are done with the task): ' + json.dumps(valid_actions)

        # Create language list of previously taken actions
        previously_taken_actions_llm = 'Previously taken actions (from oldest to newest): ' + json.dumps(self.previously_taken_actions)
        previously_taken_actions_llm = previously_taken_actions_llm.replace('"', '').replace('[', '').replace(']', '')

        # Put everything together to create message content
        content = previously_taken_actions_llm + '\n' + state_llm + '\n' + valid_actions_llm + '\n Please select one action.'

        if use_chat_history:
            # Append content to message content
            self.messages.append({"role": "user", "content": content})
        else:
            # Create message only using current message content
            self.messages = [{"role": "system", "content": self.role_system_content},
                             {"role": "user", "content": content}]

        selected_action, response_message = None, None
        trial = 0
        done = False
        while trial < max_trials:
            # Get response from LLM
            response = client.chat.completions.create(
                model=LLM_model,
                messages=self.messages,
                temperature=self.temperature
            )

            response_message = response.choices[0].message

            # Append response to chat history
            self.messages.append(response_message)

            # Select action only if it belongs to the list of possible actions
            valid_actions.append('Finished!')
            for valid_action in valid_actions:
                if valid_action in response_message.content:
                    selected_action = valid_action
                    done = True
                    break

            # If action valid, break
            if done:
                break

            # If LLM outputs non-valid action
            print('Not valid action selected!')
            print(response_message)
            not_valid_message = 'The selected action is not contained in the most updated version of the valid actions ' \
                                'list, or you are using the wrong format to request an action (format: [action] <object> (id)). ' \
                                'Please take this into consideration and try again.'

            # Append not valid message to ask LLM again
            self.messages.append({"role": "user", "content": not_valid_message})

            # Add counter trial
            trial += 1

            if trial == max_trials:
                selected_action = 'Finished!'
        self.action_count += 1
        self.previously_taken_actions.append(str(self.action_count) + ') ' + selected_action)

        return selected_action, response_message
