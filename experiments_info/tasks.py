# tasks = [
#     # {'goal': {0: {'on_plate_136': 1, 'on_wineglass_136': 1, 'on_cutleryfork_136': 1}},'id':0 },
#     {'goal': {0: { 'on_wineglass_231': 2}},'id':0 },
#     # {'goal': {0: { 'inside_plate_228': 1}}, 'id': 1},
#     # {'goal': {0: {'on_plate_72': 1}}, 'id': 1},
#     # {'goal': {0: {'on_plate_132': 2, 'on_waterglass_132': 1, 'on_wineglass_132': 1, 'on_cutleryfork_132': 1}}, 'id': 1},  # llm fails
#         #  {'goal': {0: {'on_apple_210': 1}}, 'id': 1},
#         #  {'goal': {0: {'on_apple_210': 2, 'on_beer_199': 1}}, 'id': 1},
#         #  {'goal': {0: {'inside_book_162': 1, 'turnon_163': 1}}, 'id': 2},
#         #  {'goal': {0: {'inside_mug_228': 1}}, 'id': 1},
#         #  {'goal': {0: {'inside_mug_228': 1, 'inside_plate_228': 1}}, 'id': 1},
#         #  {'goal': {0: {'inside_salmon_313': 1}}, 'id': 0},
#         # {'goal': {0: {'inside_salmon_313': 1, 'inside_bellpepper_305': 1}}, 'id': 0},
#         #  {'goal': {0: {'inside_bellpepper_305': 3}}, 'id': 0},
#             # {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
#         #  {'goal': {0: {'on_waterglass_393': 1, 'turnon_397': 1}}, 'id': 2},
#         #  {'goal': {0: {'on_beer_186': 2}}, 'id': 5},
#         #  {'goal': {0: {'on_beer_186': 2, 'inside_towel_45': 2}}, 'id': 5}
#          ]

''' env 0'''
# tasks = [
#      {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_book_111': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_mug_111': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_cutleryfork_238': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_wineglass_231': 2}}, 'id': 0},  # success or not?
# ]


# tasks = [
#      {'goal': {0: {'on_cutleryfork_111': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'inside_pie_305': 1}}, 'id': 0},
# ]

# tasks = [
#      {'goal': {0: {'inside_creamybuns_305': 1}}, 'id': 0},
# ]


# fryingpan, cutleryfork

# fridge 305, tv 264, bookshelf 105, kitchencounter 238, kitchentable 231, coffeetable 111, No dishwasher
# apple, whippedcream, chocolatesyrup, creamybuns, book ,plate, wineglass, fryingpan, cutleryfork
# failed: {'on_condimentbottle_111': 2} no valid actions
# failed to detect success: {'goal': {0: {'on_book_111': 2}}, 'id': 0}
# failed: {'goal': {0: {'on_fryingpan_111': 2}}, 'id': 0}

''' env 1'''
tasks_env_0 = [
    {'goal': {0: {'inside_bellpepper_305': 2}}, 'id': 0},
    {'goal': {0: {'on_book_111': 2}}, 'id': 0},
    {'goal': {0: {'on_mug_111': 2}}, 'id': 0},
    {'goal': {0: {'on_cutleryfork_238': 2}}, 'id': 0},
    {'goal': {0: {'on_wineglass_231': 2}}, 'id': 0},
    {'goal': {0: {'on_cutleryfork_111': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'on_apple_111': 2}}, 'id': 0},
    {'goal': {0: {'inside_pie_305': 1}}, 'id': 0},
    {'goal': {0: {'inside_creamybuns_305': 1}}, 'id': 0}
]

tasks_env_1 = [
    {'goal': {0: {'on_plate_210': 2}}, 'id': 1},
    {'goal': {0: {'on_mug_199': 1}}, 'id': 1},
    {'goal': {0: {'inside_fryingpan_228': 1}}, 'id': 1},
    {'goal': {0: {'inside_cutleryknife_228': 1}}, 'id': 1},
    {'goal': {0: {'on_dishbowl_199': 1}}, 'id': 1},
    {'goal': {0: {'on_poundcake_86': 1}}, 'id': 1},
    {'goal': {0: {'on_breadslice_86': 2}}, 'id': 1},
    {'goal': {0: {'on_apple_210': 1}}, 'id': 1},
    {'goal': {0: {'on_creamybuns_210': 2}}, 'id': 1},
    {'goal': {0: {'inside_book_83': 2}}, 'id': 1}
]
tasks_env_2 = [
    {'goal': {0: {'turnon_163': 1}}, 'id': 2},
    {'goal': {0: {'inside_book_158': 2}}, 'id': 2},
    {'goal': {0: {'inside_plate_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_cutleryfork_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_cutleryknife_165': 2}}, 'id': 2},
    {'goal': {0: {'inside_milk_162': 2}}, 'id': 2},
    {'goal': {0: {'inside_salmon_162': 1}}, 'id': 2},
    {'goal': {0: {'on_cupcake_215': 1}}, 'id': 2}
]
tasks_env_3 = [
    {'goal': {0: {'inside_plate_104': 1}}, 'id': 3},
    {'goal': {0: {'inside_waterglass_104': 2}}, 'id': 3},
    {'goal': {0: {'inside_wineglass_104': 1}}, 'id': 3},
    {'goal': {0: {'inside_cutleryfork_104': 2}}, 'id': 3},
    {'goal': {0: {'inside_apple_103': 3}}, 'id': 3},
    {'goal': {0: {'on_book_269': 3}}, 'id': 3},
    {'goal': {0: {'on_crackers_72': 1}}, 'id': 3},
    {'goal': {0: {'on_peach_72': 1}}, 'id': 3}
]
tasks_env_4 = [
    {'goal': {0: {'inside_cupcake_157': 2}}, 'id': 4},
    {'goal': {0: {'inside_pudding_157': 1, 'inside_pie_157': 1}}, 'id': 4},
    {'goal': {0: {'on_cereal_138': 1}}, 'id': 4},
    {'goal': {0: {'on_chocolatesyrup_138': 1}}, 'id': 4},
    {'goal': {0: {'on_mincedmeat_138': 1}}, 'id': 4},
    {'goal': {0: {'inside_mincedmeat_157': 1}}, 'id': 4},
    {'goal': {0: {'on_breadslice_138': 2}}, 'id': 4},
    {'goal': {0: {'inside_mug_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_plate_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_plate_156': 2, 'inside_mug_156': 2}}, 'id': 4},
    {'goal': {0: {'inside_wineglass_156': 2}}, 'id': 4},
    {'goal': {0: {'on_condimentbottle_138': 2}}, 'id': 4}
]

tasks_env_5 = [
    {'goal': {0: {'on_beer_186': 2}}, 'id': 5},
    {'goal': {0: {'on_mug_106': 1}}, 'id': 5},
    {'goal': {0: {'on_plate_106': 2}}, 'id': 5},
    {'goal': {0: {'on_cutleryfork_189': 2}}, 'id': 5},
    {'goal': {0: {'on_cutleryknife_189': 2}}, 'id': 5},
    {'goal': {0: {'on_whippedcream_189': 1}}, 'id': 5},
    {'goal': {0: {'on_milk_189': 1}}, 'id': 5},
    {'goal': {0: {'on_carrot_186': 1}}, 'id': 5}
]



# kitchencounter 210, dishwasher 228, coffeetable 86, kitchentable 199, fridge 225, bookshelf 83
# no valid actions: on_mug_210, on_peach_210
# LLM failed at {'on_apple_210': 2}


'''env 2'''

# tasks = [
#      {'goal': {0: {'inside_book_158': 1, 'turnon_163': 1}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'inside_book_158': 2}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'inside_plate_165': 2}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'inside_cutleryfork_165': 2}}, 'id': 2},
# ]


# tasks = [
#      {'goal': {0: {'inside_cutleryknife_165': 2}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'inside_milk_162': 2}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'inside_salmon_162': 1}}, 'id': 2},
# ]

# tasks = [
#      {'goal': {0: {'on_cupcake_215': 1}}, 'id': 2},
# ]

# bookshelf 158, fridge 162, kitchencounter 136, kitchentable 131, dishwasher 165, coffeetable 215
# no valid actions: inside_juice_215


''' env 3'''
# tasks = [
#      {'goal':{0: {'inside_plate_104': 1, 'inside_waterglass_104': 2, 'inside_wineglass_104': 1, 'inside_cutleryfork_104': 2}}, 'id':3},
# ]


# tasks = [
#      {'goal':{0: {'inside_cutleryfork_104': 2}}, 'id':3},
# ]

# tasks = [
#      {'goal':{0: {'inside_apple_103': 3}}, 'id':3},
# ]

# tasks = [
#      {'goal':{0: {'on_book_269': 3}}, 'id':3},
# ]

# tasks = [
#      {'goal':{0: {'on_crackers_72': 1}}, 'id':3},
# ]

# tasks = [
#      {'goal':{0: {'on_peach_72': 1}}, 'id':3},
# ]


# fridge 103, tv 298,  bookshelf 212, kitchencounter 81, kitchentable 72, dishwasher 104, coffeetable 269
# peach, apple(5), chips(2), candybar(1), crackers(2), bananas(1), milk(1), book(5)
# failed: {'on_peach_131': 1}},, seems no peach available
# failed: {'goal':{0: {'on_milk_72': 1}}, 'id':3}, File "/home/zhaoting/TUD_Projects/LLM-filter-planning/language_filter.py", line 298, in filter_interactions, id = int(object.split(' ')[1].replace('.', '')[1:-1]) IndexError: list index out of range

''' env 4 '''
''' env 4.1: Prepare food'''


# tasks = [
#      {'goal':{0: {'inside_cupcake_157': 2}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'inside_pudding_157': 1, 'inside_pie_157': 1}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'on_cereal_138': 1}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'on_chocolatesyrup_138': 1}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'on_mincedmeat_138': 1}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'inside_mincedmeat_157': 1}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'on_breadslice_138': 2}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'inside_mug_156': 2}}, 'id':4},
# ]


# tasks = [
#      {'goal':{0: {'inside_plate_156': 2}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'inside_plate_156': 2, 'inside_mug_156': 2}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'inside_wineglass_156': 2}}, 'id':4},
# ]

# tasks = [
#      {'goal':{0: {'on_condimentbottle_138': 2}}, 'id':4},
# ]

''' env 4 notes'''
# env_id 4: kitchentable is 138 instead of 136 (but on_cupcake_138 is already satisifed)
# kitchencounter 150  simulator cannot take the action: [putback] <cupcake> (210) <kitchencounter> (150)
# fridge 157 , dishwasher 156
# no juice, milk, poundcake, bellpepper, apple, salmon
# no valid actions to pick bananas: on_bananas_138 
# env failed to detect success: on_mincedmeat_157
# env failed to detact success for on_mug_156, but can detect if use inside_mug_156
# for {'goal':{0: {'inside_mug_156': 3}}, 'id':4} or {'goal':{0: {'inside_plate_156': 3}}, 'id':4}, the valid actions to putin dishwasher disappear for the third object

'''env 5'''

# tasks = [
#      {'goal': {0: {'on_beer_186': 2}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_mug_106': 1}}, 'id': 5},
# ]


# tasks = [
#      {'goal': {0: {'on_plate_106': 2}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_cutleryfork_189': 2}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_cutleryknife_189': 2}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_cutleryknife_189': 2}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_whippedcream_189': 1}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_milk_189': 1}}, 'id': 5},
# ]

# tasks = [
#      {'goal': {0: {'on_carrot_186': 1}}, 'id': 5},
# ]

# kitchencounter 189,  No dishwasher, coffeetable 106, kitchentable 186,fridge 235
# mug(3), plate(4), cutleryfork(2), cutleryknife(2), book(4), milk(2), carrot(2)
# failed :{0: {'on_plate_106': 3}} {'0': {'message': 'ScriptExcutor 0: EXECUTION_GENERAL: Script is impossible to execute\n\n'}} ['<char0> [grab] <plate> (240)']


'''Other notes'''
# [1] search function: remove  https://github.com/rperezdattari/LLM-filter-planning/blob/master/mcts/mcts.py#L109C17-L109C23
# [2] dataset all filtered_graph [simple: 1 task, medium:  hard: (LLM should sometimes success)]

# fix the bug of MCTS   

# first level MCTS always work
# second level MCTS works sometimes
# third level MCTS fails, LLM can work (can fail sometimes)


#ddl mid april workshop