from builder.sbol_graph import SBOLGraph
from builder.utility import participation_direction
from builder.utility import valid_participant_types
from builder.utility import get_name
from util.sbol_identifiers import identifiers

class GraphBuilder:
    def __init__(self,graph,prune=False):
        self._graph = SBOLGraph(graph,prune)

    @property
    def nodes(self):
        return self._graph.nodes
    @property
    def edges(self):
        return self._graph.edges

    @property
    def graph(self):
        return self._graph
        
    @graph.setter
    def graph(self,graph):
        self._graph = graph
        
    def produce_full_graph(self):
        return self._graph.graph

    def produce_components_graph(self):
        cd_edges = []
        for cd,node,edge in self._graph.get_component_definitions():
            components = self._graph.get_components(cd)
            cd_edges += [(cd,c,edge) for c in components]
        parts_graph = self._graph.sub_graph(cd_edges)
        return parts_graph


    def produce_interaction_graph(self):
        interaction_edges = []
        for md,interaction,edge  in self._graph.get_interactions():
            participations = [p[1] for p in self._graph.get_participations(interaction)]
            if len(participations) == 1:
                participation = participations[0][1]
                cd1 = self._graph.get_component_definition(participation=participation)
                p_type = self._graph.get_role(participation)
                i_type = self._graph.get_type(interaction)
                interaction_edges += participation_direction(cd1,cd1,p_type,p_type,i_type)
                continue
            for p1 in participations:
                cd1 = self._graph.get_component_definition(participation=p1)
                p1_type = self._graph.get_role(p1)
                i_type = self._graph.get_type(interaction)
                for p2 in participations:
                    if p1 == p2:
                        continue
                    p2_type = self._graph.get_role(p2)
                    if not valid_participant_types(p1_type,p2_type):
                        continue
                    cd2 = self._graph.get_component_definition(participation=p2)
                    interaction_edges += participation_direction(cd1,cd2,p1_type,p2_type,i_type)
        interaction_graph = self._graph.sub_graph(interaction_edges)
        return interaction_graph


    def produce_protein_protein_interaction_graph(self):
        ppi_edges = []
        node_attrs = {}
        interaction_graph = self.produce_interaction_graph()
        for n in interaction_graph.nodes(data=True):
            name = n[0]
            labels = n[1]
            cd_type = self._graph.get_type(name)
            if cd_type != identifiers.external.component_definition_protein:
                continue
            node_edges = interaction_graph.edges(name,data=True)
            if node_edges == []:
                continue
            for node,vertex,edge in node_edges:
                interaction_type = edge["triples"][0][1]
                def handle_edge(vertex):
                    vertex_type = self._graph.get_type(vertex)
                    if vertex_type == identifiers.external.component_definition_protein:
                        node_attrs[name] = labels
                        node_attrs[vertex] = self.nodes[vertex]
                        ppi_edge = {'triples': [(name,interaction_type,vertex)], 
                                    'weight': 1, 
                                    'display_name': identifiers.external.get_interaction_type_name(interaction_type)}
                        ppi_edges.append((name,vertex,ppi_edge))
                    else:
                        inner_edges = interaction_graph.edges(vertex,data=True)
                        for e in inner_edges:
                            handle_edge(e[1])
                    return None
                handle_edge(vertex)
        ppi_graph = self._graph.sub_graph(ppi_edges,node_attrs=node_attrs)
        return ppi_graph



