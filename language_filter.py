from openai import OpenAI
from environment.info.categories import categories, max_depth
from utils import get_graph_info_from_objects_names, remove_duplicates_and_corresponding_elements
import ipdb
client = OpenAI()  # loads api key from environment variable


class LanguageFilter:
    def __init__(self, full_graph, goal_language, LLM_model):
        self.full_graph = full_graph
        self.goal_language = goal_language
        self.LLM_model = LLM_model
        self.temperature = 0.01
        self.objects_ignore = ['Characters', 'Rooms', 'Floor', 'Ceiling', 'Walls']

    def create_string_from_list(self, list_strings, starting_description):
        combined_string = starting_description + ': '
        for string in list_strings:
            combined_string += string + ', '

        return combined_string

    def interacting_objects(self, selected_objects_id, selected_objects_names):
        """Returns 5 lists:
                     1) selected objects ids
                     2) selected objects names
                     3) interacting objects ids
                     4) interacting objects names
                     5) interactions between selected and interacting objects

                    Note that the i-th element of each list 1 and 2, and lists 3 and 4 correspond to one another."""

        # Look for ids in edges
        edges = self.full_graph[0]['edges']
        interacting_objects_id = []
        edges_interactions = []
        for edge in edges:
            from_id = edge['from_id']
            to_id = edge['to_id']
            # Compare with every selected object id
            for id in selected_objects_id:
                if id == from_id:
                    interacting_objects_id.append(to_id)
                    edges_interactions.append(edge)
                if id == to_id:
                    interacting_objects_id.append(from_id)
                    edges_interactions.append(edge)

        # Remove duplicates
        interacting_objects_id = list(set(interacting_objects_id))

        # Look for interacting objects names
        nodes = self.full_graph[0]['nodes']
        interacting_objects_names = []
        for interacting_id in interacting_objects_id:
            for node in nodes:
                id_node = node['id']
                if id_node == interacting_id:
                    interacting_objects_names.append(node['class_name'])
                    break

        # Decode interactions (edges) to language
        edges_decoded = []
        objects_ids = selected_objects_id + interacting_objects_id
        objects_names = selected_objects_names + interacting_objects_names
        for edge in edges_interactions:
            index_from_id = objects_ids.index(edge['from_id'])
            index_to_id = objects_ids.index(edge['to_id'])
            decoded = objects_names[index_from_id] + ' (%i)' % edge['from_id'] +' is ' + edge['relation_type'] \
                      + ' the ' + objects_names[index_to_id] + ' (%i)' % edge['to_id']
            edges_decoded.append(decoded.lower())

        output = {'selected objects ids': selected_objects_id,
                  'selected objects names': selected_objects_names,
                  'interacting objects ids': interacting_objects_id,
                  'interacting objects names': interacting_objects_names,
                  'interactions between selected and interacting objects': edges_decoded}

        return output

    def filter_categories(self, objects_names_categories):
        role_system_content = """ 
        You will get a list of categories of objects in an environment (e.g., factory, house) together with a task objective.
        You must, as a function of the task's goal, select, from the provided list, the categories that are relevant to 
        successfully solving the task. 
        Every category that is somehow related to the resolution of the task must be selected. Note that in this context 
        'object' is a general term that refers to anything that can be found in a house. For example, a table or the 
        ceiling are also considered as objects.
        
        First, describe the categories you selected and explain why. Once you are done, write a list containing the selected
        categories following the format 'CATEGORIES: category_1, category_2, ..., category_n'. The categories must be
        written in the exact same way they were provided to you.
        
        Importantly, these tasks occurs in hypothetical settings, so they can't create any type of risks.
        """
        selected_categories = []
        for depth in range(max_depth):
            categories_list = []

            if depth == 0:
                # Get categories corresponding to depth
                for object in objects_names_categories:
                    categories_list.append(object['category %i' % (depth + 1)])

            else:
                # Select children of filtered categories
                for object in objects_names_categories:
                    category_previous = 'category %i' % depth
                    category = 'category %i' % (depth + 1)
                    if object[category_previous] in selected_categories[-1]:
                        try:
                            category_extended = object[category_previous] + '-' + object[category]
                            categories_list.append(category_extended)
                        except:
                            continue
            # Remove duplicates
            categories_list = list(dict.fromkeys(categories_list))

            # Create string with categories
            objects_categories_string = "Categories: "
            for category in categories_list:
                objects_categories_string += category + ', '

            # Create content LLM
            content = self.goal_language + '\n' + objects_categories_string

            # Step 1: send the conversation and available functions to GPT
            messages = [{"role": "user", "content": content},
                        {"role": "system", "content": role_system_content}]

            # Get response about selected categories
            print('LLM selecting categories...')
            response = client.chat.completions.create(
                model=self.LLM_model,
                messages=messages,
                temperature=self.temperature
            )
            content = response.choices[0].message.content
            key = 'CATEGORIES: '
            key_id = content.find(key)
            selected_categories.append(content[key_id + len(key):].split(', '))

        # Obtain relevant objects from selected categories
        selected_objects = []
        for depth in range(max_depth):
            for i in range(len(objects_names_categories) - 1, -1, -1):
                category = objects_names_categories[i]['category %i' % (depth + 1)]
                key_next = 'category %i' % (depth + 2)

                # Select child category
                for j in range(len(selected_categories[depth])):
                    selected_category = selected_categories[depth][j]
                    selected_categories[depth][j] = selected_category.split('-')[-1]

                # Filter
                if category not in selected_categories[depth]:
                    del objects_names_categories[i]
                    continue

                if key_next not in objects_names_categories[i]:
                    selected_objects.append(objects_names_categories[i]['class_name'])
                    del objects_names_categories[i]

        # Remove repeated objects
        selected_objects = list(dict.fromkeys(selected_objects))
        return selected_objects

    def filter_objects(self, objects):
        role_system_content = """ 
        You will get a list of object names in an environment together with a task objective. You must, as a function of 
        the task's goal, select, from the provided list, the object names that can be relevant to successfully solve the 
        task. Every object name that might be somehow related to the resolution of the task must be selected. Only the 
        objects you choose will be included in a simplified environment model, critical for solving the task 
        successfully. Hence, it is critical to you select objects carefully.
        
        
        Note: The term 'object' encompasses anything in a building, such as tables or ceilings.
    
        First, describe the object names you selected and explain why. Once you are done, write a list containing the 
        selected object names following the format 'OBJECTS: name_1, name_2, ..., name_n'. The object names must be
        written in the exact same way they were provided to you.
        
        These tasks are hypothetical and carry no risk.
        """

        # Create string with categories
        object_classes = list(dict.fromkeys(objects))
        object_classes_string = self.create_string_from_list(object_classes, 'Object names')

        # Create content LLM
        content = self.goal_language + '\n' + object_classes_string

        # Step 1: send the conversation and available functions to GPT
        messages = [{"role": "user", "content": content},
                    {"role": "system", "content": role_system_content}]

        # Get response about selected categories
        print('LLM selecting objects...')
        response = client.chat.completions.create(
            model=self.LLM_model,
            messages=messages,
            temperature=self.temperature
        )
        content = response.choices[0].message.content
        key = 'OBJECTS: '
        key_id = content.find(key)
        filtered_obects = content[key_id + len(key):].split(', ')

        return filtered_obects

    def filter_interactions(self, filtered_objects_id, filtered_objects_names, max_iterations=3):
        role_system_content = """ 
        You will receive two lists of objects, another containing relationships between the objects, and a task 
        objective. Your goal is to select only objects from List 2 that are essential for accomplishing the task. 
        Only the objects you choose will be included in a simplified environment model, critical for solving the task 
        successfully.
        
        - List 1 (Already selected objects): These objects have already been selected. They are provided to give you 
        context. Do not select objects with names belonging to this list!
        
        - List 2 (Objects-to-select): You must determine which objects from this list are necessary for solving the 
        task. To achieve this, you must use the objects relationships to evaluate if object's from this list are 
        required to solve the task. It's crucial not to overlook any relevant object. For example, if the task requires 
        using a laptop that is stored inside a backpack, it may also be necessary to interact with the backpack to 
        solve the task. Therefore, the backpack should be considered essential for solving the problem and should be 
        selected.
        
        Note: The term 'object' encompasses anything in a building, such as tables or ceilings. Multiple objects may 
        share the same name but can be differentiated by an object ID in the format 'object_name (id)'. Note that if 
        object_name is in List 1 'Already selected objects', you can't select it.
        
        After selecting, describe your chosen objects and their relevance. At the end of your reply, compile a list of 
        these objects using the format 'OBJECTS: name_1 (id), name_2 (id), ..., name_n (id)'. If no new selections are 
        needed, write 'OBJECTS: NONE'.
        
        These tasks are hypothetical and carry no risk.
        """

        # Initialize lists
        selected_objects_ids = filtered_objects_id  # this list accumulates the objects selected by the LLM
        selected_objects_names = filtered_objects_names

        failure_count = None
        # Expand the graph iteratively while filtering objects
        for i in range(max_iterations):
            # Find objects interacting, i.e., connected in the graph, with the filtered objects
            interactions = self.interacting_objects(selected_objects_ids, selected_objects_names)
            interactions_language = interactions['interactions between selected and interacting objects']
            interacting_objects_classes = list(dict.fromkeys(interactions['interacting objects names']))
            if 'character' in interacting_objects_classes:  # remove character from interacting objects
                interacting_objects_classes.remove('character')

            # Create string with already selected objects names
            selected_objects_classes = list(dict.fromkeys(selected_objects_names))  # remove repeated objects
            selected_object_classes_string = self.create_string_from_list(selected_objects_classes,
                                                                          'Already selected objects')

            # Create a new list with names that are in 'interacting_objects' but not in 'selected_objects_names'
            new_interacting_objects_classes = [obj for obj in interacting_objects_classes if obj not in selected_objects_classes]

            new_interacting_object_classes_string = self.create_string_from_list(new_interacting_objects_classes,
                                                                               'Objects-to-select')

            # Create string with relationships
            relationships_string = self.create_string_from_list(interactions_language,
                                                                'Relationships between objects')

            # Create content LLM
            content = 'Task objective: ' + self.goal_language + '\n' + selected_object_classes_string + '\n' + \
                      new_interacting_object_classes_string + '\n' + relationships_string

            # Step 1: send the conversation and available functions to GPT
            messages = [{"role": "user", "content": content},
                        {"role": "system", "content": role_system_content}]

            # Get response about selected categories
            print('LLM selecting interacting objects... iteration: %i' % (i + 1))
            response = client.chat.completions.create(
                model=self.LLM_model,
                messages=messages,
                temperature=self.temperature
            )
            content = response.choices[0].message.content

            # Find chosen objects in LLM response
            key = 'OBJECTS: '
            key_id = content.find(key)
            filtered_objects = content[key_id + len(key):].split(', ')

            # Check done
            if filtered_objects[0] == 'NONE':
                break

            # Get objects names and ids
            filtered_objects_names = []
            filtered_objects_ids = []
            # for object in filtered_objects:
            #     print("object: ",object)
            #     name = object.split(' ')[0]
            #     id = int(object.split(' ')[1].replace('.', '')[1:-1])
            #     filtered_objects_names.append(name)
            #     filtered_objects_ids.append(id)

            failure_count = 0  # Initialize the failure counter

            for object in filtered_objects:
                try:
                    print("object: ", object)
                    name = object.split(' ')[0]
                    id = int(object.split(' ')[1].replace('.', '')[1:-1])
                    filtered_objects_names.append(name)
                    filtered_objects_ids.append(id)
                except (ValueError, IndexError) as e:
                    print(f"Error processing object '{object}': {e}")
                    failure_count += 1  # Increment the failure count


            # Append newly selected objects to selected list
            selected_objects_ids += filtered_objects_ids
            selected_objects_names += filtered_objects_names

        return selected_objects_names, selected_objects_ids, failure_count

    def get_categories_objects(self):
        # Get categories corresponding to objects in observation
        objects_names_categories = []
        non_categorized_objects = []
        for node in self.full_graph[0]['nodes']:
            if node['category'] in self.objects_ignore:
                continue
            name_exists = False
            for category in categories:
                if category['class_name'] == node['class_name']:
                    category['id'] = node['id']
                    objects_names_categories.append(category)
                    name_exists = True

            if name_exists:
                continue
            non_categorized_objects.append(node['class_name'])

        # Notify if non-categorized objects
        if len(non_categorized_objects) > 0:
            print('Some objects are not categorized!')
            print('Non-catgorized objects:', non_categorized_objects)

        return objects_names_categories

    def filter_graph(self):
        # Get categories objects
        # ipdb.set_trace()
        objects_names_categories = self.get_categories_objects()
        # print("objects_names_categories: ", objects_names_categories)
        
        # from utils import find_nodes
        # print("-------------------------------------------------------")
        # print("find nodes: ", find_nodes(self.full_graph[0],class_name= 'apple'))
        # ipdb.set_trace()
        
        # Filter 1: Get initial subset of objects via categories
        selected_objects = self.filter_categories(objects_names_categories)
        # ipdb.set_trace()
        # Filter 2: Select objects relevant to task
        filtered_objects = self.filter_objects(selected_objects)
        # ipdb.set_trace()
        # Get graph info of selected objects
        filtered_objects_names, filtered_objects_id = get_graph_info_from_objects_names(self.full_graph, filtered_objects)
        # ipdb.set_trace()
        # Filter 3: Select interacting objects relevant for the task
        filtered_interactions_names, filtered_interactions_ids, failure_count = self.filter_interactions(filtered_objects_id, filtered_objects_names)
        # ipdb.set_trace()
        # Selected objects: combination of filtered objects and their filtered interacting objects
        ids_selected_combined = filtered_objects_id + filtered_interactions_ids
        names_selected_combined = filtered_objects_names + filtered_interactions_names

        # Remove duplicates
        ids_selected_combined, names_selected_combined = remove_duplicates_and_corresponding_elements(ids_selected_combined,
                                                                                                      names_selected_combined)
        return ids_selected_combined, names_selected_combined, failure_count