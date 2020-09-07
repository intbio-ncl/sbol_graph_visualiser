import sys,os
import dash
import dash_cytoscape as cyto
cyto.load_extra_layouts()
import dash_html_components as html

from graph_builder.networkx_wrapper import NetworkXGraphWrapper
import networkx as nx

class CytoscapeVisualiser:
    def __init__(self, graph = None):
        if isinstance(graph,NetworkXGraphWrapper):
            self._graph = graph
        else:
            self._graph = NetworkXGraphWrapper(graph)

        self.preset = self._graph.graph
        self.layout = self.set_breadthfirst_layout
        self.pos = []


    # ---------------------- Set Preset (Set a sub-graph) ----------------------

    # ---------------------- Pick a layout ----------------------

    # Directly - The coordinates are provided via the elements in a position dict.
    def set_spring_layout(self):
        if self.layout == self.set_spring_layout:
            self.pos = nx.spring_layout(self.preset, iterations=200)
            self.layout = self.set_preset_layout
        else:
            self.layout = self.set_spring_layout
    
    def set_my_custom_layout(self):
        if self.layout == self.set_my_custom_layout:
            self.pos = self._tree_layout(self.preset)
        else:
            self.layout = self.set_my_custom_layout

    # Implicitly - Via setting the layout dict key to something other than preset.
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
            return {"name" : "grid"}
        else:
            self.layout = self.set_grid_layout

    def set_circle_layout(self):
        if self.layout == self.set_circle_layout:
            return {"name" : "circle"}
        else:
            self.layout = self.set_circle_layout

    def set_concentric_layout(self):
        if self.layout == self.set_concentric_layout:
            return {"name" : "concentric"}
        else:
            self.layout = self.set_concentric_layout

    def set_breadthfirst_layout(self):
        if self.layout == self.set_breadthfirst_layout:
            return {"name" : "breadthfirst"}
        else:
            self.layout = self.set_breadthfirst_layout

    def set_cose_layout(self):
        if self.layout == self.set_cose_layout:
            return {"name" : "cose"}
        else:
            self.layout = self.set_cose_layout

    def set_cose_bilkent_layout(self):
        if self.layout == self.set_cose_bilkent_layout:
            return {"name" : "cose_bilkent"}
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

    # ---------------------- Pick the node color ----------------------

    # ---------------------- Pick the edge color ----------------------

    # ---------------------- Set sizes ----------------------

    # ---------------------- Misc Settings ---------------------

    def build(self,layout_elements = {},show=True):
        elements = []

        if self.layout != self.preset and self.layout is not None:
            # Builtin presets will calculate the positons.
            layout = self.layout()

        elif self.pos == [] and self.pos is None:
            raise ValueError("Unable to visualise with no positional data.")

        cyto_nodes = []
        for node in self.preset.nodes():
            cyto_node = {
                'data': {'id': node, 'label': node},
                'locked': False
            }
            if self.pos != [] and self.pos is not None:
                cyto_node["position"] = {'x': 2000*self.pos[node][0], 'y': 2000*self.pos[node][1]}
            cyto_nodes.append(cyto_node)


        cyto_edges = []
        for u,v,edge in self.preset.edges(data=True):
            print(type(u),type(v))
            cyto_edge = {
                'data': {'source': u, 'target': v, 'label': 'Node 1 to 2'}
            }

            cyto_edges.append(cyto_edge)


        elements = elements + cyto_nodes + cyto_edges
        figure = cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout=layout,
            style={'width': '100%', 'height': '1000px'},
            elements=elements
        )
        if show:
            figure.show()
        else:
            return figure













    def _create_empty_figure(self):
        return cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '400px'},
            elements=[
            ]
        )