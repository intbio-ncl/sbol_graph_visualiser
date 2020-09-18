import os
import sys
import copy
import rdflib
import networkx as nx
import matplotlib.pyplot as plt
from graph_builder.networkx_wrapper import NetworkXGraphWrapper
from networkx.drawing.nx_pydot import write_dot
from operator import itemgetter
from functools import partial
from networkx import MultiGraph
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from sbol_rdflib_identifiers import identifiers
from color_util import SBOLTypeColors,SBOLPredicateColors,calculate_next_color,calculate_role_color
from matplotlib.lines import Line2D


class NetworkXGraphBuilder:
    def __init__(self, graph = None):
        self._graph = NetworkXGraphWrapper(graph)
        self.build_settings = {"preset":self._graph.graph,
                               "layout":None,  
                               "edge_attributes":None, 
                               "node_attributes":None,
                               "misc_calls" : [],
                               "misc" : {"node_size" : 1000, 
                                         "width" : 5, 
                                         "linewidths" : 5},
                               "meta_data" : {}}

    # Set Preset (Set a sub-graph)
    def set_full_graph_preset(self):
        '''
        Sets the rendered graph as the default graph (Whole graph.)
        :rtype: None
        '''
        self.build_settings["preset"] = self._graph.graph

    def set_interaction_preset(self):
        ''' 
        Sets the rendered graph as a graph displaying interactions between parts.
        Nodes - ComponentDefinitions
        Edges - Interactions
        :rtype: None
        '''
        parts_graph = self._graph.produce_interaction_graph()
        self.build_settings["preset"] = parts_graph

    def set_parts_preset(self):
        ''' 
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        parts_graph = self._graph.produce_parts_preset()
        self.build_settings["preset"] = parts_graph

    def set_functional_preset(self):
        ''' 
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        functional_graph = self._graph.produce_functional_preset()
        self.build_settings["preset"] = functional_graph

    # Pick a layout
    def set_no_layout(self):
        self.build_settings["layout"] = None

    def set_spring_layout(self):
        ''' 
        Draw the specified graph with a spring layout. 
        :rtype: None
        '''
        self.build_settings["layout"] =  partial(nx.spring_layout, self.build_settings["preset"], iterations=200)

    def set_circular_layout(self, **kwargs):
        ''' 
        Draw the specified graph with a circular layout. 
        :rtype: None
        '''
        self.build_settings["layout"] =  partial(nx.circular_layout, self.build_settings["preset"], **kwargs)

    def set_kamada_kawai_layout(self):
        ''' 
        Draw the graph G with a Kamada-Kawai force-directed layout.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.kamada_kawai_layout, self.build_settings["preset"])
    
    def set_planar_layout(self):
        ''' 
        Draw a planar graph with planar layout.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.planar_layout, self.build_settings["preset"])

    def set_shell_layout(self):
        ''' 	
        Draw graph with shell layout.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.shell_layout, self.build_settings["preset"])

    def set_spiral_layout(self):
        ''' 	
        Position nodes in a spiral layout.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.spiral_layout, self.build_settings["preset"])

    def set_spectral_layout(self):
        ''' 	
        Position nodes using the eigenvectors of the graph Laplacian.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.spectral_layout, self.build_settings["preset"])

    def set_random_layout(self):
        ''' 	
        Position nodes uniformly at random in the unit square.
        :rtype: None
        '''
        self.build_settings["layout"] = partial(nx.random_layout, self.build_settings["preset"])

    def set_ego_layout(self):        
        # find node with largest degree
        node_and_degree = self.build_settings["preset"].degree()
        (largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]
        # Create ego graph of main hub
        hub_ego = nx.ego_graph(self.build_settings["preset"], largest_hub)
        # Draw graph
        self.build_settings["preset"] = hub_ego
        self.build_settings["layout"] = partial(nx.spring_layout, hub_ego)
        self.build_settings["misc_calls"].append(partial(nx.draw_networkx_nodes,
                                                        hub_ego,
                                                        self.build_settings["preset"], 
                                                        nodelist=[largest_hub],
                                                        node_color='r'))
        
    # Add Edge Attributes
    def add_edge_labels(self,attribute_name = None):
        ''' 	
        Specifies the Edges should be labelled when rendered.
        :rtype: None
        '''
        if attribute_name is None:
            attribute_name = "display_name"
        self.build_settings["edge_attributes"] = nx.get_edge_attributes(self.build_settings["preset"],attribute_name)

    # Add Node Attributes
    def add_node_labels(self,attribute_name = None):
        ''' 	
        Specifies the Nodes should be labelled when rendered.
        :rtype: None
        '''
        if attribute_name is None:
            attribute_name = "display_name"
        self.build_settings["node_attributes"]  = nx.get_node_attributes(self.build_settings["preset"], attribute_name) 
    
    # Any Misc Settings.
    def add_random_node_colour(self,colour = None):
        ''' 	
        Randomly colours the nodes when rendered.
        :rtype: None
        '''
        self.build_settings["misc"]["node_color"] = range(0,len(self.build_settings["preset"].nodes))
        if colour is not None:
            self.build_settings["misc"]["cmap"] = colour
        else:
            self.build_settings["misc"]["cmap"] = plt.cm.Pastel2
    
    def add_type_node_colour(self):
        ''' 	
        Colours Nodes based on SBOL object type when rendered.
        :rtype: None
        '''
        nodes = self.build_settings["preset"].nodes
        for node in nodes:
            obj_type = self._graph.retrieve_node(node,identifiers.predicates.rdf_type)
            if obj_type is None:
                color = SBOLTypeColors["default"].value
            else:
                obj_type = self._graph._get_name(obj_type)
                color = SBOLTypeColors[obj_type].value
            nodes[node]["color"] = color

        self.build_settings["misc"]["node_color"] = [nodes[u]['color'] for u in nodes]
 

    def add_adaptive_node_color(self):
        nodes = self.build_settings["preset"].nodes
        type_curr_color = (0.255,0,0)
        type_color_map = {}
        role_color_map = {"no_role" : (0,0,0)}
        for node in nodes:
            obj_type = self._graph.retrieve_node(node,identifiers.predicates.rdf_type)
            if obj_type is None:
                type_color = SBOLTypeColors["default"].value
            else:
                obj_name = self._graph._get_name(obj_type)
                if obj_name in type_color_map.keys():
                    type_color = type_color_map[obj_name]
                else:
                    type_color = type_curr_color
                    type_color_map[obj_name] = type_curr_color
                    type_curr_color = calculate_next_color(type_curr_color)

            role = self._graph.get_sbol_object_role(node,obj_type)
            if role is None:
                role_color = role_color_map["no_role"]
            elif role in role_color_map.keys():
                role_color = role_color_map[role]
            else:
                role_color = calculate_role_color(type_color_map[obj_name],role_color_map)
                role_color_map[role] = role_color

            nodes[node]["type_color"] = type_color
            nodes[node]["role_color"] = role_color
        
        self.build_settings["misc"]["node_color"] = [nodes[u]['type_color'] for u in nodes]
        self.build_settings["misc"]["edgecolors"] = [nodes[u]['role_color'] for u in nodes]
        self.build_settings["meta_data"]["node_type_color_mapping"] = type_color_map
        self.build_settings["meta_data"]["node_role_color_mapping"] = role_color_map

    def add_random_edge_colour(self, colour = None):
        ''' 	
        Randomly colours the edges when rendered.
        :rtype: None
        '''
        self.build_settings["misc"]["edge_color"] = range(0,len(self.build_settings["preset"].edges))
        if colour is not None:
            self.build_settings["misc"]["cmap"] = colour
        else:
            self.build_settings["misc"]["edge_cmap"] = plt.cm.Greys

    def add_type_edge_colour(self, colour = None):
        ''' 	
        Colours Nodes based on SBOL object relationship type when rendered.
        :rtype: None
        '''
        edges = self.build_settings["preset"].edges()
        for u,v in edges:
            edge = edges[u,v]
            if "triples" not in edge.keys():
                color = SBOLPredicateColors["default"].value
            edge_type = self._graph._get_name(edge["triples"][0][1])
            color = SBOLPredicateColors[edge_type].value
            edges[u,v]["edge_color"] = color
        self.build_settings["misc"]["edge_color"] = [edges[u,v]['edge_color'] for u,v in edges]

    def add_adaptive_edge_color(self):
        edges = self.build_settings["preset"].edges
        curr_color = (0.255,0,0)
        color_map = {}
        for u,v in edges:
            edge = edges[u,v]
            predicate = edge["triples"][0][1]

            predicate_type = self._graph._get_name(predicate)
            if predicate_type in color_map.keys():
                color = color_map[predicate_type]
            else:
                color = curr_color
                color_map[predicate_type] = curr_color
                curr_color = calculate_next_color(curr_color)
            
            edges[u,v]["edge_color"] = color
        self.build_settings["misc"]["edge_color"] = [edges[u,v]['edge_color'] for u,v in edges]
        self.build_settings["meta_data"]["edge_color_mapping"] = color_map

    def set_node_size(self,size):
        self.build_settings["misc"]["node_size"] = int(size)

    def set_node_outline_width(self,width):
        self.build_settings["misc"]["width"] = int(width)

    def set_edge_width(self,width):
        self.build_settings["misc"]["linewidths"] = int(width)
    
    def _add_legend(self,mapping,title,location):
        def make_proxy(clr, **kwargs):
            return Line2D([0, 1], [0, 1], color=clr, **kwargs)
        types = list(mapping.keys())
        colors = list(mapping.values())
        proxies = [make_proxy(clr, lw=5) for clr in colors]
        legend = plt.legend(proxies,types, loc=location,title=title)
        plt.gca().add_artist(legend)

    # build
    def build(self):
        ''' 	
        Executes the building of a visual graph given all previous build rules.
        :rtype: None
        '''
        position = None
        node_labels = None

        if self.build_settings["layout"] is None:
            raise ValueError("No Graph Layout provided.")
        else:
            print(self.build_settings["layout"])
            position = self.build_settings["layout"]()
            y_off = 0.05
            pos_higher = {}
            for k, v in position.items():
                pos_higher[k] = (v[0], v[1] + y_off)

        if self.build_settings["edge_attributes"] is not None:
            if isinstance(self.build_settings["preset"],MultiGraph):
                raise ValueError("Can't rendered edge labels with multigraphs.")
            nx.draw_networkx_edge_labels(self.build_settings["preset"], pos_higher, edge_labels = self.build_settings["edge_attributes"])
        
        if self.build_settings["node_attributes"] is not None:
            node_labels = self.build_settings["node_attributes"]

        if node_labels is not None:
            nx.draw_networkx_labels(self.build_settings["preset"], pos_higher, node_labels)
            nx.draw(self.build_settings["preset"], position, **self.build_settings["misc"])
        else:
            nx.draw(self.build_settings["preset"], pos_higher, **self.build_settings["misc"])

        for misc_call in self.build_settings["misc_calls"]:
            misc_call()


        # generate proxies with the above function
        if "edge_color_mapping" in self.build_settings["meta_data"].keys():
            self._add_legend(self.build_settings["meta_data"]["edge_color_mapping"],"Edge Types","upper left")

        if "node_type_color_mapping" in self.build_settings["meta_data"].keys():
            self._add_legend(self.build_settings["meta_data"]["node_type_color_mapping"],"Node Types","upper right")
        
        if "node_role_color_mapping" in self.build_settings["meta_data"].keys():
            self._add_legend(self.build_settings["meta_data"]["node_role_color_mapping"],"Node Roles","lower right")
        plt.show()

    def save_visualisation(self):
        plt.savefig(self.build_settings["preset"].graph_name + ".png")

    def show_graph(self):
        plt.show()

