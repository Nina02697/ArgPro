from mesa.time import BaseScheduler
import random

class RandomSequentialDebateActivation(BaseScheduler):
    def __init__(self, model):
        super().__init__(model)
        self.last_shuffled_order = []

    def step(self):
        # Create a list of all agents from the AgentSet for random shuffling
        agents = list(self.agents)
        random.shuffle(agents)
        self.last_shuffled_order = agents  # Store the shuffled order
        print("Ordre des agents pour cette étape:", [agent.unique_id for agent in agents])
        # Execute the steps for each agent in the shuffled order
        

        self.steps += 1
        self.time += 1
