# exp_1 = {'policy type': 'LLM',
#          'policy execution': 'online',
#          'LLM model': 'gpt-4-1106-preview',
#          'filter objects': True}

exp_1 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4o',
         'Dataset': '1task',
         'filter objects': True}

exp_2 = {'policy type': 'LLM',
         'policy execution': 'online',
         'Dataset': '1task',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_1_2 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4o',
         'Dataset': '2task',
         'filter objects': True}

exp_2_2 = {'policy type': 'LLM',
         'policy execution': 'online',
         'Dataset': '2task',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_1_3 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4o',
         'Dataset': '3task',
         'filter objects': True}

exp_2_3 = {'policy type': 'LLM',
         'policy execution': 'online',
         'Dataset': '3task',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_1_4 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4o',
         'Dataset': '4task',
         'filter objects': True}

exp_2_4 = {'policy type': 'LLM',
         'policy execution': 'online',
         'Dataset': '4task',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_1_5 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4o',
         'Dataset': '5task',
         'filter objects': True}

exp_2_5 = {'policy type': 'LLM',
         'policy execution': 'online',
         'Dataset': '5task',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_3 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-4o',
         'Dataset': '5task',
         'filter objects': True}



exp_4 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-4-1106-preview',
         'Dataset': '5task',
         'filter objects': False}

exp_5 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_6 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': False}

exp_7 = {'policy type': 'mcts_2',
         'policy execution': 'offline',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

experiments = [exp_1, exp_2, exp_1_2, exp_2_2, exp_1_3, exp_2_3, exp_1_4, exp_2_4, exp_1_5, exp_2_5]  #exp_1, exp_2, exp_3, exp_4, exp_5, exp_6]
# experiments = [exp_2_2]  