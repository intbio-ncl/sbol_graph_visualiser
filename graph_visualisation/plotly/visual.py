import sys,os
import plotly.graph_objects as go
import networkx as nx
from graph_builder.networkx_wrapper import NetworkXGraphWrapper

sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from rdflib import URIRef,Literal
from sbol_rdflib_identifiers import identifiers
from color_util import SBOLTypeColors,SBOLPredicateColors,calculate_next_color,calculate_role_color


class PlotlyVisualiser:
    def __init__(self, graph = None):
        if isinstance(graph,NetworkXGraphWrapper):
            self._graph = graph
        else:
            self._graph = NetworkXGraphWrapper(graph)

        self.preset = self._graph.graph
        self.layout = self.set_spring_layout
        self.pos = []
        self.node_text_preset = self.add_node_no_labels
        self.edge_text_preset = None
        self.node_color_preset = self.add_standard_node_color
        self.edge_color_preset = self.add_standard_edge_color
        self.node_marker_type = "markers"
        self.edge_marker_type = "markers"
        self.misc_node_settings = {
                                   "legends" : [],
                                   "marker" : {"line" : dict(width=3,color='#FA8072'),
                                               "size" : 15}
                                    }
        self.misc_edge_settings = {"legends" : [],
                                  "line" : {"width" : 1.0}}
        self.edge_pos = []
        self.node_pos = []

    def _set_positions(self):
        self.edge_pos = []
        self.node_pos = []
        if self.pos == []:
            raise ValueError("Unable to set position as no layout has been defined.")
        for edge in self.preset.edges():
            x0, y0 = self.pos[edge[0]]
            x1, y1 = self.pos[edge[1]]
            self.edge_pos.append([[x0,y0],[x1,y1]])
        for node in self.preset.nodes():
            x, y = self.pos[node]
            self.node_pos.append([x,y])


    # ---------------------- Set Preset (Set a sub-graph) ----------------------
    def set_full_graph_preset(self):
        '''
        :type: preset
        Sets the rendered graph as the default graph (Whole graph.)
        :rtype: None
        '''
        # Shouldn't need to set positions when swapping to orig graph as they already have there positions bound.
        # If a preset is added that introduces nodes that are not in the orig graph then 
        # potentially the positions must be recalulated.
        # Kept it like this as noticable performance drop.
        self.preset = self._graph.graph

    def set_interaction_preset(self):
        ''' 
        :type: preset
        Sets the rendered graph as a graph displaying interactions between parts.
        Nodes - ComponentDefinitions
        Edges - Interactions
        :rtype: None
        '''
        self._set_positions()
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
        self._set_positions()
        components_preset = self._graph.produce_components_preset()
        self.preset = components_preset

    def set_parts_preset(self):
        self._set_positions()
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
        self._set_positions()
        functional_graph = self._graph.produce_functional_preset()
        self.preset = functional_graph

    def set_parent_preset(self):
        self._set_positions()
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
            self._set_positions()
        else:
            self.layout = self.set_spring_layout

    def set_circular_layout(self):
        ''' 
        Draw the specified graph with a circular layout. 
        :rtype: None
        '''
        if self.layout == self.set_circular_layout:
            self.pos = nx.circular_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_circular_layout

    def set_kamada_kawai_layout(self):
        ''' 
        Draw the graph G with a Kamada-Kawai force-directed layout.
        :rtype: None
        '''
        if self.layout == self.set_kamada_kawai_layout:
            self.pos = nx.kamada_kawai_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_kamada_kawai_layout

    def set_planar_layout(self):
        ''' 
        Draw a planar graph with planar layout.
        :rtype: None
        '''
        if self.layout == self.set_planar_layout:
            self.pos = nx.planar_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_planar_layout

    def set_shell_layout(self):
        ''' 	
        Draw graph with shell layout.
        :rtype: None
        '''
        if self.layout == self.set_shell_layout:
            self.pos = nx.shell_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_shell_layout

    def set_spiral_layout(self):
        ''' 	
        Position nodes in a spiral layout.
        :rtype: None
        '''
        if self.layout == self.set_spiral_layout:
            self.pos = nx.spiral_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_spiral_layout
            
    def set_spectral_layout(self):
        ''' 	
        Position nodes using the eigenvectors of the graph Laplacian.
        :rtype: None
        '''
        if self.layout == self.set_spectral_layout:
            self.pos = nx.spectral_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_spectral_layout
            
    def set_random_layout(self):
        ''' 	
        Position nodes uniformly at random in the unit square.
        :rtype: None
        '''
        if self.layout == self.set_random_layout:
            self.pos = nx.random_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_random_layout
            
    def set_graphviz_layout(self):
        ''' 	
        Create node positions using Graphviz.
        :rtype: None
        '''
        if self.layout == self.set_graphviz_layout:
            self.pos = nx.nx_agraph.graphviz_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_graphviz_layout
            
    def set_pydot_layout(self):
        ''' 	
        Create node positions using pydot.
        :rtype: None
        '''
        if self.layout == self.set_pydot_layout:
            self.pos = nx.nx_pydot.pydot_layout(self.preset)
            self._set_positions()
        else:
            self.layout = self.set_pydot_layout
            
    # ---------------------- Pick the node content ----------------------

    def add_node_no_labels(self):
        if self.node_text_preset == self.add_node_no_labels:
            return [None] * len(self.preset.nodes())
        else:
            self.node_text_preset = self.add_node_no_labels

    def add_node_adjacency_labels(self):
        if self.node_text_preset == self.add_node_adjacency_labels:
            node_text = []
            for node, adjacencies in enumerate(self.preset.adjacency()):
                node_text.append('# of connections: '+str(len(adjacencies[1])))
            return node_text
        else:
            self.node_text_preset = self.add_node_adjacency_labels

    def add_node_name_labels(self):
        if self.node_text_preset == self.add_node_name_labels:
            node_text = []
            names = nx.get_node_attributes(self.preset,"display_name")
            for v in names.values():
                node_text.append(v)
            return node_text
        else:
            self.node_text_preset = self.add_node_name_labels
    
    def add_node_type_labels(self):
        if self.node_text_preset == self.add_node_type_labels:
            node_text = []
            for node in self.preset.nodes:
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
            for node in self.preset.nodes:
                edges = [[e for e in edge[2]["triples"]] for edge in self.preset.edges(node,data=True)]
                node_type = self._graph.triplepack_search((node,identifiers.predicates.rdf_type,None),edges)
                if node_type is None:
                    node_text.append("N/A")
                    continue
                if node_type in identifiers.objects.top_levels:
                    node_text.append("Top Level")
                    continue
                node_type = node_type[2]
                parent = self._graph._get_parent(node,edges,self.preset.edges)
                if parent is None:
                    node_text.append("No Parent")
                else:
                    node_text.append(self._graph._get_name(str(parent)))
            return node_text
        else:
            self.node_text_preset = self.add_node_parent_labels

    # ---------------------- Pick the edge content ----------------------

    def add_edge_no_labels(self):
        if self.edge_text_preset == self.add_edge_no_labels:
            return []
        else:
            self.edge_text_preset = self.add_edge_no_labels

    def add_edge_name_labels(self):
        if self.edge_text_preset == self.add_edge_name_labels:
            edge_names = []
            for index,edge in enumerate(self.preset.edges(data=True)):
                edge_colour = self.misc_edge_settings["line"]["color"][index]
                marker = dict(color = edge_colour,opacity = 0)
                x0, y0 = self.pos[edge[0]]
                x1, y1 = self.pos[edge[1]]
                edge_names.append(dict(type='scatter',
                            x=[(x0 + x1) / 2],
                            y=[(y0 + y1) / 2],
                            mode=self.edge_marker_type,
                            hoverinfo='text',
                            text=edge[2]["display_name"],
                            showlegend=False,
                            marker=marker))
            return edge_names
        else:
            self.edge_text_preset = self.add_edge_name_labels

    # ---------------------- Pick the node color ----------------------

    def add_standard_node_color(self):
        if self.node_color_preset == self.add_standard_node_color:
            self.misc_node_settings["legends"].clear()
            nodes = self.preset.nodes()
            standard_color = "#888"
            hide_legend = {"showlegend" : False}
            self.misc_node_settings["marker"]["line"]["color"] = ["#800000" for e in nodes]
            self.misc_node_settings["legends"] = self.misc_node_settings["legends"] + [hide_legend for e in nodes]
            return [standard_color for e in nodes]
        else:
            self.node_color_preset = self.add_standard_node_color

    def add_node_adjacency_color(self):
        if self.node_color_preset == self.add_node_adjacency_color:
            self.misc_node_settings["legends"].clear()
            legends = []
            adj_colors = []
            adj_curr_color = (255,0,0)
            adj_color_map = {}
            for node, adjacencies in enumerate(self.preset.adjacency()):
                node_adj = len(adjacencies[1])
                if node_adj in adj_color_map.keys():
                    adj_colors.append(adj_color_map[node_adj])
                else:
                    adj_color = adj_curr_color
                    adj_color_map[node_adj] = adj_color
                    adj_colors.append(adj_color)
                    adj_curr_color = calculate_next_color(adj_curr_color)
                adj = [node_adj]
                legends = self._produce_legend(adj,legends)
                

            self.misc_node_settings["marker"]["line"]["color"] = ["rgb" + str(u) for u in adj_colors]
            self.misc_node_settings["legends"] = self.misc_node_settings["legends"] + legends
            return ["rgb" + str(u) for u in adj_colors]
        else:
            self.node_color_preset = self.add_node_adjacency_color


    def add_adaptive_node_color(self):
        if self.node_color_preset == self.add_adaptive_node_color:

            self.misc_node_settings["legends"].clear()
            legends = []
            nodes = self.preset.nodes()
            type_curr_color = (255,0,0)
            type_color_map = {"no_type" : (0,0,0)}
            role_color_map = {"" : (0,0,0)}
            for node in nodes:
                obj_type = self._graph.retrieve_node(node,identifiers.predicates.rdf_type)
                if obj_type is None:
                    type_color = type_color_map["no_type"]
                    obj_type = None
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
                    role = ""
                    role_color = role_color_map[role]
                elif role in role_color_map.keys():
                    role_color = role_color_map[role]
                else:
                    role_color = calculate_role_color(type_color_map[obj_name],role_color_map)
                    role_color_map[role] = role_color

                nodes[node]["type_color"] = type_color
                nodes[node]["role_color"] = role_color

                obj_names = [obj_name,role]
                legends = self._produce_legend(obj_names,legends)

            self.misc_node_settings["marker"]["line"]["color"] = ["rgb" + str(nodes[u]['role_color']) for u in nodes]
            self.misc_node_settings["legends"] = self.misc_node_settings["legends"] + legends
            
            return ["rgb" + str(nodes[u]['type_color']) for u in nodes]
        else:
            self.node_color_preset = self.add_adaptive_node_color

    # ---------------------- Pick the edge color ----------------------

    def add_standard_edge_color(self):
        if self.edge_color_preset == self.add_standard_edge_color:
            self.misc_edge_settings["legends"].clear()
            edges = self.preset.edges
            standard_color = "#888"
            hide_legend = {"showlegend" : False}
            self.misc_edge_settings["legends"] = self.misc_edge_settings["legends"] + [hide_legend for e in edges]
            self.misc_edge_settings["line"]["color"] = [standard_color for e in edges]
            return [standard_color for e in edges]
        else:
            self.edge_color_preset = self.add_standard_edge_color

    def add_adaptive_edge_color(self):
        if self.edge_color_preset == self.add_adaptive_edge_color:
            self.misc_edge_settings["legends"].clear()
            edges = self.preset.edges
            curr_color = (255,0,0)
            color_map = {}
            legends = []
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

                predicate_names = [predicate_type]
                legends = self._produce_legend(predicate_names,legends)
                
            self.misc_edge_settings["line"]["color"] = ["rgb" + str(edges[u,v]['edge_color']) for u,v in edges]
            self.misc_edge_settings["legends"] = self.misc_edge_settings["legends"] + legends
            return ["rgb" + str(edges[u,v]['edge_color']) for u,v in edges]
        else:
            self.edge_color_preset = self.add_adaptive_edge_color


    # ---------------------- Set sizes ----------------------
    def node_size(self,size = None):
        if size is None:
            return self.misc_node_settings["marker"]["size"] 
        self.misc_node_settings["marker"]["size"] = float(size)

    def node_edge_size(self,width = None):
        if width is None:
            return self.misc_node_settings["marker"]["line"]["width"]
        self.misc_node_settings["marker"]["line"]["width"] = float(width)

    def edge_width(self,width = None):
        if width is None:
            return self.misc_edge_settings["line"]["width"]
        self.misc_edge_settings["line"]["width"] = float(width)

    # ---------------------- Misc Settings ----------------------
    def misc_node_label_persistence(self,is_persistent = None):
        if is_persistent is None:
            if self.node_marker_type == "markers+text":
                return True
            else:
                return False
        if is_persistent:
            self.node_marker_type = "markers+text"
        else:
            self.node_marker_type = "markers"    
    
    def misc_edge_label_persistence(self,is_persistent = None):
        if is_persistent is None:
            if self.edge_marker_type == "markers+text":
                return True
            else:
                return False
        if is_persistent:
            self.edge_marker_type = "markers+text"
        else:
            self.edge_marker_type = "markers"    

    def build(self,layout_elements = {},show=True):
        if self.preset is None:
            raise ValueError("No preset defined.")

        if self.layout is None:
            raise ValueError("Unable to visualise with no positional data.")
        self.layout()
        
        if self.pos == []:
            raise ValueError("Unable to visualise with no positional data.")
        
        data = []
        edge_color = self.edge_color_preset()  
        edges_list = []
        for index, e in enumerate(self.edge_pos):
            line = self._get_specific_node_settings(index,self.misc_edge_settings["line"])
            line["color"] = edge_color[index]
            if len(self.misc_edge_settings["legends"]) > index:
                legend = self.misc_edge_settings["legends"][index]
            else:
                legend = {}
            edges_list.append(dict(type='scatter',
                        x=[e[0][0],e[1][0]],
                        y=[e[0][1],e[1][1]],
                        mode='lines',
                        hoverinfo='none',
                        line=line,
                        **legend))
        data = data + edges_list


        if self.node_text_preset is not None:
            node_text = self.node_text_preset()
        if self.node_color_preset is not None:
            node_color = self.node_color_preset()
        node_list = []
        for index,e in enumerate(self.node_pos):
            # Some settings are generic (Same for all nodes), some are unique
            # When a list appears in the settings its unique so use node pos index to find its value.
            specialised_node_settings = self._get_specific_node_settings(index,self.misc_node_settings["marker"])

            if len(self.misc_node_settings["legends"]) > index:
                legend = self.misc_node_settings["legends"][index]
            else:
                legend = {}
            marker = dict(color = node_color[index],**specialised_node_settings)
            node_list.append(dict(type='scatter',
                                    x=[e[0]],
                                    y=[e[1]],
                                    mode=self.node_marker_type,
                                    hoverinfo='text',
                                    text=node_text[index],
                                    marker=marker,
                                    **legend))
        data = data + node_list


        if self.edge_text_preset is not None:
            data = data + self.edge_text_preset()

        if len(self.misc_node_settings["legends"]) > 0 or  len(self.misc_edge_settings["legends"]) > 0:
            display_legend = True
        else:
            display_legend = False

        fig = go.Figure(data=data,
                        layout=go.Layout(
                            hovermode='closest',
                            showlegend=display_legend,
                            legend = dict(bgcolor = 'rgb(229, 236, 246)'),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            margin=go.layout.Margin(
                                l=0, #left margin
                                r=0, #right margin
                                b=0, #bottom margin
                                t=15, #top margin
                            ),
                            paper_bgcolor="rgb(229, 236, 246)",
                            **layout_elements),

                            )
        if show:
            fig.show()
        else:
            return fig


    def _get_specific_node_settings(self,index,mapping):
        misc_node_settings = {}
        for k,v in mapping.items():
                    if isinstance(v,dict):
                        misc_node_settings[k] = {}
                        for k1,v1 in v.items():
                            if isinstance(v1,(list,tuple,set)):
                                v1 = v1[index]
                            misc_node_settings[k][k1] = v1
                    elif isinstance(v,(list,tuple,set)):
                        misc_node_settings[k] = v[index]
                    else:
                        misc_node_settings[k] = v
        return misc_node_settings

    def _produce_legend(self,names,legends):
        name = ""
        group = ""
        for n in names:
            try:
                name = name + " " + str(n)
            except KeyError:
                name = name + " Unknown"

            group = name
        if name in [n["name"] for n in legends]:
            show = False
        else:
            show = True
        legends.append({"name" : name, "legendgroup" : group, "showlegend" : show})
        return legends

    def _create_empty_figure(self):
        return {
                'data': [],
                'layout': go.Layout(
                    xaxis={
                        'showticklabels': False,
                        'ticks': '',
                        'showgrid': False,
                        'zeroline': False
                    },
                    yaxis={
                        'showticklabels': False,
                        'ticks': '',
                        'showgrid': False,
                        'zeroline': False
                    }
                )
            }
            
if __name__ == "__main__":
    g = PlotlyVisualiser(sys.argv[1])
    g.add_adaptive_node_color()
    g.add_adaptive_node_color()