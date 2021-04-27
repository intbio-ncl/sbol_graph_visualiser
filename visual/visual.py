import sys,os
import math
import re

import dash
import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
from rdflib import Literal,URIRef


from util.color_util import calculate_next_color
from util.color_util import calculate_role_color
from util.sbol_identifiers import identifiers

from builder.builder import GraphBuilder



class CytoscapeVisualiser:

    def __init__(self, graph = None):
        if graph is None:
            self._graph = None
        elif isinstance(graph,GraphBuilder):
            self._graph = graph
            self.graph_view = self._graph.graph._graph
        else:
            self._graph = GraphBuilder(graph)
            self.graph_view = self._graph.graph._graph

        cyto.load_extra_layouts()
        self.pos = []
        self.mode = self.set_network_mode
        self.layout = self.set_spring_layout
        self.node_text_preset = self.add_node_no_labels
        self.edge_text_preset = None
        self.node_color_preset = self.add_standard_node_color
        self.edge_color_preset = self.add_standard_edge_color
        self.node_size_preset = self.add_standard_node_size

        self.elements = []
        self._edge_width = 1
        self._node_text_size = 5
        self._edge_text_size = 5
        self._node_shape_preset = self.set_circle_node_shape
        self.edge_shape = "straight"
        self._node_edge_colors = []
        self.cyto_shapes = ["circle",
                            "square",
                            "triangle",
                            "rectangle",
                            "diamond",
                            "hexagon",
                            "octagon",
                            "vee",
                            "parallelogram",
                            "roundrect",
                            "ellipse"]


    def copy_settings(self):
        current_settings = [
            self.layout,
            self.node_text_preset,
            self.edge_text_preset,
            self.node_color_preset,
            self.edge_color_preset,
        ]

        return current_settings

    # ---------------------- Set Preset (Sets one or more other settings to focus on a specific thing in the graph) ----------------------
    def _set_preset(self,functions):
        for func in functions:
            func()
        return functions

    def set_protein_protein_interaction_preset(self):
        preset_functions = [
            self.set_network_mode,
            self.set_protein_protein_interaction_view,
            self.add_node_name_labels,
            self.add_standard_node_color,
            self.set_cola_layout,
            self.add_adaptive_edge_color,
            self.add_edge_name_labels]
        return self._set_preset(preset_functions)

    def set_interaction_preset(self):
        preset_functions = [
            self.set_network_mode,
            self.set_interaction_view,
            self.add_node_name_labels,
            self.set_klay_layout,
            self.add_adaptive_node_color,
            self.add_adaptive_edge_color,
            self.add_edge_name_labels]
        return self._set_preset(preset_functions)

    def set_interaction_genetic_preset(self):
        preset_functions = [
            self.set_network_mode,
            self.set_genetic_interaction_view,
            self.add_node_name_labels,
            self.set_klay_layout,
            self.add_adaptive_node_color,
            self.add_adaptive_edge_color,
            self.add_edge_name_labels]
        return self._set_preset(preset_functions)

    def set_adjacency_preset(self):
        preset_functions = [
            self.set_network_mode,
            self.set_full_graph_view,
            self.add_node_adjacency_labels,
            self.add_standard_edge_color,
            self.set_circular_layout,
            self.add_edge_no_labels,
            self.add_node_total_adjacency_color]
        return self._set_preset(preset_functions)

    def set_heirarchy_preset(self):
        preset_functions = [
            self.set_tree_mode,
            self.set_heirarchy_view,
            self.add_node_name_labels,
            self.add_standard_edge_color,
            self.set_dagre_layout,
            self.add_adaptive_node_color,
            self.add_edge_no_labels]
        return self._set_preset(preset_functions)

    def set_component_preset(self):
        preset_functions = [
            self.set_tree_mode,
            self.set_components_view,
            self.add_node_name_labels,
            self.add_standard_edge_color,
            self.set_cose_layout,
            self.add_adaptive_node_color,
            self.add_edge_no_labels]
        return self._set_preset(preset_functions)


    
    # ---------------------- Set Mode (Type of graph) ------------------------------------
    def set_network_mode(self):
        if self.mode == self.set_network_mode:
            self.graph_view = self.graph_view.get_network()
        else:
            self.mode = self.set_network_mode

    def set_tree_mode(self):
        if self.mode == self.set_tree_mode:
            self.graph_view = self.graph_view.get_tree()
        else:
            self.mode = self.set_tree_mode

    # ---------------------- Set Graph (Set a different graph view) ----------------------
    def set_full_graph_view(self):
        self.graph_view = self._graph.produce_full_graph()

    def set_interaction_view(self):
        interaction_graph = self._graph.produce_interaction_graph()
        self.graph_view = interaction_graph

    def set_genetic_interaction_view(self):
        interaction_graph = self._graph.produce_genetic_interaction_graph()
        self.graph_view = interaction_graph

    def set_protein_protein_interaction_view(self):
        ppi_graph = self._graph.produce_protein_protein_interaction_graph()
        self.graph_view = ppi_graph

    def set_heirarchy_view(self):
        heirarchy_preset = self._graph.produce_heirarchy_graph
        self.graph_view = heirarchy_preset

    def set_components_view(self):
        components_preset = self._graph.produce_components_graph()
        self.graph_view = components_preset


    # ---------------------- Pick a layout ----------------------
    def set_spring_layout(self):
        if self.layout == self.set_spring_layout:
            self.pos = nx.spring_layout(self.graph_view.graph, iterations=200)
    
        else:
            self.layout = self.set_spring_layout

    def set_circular_layout(self):
        if self.layout == self.set_circular_layout:
            self.pos = nx.circular_layout(self.graph_view.graph)
    
        else:
            self.layout = self.set_circular_layout

    def set_kamada_kawai_layout(self):
        if self.layout == self.set_kamada_kawai_layout:
            self.pos = nx.kamada_kawai_layout(self.graph_view.graph)
    
        else:
            self.layout = self.set_kamada_kawai_layout

    def set_planar_layout(self):
        if self.layout == self.set_planar_layout:
            self.pos = nx.planar_layout(self.graph_view.graph)
    
        else:
            self.layout = self.set_planar_layout

    def set_no_layout(self):
        if self.layout == self.set_no_layout:
            self.pos = None
            return {"name" : "preset"}
        else:
            self.layout = self.set_no_layout

    def set_concentric_layout(self):
        if self.layout == self.set_concentric_layout:
            self.pos = None
            return {"name" : "concentric"}
        else:
            self.layout = self.set_concentric_layout

    def set_breadthfirst_layout(self):
        if self.layout == self.set_breadthfirst_layout:
            self.pos = None
            return {"name" : "breadthfirst",
                    'directed': True,}
        else:
            self.layout = self.set_breadthfirst_layout

    def set_cose_layout(self):
        if self.layout == self.set_cose_layout:
            self.pos = None
            return {"name" : "cose",
                    'idealEdgeLength': 100,
                    'nodeOverlap': 20,
                    'refresh': 20,
                    'fit': True,
                    'padding': 30,
                    'randomize': False,
                    'componentSpacing': 100,
                    'nodeRepulsion': 400000,
                    'edgeElasticity': 100,
                    'nestingFactor': 5,
                    'gravity': 80,
                    'numIter': 1000,
                    'initialTemp': 200,
                    'coolingFactor': 0.95,
                    'minTemp': 1.0}
        else:
            self.layout = self.set_cose_layout

    def set_cose_bilkent_layout(self):
        if self.layout == self.set_cose_bilkent_layout:
            self.pos = None
            return {"name" : "cose-bilkent"}
        else:
            self.layout = self.set_cose_bilkent_layout

    def set_cola_layout(self):
        if self.layout == self.set_cola_layout:
            self.pos = None
            return {"name" : "cola"}
        else:
            self.layout = self.set_cola_layout

    def set_euler_layout(self):
        if self.layout == self.set_euler_layout:
            self.pos = None
            return {"name" : "euler"}
        else:
            self.layout = self.set_euler_layout

    def set_spread_layout(self):
        if self.layout == self.set_spread_layout:
            self.pos = None
            return {"name" : "spread"}
        else:
            self.layout = self.set_spread_layout

    def set_dagre_layout(self):
        if self.layout == self.set_dagre_layout:
            self.pos = None
            return {"name" : "dagre"}
        else:
            self.layout = self.set_dagre_layout

    def set_klay_layout(self):
        if self.layout == self.set_klay_layout:
            self.pos = None
            return {"name" : "klay",
                    'idealEdgeLength': 100,
                    'nodeOverlap': 20,
                    'refresh': 20,
                    'fit': True,
                    'padding': 30,
                    'randomize': False,
                    'componentSpacing': 100,
                    'nodeRepulsion': 400000,
                    'edgeElasticity': 100,
                    'nestingFactor': 5,
                    'gravity': 80,
                    'numIter': 1000,
                    'initialTemp': 200,
                    'coolingFactor': 0.95,
                    'minTemp': 1.0}
        else:
            self.layout = self.set_klay_layout
   
   
    # ---------------------- Pick the node content ----------------------

    def add_node_no_labels(self):
        if self.node_text_preset == self.add_node_no_labels:
            return [None] * len(self.graph_view.nodes())
        else:
            self.node_text_preset = self.add_node_no_labels

    def add_node_adjacency_labels(self):
        if self.node_text_preset == self.add_node_adjacency_labels:
            node_text = []
            if isinstance(self._graph.graph,nx.classes.digraph.DiGraph):
                for node in self.graph_view.nodes:
                    num_in = len(self.graph_view.in_edges(node))
                    num_out = len(self.graph_view.out_edges(node)) 
                    node_text.append(f"# IN: {str(num_in)}, # OUT: {str(num_out)}")

            else:
                for node, adjacencies in enumerate(self.graph_view.adjacency):
                    node_text.append('# of connections: '+ str(len(adjacencies[1])))
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
                        node_text.append(self._get_name(str(edge[2])))
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
        
    def add_node_role_labels(self):
        if self.node_text_preset == self.add_node_role_labels:
            node_texts = []
            nodes = self.graph_view.nodes()
            for node in nodes:
                obj_type = self._graph.graph.get_rdf_type(node)
                if obj_type is None:
                    node_texts.append("No Type")
                    continue
                role = self._graph.graph.get_role(node)
                if role is not None:
                    node_texts.append(self._get_name(str(obj_type)) + " - " + identifiers.translate_role(role))
                    continue
                role = self._graph.graph.get_type(node)
                if role is not None:
                    node_texts.append(self._get_name(str(obj_type)) + " - " + identifiers.translate_role(role))
                    continue
                else:
                    node_texts.append(self._get_name(str(obj_type)))
            
            return node_texts
        else:
            self.node_text_preset = self.add_node_role_labels


    def add_standard_node_size(self):
        if self.node_size_preset == self.add_standard_node_size:
            standard_size = 20
            return [standard_size for node in self.graph_view.nodes()]
        else:
            self.node_size_preset = self.add_standard_node_size

    def add_type_node_size(self):
        from random import randint
        if self.node_size_preset == self.add_type_node_size:
            node_sizes = []
            for node in self.graph_view.nodes():
                if self._graph.graph.get_rdf_type(node) is None:
                    node_sizes.append(10)
                else:
                    node_sizes.append(20)
            return node_sizes
        else:
            self.node_size_preset = self.add_type_node_size

    # ---------------------- Pick the node color ----------------------

    def add_standard_node_color(self):
        if self.node_color_preset == self.add_standard_node_color:
            standard_color = "#888"
            return [{"standard" : standard_color} for node in self.graph_view.nodes()]
        else:
            self.node_color_preset = self.add_standard_node_color

    def add_node_total_adjacency_color(self):
        if self.node_color_preset == self.add_node_total_adjacency_color:
            self._node_edge_colors.clear()
            adj_colors = []
            adj_curr_color = (255,0,0)
            adj_color_map = {}
            for node in self.graph_view.nodes:
                node_adj = len(self.graph_view.in_edges(node)) + len(self.graph_view.out_edges(node)) 
                if node_adj in adj_color_map.keys():
                    pass
                else:
                    adj_color = adj_curr_color
                    adj_color_map[node_adj] = adj_color
                    adj_curr_color = calculate_next_color(adj_curr_color)
                adj_colors.append({str(node_adj) : "rgb" +  str(adj_color)})
            return adj_colors
        else:
            self.node_color_preset = self.add_node_total_adjacency_color
    
    def add_node_in_adjacency_color(self):
        if self.node_color_preset == self.add_node_in_adjacency_color:
            if not isinstance(self.graph_view.graph,nx.classes.digraph.DiGraph):
                raise ValueError("Graph doesnt have input/output edges.")
            self._node_edge_colors.clear()
            adj_colors = []
            adj_curr_color = (255,0,0)
            adj_color_map = {}
            for node in self.graph_view.nodes:
                node_adj = len(self.graph_view.in_edges(node)) 
                if node_adj in adj_color_map.keys():
                    pass
                else:
                    adj_color = adj_curr_color
                    adj_color_map[node_adj] = adj_color
                    adj_curr_color = calculate_next_color(adj_curr_color)
                adj_colors.append({str(node_adj) : "rgb" +  str(adj_color)})
            return adj_colors
        else:
            self.node_color_preset = self.add_node_in_adjacency_color

    def add_node_out_adjacency_color(self):
        if self.node_color_preset == self.add_node_out_adjacency_color:
            if not isinstance(self.graph_view.graph,nx.classes.digraph.DiGraph):
                raise ValueError("Graph doesnt have input/output edges.")
            self._node_edge_colors.clear()
            adj_colors = []
            adj_curr_color = (255,0,0)
            adj_color_map = {}
            for node in self.graph_view.nodes:
                node_adj = len(self.graph_view.out_edges(node)) 
                if node_adj in adj_color_map.keys():
                    pass
                else:
                    adj_color = adj_curr_color
                    adj_color_map[node_adj] = adj_color
                    adj_curr_color = calculate_next_color(adj_curr_color)
                adj_colors.append({str(node_adj) : "rgb" +  str(adj_color)})
            return adj_colors
        else:
            self.node_color_preset = self.add_node_out_adjacency_color

    def add_adaptive_node_color(self):
        if self.node_color_preset == self.add_adaptive_node_color:
            node_colors = []
            node_edge_colors = []
            nodes = self.graph_view.nodes()
            type_curr_color = (255,0,0)
            type_color_map = {"no_type" : (0,0,0)}
            role_color_map = {"no_role" : (0,0,0)}
            for node in nodes:
                obj_type = self._graph.graph.get_rdf_type(node)
                if obj_type is None:
                    type_color = type_color_map["no_type"]
                    obj_type = "No Type"
                else:
                    obj_name = self._get_name(str(obj_type))
                    if obj_name in type_color_map.keys():
                        type_color = type_color_map[obj_name]
                    else:
                        type_color = type_curr_color
                        type_color_map[obj_name] = type_curr_color
                        type_curr_color = calculate_next_color(type_curr_color)
                        
                
                def node_edge_color(role):
                    if role is None:
                        role_color = role_color_map[role]
                    elif role in role_color_map.keys():
                        role_color = role_color_map[role]
                    else:
                        role_color = calculate_role_color(type_color_map[obj_name],role_color_map)
                        role_color_map[role] = role_color

                    role = role.replace(" ","").lower()
                    node_colors.append({self._get_name(obj_type) : "rgb" +  str(type_color)})
                    node_edge_colors.append({self._get_name(role) : "rgb" +  str(role_color)})
                    

                role = self._graph.graph.get_role(node)
                if role is not None:
                    node_edge_color(role)
                    continue
                role = self._graph.graph.get_type(node)
                if role is not None:
                    node_edge_color(role)
                    continue
                else:
                    node_edge_color("no_role")
                    continue

            self._node_edge_colors = node_edge_colors
            return node_colors
        else:
            self.node_color_preset = self.add_adaptive_node_color
    
    
    # ---------------------- Pick the edge color ----------------------
    def add_standard_edge_color(self):
        if self.edge_color_preset == self.add_standard_edge_color:
            return [{"standard" : "#888"} for e in self.graph_view.edges]
        else:
            self.edge_color_preset = self.add_standard_edge_color

    def add_adaptive_edge_color(self):
        edge_colors = []
        if self.edge_color_preset == self.add_adaptive_edge_color:
            edges = self.graph_view.edges
            curr_color = (255,0,0)
            color_map = {}
            for u,v in edges:
                edge = edges[u,v]
                predicate = edge["triples"][0][1]
                predicate_type = self._get_name(predicate)
                if predicate_type in color_map.keys():
                    color = color_map[predicate_type]
                else:
                    color = curr_color
                    color_map[predicate_type] = curr_color
                    curr_color = calculate_next_color(curr_color)
                
                edge_colors.append({self._get_name(predicate_type) : "rgb" +  str(color)})

            return edge_colors
        else:
            self.edge_color_preset = self.add_adaptive_edge_color

    # ---------------------- Pick the edge content ----------------------
    def add_edge_no_labels(self):
        if self.edge_text_preset == self.add_edge_no_labels:
            return [None] * len(self.graph_view.edges())
        else:
            self.edge_text_preset = self.add_edge_no_labels

    def add_edge_name_labels(self):
        if self.edge_text_preset == self.add_edge_name_labels:
            edge_names = []
            for index,edge in enumerate(self.graph_view.edges(data=True)):
                edge_names.append(edge[2]["display_name"])
            return edge_names
        else:
            self.edge_text_preset = self.add_edge_name_labels

    
    # ---------------------- Set Node Shape ----------------------
    def set_adaptive_node_shape(self):
        if self._node_shape_preset == self.set_adaptive_node_shape:
            default_shape = self.cyto_shapes[0]
            cyto_shapes = self.cyto_shapes[1:]
            node_shapes = []
            shape_map = {"no_type" : default_shape}
            counter = 0
            nodes = self.graph_view.nodes()
            for node in nodes:
                obj_type = self._graph.graph.get_rdf_type(node)
                if obj_type is None:
                    shape = shape_map["no_type"]
                    obj_type = "No Type"
                else:
                    obj_type = self._get_name(obj_type)
                    if obj_type in shape_map.keys():
                        shape = shape_map[obj_type]
                    else:
                        shape = cyto_shapes[counter]
                        shape_map[obj_type] = shape
                        if counter == len(cyto_shapes):
                            counter = 0
                        else:
                            counter = counter + 1 
                node_shapes.append({obj_type : shape})
            return node_shapes
        else:
            self._node_shape_preset = self.set_adaptive_node_shape

    def set_circle_node_shape(self):
        if self._node_shape_preset == self.set_circle_node_shape:
            return [{"standard" : "circle"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_circle_node_shape

    def set_square_node_shape(self):
        if self._node_shape_preset == self.set_square_node_shape:
            return [{"standard" : "square"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_square_node_shape

    def set_triangle_node_shape(self):
        if self._node_shape_preset == self.set_triangle_node_shape:
            return [{"standard" : "triangle"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_triangle_node_shape

    def set_rectangle_node_shape(self):
        if self._node_shape_preset == self.set_rectangle_node_shape:
            return [{"standard" : "rectangle"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_rectangle_node_shape

    def set_diamond_node_shape(self):
        if self._node_shape_preset == self.set_diamond_node_shape:
            return [{"standard" : "diamond"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_diamond_node_shape

    def set_hexagon_node_shape(self):
        if self._node_shape_preset == self.set_hexagon_node_shape:
            return [{"standard" : "hexagon"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_hexagon_node_shape

    def set_octagon_node_shape(self):
        if self._node_shape_preset == self.set_octagon_node_shape:
            return [{"standard" : "octagon"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_octagon_node_shape
            
    def set_vee_node_shape(self):
        if self._node_shape_preset == self.set_vee_node_shape:
            return [{"standard" : "vee"} for node in self.graph_view.nodes]
        else:
            self._node_shape_preset = self.set_vee_node_shape
    
    
    # ---------------------- Set edge shape ----------------------
    def set_straight_edge_shape(self):
        self.edge_shape = "straight"

    def set_bezier_edge_shape(self):
        self.edge_shape = "bezier"

    def set_taxi_edge_shape(self):
        self.edge_shape = "taxi"

    def set_unbundled_bezier_edge_shape(self):
        self.edge_shape = "unbundled-bezier"
        
    def set_loop_edge_shape(self):
        self.edge_shape = "loop"

    def set_haystack_edge_shape(self):
        self.edge_shape = "haystack"

    def set_segments_edge_shape(self):
        self.edge_shape = "segments"
   
  # ---------------------- Misc Settings ---------------------
    def edge_width(self,width = None): 
        if width is None:
            return self._edge_width
        self._edge_width = float(width)

    def node_text_size(self,size = None):
        if size is None:
            return self._node_text_size
        self._node_text_size = float(size)

    def edge_text_size(self,size = None):
        if size is None:
            return self._edge_text_size
        self._edge_text_size = float(size)

    def build(self,layout_elements = {},show=True):
        elements = []
        stylesheet = []
        temp_node_selectors = []
        temp_edge_selectors = []

        self.mode()
        if self.layout != self.graph_view.graph and self.layout is not None:
            # Builtin presets will calculate the positons.
            layout = self.layout()
        elif self.pos == [] and self.pos is None:
            raise ValueError("Unable to visualise with no positional data.")

        if self.node_text_preset is not None:
            node_text = self.node_text_preset()
            stylesheet.append({'selector': 'node','style': {'content': 'data(label)',
                                                            "height" : "data(size)",
                                                            "width" : "data(size)",
                                                            "font-size" : self._node_text_size}})
        node_color = self.node_color_preset()
        node_shapes = self._node_shape_preset()
        node_sizes = self.node_size_preset()
        cyto_nodes = []
        for index,node in enumerate(self.graph_view.nodes(data=True)):
            label = node[1]
            node = node[0]
            color_key =  list(node_color[index].keys())[0]
            node_shape = node_shapes[index]
            node_size = node_sizes[index]
            node_shape_value = str(list(node_shape.values())[0])

            try:
                node_edge_color_key = list(self._node_edge_colors[index].keys())[0]
                node_edge_color_color = self._node_edge_colors[index][node_edge_color_key]
                node_edge_color_key = node_edge_color_key.lower()
            except IndexError:
                node_edge_color_key = "no_edge_color"
                node_edge_color_color = "#888"

            try:
                parent = label["parent"]
            except KeyError:
                parent = None
            try:
                is_parent = label["is_parent"]
            except KeyError:
                is_parent = False
                
            if is_parent:
                cyto_node = {
                    'data': {'id': node, 'label': node_text[index], 'parent' : parent,"size" : node_size},
                    "classes" : "top-center " + "parent"
                }

            else:
                cyto_node = {
                    'data': {'id': node, 'label': node_text[index], 'parent' : parent,"size" : node_size},
                    "classes" : "top-center " + color_key + " " + node_edge_color_key + " " + node_shape_value,
                }

                if color_key not in temp_node_selectors:
                    stylesheet.append({"selector" : "." + color_key,"style" : {"background-color" : node_color[index][color_key]}})    
                    temp_node_selectors.append(color_key)                             
                if node_edge_color_key not in temp_edge_selectors:
                    stylesheet.append({"selector" : "." + node_edge_color_key,"style" : {"border-color": node_edge_color_color,
                                                                                        "border-width": "3"}})                                    
                    temp_edge_selectors.append(node_edge_color_key)

            if self.pos != [] and self.pos is not None:
                cyto_node["position"] = {'x': 2000 * self.pos[node][0], 'y': 2000 * self.pos[node][1]}
            cyto_nodes.append(cyto_node)


        cyto_edges = []
        if self.edge_text_preset is not None:
            edge_text = self.edge_text_preset()
        else:
            edge_text = ["" for e in self.graph_view.edges]

        stylesheet.append({'selector': 'edge','style': {'content': 'data(label)',
                                                'height' : self._edge_width,
                                                "width" : self._edge_width,
                                                "mid-target-arrow-color": "grey",
                                                "mid-target-arrow-shape": "triangle",
                                                "font-size" : self._edge_text_size}})
        if self.edge_color_preset is not None:
            edge_color = self.edge_color_preset()  
        
        for index,e in enumerate(self.graph_view.edges(data=True)):
            u,v,edge  = e
            color_key =  list(edge_color[index].keys())[0]
            cyto_edge = {
                'data': {'source': u, 'target': v, 'label': edge_text[index]},
                "classes" : "center-right " + color_key,
                "size" : self._edge_width
            }

            if color_key not in temp_edge_selectors:
                stylesheet.append({"selector" : "." + color_key,"style" : {"line-color" : edge_color[index][color_key],
                                                                            'curve-style': self.edge_shape,
                                                                            "mid-target-arrow-color": edge_color[index][color_key],
                                                                            "mid-target-arrow-shape": "triangle"}})
                temp_edge_selectors.append(color_key)
            cyto_edges.append(cyto_edge)

        stylesheet.append({
        'selector': ':selected',
        "style": {
            "background-color" : "white",
            "border-width": 2,
            "border-color": "black",
            "label": "data(label)",
            'z-index': 9999
        }})
        for shape in self.cyto_shapes:
            stylesheet.append({
                'selector': '.' + shape,
                'style': {
                    'shape': shape
                }})

        self.elements = elements + cyto_nodes + cyto_edges
        figure = cyto.Cytoscape(
            id='cytoscape_graph',
            layout=layout,
            style={'width': '100%', 'height': '1200px'},
            elements=self.elements,
            stylesheet = stylesheet
        )
        return figure
    
    def _create_empty_figure(self):
        return cyto.Cytoscape(
            id='cytoscape_graph',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '400px'},
            elements=[
            ]
        )

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', uri)