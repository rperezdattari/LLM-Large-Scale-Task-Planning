exp_1 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-4-1106-preview',
         'filter objects': True}

exp_2 = {'policy type': 'LLM',
         'policy execution': 'online',
         'LLM model': 'gpt-3.5-turbo-1106',
         'filter objects': True}

exp_3 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-4-1106-preview',
         'filter objects': True}

exp_4 = {'policy type': 'mcts',
         'policy execution': 'offline',
         'LLM model': 'gpt-4-1106-preview',
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

experiments = [exp_4]  #exp_1, exp_2, exp_3, exp_4, exp_5, exp_6]