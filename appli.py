import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from graphss import DebateTree
from semantic import GradualSemantic, scoring_function_hcat
from protocol import OnlineDebate
import random
from pyvis.network import Network




def draw_networkx_graph(G, title="Graph"):
    if not G:
        st.error("No graph available to display.")
        return
    plt.figure(figsize=(8, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=node_color, edge_color=edge_color, node_size=node_size, width=edge_width)
    st.pyplot(plt.gcf())
    st.caption(title)
    plt.clf()  # Clear the current figure to prevent reuse


def simulate_debate(nb_agents, nb_of_arguments, comfort_limit, seed, protocol):
    random.seed(seed)
    id = f"{nb_of_arguments}_{nb_agents}_{comfort_limit}_{seed}"
    Hcat = GradualSemantic(scoring_function_hcat, nb_of_arguments)
    argument_graph = DebateTree()
    argument_graph.random_initialize(nb_of_arguments)
    debate_model = OnlineDebate(nb_agents, argument_graph, Hcat, comfort_limit, subgraph_creation='random', lightmode=True, protocol=protocol)
    stats, opinion_graphs, public_graph_states,public_values_per_Round,agents_in_comfort_zone,opinions= debate_model.run_model(nb_of_arguments)
    if not isinstance(stats, pd.DataFrame):
        stats = pd.DataFrame([stats])
    stats['ID'] = id
    opinions = {}
    for agent in debate_model.schedule.agents:
        opinions[agent.unique_id] = agent.get_opinion(debate_model.get_semantic())
    
    return debate_model, stats, opinion_graphs, public_graph_states,public_values_per_Round,agents_in_comfort_zone,opinions



st.title("Debate Simulation Interface")

# Setup simulation parameters
# Section des paramètres de simulation
st.sidebar.subheader("Simulation Parameters")
nb_agents = st.sidebar.number_input("Number of Agents", min_value=1, value=4, step=1)
nb_of_arguments = st.sidebar.number_input("Number of Arguments", min_value=1, value=20, step=1)
comfort_limit = st.sidebar.slider("Comfort Limit", min_value=0.0001, max_value=1.0, value=0.05)
seed = st.sidebar.number_input("Seed", min_value=1, value=500, step=1)
protocol = st.sidebar.selectbox("Protocol", options=["simplified"], index=0)

st.sidebar.markdown("---")

# Section des paramètres de style
st.sidebar.subheader("Style Parameters")
node_color = st.sidebar.color_picker("Node Color", value="#FFA979")
edge_color = st.sidebar.color_picker("Edge Color", value="#000000")
node_size = st.sidebar.slider("Node Size", min_value=100, max_value=2000, value=1100, step=100)
edge_width = st.sidebar.slider("Edge Width", min_value=1, max_value=10, value=1)

if st.sidebar.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        debate_model, stats, opinion_graphs, public_graph_states,public_values_per_Round,agents_in_comfort_zone,opinions = simulate_debate(
            nb_agents, nb_of_arguments, comfort_limit, seed, protocol)
        st.success("Simulation completed!")
        st.session_state['initial_graph'] = debate_model.argument_graph.to_networkx()
        st.session_state['stats'] = stats
        st.session_state['opinion_graphs'] = opinion_graphs
        st.session_state['public_graph_states'] = public_graph_states
        st.session_state['public_values_per_Round'] = public_values_per_Round
        st.session_state['agents_in_comfort_zone'] = agents_in_comfort_zone
        st.session_state['agent_opinions'] = opinions
        
                


# Always display Universe Graph and Simulation Results
if 'initial_graph' in st.session_state:
    st.subheader("Universe Graph")
    draw_networkx_graph(st.session_state['initial_graph'], "Universe Graph:")



if 'stats' in st.session_state:
    st.subheader("Simulation Results :")
    st.write(st.session_state['stats'])




# Conditional display of opinion and public graphs
if 'opinion_graphs' in st.session_state:
    # Styling for the selectbox label
    st.markdown("""
                <style>
                .label-style {
                    font-size: 24px;
                    
                    font-weight: bold;
                }
                </style>
                """, unsafe_allow_html=True)
    
    # Display styled label with HTML
    st.markdown('<p class="label-style">Select Agent</p>', unsafe_allow_html=True)
    
    # Create the selectbox without a label
    agent_id = st.selectbox("", options=range(len(st.session_state['opinion_graphs'])), format_func=lambda x: f"Agent {x}")
    
    # Display the opinion of the selected agent
    if 'agent_opinions' in st.session_state:
        opinion_value = st.session_state['agent_opinions'][agent_id]
        rounded_value = round(opinion_value, 4)

        st.markdown(f"<h3>Opinion of Agent {agent_id} is : <span style='color: red;'>{rounded_value}</span></h3>", unsafe_allow_html=True)
    # Display the opinion graph for the selected agent
    agent_opinion_graph = st.session_state['opinion_graphs'][agent_id]
    draw_networkx_graph(agent_opinion_graph, f"Opinion Graph - Agent {agent_id}")

    

# Ajoutez une fonction pour afficher les nœuds ajoutés pour chaque étape
# Ajoutez une fonction pour afficher les nœuds ajoutés pour chaque étape
def display_added_nodes_for_step(step):
    added_nodes_info_step = st.session_state.get('added_nodes_info', {}).get(step, [])
    if added_nodes_info_step:
        st.subheader(f"Nodes Added - Round {step}:")
        for node_info in added_nodes_info_step:
            st.write(f"<span style='font-size: 24px;font-family:serif;'>Node {node_info['node']} added by Agent {node_info['agent']}</span>", unsafe_allow_html=True)



if 'public_graph_states' in st.session_state and 'stats' in st.session_state:
    max_step = st.session_state['stats']['Steps'].max() - 1
    if max_step > 0:
        # CSS styling for the slider label
        st.markdown("""
                    <style>
                    .slider-label-style {
                        font-size: 20px;
                        color: lightblue
                        font-weight: bold;
                    }
                    </style>
                    """, unsafe_allow_html=True)
        
        # Display styled label for the slider with HTML
        st.markdown('<p class="slider-label-style">Select Round</p>', unsafe_allow_html=True)

        # Create the slider without a label
        step = st.slider("", 0, max_step, 0)

        if 'public_values_per_Round' in st.session_state:
            public_value_round = st.session_state['public_values_per_Round'][step]
            # Round the value to 4 decimal places
            rounded_public_value = round(public_value_round, 4)
            # Using HTML and CSS to style the display of the public value
            st.markdown(f"<h3>Public value at round {step} is : <span style='color: red;'>{rounded_public_value}</span></h3>", unsafe_allow_html=True)
        added_nodes_info = {}
        for i, state in enumerate(st.session_state['public_graph_states']):
            if i > 0:
                previous_state = st.session_state['public_graph_states'][i - 1]
                added_nodes = [node for node in state.nodes if node not in previous_state.nodes]
                added_nodes_info[i] = []
                for node in added_nodes:
                    agent_id = state.nodes[node]['agent_id']
                    added_nodes_info[i].append({'node': node, 'agent': agent_id})
        st.session_state['added_nodes_info'] = added_nodes_info
        # Display the public graph corresponding to the selected round
        public_graph = st.session_state['public_graph_states'][step]
        display_added_nodes_for_step(step)
        draw_networkx_graph(public_graph, "Public Graph")

    else:
        st.write("No simulation data available.")


# Display agents in comfort zone
if 'agents_in_comfort_zone' in st.session_state:
    agents_list = ", ".join(str(agent) for agent in st.session_state['agents_in_comfort_zone'])
    st.subheader("Agents in Comfort zone:")
    st.markdown(f"<p style='color: red; font-size: 24px;'>[{agents_list}]</p>", unsafe_allow_html=True)

def plot_public_values_over_time(public_values_per_round):
    rounds = range(len(public_values_per_round))
    fig, ax = plt.subplots()  # Création de la figure et des axes
    ax.plot(rounds, public_values_per_round, marker='o', linestyle='-')
    ax.set_xlabel('Round')
    ax.set_ylabel('Public Value')
    ax.set_title('Evolution of public values over rounds')
    ax.grid(True)
    st.pyplot(fig)  # Affichage de la figure

#Affichage du graphique dans votre interface Streamlit
if 'public_values_per_Round' in st.session_state:
    st.subheader("Evolution of public values over rounds")
    plot_public_values_over_time(st.session_state['public_values_per_Round'])