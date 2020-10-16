import sys,os
import dash
import dash_cytoscape as cyto
cyto.load_extra_layouts()
import dash_html_components as html
import math
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from color_util import SBOLTypeColors,SBOLPredicateColors,calculate_next_color,calculate_role_color
from sbol_rdflib_identifiers import identifiers
from graph_builder.networkx_wrapper import NetworkXGraphWrapper
from graph_visualisation.abstract_visualiser import AbstractVisualiser
import networkx as nx


class CytoscapeVisualiser(AbstractVisualiser):

    def __init__(self, graph = None):
        super().__init__(graph)
        self.elements = []
        self._node_size = 15
        self._edge_width = 1
        self._node_edge_size = 3
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

    # ---------------------- Set Clustering ----------------------------------------------------------------------------------------------

    def set_non_clustering(self):
        self._reset_parent_labels()
        
    def set_type_clustering(self):
        '''
        Definition:
            Cluster as to wether a node has a rdf_type egde.
            Only two levels of clustering.
        '''
        self._reset_parent_labels()
        objects = self.graph_view.search((None,identifiers.predicates.rdf_type,None),)
        for n,v,e in objects:
            node_edges = self.graph_view.edges(n)
            self.graph_view.nodes[n]["is_parent"] = True
            for node_edge in node_edges:
                self.graph_view.nodes[node_edge[1]]["parent"] = n

    def set_parent_clustering(self):
        '''
        Cluster Based on SBOL parent-child relationships.
        TopLevels are roots, Non-TopLevels with rdf-types are branches and leafs, 
        Non-rdf-type elements aren't clustered.
        '''
        def handle_object(element):
            node_edges = self.graph_view.edges(element,data=True)
            for n,v,e in node_edges:
                predicate = e["triples"][0][1]
                if predicate in identifiers.predicates.ownership_predicates:
                    self.graph_view.nodes[n]["is_parent"] = True
                    self.graph_view.nodes[v]["parent"] = element
                elif (predicate == identifiers.predicates.component and 
                self._graph.retrieve_node(n,identifiers.predicates.rdf_type) == identifiers.objects.component_definition):
                    self.graph_view.nodes[n]["is_parent"] = True
                    self.graph_view.nodes[v]["parent"] = element
                node_type = self._graph.retrieve_node(v,identifiers.predicates.rdf_type)
                if node_type is not None:
                    handle_object(v)
        self._reset_parent_labels()
        components = self.graph_view.search((None,identifiers.predicates.rdf_type,None))
        top_levels = [c for c in components if c[1] in identifiers.objects.top_levels]
            
        for obj in top_levels:
            handle_object(obj[0])

    def _reset_parent_labels(self):
        for node in self.graph_view.nodes(data=True):
            try:
                del node[1]["parent"]
            except KeyError:
                pass

            try:
                del node[1]["is_parent"]
            except KeyError:
                pass
    # ---------------------- Set Preset (Sets one or more other settings to focus on a specific thing in the graph) ----------------------
    def set_protein_protein_interaction_preset(self):
        '''
        Master Function to provide insight into Interactions between components.
        '''
        parent_sub_functions = super().set_protein_protein_interaction_preset()
        sub_class_sub_functions = [
            self.set_cola_layout,
            self.add_adaptive_edge_color,
            self.add_edge_name_labels]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_interaction_preset(self):
        '''
        Master Function to provide insight into Interactions between components.
        '''
        parent_sub_functions = super().set_interaction_preset()
        sub_class_sub_functions = [
            self.set_klay_layout,
            self.add_adaptive_node_color,
            self.add_adaptive_edge_color,
            self.add_edge_name_labels]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_parts_preset(self):
        '''
        Master Function to provide insight into heiraachy of components.
        '''
        parent_sub_functions = super().set_parts_preset()
        sub_class_sub_functions = [
            self.set_dagre_layout,
            self.add_adaptive_node_color]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_parent_preset(self):
        '''
        Master Function to provide insight into parent-child relationship between sbol elements.
        '''
        parent_sub_functions = super().set_parent_preset()
        sub_class_sub_functions = [
            self.set_breadthfirst_layout,
            self.add_edge_name_labels,
            self.add_adaptive_node_color,
            self.add_adaptive_edge_color]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_adjacency_preset(self):
        parent_sub_functions = super().set_adjacency_preset()
        sub_class_sub_functions = [
            self.set_circular_layout,
            self.add_edge_no_labels,
            self.add_node_total_adjacency_color
        ]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_functional_preset(self):
        '''
        Master Function to provide insight into the Functional aspect of a graph.
        '''
        parent_sub_functions = super().set_functional_preset()

        sub_class_sub_functions = [
            self.set_concentric_layout,
            self.add_adaptive_node_color
        ]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_component_preset(self):
        '''
        Master Function to display interconected components of the graph.
        '''
        parent_sub_functions = super().set_component_preset()
        sub_class_sub_functions = [
            self.set_dagre_layout,
            self.add_adaptive_node_color,
            self.add_edge_no_labels
        ]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_combinatorial_derivation_preset(self):
        '''
        Master Function to attempt to make a preset that makes cbd more easy to understabd
        '''
        parent_sub_functions = super().set_combinatorial_derivation_preset()
        sub_class_sub_functions = [
            self.set_breadthfirst_layout,
            self.add_edge_name_labels,
            self.add_adaptive_node_color,
            self.add_adaptive_edge_color
        ]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)
        
    def set_common_part_preset(self):
        '''
        Master Function to attempt to make common parts between constructs more visible.
        '''
        parent_sub_functions = super().set_common_part_preset()
        sub_class_sub_functions = [
            self.set_breadthfirst_layout,
            self.add_edge_no_labels,
            self.add_node_in_adjacency_color
        ]
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)
    
    def set_glyph_preset(self):
        '''
        Master function to attempt to display the graph in a glyph like form.
        '''
        parent_sub_functions = super().set_glyph_preset()
        sub_class_sub_functions = []
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    def set_DBTL_preset(self):
        '''
        Master Function to provide insight into parent-child relationship between sbol elements.
        '''
        parent_sub_functions = super().set_DBTL_preset()
        sub_class_sub_functions = []
        return parent_sub_functions + self._set_preset(sub_class_sub_functions)

    # ---------------------- Pick a layout ----------------------
    def set_no_layout(self):
        if self.layout == self.set_no_layout:
            self.pos = None
            return {"name" : "preset"}
        else:
            self.layout = self.set_no_layout

    def set_random_layout(self):
        if self.layout == self.set_random_layout:
            self.pos = None
            return {"name" : "random"}
        else:
            self.layout = self.set_random_layout

    def set_grid_layout(self):
        if self.layout == self.set_grid_layout:
            self.pos = None
            row_num = cols_num = (math.ceil(math.sqrt(len(self.graph_view.nodes)))) 

            return {"name" : "grid",
                    "rows" : row_num,
                    "cols" : cols_num}
        else:
            self.layout = self.set_grid_layout

    def set_semi_circular_layout(self):
        if self.layout == self.set_semi_circular_layout:
            self.pos = None
            return {"name" : "circle",
                    'radius': 250,
                    'startAngle': math.pi * 1/6,
                    'sweep': math.pi * 2/3}
        else:
            self.layout = self.set_semi_circular_layout

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

    # ---------------------- Pick the node color ----------------------
    def add_standard_node_color(self):
        if self.node_color_preset == self.add_standard_node_color:
            return [{"standard" : color} for color in super().add_standard_node_color()]
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
                obj_type = self._graph.retrieve_node(node,identifiers.predicates.rdf_type)
                if obj_type is None:
                    type_color = type_color_map["no_type"]
                    obj_type = "No Type"
                else:
                    obj_name = self._graph._get_name(str(obj_type))
                    if obj_name in type_color_map.keys():
                        type_color = type_color_map[obj_name]
                    else:
                        type_color = type_curr_color
                        type_color_map[obj_name] = type_curr_color
                        type_curr_color = calculate_next_color(type_curr_color)
                        
                role = self._graph.get_sbol_object_role(node,obj_type)
                if role is None:
                    role = "no_role"
                    role_color = role_color_map[role]
                elif role in role_color_map.keys():
                    role_color = role_color_map[role]
                else:
                    role_color = calculate_role_color(type_color_map[obj_name],role_color_map)
                    role_color_map[role] = role_color

                role = role.replace(" ","").lower()
                node_colors.append({self._graph._get_name(obj_type) : "rgb" +  str(type_color)})
                node_edge_colors.append({self._graph._get_name(role) : "rgb" +  str(role_color)})
            
            self._node_edge_colors = node_edge_colors
            return node_colors
        else:
            self.node_color_preset = self.add_adaptive_node_color

    # ---------------------- Pick the edge color ----------------------
    def add_standard_edge_color(self):
        if self.edge_color_preset == self.add_standard_edge_color:
            return [{"standard" : color} for color in super().add_standard_edge_color()]
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
                predicate_type = self._graph._get_name(predicate)
                if predicate_type in color_map.keys():
                    color = color_map[predicate_type]
                else:
                    color = curr_color
                    color_map[predicate_type] = curr_color
                    curr_color = calculate_next_color(curr_color)
                
                edge_colors.append({self._graph._get_name(predicate_type) : "rgb" +  str(color)})

            return edge_colors
        else:
            self.edge_color_preset = self.add_adaptive_edge_color
    
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
                obj_type = self._graph.retrieve_node(node,identifiers.predicates.rdf_type)
                if obj_type is None:
                    shape = shape_map["no_type"]
                    obj_type = "No Type"
                else:
                    obj_type = self._graph._get_name(obj_type)
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

    def set_parts_node_shape(self):
        if self._node_shape_preset == self.set_parts_node_shape:
            default_shape = self.cyto_shapes[0]
            shape_map = {}
            cyto_shapes = self.cyto_shapes[1:]
            node_shapes = {}
            counter = 0
            components = self._graph.search((None,
                identifiers.predicates.rdf_type,[identifiers.objects.component_definition,
                                                identifiers.objects.component,
                                                identifiers.objects.functional_component])) 
            for component in components:
                if not self.graph_view.has_node(component[0]):
                    continue
                predicate = component[2]["triples"][0][2]
                if predicate != identifiers.objects.component_definition:
                    component_definition = self._graph.retrieve_node(component[0],identifiers.predicates.definition)
                    if component_definition is None:
                        raise ValueError(f'{component[0]} is a component with no definition.')
                else:
                    component_definition = component[0]

            
                component_type = self._graph.retrieve_node(component_definition,identifiers.predicates.type)
                if component_type is None:
                    raise ValueError(f'{component[0]} doesnt have a type.')

                component_role = self._graph.retrieve_node(component_definition,identifiers.predicates.role)
                identifier_name = identifiers.external.get_component_definition_identifier_name(component_type,component_role)
                
                if identifier_name in shape_map.keys():
                    shape = shape_map[identifier_name]
                else:
                    shape = cyto_shapes[counter]
                    shape_map[identifier_name] = shape
                    if counter == len(cyto_shapes):
                        counter = 0
                    else:
                        counter = counter + 1 

                node_shapes[component[0]] = {"type" : identifier_name , "shape" : shape}
            
            final_node_shapes = []
            for node in self.graph_view.nodes:
                try:
                    shape = node_shapes[node]
                    shape = {shape["type"] : shape["shape"]}
                except KeyError:
                    shape = {"standard" : default_shape}
                final_node_shapes.append(shape)
            return final_node_shapes
        else:
            self._node_shape_preset = self.set_parts_node_shape

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
    def node_size(self,size = None):
        if size is None:
            return self._node_size
        self._node_size = float(size)

    def node_edge_size(self,width = None):
        if width is None:
            return self._node_edge_size
        self._node_edge_size = float(width)

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
                                                            "height" : self._node_size,
                                                            "width" : self._node_size,
                                                            "font-size" : self._node_text_size}})
        node_color = self.node_color_preset()
        node_shapes = self._node_shape_preset()
        cyto_nodes = []
        for index,node in enumerate(self.graph_view.nodes(data=True)):
            label = node[1]
            node = node[0]
            color_key =  list(node_color[index].keys())[0]
            node_shape = node_shapes[index]
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
                    'data': {'id': node, 'label': node_text[index], 'parent' : parent},
                    "classes" : "top-center " + "parent"
                }

            else:
                cyto_node = {
                    'data': {'id': node, 'label': node_text[index], 'parent' : parent},
                    "classes" : "top-center " + color_key + " " + node_edge_color_key + " " + node_shape_value,
                }

                if color_key not in temp_node_selectors:
                    stylesheet.append({"selector" : "." + color_key,"style" : {"background-color" : node_color[index][color_key]}})    
                    temp_node_selectors.append(color_key)                             
                if node_edge_color_key not in temp_edge_selectors:
                    stylesheet.append({"selector" : "." + node_edge_color_key,"style" : {"border-color": node_edge_color_color,
                                                                                        "border-width": self._node_edge_size}})                                    
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