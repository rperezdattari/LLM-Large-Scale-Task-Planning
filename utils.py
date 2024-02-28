def delete_node(graph, del_node):
    index_node = 0
    remove_index_list = []
    for node in graph['nodes']:
        if node['id'] == del_node['id']:
            remove_index_list.append(index_node)
        index_node += 1

    for remove_index in remove_index_list:
        del graph['nodes'][remove_index]


def remove_object(graph, object_name, remove=[]):
    obj_remove = find_nodes(graph, class_name=object_name)
    i = 0
    j_remove = 0
    while len(obj_remove) > 0:
        i += 1

        if len(remove) > 0:
            if i > len(remove):
                break

            if not remove[i-1]:
                j_remove += 1
                continue
            else:
                remove_edges(graph, obj_remove[j_remove])
                delete_node(graph, obj_remove[j_remove])
                obj_remove = find_nodes(graph, class_name=object_name)
        else:
            remove_edges(graph, obj_remove[0])
            delete_node(graph, obj_remove[0])
            obj_remove = find_nodes(graph, class_name=object_name)
    return graph


def find_nodes(graph, **kwargs):
    if len(kwargs) == 0:
        return None
    else:
        k, v = next(iter(kwargs.items()))
        return [n for n in graph['nodes'] if n[k] == v]


def find_edges_from(graph, id):
    nb_list = [(e['relation_type'], e['to_id']) for e in graph['edges'] if e['from_id'] == id]
    return [(rel, find_nodes(graph, id=n_id)[0]) for (rel, n_id) in nb_list]


def find_edges_to(graph, id):
    nb_list = [(e['relation_type'], e['from_id']) for e in graph['edges'] if e['to_id'] == id]
    return [(rel, find_nodes(graph, id=n_id)[0]) for (rel, n_id) in nb_list]


def clean_graph(graph):
    new_nodes = []
    for n in graph['nodes']:
        nc = dict(n)
        if 'bounding_box' in nc:
            del nc['bounding_box']
        new_nodes.append(nc)
    return {'nodes': new_nodes, 'edges': list(graph['edges'])}


def remove_edges(graph, n, fr=True, to=True):
    n_id = n['id']
    new_edges = [e for e in graph['edges'] if 
                 (e['from_id'] != n_id or not fr) and (e['to_id'] != n_id or not to)]
    graph['edges'] = new_edges


def remove_edge(graph, fr_id, rel, to_id):
    new_edges = [e for e in graph['edges'] if 
                 not (e['from_id'] == fr_id and e['to_id'] == to_id and e['relation_type'] == rel)]
    graph['edges'] = new_edges


def add_node(graph, n):
    graph['nodes'].append(n)


def add_edge(graph, fr_id, rel, to_id):
    graph['edges'].append({'from_id': fr_id, 'relation_type': rel, 'to_id': to_id})


def add_cat(graph):
    graph_1 = clean_graph(graph)
    sofa = find_nodes(graph_1, class_name='sofa')[-2]
    add_node(graph_1, {'class_name': 'cat', 'category': 'Animals', 'id': 1000, 'properties': [], 'states': []})
    add_edge(graph_1, 1000, 'ON', sofa['id'])
    return graph_1


def open_fridge(graph):
    graph1 = add_beer(graph)
    graph_1 = clean_graph(graph)
    fridge = find_nodes(graph_1, class_name='fridge')[0]
    fridge['states'] = ['OPEN']
    return graph_1


def add_beer(graph, id=1001):
    graph_1 = clean_graph(graph)
    fridge = find_nodes(graph_1, class_name='fridge')[0]
    
    add_node(graph_1, {'category': 'food', 'class_name': 'beer', 'id': id, 'properties': [], 'states': []})
    add_edge(graph_1, id, 'INSIDE', fridge['id'])
    return graph_1


def remove_duplicates_and_corresponding_elements(list1, list2):
    """Removes duplicates in list"""
    if len(list1) != len(list2):
        raise ValueError("The two lists must be of the same length")

    unique_elements = set()
    indices_to_remove = set()

    # Identify indices of duplicates in list1
    for i, element in enumerate(list1):
        if element in unique_elements:
            indices_to_remove.add(i)
        else:
            unique_elements.add(element)

    # Remove duplicates and corresponding elements from the lists
    list1[:] = [element for i, element in enumerate(list1) if i not in indices_to_remove]
    list2[:] = [element for i, element in enumerate(list2) if i not in indices_to_remove]

    return list1, list2


def get_graph_info_from_objects_names(graph, objects_names):
    filtered_objects_names = []
    filtered_objects_id = []
    for object_name in objects_names:
        nodes = find_nodes(graph[0], class_name=object_name.lower())
        for node in nodes:
            filtered_objects_names.append(node['class_name'])
            filtered_objects_id.append(node['id'])

    return filtered_objects_names, filtered_objects_id


def get_total_states(graph):
    total_states = 0
    for node in graph[0]['nodes']:
        total_states += len(node['states'])

    return total_states