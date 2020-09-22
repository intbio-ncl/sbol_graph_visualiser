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
        self.edge_shape = "straight"
        self._node_edge_colors = []


    def copy_settings(self):
        current_settings = [
            self.layout,
            self.node_text_preset,
            self.edge_text_preset,
            self.node_color_preset,
            self.edge_color_preset,
        ]

        return current_settings


    def set_preset_layout(self):
        if self.layout == self.set_preset_layout:
            return {"name" : "preset"}
        else:
            self.layout = self.set_preset_layout

    def set_random_layout(self):
        if self.layout == self.set_random_layout:
            return {"name" : "random"}
        else:
            self.layout = self.set_random_layout

    def set_grid_layout(self):
        if self.layout == self.set_grid_layout:
            row_num = cols_num = (math.ceil(math.sqrt(len(self._graph.nodes)))) 

            return {"name" : "grid",
                    "rows" : row_num,
                    "cols" : cols_num}
        else:
            self.layout = self.set_grid_layout

    def set_semi_circular_layout(self):
        if self.layout == self.set_semi_circular_layout:
            return {"name" : "circle",
                    'radius': 250,
                    'startAngle': math.pi * 1/6,
                    'sweep': math.pi * 2/3}
        else:
            self.layout = self.set_semi_circular_layout

    def set_concentric_layout(self):
        if self.layout == self.set_concentric_layout:
            return {"name" : "concentric"}
        else:
            self.layout = self.set_concentric_layout

    def set_breadthfirst_layout(self):
        if self.layout == self.set_breadthfirst_layout:
            return {"name" : "breadthfirst",
                    'directed': True,}
        else:
            self.layout = self.set_breadthfirst_layout

    def set_cose_layout(self):
        if self.layout == self.set_cose_layout:
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
            return {"name" : "cose-bilkent"}
        else:
            self.layout = self.set_cose_bilkent_layout

    def set_cola_layout(self):
        if self.layout == self.set_cola_layout:
            return {"name" : "cola"}
        else:
            self.layout = self.set_cola_layout

    def set_euler_layout(self):
        if self.layout == self.set_euler_layout:
            return {"name" : "euler"}
        else:
            self.layout = self.set_euler_layout

    def set_spread_layout(self):
        if self.layout == self.set_spread_layout:
            return {"name" : "spread"}
        else:
            self.layout = self.set_spread_layout

    def set_dagre_layout(self):
        if self.layout == self.set_dagre_layout:
            return {"name" : "dagre"}
        else:
            self.layout = self.set_dagre_layout

    def set_klay_layout(self):
        if self.layout == self.set_klay_layout:
            return {"name" : "klay"}
        else:
            self.layout = self.set_klay_layout
            
    # ---------------------- Pick the node content ----------------------

    # ---------------------- Pick the edge content ----------------------
    def add_edge_no_labels(self):
        if self.edge_text_preset == self.add_edge_no_labels:
            return [None] * len(self.preset.edges())
        else:
            self.edge_text_preset = self.add_edge_no_labels

    def add_edge_name_labels(self):
        if self.edge_text_preset == self.add_edge_name_labels:
            edge_names = []
            for index,edge in enumerate(self.preset.edges(data=True)):
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

    def add_node_adjacency_color(self):
        if self.node_color_preset == self.add_node_adjacency_color:
            adj_colors = []
            adj_curr_color = (255,0,0)
            adj_color_map = {}
            for node, adjacencies in enumerate(self.preset.adjacency()):
                node_adj = len(adjacencies[1])
                if node_adj in adj_color_map.keys():
                    pass
                else:
                    adj_color = adj_curr_color
                    adj_color_map[node_adj] = adj_color
                    adj_curr_color = calculate_next_color(adj_curr_color)
                adj_colors.append({str(node_adj) : "rgb" +  str(adj_color)})
            return adj_colors
        else:
            self.node_color_preset = self.add_node_adjacency_color
    
    def add_adaptive_node_color(self):
        if self.node_color_preset == self.add_adaptive_node_color:
            node_colors = []
            node_edge_colors = []
            nodes = self.preset.nodes()
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
            edges = self.preset.edges
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
    

    def build(self,layout_elements = {},show=True):
        elements = []
        stylesheet = []
        temp_node_selectors = []
        temp_edge_selectors = []
        if self.layout != self.preset and self.layout is not None:
            # Builtin presets will calculate the positons.
            layout = self.layout()

        elif self.pos == [] and self.pos is None:
            raise ValueError("Unable to visualise with no positional data.")

        if self.node_text_preset is not None:
            node_text = self.node_text_preset()
            stylesheet.append({'selector': 'node','style': {'content': 'data(label)',
                                                            "height" : self._node_size,
                                                            "width" : self._node_size}})
        if self.node_color_preset is not None:
            node_color = self.node_color_preset()
        cyto_nodes = []
        for index,node in enumerate(self.preset.nodes()):
            color_key =  list(node_color[index].keys())[0]
            try:
                node_edge_color_key = list(self._node_edge_colors[index].keys())[0]
                node_edge_color_color = self._node_edge_colors[index][node_edge_color_key]
                node_edge_color_key = node_edge_color_key.lower()
            except IndexError:
                node_edge_color_key = "no_edge_color"
                node_edge_color_color = "#888"

            cyto_node = {
                'data': {'id': node, 'label': node_text[index]},
                "classes" : "top-center " + color_key + " " + node_edge_color_key,
            }
            if self.pos != [] and self.pos is not None:
                cyto_node["position"] = {'x': 2000 * self.pos[node][0], 'y': 2000 * self.pos[node][1]}
            cyto_nodes.append(cyto_node)


            if color_key not in temp_node_selectors:
                stylesheet.append({"selector" : "." + color_key,"style" : {"background-color" : node_color[index][color_key]}})    
                temp_node_selectors.append(color_key)                             
            if node_edge_color_key not in temp_edge_selectors:
                stylesheet.append({"selector" : "." + node_edge_color_key,"style" : {"border-color": node_edge_color_color,
                                                                                     "border-width": self._node_edge_size}})                                    
                temp_edge_selectors.append(node_edge_color_key)






        cyto_edges = []
        if self.edge_text_preset is not None:
            edge_text = self.edge_text_preset()
        else:
            edge_text = ["" for e in self.preset.edges]

        stylesheet.append({'selector': 'edge','style': {'content': 'data(label)',
                                                'height' : self._edge_width,
                                                "width" : self._edge_width,
                                                "mid-target-arrow-color": "grey",
                                                "mid-target-arrow-shape": "triangle"}})
        if self.edge_color_preset is not None:
            edge_color = self.edge_color_preset()  
        
        for index,e in enumerate(self.preset.edges(data=True)):
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