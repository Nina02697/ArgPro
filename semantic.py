
import copy
import graphss

class GradualSemantic():
   

    def __init__(self, scoring_function, nb_of_iterations):
        self.scoring_function = scoring_function
        self.nb_of_iterations=nb_of_iterations
    
    def get_argument_value(self, arg, debate_graph):
        
        for i in range(self.nb_of_iterations):
            f = self.scoring_function(arg, i, debate_graph)
        return f

    def get_argument_effect(self, arg, edges, debate_graph):
        """ Used in the agent's strategies : this function determines the effect of adding an argument and the corresponding edges 
        to a graph on the value of the issue (Hypothetical value)
        """
        
        #original_value = self.get_argument_value(debate_graph.get_issue(), debate_graph)
        new_graph = debate_graph.deep_copy()
        new_graph.add_node(arg)
        new_graph.add_edges_from(edges)
        new_value = self.get_argument_value(new_graph.get_issue(), new_graph)

        del(new_graph)
        return new_value

def scoring_function_hcat(a,i, debate_graph):
    
    # Weight of argument a
    weight = debate_graph.get_argument_weight(a)
    if i == 0:
        return weight
    # list of predecessors of argument a
    B = list(debate_graph.predecessors(a))
    # if 0 attacks, then score=weight
    if len(B) == 0:
        return weight
    # Hcat
    f = weight / (1 + sum([scoring_function_hcat(b,i-1, debate_graph) for b in B]))
    return f

