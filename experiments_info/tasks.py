tasks = [
    # {'goal': {0: {'on_plate_136': 1, 'on_wineglass_136': 1, 'on_cutleryfork_136': 1}},'id':0 },
    # {'goal': {0: { 'on_wineglass_231': 2}},'id':0 },
    # {'goal': {0: { 'inside_plate_228': 1}}, 'id': 1},
         {'goal': {0: {'on_apple_210': 1}}, 'id': 1},
         {'goal': {0: {'on_apple_210': 2, 'on_beer_199': 1}}, 'id': 1},
         {'goal': {0: {'inside_book_162': 1, 'turnon_163': 1}}, 'id': 2},
         {'goal': {0: {'inside_mug_228': 1}}, 'id': 1},
         {'goal': {0: {'inside_mug_228': 1, 'inside_plate_228': 1}}, 'id': 1},
         {'goal': {0: {'inside_salmon_313': 1}}, 'id': 0},
         {'goal': {0: {'inside_bellpepper_305': 3}}, 'id': 0},
         {'goal': {0: {'on_waterglass_393': 1, 'turnon_397': 1}}, 'id': 2},
         {'goal': {0: {'on_beer_186': 2}}, 'id': 5},
         {'goal': {0: {'on_beer_186': 2, 'inside_towel_45': 2}}, 'id': 5}]



# [1] search function: remove  https://github.com/rperezdattari/LLM-filter-planning/blob/master/mcts/mcts.py#L109C17-L109C23
# [2] dataset all filtered_graph [simple: 1 task, medium:  hard: (LLM should sometimes success)]


#ddl mid april workshop