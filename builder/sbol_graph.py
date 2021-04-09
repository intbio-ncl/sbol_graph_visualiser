from builder.graph import GraphWrapper
from util.sbol_identifiers import identifiers

class SBOLGraph:
    def __init__(self,graph,prune=False):
        self._graph = GraphWrapper(graph,prune)
        
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

    def sub_graph(self,edges,node_attrs={}):
        return self._graph.sub_graph(edges,node_attrs)


    def get_rdf_type(self,subject):
        return self._graph.retrieve_node(subject,identifiers.predicates.rdf_type)

    def get_component_definitions(self):
        return self._graph.search((None,identifiers.predicates.rdf_type,
                                identifiers.objects.component_definition))

    def get_component_definition(self,participation=None):
        if participation is not None:
            fc = self._graph.retrieve_node(participation,identifiers.predicates.participant)
            cd = self._graph.retrieve_node(fc,identifiers.predicates.definition)
            return cd
                            
    def get_interactions(self):
        return self._graph.search((None,identifiers.predicates.interaction,None))

    def get_components(self,cd=None,sa=None):
        if cd is not None:
            return self._graph.retrieve_nodes(cd,identifiers.predicates.component)
        if sa is not None:
            return self._graph.retrieve_nodes(sa,identifiers.predicates.component)
        return self._graph.search((cd,identifiers.predicates.component,None))
    
    def get_participations(self,interaction):
        return self._graph.search((interaction,identifiers.predicates.participation,None))
    
    def get_type(self,subject):
        return self._graph.retrieve_node(subject,identifiers.predicates.type)

    def get_role(self,subject):
        return self._graph.retrieve_node(subject,identifiers.predicates.role)

    def get_sequence_annotations(self,cd):
        return self._graph.retrieve_nodes(cd,identifiers.predicates.sequence_annotation)

    def get_sequence_constraints(self,cd):
        return self._graph.retrieve_nodes(cd,identifiers.predicates.sequence_constraint)

    def get_locations(self,sa):
        return self._graph.retrieve_nodes(sa,identifiers.predicates.location)

    def get_functional_components(self):
        return self._graph.search((module_definition[0],identifiers.predicates.functional_component,None))

    def get_component_instances(self):
        return self._graph.search((None,[identifiers.predicates.component,identifiers.predicates.functional_component],None))
    
    def get_definition(self):
        self.retrieve_node(p,identifiers.predicates.definition)

    def get_module_definitions(self):
        return self._graph.search((None,identifiers.predicates.rdf_type,identifiers.objects.module_definition))

    def get_modules(self):
        return self.retrieve_nodes(s,identifiers.predicates.module)
