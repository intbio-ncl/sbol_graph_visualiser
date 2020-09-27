import sys,os
import plotly.graph_objects as go
import networkx as nx
from graph_builder.networkx_wrapper import NetworkXGraphWrapper

sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from rdflib import URIRef,Literal
from sbol_rdflib_identifiers import identifiers
from color_util import SBOLTypeColors,SBOLPredicateColors,calculate_next_color,calculate_role_color


class AbstractVisualiser:
    def __init__(self, graph = None):
        if isinstance(graph,NetworkXGraphWrapper):
            self._graph = graph
        else:
            self._graph = NetworkXGraphWrapper(graph)

        self.graph_view = self._graph.graph
        self.layout = self.set_spring_layout
        self.pos = []

        self.node_text_preset = self.add_node_no_labels
        self.edge_text_preset = None
        self.node_color_preset = self.add_standard_node_color
        self.edge_color_preset = self.add_standard_edge_color


    # ---------------------- Set Preset (Sets one or more other settings to focus on a specific thing in the graph) ----------------------

    def _set_preset(self,functions):
        for func in functions:
            func()
        return functions

    def set_interaction_preset(self):
        '''
        Master Function to provide insight into Interactions between components.
        '''
        sub_functions = [
            self.set_interaction_view,
            self.add_node_name_labels
        ]
        return self._set_preset(sub_functions)


    def set_parts_preset(self):
        '''
        Master Function to provide insight into heiraachy of components.
        '''
        sub_functions = [
            self.set_parts_view,
            self.add_standard_edge_color,
            self.add_node_name_labels
        ]
        return self._set_preset(sub_functions)

    def set_parent_preset(self):
        '''
        Master Function to provide insight into parent-child relationship between sbol elements.
        '''
        sub_functions = [
            self.set_parent_view,
            self.add_node_name_labels
        ]
        return self._set_preset(sub_functions)

    def set_adjacency_preset(self):
        '''
        Master Function to best show how nodes are interconnected.
        '''
        sub_functions = [
            self.set_full_graph_view,
            self.add_node_adjacency_labels,
            self.add_standard_edge_color,
        ]
        return self._set_preset(sub_functions)

    def set_functional_preset(self):
        '''
        Master Function to provide insight into the Functional aspect of a graph.
        '''
        sub_functions = [
            self.set_functional_view,
            self.add_node_name_labels,
            self.add_standard_edge_color,
        ]
        return self._set_preset(sub_functions)

    def set_component_preset(self):
        '''
        Master Function to display interconected components of the graph.
        '''
        sub_functions = [
            self.set_components_view,
            self.add_node_name_labels,
            self.add_standard_edge_color,
        ]
        return self._set_preset(sub_functions)

    def set_DBTL_preset(self):
        '''
        Master Function to provide insight into parent-child relationship between sbol elements.
        '''
        sub_functions = [
            self.set_parent_view,
            self.add_node_name_labels,

        ]
        return self._set_preset(sub_functions)


    # ---------------------- Set Graph (Set a different graph view) ----------------------
    def set_full_graph_view(self):
        '''
        :type: preset
        Sets the rendered graph as the default graph (Whole graph.)
        :rtype: None
        '''
        self.graph_view = self._graph.graph

    def set_interaction_view(self):
        ''' 
        :type: preset
        Sets the rendered graph as a graph displaying interactions between parts.
        Nodes - ComponentDefinitions
        Edges - Interactions
        :rtype: None
        '''
        parts_graph = self._graph.produce_interaction_graph()
        self.graph_view = parts_graph

    def set_components_view(self):
        ''' 
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        components_preset = self._graph.produce_components_preset()
        self.graph_view = components_preset

    def set_parts_view(self):
        parts_graph = self._graph.produce_parts_preset()
        self.graph_view = parts_graph

    def set_functional_view(self):
        ''' 
        :type: preset
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        functional_graph = self._graph.produce_functional_preset()
        self.graph_view = functional_graph

    def set_parent_view(self):
        parent_graph = self._graph.produce_parent_preset()
        self.graph_view = parent_graph

    # ---------------------- Pick a layout ----------------------
    def set_spring_layout(self):
        ''' 
        Draw the specified graph with a spring layout. 
        :rtype: None
        '''
        if self.layout == self.set_spring_layout:
            self.pos = nx.spring_layout(self.graph_view, iterations=200)
    
        else:
            self.layout = self.set_spring_layout

    def set_circular_layout(self):
        ''' 
        Draw the specified graph with a circular layout. 
        :rtype: None
        '''
        if self.layout == self.set_circular_layout:
            self.pos = nx.circular_layout(self.graph_view)
    
        else:
            self.layout = self.set_circular_layout

    def set_kamada_kawai_layout(self):
        ''' 
        Draw the graph G with a Kamada-Kawai force-directed layout.
        :rtype: None
        '''
        if self.layout == self.set_kamada_kawai_layout:
            self.pos = nx.kamada_kawai_layout(self.graph_view)
    
        else:
            self.layout = self.set_kamada_kawai_layout

    def set_planar_layout(self):
        ''' 
        Draw a planar graph with planar layout.
        :rtype: None
        '''
        if self.layout == self.set_planar_layout:
            self.pos = nx.planar_layout(self.graph_view)
    
        else:
            self.layout = self.set_planar_layout

    def set_shell_layout(self):
        ''' 	
        Draw graph with shell layout.
        :rtype: None
        '''
        if self.layout == self.set_shell_layout:
            self.pos = nx.shell_layout(self.graph_view)
    
        else:
            self.layout = self.set_shell_layout

    def set_spiral_layout(self):
        ''' 	
        Position nodes in a spiral layout.
        :rtype: None
        '''
        if self.layout == self.set_spiral_layout:
            self.pos = nx.spiral_layout(self.graph_view)
    
        else:
            self.layout = self.set_spiral_layout
            
    def set_spectral_layout(self):
        ''' 	
        Position nodes using the eigenvectors of the graph Laplacian.
        :rtype: None
        '''
        if self.layout == self.set_spectral_layout:
            self.pos = nx.spectral_layout(self.graph_view)
    
        else:
            self.layout = self.set_spectral_layout
            
    def set_random_layout(self):
        ''' 	
        Position nodes uniformly at random in the unit square.
        :rtype: None
        '''
        if self.layout == self.set_random_layout:
            self.pos = nx.random_layout(self.graph_view)
    
        else:
            self.layout = self.set_random_layout
    
    # ---------------------- Pick the node content ----------------------

    def add_node_no_labels(self):
        if self.node_text_preset == self.add_node_no_labels:
            return [None] * len(self.graph_view.nodes())
        else:
            self.node_text_preset = self.add_node_no_labels

    def add_node_adjacency_labels(self):
        if self.node_text_preset == self.add_node_adjacency_labels:
            node_text = []
            for node, adjacencies in enumerate(self.graph_view.adjacency()):
                node_text.append('# of connections: '+str(len(adjacencies[1])))
            return node_text
        else:
            self.node_text_preset = self.add_node_adjacency_labels

    def add_node_name_labels(self):
        if self.node_text_preset == self.add_node_name_labels:
            node_text = []
            names = nx.get_node_attributes(self.graph_view,"display_name")
            for v in names.values():
                node_text.append(v)
            return node_text
        else:
            self.node_text_preset = self.add_node_name_labels
    
    def add_node_type_labels(self):
        if self.node_text_preset == self.add_node_type_labels:
            node_text = []
            for node in self.graph_view.nodes:
                edges = [[e for e in edge[2]["triples"]] for edge in self._graph.edges(node,data=True)]
                found = False
                for edge in edges:
                    edge = edge[0]
                    if edge[1] == identifiers.predicates.rdf_type:
                        node_text.append(self._graph._get_name(str(edge[2])))
                        found = True
                        break
                if not found:
                    # I think this should only be literals and external identifiers.
                    if isinstance(edge[2],Literal):
                        node_text.append("Literal")
                    elif isinstance(edge[2],URIRef):
                        node_text.append("Identifier")
                    else:
                        node_text.append("?")
            return node_text
        else:
            self.node_text_preset = self.add_node_type_labels
        
    def add_node_parent_labels(self):
        if self.node_text_preset == self.add_node_parent_labels:
            node_text = []
            # A parent is essentially a triple child - parent - edge
            # If a node doesnt have a parent don't add it as it will already be present.
            for node in self.graph_view.nodes:
                edges = [[e for e in edge[2]["triples"]] for edge in self.graph_view.edges(node,data=True)]
                node_type = self._graph.triplepack_search((node,identifiers.predicates.rdf_type,None),edges)
                if node_type is None:
                    node_text.append("N/A")
                    continue
                if node_type in identifiers.objects.top_levels:
                    node_text.append("Top Level")
                    continue
                node_type = node_type[2]
                parent = self._graph._get_parent(node,edges,self.graph_view.edges)
                if parent is None:
                    node_text.append("No Parent")
                else:
                    node_text.append(self._graph._get_name(str(parent)))
            return node_text
        else:
            self.node_text_preset = self.add_node_parent_labels


    # ---------------------- Pick the node color ----------------------

    def add_standard_node_color(self):
        nodes = self.graph_view.nodes()
        standard_color = "#888"
        return [standard_color for e in nodes]


    # ---------------------- Pick the edge color ----------------------
    def add_standard_edge_color(self):
        edges = self.graph_view.edges
        standard_color = "#888"
        return [standard_color for e in edges]