
import networkx as nx
import random
import copy
import matplotlib.pyplot as plt
import re
from pathlib import Path

from datetime import datetime  # Import pour obtenir l'heure actuelle




class UniverseGraph(nx.DiGraph):
    """
    flat argumentation graph.
    
    
    """
    def __init__(self, issue=None, nodes=None):
        super().__init__(nodes)
        self.issue = issue
        if self.issue is not None:
            self.add_node(self.issue, agent_id='initial')

    def add_node(self, node_for_adding, agent_id=None, **attr):
        # Adds agent ID
        super().add_node(node_for_adding, agent_id=agent_id, **attr)

    def add_edge(self, u_of_edge, v_of_edge, agent_id=None, **attr):
        # adds Agent ID
        super().add_edge(u_of_edge, v_of_edge, agent_id=agent_id, **attr)

    def get_issue(self):
        # Return the issue of the debate
        return self.issue

    def get_size(self):
        # size of the graph
        return len(list(self.nodes))
    
    def get_edges_between(self, a, graph):
        """
        return arcs of an argument
        """
        in_edges = [e for e in self.in_edges(a) if e[0] in graph.nodes]
        out_edges = [e for e in self.out_edges(a) if e[1] in graph.nodes]
        return in_edges + out_edges

    def get_argument_weight(self, arg):
        # default weight of an argument in a flat graph
        return 1

    
    # def create_subgraph(self):

    #     """ This function creates a random DebateGraph object which is a subgraph of the parent graph 
    #     It is a connected graph which contains the issue. 
    #     """

    #     # generating a random size for the subgraph
    #     S = random.randint(2, self.get_size()-1)
    #     print("Size of subgraph : ", S)

    #     # Initialization
        
    #     s_graph = OpinionGraph(self, self.issue)
    #     current_node = self.issue

    #     # building loop
    #     while s_graph.get_size() < S:

    #         #selecting a random edge 
    #         edges_toward_cn = [e for e in list(self.in_edges(current_node)) if e[0] not in s_graph.nodes]

    #         # if no edges exist, we add a random node from the rest of the graph
    #         if len(edges_toward_cn) > 0:
    #             edge = random.sample(edges_toward_cn, 1)[0]
    #             new_node = edge[0]
            
    #         else :
    #             break 
                
    #             #s_graph.add_edge(edge)

    #         s_graph.add_node(new_node)
    #         # getting all edges between the new node and the subgraph
    #         in_edges = [e for e in self.in_edges(new_node) if e[0] in s_graph.nodes]
    #         out_edges = [e for e in self.out_edges(new_node) if e[1] in s_graph.nodes]

            
    #         s_graph.add_edges_from(in_edges)
    #         s_graph.add_edges_from(out_edges)

    #         current_node = new_node
        
    #     return s_graph
    def create_subgraph(self):
        """
        Cette fonction crée un objet OpinionGraph qui est un sous-graphe aléatoire du graphe parent.
        """
        # Génération d'une taille aléatoire pour le sous-graphe
        S = random.randint(2, self.get_size() - 1)
        print("Taille du sous-graphe : ", S)

        # Initialisation du sous-graphe
        s_graph = OpinionGraph(self, self.issue)
        current_node = self.issue

        # Construction du sous-graphe
        while s_graph.get_size() < S:
            # Sélection de plusieurs prédécesseurs pour le nœud courant
            predecessors = list(self.predecessors(current_node))

            #Vérification que la liste des prédécesseurs n'est pas vide
            if predecessors:
               # num_predecessors_to_select = random.randint(1, len(predecessors))  # Vous pouvez ajuster le nombre maximum de prédécesseurs sélectionnés ici
                #selected_predecessors = random.sample(predecessors)#, num_predecessors_to_select)

                for new_node in predecessors:
                    if s_graph.get_size() >= S:
                        break

                    # Ajout du nouveau nœud au sous-graphe
                    s_graph.add_node(new_node)

                    # Ajout des arêtes entre le nouveau nœud et les nœuds existants dans le sous-graphe
                    in_edges = [e for e in self.in_edges(new_node) if e[0] in s_graph.nodes]
                    out_edges = [e for e in self.out_edges(new_node) if e[1] in s_graph.nodes]
                    s_graph.add_edges_from(in_edges)
                    s_graph.add_edges_from(out_edges)

                    current_node = new_node
            else:
                break  # Sortir de la boucle si aucun prédécesseur n'est disponible


        return s_graph
    

 
    def print_arg(self, arg):
        # Print info of an argument
        print(f"Argument {arg}:")
        attackers = list(self.predecessors(arg))
        if attackers:
            print(f"  Attacked: {', '.join(map(str, attackers))}")
        else:
            print("  No attacks.")

        attacks = list(self.successors(arg))
        if attacks:
            print(f"  Attacks: {', '.join(map(str, attacks))}")
        else:
            print("  Doesn't attack any argument.")

    def view_graph(self):
        # prints arguments and arcs of a graph
        print("Arguments :")
        for arg in self.nodes:
            self.print_arg(arg)
        print("Arcs")
        for edge in self.edges:
            print(edge[0], " ============> ", edge[1])
    

    def draw(self, time=None, title=None, save=True):
        """
        Draw a graph and saves the image.
        """
        plt.figure(figsize=(8, 6))
        ax = plt.gca()
        if title is not None:
            sanitized_title = re.sub('[^a-zA-Z0-9 \n.]', '', title)
            ax.set_title(sanitized_title)
        else:
            sanitized_title = "graph"
        
        #  datetime.now() to get a unique ID 
        unique_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        
        nx.draw(self, pos=nx.spring_layout(self), node_size=700, with_labels=True, labels={n: str(n) for n in self.nodes})
        
        if save:
            if time is not None:
                time_str = re.sub(":", "_", str(time))
                path = f'Figures/{time_str}/'
            else:
                path = 'Figures/'
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # Adds a unique ID
            plt.savefig(f'{path}{sanitized_title}_{unique_id}.png', format="PNG")
            
        #plt.show()
    def __str__(self) -> str:
        return str(self.issue) + str(self.nodes)
    def deep_copy(self):
        # A copy which changes the graph object but keeps the same node objects
        
        return copy.deepcopy(self)
    
    
    
    def get_influence_index(self, arg):
        """Returns an influence index computed from the graph's distance to the issue"""
        

        paths = [ p for p in nx.all_simple_paths(self, source=arg, target=self.issue)]
        if len(paths) == 0:
            return 0
        else:
            path = random.sample(paths, 1)[0]
            return 1/len(path)
   



path = "C:/Users/AIT FERHAT/Desktop/TER_Code/Res"

    
def graph_name_generation(graph, ext, id=0):
  
   
        graph_name = "debate_graph_"
        graph_name += "star_" + str(len(list(graph.predecessors(0)))) + "_"
        graph_name += "arg_" + str(len(graph))
        if(id != 0):
            graph_name += "_" + str(id)
        graph_name += "." + ext
        return graph_name
def graph_name_gene(graph, ext, id=0):
  
   
        graph_name = "opinion_graph_"
        graph_name += "star_" + str(len(list(graph.predecessors(0)))) + "_"
        graph_name += "arg_" + str(len(graph))
        if(id != 0):
            graph_name += "_" + str(id)
        graph_name += "." + ext
        return graph_name
def graph_name_ge(graph, ext, id=0):
  
   
        graph_name = "public_graph_"
        graph_name += "star_" + str(len(list(graph.predecessors(0)))) + "_"
        graph_name += "arg_" + str(len(graph))
        if(id != 0):
            graph_name += "_" + str(id)
        graph_name += "." + ext
        return graph_name

def export_apx(graph):
        """
        Function to convert a given graph to aspartix format (apx).
        """
        graph_apx = ""
        for arg in graph:
            graph_apx += "arg(" + str(arg) + ").\n"
        for arg1,dicoAtt in graph.adjacency():
            if dicoAtt: 
                for arg2, eattr in dicoAtt.items():
                    graph_apx += "att(" + str(arg1) + "," + str(arg2) + ").\n"
        return graph_apx

def save_graph(graph, path, ext, id=0):
        """
        This function saves a given graph in a given directory in a given format with or without an id 
        at the end of the name. The path of the directory in parameter must exist.
        """
        gr_name = graph_name_generation(graph, ext, id)
        graph_apx = export_apx(graph)

        full_path = ""
        if(path[-1] == "/"):
            full_path = path + gr_name
        else:
            full_path = path + "/" + gr_name

        
        try:
            with open(full_path, "w") as fic:
                fic.write(graph_apx)
        except FileNotFoundError:
            print("Wrong file or file path :",path)
            quit()

def save_graphO(graph, path, ext, id=0):
        """
        This function saves a given graph in a given directory in a given format with or without an id 
        at the end of the name. The path of the directory in parameter must exist.
        """
        gr_name = graph_name_gene(graph, ext, id)
        graph_apx = export_apx(graph)

        full_path = ""
        if(path[-1] == "/"):
            full_path = path + gr_name
        else:
            full_path = path + "/" + gr_name

        
        try:
            with open(full_path, "w") as fic:
                fic.write(graph_apx)
        except FileNotFoundError:
            print("Wrong file or file path :",path)
            quit()


def save_graphP(graph, path, ext, id=0):
        """
        This function saves a given graph in a given directory in a given format with or without an id 
        at the end of the name. The path of the directory in parameter must exist.
        """
        gr_name = graph_name_ge(graph, ext, id)
        graph_apx = export_apx(graph)

        full_path = ""
        if(path[-1] == "/"):
            full_path = path + gr_name
        else:
            full_path = path + "/" + gr_name

        
        try:
            with open(full_path, "w") as fic:
                fic.write(graph_apx)
        except FileNotFoundError:
            print("Wrong file or file path :",path)
            quit()






class Universe_Dgraph(UniverseGraph):
    """
    Directed acyclic graph
    """
    
    def __init__(self, issue=None, nodes=None):
        super().__init__(issue=issue, nodes=nodes)
   
    def random_initialize(self, nb_args,p=0.5, seed=None, connected=True):
       
        
        
        self.issue = 0
        arguments = [i for i in range(nb_args)]
        self.add_nodes_from(arguments)

        # Création d'un graphe aléatoire non dirigé
        G = nx.fast_gnp_random_graph(nb_args,p, directed=False, seed=seed)

        # Ajout d'arcs dirigés basés sur les arêtes du graphe non dirigé, pour maintenir l'acyclicité
        for (u, v) in G.edges():
            if u < v:
                self.add_edge(v, u)
        
        # Si nécessaire, connecte tous les nœuds au sujet de débat
        if connected:
            U = self.to_undirected()  # Version non dirigée de notre graphe
            while not nx.is_connected(U):
                main_component = nx.node_connected_component(U, self.issue)
                components = nx.connected_components(U)
                for component in components:
                    if self.issue not in component:
                        u = random.choice(list(component))
                        v = random.choice(list(main_component))
                        self.add_edge(u, v)
                U = nx.Graph(self.edges)  # Mise à jour de la version non dirigée

            # Inverse les arêtes pour assurer un chemin vers le sujet du débat
            ancestors = nx.ancestors(self, self.issue)
            ancestors.add(self.issue)
            unconnected_nodes = self.nodes - ancestors
            while len(unconnected_nodes) > 0:
                for node in unconnected_nodes:
                    ancestor_neighbor = [a for a in ancestors if (a, node) in self.edges]
                    if ancestor_neighbor:
                        for d in ancestor_neighbor:
                            self.add_edge(node, d)
                            self.remove_edge(d, node)
                ancestors = nx.ancestors(self, self.issue)
                ancestors.add(self.issue)
                unconnected_nodes = self.nodes - ancestors

        assert nx.is_directed_acyclic_graph(self), "Le graphe doit être acyclique."
        Z=self.get_size()
        print("Taille du graphe:",Z)
    def count_nodes(self):
        """
        Retourne le nombre total de nœuds dans le graphe.
        """
        return self.number_of_nodes()
    def get_attackers(self):
        """
        Retourne un dictionnaire où chaque clé est un nœud et chaque valeur
        est une liste contenant les identifiants des nœuds attaquants (prédécesseurs) de ce nœud.
        """
        attackers = {node: list(self.predecessors(node)) for node in self.nodes}
        return attackers  
    
    

class OpinionGraph(UniverseGraph):
    """
    Représente un sous-graphe d'opinion, basé sur un Universe_DGraph.
    
    Paramètres:
        parent (Universe_DGraph): Le graphe parent dont ce sous-graphe est dérivé.
        issue (int): Le sujet du débat.
        nodes (iterable, optional): Les nœuds à inclure dans ce sous-graphe.
    """
    def __init__(self, parent, issue=None, nodes=None):
        super().__init__(issue, nodes)
        self.parent = parent  # Référence au graphe parent

    def view_graph(self):
        # Affiche le graphe d'opinion
        return super().view_graph()
    
    def get_argument_weight(self, arg):
        # Retourne le poids d'un argument dans le graphe d'opinion
        # Ici, tous les arguments ont un poids par défaut de 1
        return 1

    def deep_copy(self):
        return super().deep_copy()
class DebateTree(UniverseGraph):

   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.issue = None

    def random_initialize(self, nb_args, seed=None):
        
        #return super().random_initialize(nb_args, p=p, seed=seed)

        """
        Function to randomly generated a rooted tree, where the root is the issue, and all edges point towards it. 
        Method : we generate a random free tree and then root it. 
        """

        self.issue = 0
        random_tree = nx.generators.trees.random_tree(nb_args, seed)
        arguments = [n for n in range(nb_args)]
        self.add_nodes_from(arguments)

        # rooting by performing a depth first search and then reversing the direction of the edges
        for edge in nx.algorithms.traversal.depth_first_search.dfs_edges(random_tree, source= self.issue):
            self.add_edge(edge[1], edge[0])
        
      
        
        
    
    def has_attack(self, source, target):
        """
        Check if there is a directed edge from source to target, representing an attack.
        """
        return self.has_edge(source, target)
    def to_networkx(self):
        G = nx.DiGraph()
        G.add_edges_from(self.edges)
        return G

