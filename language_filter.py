from openai import OpenAI
from environment.info.categories import categories, max_depth
from utils import get_graph_info_from_objects_names, remove_duplicates_and_corresponding_elements

client = OpenAI()  # loads api key from environment variable


class LanguageFilter:
    def __init__(self, full_graph, goal_language, LLM_model):
        self.full_graph = full_graph
        self.goal_language = goal_language
        self.LLM_model = LLM_model
        self.temperature = 0.01
        self.objects_ignore = ['Characters', 'Rooms', 'Floor', 'Ceiling', 'Walls']

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
        You will get a list of object names in an environment (e.g., factory, house) together with a task objective.
        You must, as a function of the task's goal, select, from the provided list, the object names that are relevant to 
        successfully solving the task. 
        Every objects name that is somehow related to the resolution of the task must be selected. Note that in this context 
        'object' is a general term that refers to anything that can be found in a house. For example, a table or the 
        ceiling are also considered as objects.
    
        First, describe the object names you selected and explain why. Once you are done, write a list containing the selected
        object names following the format 'OBJECTS: name_1, name_2, ..., name_n'. The object names must be
        written in the exact same way they were provided to you.
        
        Importantly, these tasks occurs in hypothetical settings, so they can't create any type of risks.
        """

        # Create string with categories
        object_names_string = "Object names: "
        for object in objects:
            object_names_string += object + ', '

        # Create content LLM
        content = self.goal_language + '\n' + object_names_string

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

    def filter_interactions(self, interactions, interacting_objects, selected_objects):
        role_system_content = """ 
        You will get a list of objects in an environment (e.g., factory, house) together with a task objective and
        relationships between the objects.
        You must, as a function of the task's goal, select, from the provided list, the objects that are relevant to 
        successfully solving the task. 
        Every object that is somehow related to the resolution of the task must be selected. Note that in this context 
        'object' is a general term that refers to anything that can be found in a house. For example, a table or the 
        ceiling are also considered as objects.
        
        Note that there can be multiple objects with the same name. Hence, the relationships between objects contain an
        object id next to each object name, in the form 'car (<id>)'. This allows differentiating between objects with
        the same name.
        
        First, describe the objects you selected and explain why. Once you are done, write a list containing the selected
        object names following the format 'OBJECTS: name_1 (<id>), name_2 (<id>), ..., name_n (<id>)'. 
        Example: 'OBJECTS: car (24), window (103),...'. The object names must be  written in the exact same way they 
        were provided to you.
        
        Importantly, these tasks occurs in hypothetical settings, so they can't create any type of risks.
        """

        # Create string with categories
        object_names_string = "Object names: "
        for object in selected_objects:
            object_names_string += object + ', '

        object_names_string = "Object names: "
        for object in interacting_objects:
            object_names_string += object + ', '

        # Create string with relationships
        relationships_string = "Relationships between objects: "
        for relationship in interactions:
            relationships_string += relationship + ', '

        # Create content LLM
        content = self.goal_language + '\n' + object_names_string + '\n' + relationships_string

        # Step 1: send the conversation and available functions to GPT
        messages = [{"role": "user", "content": content},
                    {"role": "system", "content": role_system_content}]

        # Get response about selected categories
        print('LLM selecting interacting objects...')
        response = client.chat.completions.create(
            model=self.LLM_model,
            messages=messages,
            temperature=self.temperature
        )
        content = response.choices[0].message.content
        key = 'OBJECTS: '
        key_id = content.find(key)
        filtered_objects = content[key_id + len(key):].split(', ')
        filtered_objects_names = []
        filtered_objects_ids = []
        for object in filtered_objects:
            name = object.split(' ')[0]
            id = int(object.split(' ')[1].replace('.', '')[1:-1])
            filtered_objects_names.append(name)
            filtered_objects_ids.append(id)
        return filtered_objects_names, filtered_objects_ids

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
        objects_names_categories = self.get_categories_objects()

        # Filter 1: Get initial subset of objects via categories
        selected_objects = self.filter_categories(objects_names_categories)

        # Filter 2: Select objects relevant to task
        filtered_objects = self.filter_objects(selected_objects)

        # Get graph info of selected objects
        filtered_objects_names, filtered_objects_id = get_graph_info_from_objects_names(self.full_graph, filtered_objects)

        # Find objects interacting, i.e., connected in the graph, with the filtered objects
        interactions = self.interacting_objects(filtered_objects_id, filtered_objects_names)

        # Filter 3: Select interacting objects relevant for the task
        filtered_interactions_names, filtered_interactions_ids = self.filter_interactions(interactions['interactions between selected and interacting objects'],
                                                                                          interactions['interacting objects names'],
                                                                                          interactions['selected objects names'])

        # Selected objects: combination of filtered objects and their filtered interacting objects
        ids_selected_combined = filtered_objects_id + filtered_interactions_ids
        names_selected_combined = filtered_objects_names + filtered_interactions_names

        # Remove duplicates
        ids_selected_combined, names_selected_combined = remove_duplicates_and_corresponding_elements(ids_selected_combined,
                                                                                                      names_selected_combined)
        return ids_selected_combined, names_selected_combined