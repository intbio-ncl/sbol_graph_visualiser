import os
import sys
import copy
import rdflib
import networkx as nx
import matplotlib.pyplot as plt
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
import rdf_util

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_graph, rdflib_to_networkx_digraph
from networkx.drawing.nx_pydot import write_dot
from operator import itemgetter
from functools import partial

try:
    import pygraphviz
    import pydot
except ImportError:
    pass


class NetworkXGraphWrapper:
    def __init__(self, graph = None):
        if isinstance(graph,NetworkXGraphWrapper):
            self.graph = copy.deepcopy(graph.graph)
        elif isinstance(graph,rdflib.Graph):
            self.graph = rdflib_to_networkx_graph(copy.deepcopy(graph))
        else:
            self.graph_name = graph
            self.graph = rdflib.Graph()
            if graph is not None:
                self.graph.load(graph)
            self.graph = rdflib_to_networkx_graph(self.graph)
        
        self.generate_labels()
  

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def edges(self):
        return self.graph.edges
    
    @property
    def adjacency(self):
        return self.graph.adj

    @property
    def degree(self):
        return self.graph.degree

    def shortest_path(self):
        return dict(nx.all_pairs_shortest_path(self.graph))
    
    def density(self):
        return nx.density(self.graph)

    def path_lengths(self):
        path_lengths = []
        for v in self.graph.nodes():
            spl = dict(nx.single_source_shortest_path_length(self.graph, v))
            for p in spl:
                path_lengths.append(spl[p])

        return path_lengths

    def average_shortest_path(self):
        path_lengths = self.path_lengths()
        return (sum(path_lengths) / len(path_lengths))

    def histogram(self):
        pathlengths = self.path_lengths()

        # histogram of path lengths
        dist = {}
        for p in pathlengths:
            if p in dist:
                dist[p] += 1
            else:
                dist[p] = 1
        return dist

    def generate_labels(self):
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            for subject,node,edge in self.graph.edges:
                if "display_name" not in self.nodes[subject].keys():
                    if isinstance(node,rdflib.URIRef):
                        name = rdf_util.get_name(node)
                    else:
                        name = node
                    self.graph.nodes[subject]["display_name"] = name
                if isinstance(node,rdflib.URIRef):
                    name = rdf_util.get_name(node)
                else:
                    name = node
                self.graph.nodes[node]["display_name"] = name
                if isinstance(edge,rdflib.URIRef):
                    name = rdf_util.get_name(edge)
                else:
                    name = edge
                nx.set_edge_attributes(self.graph,{ (subject,node,edge) : {"display_name" : name }})

        elif isinstance(self.graph,nx.classes.graph.Graph):
            for subject,node in self.graph.edges:
                if "display_name" not in self.nodes[subject].keys():
                    if isinstance(node,rdflib.URIRef):
                        name = rdf_util.get_name(node)
                    else:
                        name = node
                    self.graph.nodes[subject]["display_name"] = name

                if isinstance(node,rdflib.URIRef):
                    name = rdf_util.get_name(node)
                else:
                    name = node
                self.graph.nodes[node]["display_name"] = name

                edge = self.graph.edges[subject,node]
                if "triples" in edge.keys():
                    nx.set_edge_attributes(self.graph,{ (subject,node) : {"display_name" : rdf_util.get_name(edge["triples"][0][1]) }})
                    del edge["triples"]

        elif isinstance(self.graph,nx.classes.digraph.DiGraph):
            for subject,node in self.graph.edges:
                print(subject,node)

    def prune_graph(self, prune_edges = None):
        if prune_edges is None:
            prune_list = rdf_util.prune_list
        elif isinstance(prune_edges,list):
            prune_list = prune_edges
        else:
            prune_list = [prune_edges]

        to_prune_edges = []
        for n1,n2 in self.graph.edges:
            edge = self.graph.edges[n1,n2]
            if "display_name" in edge.keys():
                if edge["display_name"] in [rdf_util.get_name(p) for p in rdf_util.prune_list]:
                    to_prune_edges.append((n1,n2))

        self.graph.remove_edges_from(to_prune_edges)
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))
    
    def get_edge_attributes(self,attribute_name):
        edge_attributes = {}
        edge_labels = nx.get_edge_attributes(self.graph,attribute_name)
        for (subject,node,edge),v in edge_labels.items():
            edge_attributes[(subject,node)] = v
        return edge_attributes



class NetworkXGraphBuilder:
    def __init__(self, graph = None):
        if graph is None:
            self._graph = 1
        elif isinstance(graph,NetworkXGraphWrapper):
            self._graph = graph
        elif isinstance(graph,rdflib.Graph):
            self.graph = rdflib_to_networkx_graph(copy.deepcopy(graph))
            self.graph = NetworkXGraphWrapper(self.graph)
        self.build_settings = {"layout":None, "edge_attributes":None, "node_attributes":None,"misc":{}}

    # Pick a layout
    def add_spring_layout(self):
        self.build_settings["layout"] =  partial(nx.spring_layout, self._graph.graph, iterations=200)

    def add_circular_layout(self, **kwargs):
        self.build_settings["layout"] =  partial(nx.circular_layout, self._graph.graph, **kwargs)

    def add_kamada_kawai_layout(self):
        self.build_settings["layout"] = partial(nx.kamada_kawai_layout, self._graph.graph)
    
    def add_planar_layout(self):
        self.build_settings["layout"] = partial(nx.planar_layout, self._graph.graph)

    def add_shell_layout(self):
        self.build_settings["layout"] = partial(nx.shell_layout, self._graph.graph)

    def add_spiral_layout(self):
        self.build_settings["layout"] = partial(nx.spiral_layout, self._graph.graph)

    def add_spectral_layout(self):
        self.build_settings["layout"] = partial(nx.spectral_layout, self._graph.graph)

    def add_random_layout(self):
        self.build_settings["layout"] = partial(nx.random_layout, self._graph.graph)

    def add_graphviz_layout(self):
        self.build_settings["layout"] = partial(nx.nx_agraph.graphviz_layout, self._graph.graph)

    def add_pydot_layout(self):
        self.build_settings["layout"] = partial(nx.nx_pydot.pydot_layout, self._graph.graph)


    # Add Edge Attributes
    def add_edge_labels(self,attribute_name = None):
        if attribute_name is None:
            attribute_name = "display_name"
        self.build_settings["edge_attributes"] = nx.get_edge_attributes(self._graph.graph,attribute_name)


    # Add Node Attributes
    def add_node_labels(self,attribute_name = None):
        if attribute_name is None:
            attribute_name = "display_name"
        self.build_settings["node_attributes"]  = nx.get_node_attributes(self._graph.graph, attribute_name) 
    
    # Any Misc Settings.
    def add_node_colour(self,colour = None):
        self.build_settings["misc"]["node_color"] = range(0,len(self._graph.nodes))
        if colour is not None:
            self.build_settings["misc"]["cmap"] = colour
        else:
            self.build_settings["misc"]["cmap"] = plt.cm.Pastel2

    def add_edge_colour(self, colour = None):
        self.build_settings["misc"]["edge_color"] = range(0,len(self._graph.edges))
        if colour is not None:
            self.build_settings["misc"]["cmap"] = colour
        else:
            self.build_settings["misc"]["edge_cmap"] = plt.cm.Greys

    # build
    def build(self):
        position = None
        node_labels = None

        if self.build_settings["layout"] is None:
            raise ValueError("No Graph Layout provided.")
        else:
            position = self.build_settings["layout"]()

        if self.build_settings["edge_attributes"] is not None:
            nx.draw_networkx_edge_labels(self._graph.graph, position, edge_labels = self.build_settings["edge_attributes"])
        
        if self.build_settings["node_attributes"] is not None:
            node_labels = self.build_settings["node_attributes"]

        if node_labels is not None:
            nx.draw(self._graph.graph, position, labels = node_labels, **self.build_settings["misc"])
        else:
            nx.draw(self._graph.graph, position, **self.build_settings["misc"])
            
        plt.show()


    def save_visualisation(self):
        plt.savefig(self._graph.graph.graph_name + ".png")

    def show_graph(self):
        plt.show()

    def circular_tree(self):
        
        plt.figure(figsize=(8, 8))
        nx.draw(self._graph.graph, pos, node_size=20, alpha=0.5, node_color="blue", with_labels=False)
        plt.axis('equal')
        plt.show()

    def ego_graph(self):
        # find node with largest degree
        node_and_degree = self._graph.graph.degree()
        (largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]
        # Create ego graph of main hub
        hub_ego = nx.ego_graph(self._graph.graph, largest_hub)
        # Draw graph
        pos = nx.spring_layout(hub_ego)
        nx.draw(hub_ego, pos, node_color='b', node_size=len(self.nodes), with_labels=True)
        # Draw ego as large and red
        nx.draw_networkx_nodes(hub_ego, pos, nodelist=[largest_hub], node_size=300, node_color='r')
        plt.show()
    
    def random_geometric_graph(self):
        # position is stored as node attribute data for random_geometric_graph
        pos = self.nodes
        # find node near center (0.5,0.5)
        dmin = 1
        ncenter = 0
        for n in pos:
            x, y = pos[n]
            d = (x - 0.5)**2 + (y - 0.5)**2
            if d < dmin:
                ncenter = n
                dmin = d

        # color by path length from node near center
        p = dict(nx.single_source_shortest_path_length(self._graph.graph, ncenter))

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_edges(self._graph.graph, pos, nodelist=[ncenter], alpha=0.4)
        nx.draw_networkx_nodes(self._graph.graph, pos, nodelist=list(p.keys()),
                            node_size=80,
                            node_color=list(p.values()),
                            cmap=plt.cm.Reds_r)

        plt.xlim(-0.05, 1.05)
        plt.ylim(-0.05, 1.05)
        plt.axis('off')
        plt.show()
    
if __name__ == "__main__":
    graph = NetworkXGraphWrapper(sys.argv[1])
    graph.prune_graph()
    visual_builder = NetworkXGraphBuilder(graph)

    visual_builder.add_pydot_layout()
    visual_builder.add_node_labels()
    visual_builder.add_edge_labels()
    visual_builder.add_node_colour()
    #visual_builder.add_edge_colour()
    visual_builder.build()

