from agents import DebateAgent
from graphss import  UniverseGraph,save_graph,save_graphO,save_graphP
from scheduler import RandomSequentialDebateActivation
from datetime import datetime
import networkx as nx
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import time 
import pandas as pd
import shutil
import networkx as nx
import sys 
import copy
from pathlib import Path
from copy import Error
from re import S

class OnlineDebate(Model):
    """
    Model implementing the protocol for the Online Debate Games.
    """

    def __init__(self, num_agents, argument_graph,semantic, comfort_limit, subgraph_creation,lightmode=False, protocol = 'simplified'):
        """
        Initialize a new debate model with the given parameters.
        """
        
        super().__init__()
        self.num_agents = num_agents
        self.argument_graph = argument_graph
        self.semantic = semantic

        self.comfort_limit = comfort_limit
        self.subgraph_creation = subgraph_creation
        self.lightmode=lightmode
        self.protocol = protocol
        self.schedule = RandomSequentialDebateActivation(self)
        self.public_graph = UniverseGraph(argument_graph.get_issue())

        self.time = str(datetime.now()).replace('.', '_').replace(':', '_') # a time marker to help save all relevant informations
        if lightmode:
            Path("tmp/" + self.time).mkdir(parents=True, exist_ok=True)   # folder to stock the state files of the model during game iteration
        self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph) # the current vlue of the issue in the public board
        # Initialize an empty list to store public values for each step
        self.public_values_per_Round = [1]
        self.public_values = []
        self.state = [] # a list keeping track of or all states of the game - in lightmode, only the last state of the game 
        self.strategies = [] # a list keeping track of all of the agent's strategies during the game
        self.opinions = [] # a list keeping track of all of the agent's opinions during the game
        self.agent_argument_set = set() # the set containing all of the arguments known by the agents
        self.strategy_evaluation = {}  # Initialize the strategy evaluation attribute
        self.public_graph_states = []  # Liste pour stocker les états du graphe public
        self.public_graph_states.append(copy.deepcopy(self.public_graph))  # Store the initial state

        self.opinion_graphs=[]

        print("===============  INITIALIZATION =========================================")
        print()
        print("Global Argument Graph for the game : ")

        self.argument_graph.view_graph()  #printing graph on command line
        self.argument_graph.draw(title="Graphe univers")
        save_graph(argument_graph,"C:/Users/AIT FERHAT/Desktop/TER_Code/Res","apx",id=0)
        print("Value of the Issue : ", self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph))
        print("///////////////////////////////////////////////////////////////////////////////////////////")
        # Create each agent and their opinion graph
        for i in range(self.num_agents):
            
            opinion_graph = argument_graph.create_subgraph()
            opinion_graph.view_graph()
            print("/////////////////////////////////////////////////////////////////////////////////")

            title_with_agent_id = f"Graphe d'opinion - Agent {i}"
            opinion_graph.draw(title=title_with_agent_id)
            save_graphO(opinion_graph,"C:/Users/AIT FERHAT/Desktop/TER_Code/Res","apx",id=1)
           
            
            agent = DebateAgent(i, model=self, opinion_graph = opinion_graph,comfort_limit=self.comfort_limit)
            self.agent_argument_set = self.agent_argument_set.union(set(list(opinion_graph.nodes)))
            self.opinion_graphs.append(opinion_graph)  # Store the opinion graph

            self.schedule.add(agent)
        
        

             
            
   
    def get_semantic(self):
        return self.semantic
    
    def get_time(self):
        return self.time
    
    

    
    def implement_strategy(self, strategy, agent):
        added_node = None
        adding_agent = None

        
        self.strategies[-1][agent.name] = strategy
        if strategy != 'NOTHING':
            # Vérifie si l'argument a déjà été ajouté au graphe
            if not self.public_graph.has_node(strategy[0]):
                # Si l'argument n'existe pas déjà, ajoute le nœud avec l'ID de l'agent comme attribut
                self.public_graph.add_node(strategy[0], agent_id=agent.name)
                added_node = strategy[0]
                adding_agent = agent.name


                print("Argument ajouté:", strategy[0], "par l'agent :", agent.name)
                # Ajoute les arêtes avec l'ID de l'agent comme attribut pour chaque arête
                edges_with_agent_id = [(u, v, {'agent_id': agent.name}) for u, v in strategy[1]]
                self.public_graph.add_edges_from(edges_with_agent_id)
            else:
                print(f"L'argument '{strategy[0]}' a déjà été joué et ne peut pas être rejoué par l'agent {agent.name}.")
        return self.public_graph,added_node,adding_agent
  
    def check_equilibre(self):
        for s in self.strategies[-1].values():
            if s != 'NOTHING':
                return False
        return True

    def check_strategies(self):
       
       
        
        self.strategy_evaluation = dict()
        
        # Iterate over all agents and their opinion graphs.
        for agent in self.schedule.agents:
            opinion_graph = agent.opinion_graph
            
            # Iterate over all arguments in the agent's opinion graph.
            for arg in opinion_graph.nodes:
                # Check if the argument has not been published yet.
                if arg not in self.public_graph.nodes:
                    #print("Testing argument ", arg)
                    #print(f"Testing argument {arg} from Agent ID: {agent.unique_id}")

                    # Get the edges between the argument and the current public graph.
                    edges = self.argument_graph.get_edges_between(arg, self.public_graph)
                    # Calculate the effect of publishing the argument.
                    new_value = self.semantic.get_argument_effect(arg, edges, self.public_graph)
                    #print('New value : ', new_value)
                    # Store the effect in the strategy evaluation dictionary.
                    self.strategy_evaluation[arg] = new_value
            

        
        # Print debugging information.
        #print("End of testing")
        #print("Current public value:", self.current_value)
        
        return self.strategy_evaluation

    def get_public_value(self, step = 0, beginning = True):
        

        # create the  model and compute its value 
        public_debate = self.argument_graph.deep_copy()
        all_nodes = copy.deepcopy(public_debate.nodes)
        
        for arg in all_nodes:
            if arg not in self.agent_argument_set:
                public_debate.remove_node(arg)

        for agent in self.schedule.agents:
            for arg in public_debate.nodes:
                if beginning:
                    agent_debate = agent.opinion_graph
                elif not self.lightmode:
                    agent_debate = agent.state[step]
                else:
                    raise("The parameter beginning should be true when using lightmode")

        public_value = self.semantic.get_argument_value(public_debate.get_issue(), public_debate)
        
        del(all_nodes)
        
        return public_value, public_debate   
    

   
    
 
    def step(self, i):
        print("------------------ Round ", i, "---------------------------------------")
        self.current_step = i
        self.public_graph.view_graph()
        title_with_step = f"Public graph - Round {i}"
        self.public_graph.draw(title=title_with_step)
        save_graphP(self.public_graph, "C:/Users/AIT FERHAT/Desktop/TER_Code/Res", "apx", id=2)

        
        self.state = [self.public_graph.deep_copy()]
        #Sauvegarde de l'état actuel du graphe public
        #self.public_graph_states.append(copy.deepcopy(self.public_graph))
    
        self.strategies.append({})  # Utiliser append pour ajouter un nouveau dictionnaire pour cette étape
         # Sauvegarde de l'état actuel des graphes d'opinion de chaque agent
        for agent in self.schedule.agents:
            agent.opinion_graph_states.append(copy.deepcopy(agent.opinion_graph))
        
        self.schedule.step()
        
        for agent in self.schedule.last_shuffled_order:
            print("###########################################################################################################################")
            self.check_strategies()
            agent.step()
            agent.advance()
            self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph)
            
            # Vérifier et mettre à jour les stratégies après chaque action de l'agent

            

        
        if self.check_equilibre():
            print("Debate has reached an equilibrium. Ending debate.")
            return True  # This can signal to the caller that the debate should end
        
        self.public_graph_states.append(copy.deepcopy(self.public_graph))

        return False

 



    def run_model(self, step_count):
        # Initialize the strategies list with an empty dictionary for each step.
        self.public_graphs = []  # Ensure this is cleared or correctly initialized
        self.opinion_graphs = [agent.opinion_graph for agent in self.schedule.agents]  # Assuming these are static
        
        self.strategies = [{} for _ in range(step_count)]
        public_value, public_debate = self.get_public_value(beginning = True)
        del(public_debate)
        stats = {'O. V.' : round(self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph),5), 'P.V.' : round(public_value,5),'Nb Agents' : self.num_agents, 'Nb of Arguments' : len(self.argument_graph), 'Args of Agents' : len(self.agent_argument_set)}
        
        
        # agent's stats 
        if self.lightmode:
            intersect = self.argument_graph.nodes

            for agent in self.schedule.agents:
                stats['Agent ' + str(agent.name) + ' O.V.'] = round(self.semantic.get_argument_value(agent.opinion_graph.get_issue(), agent.opinion_graph), 5)
                intersect = set(intersect).intersection(agent.opinion_graph.nodes)

                #stats['Agent ' + str(agent.name) + ' Opinion Influence Index'] = agent.influence_index(opinion = True)
                #stats['Agent ' + str(agent.name) + ' public Influence Index'] = agent.influence_index(opinion = False)

            #stats['Common Arguments'] = len(intersect)
        
        steps= 0
        #self.public_graph_states.append(copy.deepcopy(self.public_graph))  # Capturing the state post-step
        for i in range(step_count):
            self.step(i)
            if self.check_equilibre():
                steps = i
                break
            # Add the current public value to the list of public values for this step
            self.public_values_per_Round.append(self.current_value)
        #####################################################################################
        self.public_values.append(self.current_value)
        #####################################################################################
        print("====================================== END OF DEBATE ============================================")

        #updating the stats of the debate :
        stats['F. V.'] = round(self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph),5)
        stats['Args Played'] = len(self.public_graph)

        stats['Steps'] = steps + 1


        stats['Comfort Limit'] = self.comfort_limit
    

        # computing the nb of agents in their comfort zone 

                # at the beginning of the debate
        if self.opinions:
            agents_in_comfort_zone = []
            for agent, opinion in self.opinions[0].items():
                op, comfort_limit, model_value = opinion
                if model_value >= op - comfort_limit and model_value <= op + comfort_limit:
                    agents_in_comfort_zone.append(agent)
            stats['C_Z. Step 0'] = len(agents_in_comfort_zone)
        else:
            stats['C_Z. Step 0'] = 0

        # after the end of the debate
        agents_in_comfort_zone = []
        for agent in self.schedule.agents:
            op = agent.get_opinion(self.semantic)
            if self.current_value >= op - agent.comfort_limit and self.current_value <= op + agent.comfort_limit:
                agents_in_comfort_zone.append(agent)

        stats['C_Z. Final Step'] = len(agents_in_comfort_zone)

                
        print("Final public Value of the Issue : ", stats['F. V.'])
        print("Universe Value of the Issue : ", stats['O. V.'])
        print("Agents in comfort : ", [agent.unique_id for agent in agents_in_comfort_zone])
        
        # final stats for the agents 
        if self.lightmode:
            for agent in self.schedule.agents:
                stats['Agent ' + str(agent.name) + ' F.V.'] = round(self.semantic.get_argument_value(agent.opinion_graph.get_issue(), agent.opinion_graph), 5)
                #stats['Agent ' + str(agent.name) + ' F. N. Args'] = len(agent.opinion_graph.nodes)

                stats['Agent ' + str(agent.name) + ' Dissatisfaction'] = abs(stats['Agent ' + str(agent.name) + ' F.V.'] - stats['F. V.']) 
            
        # Collect opinions of agents
        agents_opinions = {}
        for agent in self.schedule.agents:
            agent_opinion = agent.get_opinion(self.semantic)
            agents_opinions[agent.unique_id] = agent_opinion

        return stats,self.opinion_graphs,self.public_graph_states,self.public_values_per_Round,agents_in_comfort_zone,agents_opinions