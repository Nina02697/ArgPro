from mesa import Agent
import random
import networkx as nx

class DebateAgent(Agent):
    
    def __init__(self, unique_id, model, opinion_graph, comfort_limit=0.05):
        """
        Creates a new agent with a given opinion graph and comfort limit.
        """
        super().__init__(unique_id, model)
        self.opinion_graph = opinion_graph
        self.comfort_limit = comfort_limit
        self.opinion = None  # Opinion is initially None and updated based on the agent's own opinion graph.
        self.current_strategy = None
        self.name = unique_id
        self.state = []
        self.opinion_graph_states = []

    def get_opinion(self, semantic):
        
        #agent's opinion based on the current semantic analysis of the debate.
        self.opinion = semantic.get_argument_value(self.opinion_graph.get_issue(), self.opinion_graph)
        #print("Self opinion =",self.opinion)
        print(f" Self opinion of agent {self.name} = {self.opinion} ")  # Includes the agent's ID in the output

        return self.opinion

    def get_better_strategies(self, comfort_zone):
        
        #get strategies that might influence the debate positively towards the agent's opinion.
        better_strategies = []
        original_value = self.model.current_value
        
        print('Public value : ', original_value )
        for arg in self.opinion_graph.nodes:
            if arg in self.model.strategy_evaluation.keys():
                new_value = self.model.strategy_evaluation[arg]
                if abs(self.opinion - new_value) < abs(self.opinion - original_value):
                    edges = self.model.argument_graph.get_edges_between(arg, self.model.public_graph)
                    better_strategies.append((arg, edges))
        print('Better_strategies=',better_strategies)
        return better_strategies

    def get_comfort_strategies(self):
       
        """Identifies strategies that help maintain the debate within the agent's comfort zone."""
        comfort_strategies = []
        original_value = self.model.current_value
        print('Public value : ', original_value )

        for arg in self.opinion_graph.nodes:
            if arg in self.model.strategy_evaluation.keys():
                new_value = self.model.strategy_evaluation[arg]
                if new_value != original_value and self.opinion - self.comfort_limit < new_value < self.opinion + self.comfort_limit:
                    edges = self.model.argument_graph.get_edges_between(arg, self.model.public_graph)
                    comfort_strategies.append((arg, edges))
        print("Comfort_strategies=",comfort_strategies)
        return comfort_strategies
    
    def __str__(self) -> str:
        return str(self.name)
    
    def __repr__(self):
        return self.__str__()
        

    def step(self):
        
        """Determines the agent's strategy for the current step based on the debate's state and the agent's comfort zone."""
        # Update the agent's opinion based on the current debate semantic
        print("Tour de l'agent:",self.unique_id)

        self.get_opinion(self.model.get_semantic())
        #print("Agent's opinion : ", self.opinion )
        #self.model.opinions[-1][self.name] = (self.opinion, self.comfort_limit, self.model.current_value)
        comfort_zone = [self.opinion - self.comfort_limit, self.opinion + self.comfort_limit]
        if self.model.current_value > comfort_zone[1] or self.model.current_value < comfort_zone[0]:
            better_strategies = self.get_better_strategies(comfort_zone)
            strategy = random.choice(better_strategies) if better_strategies else 'NOTHING'
        else:
            comfort_strategies = self.get_comfort_strategies()
            strategy = random.choice(comfort_strategies) if comfort_strategies else 'NOTHING'
        self.current_strategy = strategy
        
        return strategy
        """
        
        """
    

    def advance(self):
        
        if self.current_strategy != 'NOTHING':
            self.model.implement_strategy(self.current_strategy, self)
 
        
        

    def influence_index(self, opinion=True):
        
        """Computes the sum of all influence index of the agent's known arguments
             computes the influence in the agent's opinion graph
        """

        
        graph = self.opinion_graph
        
        
        sum = 0
        for arg in self.opinion_graph.nodes:
            sum += graph.get_influence_index(arg)

        del(graph)
        return sum