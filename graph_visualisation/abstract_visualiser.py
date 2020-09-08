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

    # ---------------------- Set Preset (Set a sub-graph) ----------------------
    def set_full_graph_preset(self):
        '''
        :type: preset
        Sets the rendered graph as the default graph (Whole graph.)
        :rtype: None
        '''
        self.preset = self._graph.graph

    def set_interaction_preset(self):
        ''' 
        :type: preset
        Sets the rendered graph as a graph displaying interactions between parts.
        Nodes - ComponentDefinitions
        Edges - Interactions
        :rtype: None
        '''
        parts_graph = self._graph.produce_interaction_graph()
        self.preset = parts_graph

    def set_components_preset(self):
        ''' 
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        components_preset = self._graph.produce_components_preset()
        self.preset = components_preset

    def set_parts_preset(self):
        parts_graph = self._graph.produce_parts_preset()
        self.preset = parts_graph

    def set_functional_preset(self):
        ''' 
        :type: preset
        Sets the rendered graph as a graph displaying 
        CD's as subparts of other CD's.
        Nodes - ComponentDefinitions
        Edges - Components (Instances of CD's)
        :rtype: None
        '''
        functional_graph = self._graph.produce_functional_preset()
        self.preset = functional_graph

    def set_parent_preset(self):
        parent_graph = self._graph.produce_parent_preset()
        self.preset = parent_graph

    # ---------------------- Pick a layout ----------------------
    def set_spring_layout(self):
        ''' 
        Draw the specified graph with a spring layout. 
        :rtype: None
        '''
        if self.layout == self.set_spring_layout:
            self.pos = nx.spring_layout(self.preset, iterations=200)
    
        else:
            self.layout = self.set_spring_layout

    def set_circular_layout(self):
        ''' 
        Draw the specified graph with a circular layout. 
        :rtype: None
        '''
        if self.layout == self.set_circular_layout:
            self.pos = nx.circular_layout(self.preset)
    
        else:
            self.layout = self.set_circular_layout

    def set_kamada_kawai_layout(self):
        ''' 
        Draw the graph G with a Kamada-Kawai force-directed layout.
        :rtype: None
        '''
        if self.layout == self.set_kamada_kawai_layout:
            self.pos = nx.kamada_kawai_layout(self.preset)
    
        else:
            self.layout = self.set_kamada_kawai_layout

    def set_planar_layout(self):
        ''' 
        Draw a planar graph with planar layout.
        :rtype: None
        '''
        if self.layout == self.set_planar_layout:
            self.pos = nx.planar_layout(self.preset)
    
        else:
            self.layout = self.set_planar_layout

    def set_shell_layout(self):
        ''' 	
        Draw graph with shell layout.
        :rtype: None
        '''
        if self.layout == self.set_shell_layout:
            self.pos = nx.shell_layout(self.preset)
    
        else:
            self.layout = self.set_shell_layout

    def set_spiral_layout(self):
        ''' 	
        Position nodes in a spiral layout.
        :rtype: None
        '''
        if self.layout == self.set_spiral_layout:
            self.pos = nx.spiral_layout(self.preset)
    
        else:
            self.layout = self.set_spiral_layout
            
    def set_spectral_layout(self):
        ''' 	
        Position nodes using the eigenvectors of the graph Laplacian.
        :rtype: None
        '''
        if self.layout == self.set_spectral_layout:
            self.pos = nx.spectral_layout(self.preset)
    
        else:
            self.layout = self.set_spectral_layout
            
    def set_random_layout(self):
        ''' 	
        Position nodes uniformly at random in the unit square.
        :rtype: None
        '''
        if self.layout == self.set_random_layout:
            self.pos = nx.random_layout(self.preset)
    
        else:
            self.layout = self.set_random_layout
            
    def set_graphviz_layout(self):
        ''' 	
        Create node positions using Graphviz.
        :rtype: None
        '''
        if self.layout == self.set_graphviz_layout:
            self.pos = nx.nx_agraph.graphviz_layout(self.preset)
    
        else:
            self.layout = self.set_graphviz_layout
            
    def set_pydot_layout(self):
        ''' 	
        Create node positions using pydot.
        :rtype: None
        '''
        if self.layout == self.set_pydot_layout:
            self.pos = nx.nx_pydot.pydot_layout(self.preset)
    
        else:
            self.layout = self.set_pydot_layout