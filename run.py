
from graphss import DebateTree
from semantic import GradualSemantic, scoring_function_hcat
from protocol import OnlineDebate
import random
import pandas as pd
import numpy as np


def run_debate(nb_agents, nb_of_arguments, lightmode = True, comfort_limit = 0.05, seed = 500,protocol = 'simplified'):

    """ One debate simulation. 
    gamestats : a dataframe where the stats of this debate will be added
    lightmode = if Tue, keeps the program light by not keeping in memory all of the debate information - useful when analysing hundreds of debates 
    """

    if seed is not None:
        random.seed(seed)
    

    id = str(nb_of_arguments) + '_' + str(nb_agents) + '_' + str(comfort_limit)  + '_' + str(seed) 


    # Hyperparameters
    nb_of_iterations = nb_of_arguments

    subgraph_creation = 'random'   #'custom' = all agents have a least one link to zero; 'random' = completely random
    Hcat = GradualSemantic(scoring_function_hcat, nb_of_iterations)

    argument_graph = DebateTree()
    argument_graph.random_initialize(nb_of_arguments)

    debate_model = OnlineDebate(nb_agents, argument_graph, Hcat, comfort_limit, subgraph_creation= subgraph_creation, 
                        lightmode=lightmode,protocol=protocol)
       # Run the model and capture statistics
    stats = debate_model.run_model(nb_of_iterations)

    # Ensure 'stats' is a DataFrame before attempting to save it
    if not isinstance(stats, pd.DataFrame):
        stats = pd.DataFrame([stats])  # Convert stats dictionary to a DataFrame assuming 'stats' is a dictionary

    # Add a unique ID to the DataFrame
    stats['ID'] = id
    
    # Save the statistics to an Excel file
    stats.to_excel(f'game_stats_{comfort_limit}.xlsx')
    
    return debate_model, stats

def run_debate_id(id, lightmode = False,protocol = 'simplified'):

    """ Run a debate identified by its unique id 
    id format : " nb_agents_nb_of_arguments_comfort_limit_seed"
    """

    params = id.split("_")
    print(params)
    nb_of_arguments = int(params[0])
    nb_agents = int(params[1])
    comfort_limit = float(params[2])
    seed = int(params[3])
    

    debate_model, stats = run_debate(nb_agents = nb_agents, nb_of_arguments = nb_of_arguments, lightmode = lightmode, comfort_limit = comfort_limit, seed =seed,protocol = protocol)
    
    # Ensure 'stats' is a DataFrame before attempting to save it
    if not isinstance(stats, pd.DataFrame):
        stats = pd.DataFrame([stats])  # Convert stats dictionary to a DataFrame assuming 'stats' is a dictionary

    # Add a unique ID to the DataFrame
    stats['ID'] = id
    
    # Save the statistics to an Excel file
    stats.to_excel(f'game_stats_{comfort_limit}_limit.xlsx')

    return debate_model, stats
 



if __name__ == '__main__':
    protocol = 'simplified'
    number_of_debates = 1
    number_of_arguments = 6
    number_of_agents = 2
    max_comfort_limit = 1
    min_comfort_limit = 0.0001
    seed = 500
    comfort_limit = 0.05
    game_stats = pd.DataFrame()

    for i in range(number_of_debates):

        debate_model, stats = run_debate(number_of_agents,number_of_arguments, lightmode=True,comfort_limit = comfort_limit, seed = seed,protocol="simplified")
        del(debate_model)

        stats_df = pd.DataFrame.from_records([stats])
        stats = pd.concat([game_stats, stats_df], sort=False).fillna(0)
        #if i % 50 == 0:
            #stats.to_excel('Debate_Stats.xlsx')
        
            #seed += 1

        seed += 1
    
        
        