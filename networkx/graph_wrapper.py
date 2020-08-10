import os
import sys
import re
import copy
import rdflib
import networkx as nx
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from sbol_rdflib_identifiers import identifiers
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_graph, rdflib_to_networkx_digraph

class NetworkXGraphWrapper:
    def __init__(self, graph = None, graph_type = "graph"):
        if graph_type == "graph":
            graph_type = rdflib_to_networkx_graph
        elif graph_type == "directed":
            graph_type = rdflib_to_networkx_digraph
        elif graph_type == "multidirected":
            graph_type = rdflib_to_networkx_multidigraph

        if isinstance(graph,NetworkXGraphWrapper):
            self.graph = copy.deepcopy(graph.graph)
        elif isinstance(graph,rdflib.Graph):
            self.graph = graph_type(copy.deepcopy(graph))
        else:
            self.graph_name = graph
            self.graph = rdflib.Graph()
            if graph is not None:
                self.graph.load(graph)
            self.graph = graph_type(self.graph)
        

        self.prune_nodes = [identifiers.objects.sequence]
        self.prune_edges = [identifiers.predicates.version,
                           identifiers.predicates.display_id,
                           identifiers.predicates.persistent_identity,
                           identifiers.predicates.access,
                           identifiers.predicates.direction,
                           identifiers.predicates.sequence,
                           identifiers.predicates.encoding,
                           identifiers.predicates.elements]
        self._generate_labels()
  

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def edges(self):
        return self.graph.edges
    
    @property
    def adjacency(self):
        return self.graph.adj

    @property
    def degree(self):
        return self.graph.degree

    def shortest_path(self):
        return dict(nx.all_pairs_shortest_path(self.graph))
    
    def density(self):
        return nx.density(self.graph)

    def path_lengths(self):
        path_lengths = []
        for v in self.graph.nodes():
            spl = dict(nx.single_source_shortest_path_length(self.graph, v))
            for p in spl:
                path_lengths.append(spl[p])

        return path_lengths

    def average_shortest_path(self):
        path_lengths = self.path_lengths()
        return (sum(path_lengths) / len(path_lengths))

    def histogram(self):
        pathlengths = self.path_lengths()
        # histogram of path lengths
        dist = {}
        for p in pathlengths:
            if p in dist:
                dist[p] += 1
            else:
                dist[p] = 1
        return dist
    
    def write_graphml(self,fn):
        if isinstance(self.graph,nx.classes.multidigraph.MultiDiGraph):
            new_graph = nx.classes.multidigraph.MultiDiGraph()
        elif isinstance(self.graph,nx.classes.graph.Graph):
            new_graph = nx.classes.graph.Graph()

        for u,v in self.graph.edges:
            orig_edge = self.graph.edges[u,v]
            new_edge = {}
            if "triples" in orig_edge.keys():
                new_edge["predicate"] = str(orig_edge["triples"][0][1])
            else:
                new_edge["predicate"] = "Unknown"
            
            if isinstance(u,rdflib.URIRef):
                u = str(u)
            if isinstance(v,rdflib.URIRef):
                v = str(v)
            print(u,v,new_edge)
            new_graph.add_edges_from([(u,v,new_edge)])
                
        nx.write_graphml(new_graph, fn)

    def search(self,pattern):
        '''
        Given a tuple of size 3 search the graph for the related edge.
        provide None in the index where the search is to be made. 
        :return: list of matches
        :rtype: list
        '''
        matches = []
        (s, p, o) = pattern
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            for subject,node,edge in self.graph.edges:
                if (subject == s or not s) and (edge == p or not p) and (node == o or not o):
                    matches.append((subject,node,edge))

        elif isinstance(self.graph,nx.classes.graph.Graph):
            for subject,node in self.graph.edges:
                edge = self.graph.edges[subject,node]
                triple = edge["triples"][0]
                if (triple[0] == s or not s) and (triple[1] == p or not p) and (triple[2] == o or not o):
                    matches.append((triple[0],triple[2],edge))

        return matches

    def remove(self,edges):
        '''
        Removes Given a list of/single tuple of size two or three removes two 
        nodes and optional edge from graph.
        :rtype: None
        '''
        self.graph.remove_edges_from(edges)
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))

    def add(self,edges):
        '''
        Adds Given a list of/single tuple of size two or three adds two nodes
        and optional edge to graph.
        :rtype: None
        '''
        self.graph.add_edges_from(edges)

    def prune_graph(self, prune_nodes = None, prune_edges = None):
        '''
        Prunes the graph with the intention of simplification.
        Can provide a collection of predicates or if not provided 
        use default list.
        :rtype: None
        '''
        if prune_edges is None:
            prune_edges = self.prune_edges
        elif isinstance(prune_edges,(list,set,tuple)):
            pass
        else:
            prune_edges = [prune_edges]

        if prune_nodes is None:
            prune_nodes = self.prune_nodes
        elif isinstance(prune_nodes,(list,set,tuple)):
            pass
        else:
            prune_nodes = [prune_nodes]

        to_prune_edges = []
        to_prune_nodes = []
        if isinstance(self.graph,nx.classes.multidigraph.MultiDiGraph):
            for n1,n2,edge in self.graph.edges:
                if edge in [p for p in prune_edges]:
                    to_prune_edges.append((n1,n2))
        elif isinstance(self.graph,nx.classes.graph.Graph):
            for n1,n2 in self.graph.edges:
                if n1 in prune_nodes:
                    to_prune_nodes.append(n1)
                if n2 in prune_nodes:
                    to_prune_nodes.append(n2)
                edge = self.graph.edges[n1,n2]
                if "display_name" in edge.keys():
                    if edge["display_name"] in [self._get_name(p) for p in prune_edges]:
                        to_prune_edges.append((n1,n2))

        self.graph.remove_nodes_from(to_prune_nodes)
        self.graph.remove_edges_from(to_prune_edges)
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))

    def get_edge_attributes(self,attribute_name):
        '''
        Each edge can contain meta data, this method provides this.
        :return: Dict of edges mapping to labels/attributes.
        :rtype: dict
        '''
        edge_attributes = {}
        edge_labels = nx.get_edge_attributes(self.graph,attribute_name)
        for (subject,node,edge),v in edge_labels.items():
            edge_attributes[(subject,node)] = v
        return edge_attributes
    
    def produce_parts_preset(self):
        '''
        Creates a SubGraph from the larger graph that displays 
        ComponentDefs and said CD's as subparts of other CD's
        :return: Interaction SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        components = self.search((None,identifiers.predicates.component,None))
        cd_edges = []
        for s,p,o in components:
            cd = self.search((p,identifiers.predicates.definition,None))
            if cd == []:
                raise ValueError(f'{p} is a component with no definition')
            cd = cd[0][1]
            cd_edges.append((s,cd,o))
        
        parts_graph = self._sub_graph(cd_edges)
        return parts_graph
        

    def produce_interaction_graph(self):
        '''
        Creates a SubGraph from the larger graph that displays 
        Interactions between ComponentDefs.
        :return: Interaction SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        interaction_edges = []
        interactions = self.search((None,identifiers.predicates.interaction,None))
        for interaction in interactions:
            done_list = []
            participants = self.search((interaction[1],identifiers.predicates.participation,None))
            for participant1 in participants:
                for participant2 in participants:
                    if participant1 == participant2 or (participant1[2] in done_list and participant2[2] in done_list):
                        continue
                    fc1 = self.search((participant1[1],identifiers.predicates.participant,None))
                    fc2 = self.search((participant2[1],identifiers.predicates.participant,None))
                    if fc1 == []:
                        raise ValueError(f'{participant1[1]} is a participant with no component')
                    if fc2 == []:
                        raise ValueError(f'{participant2[1]} is a participant with no component')

                    cd1 = self.search((fc1[0][1],identifiers.predicates.definition,None))
                    if cd1 == []:
                        raise ValueError(f'{fc1[1]} is a component with no definition')

                    cd2 = self.search((fc2[0][1],identifiers.predicates.definition,None))
                    if cd2 == []:
                        raise ValueError(f'{fc2[1]} is a component with no definition')

                    cd1 = cd1[0][1]
                    cd2 = cd2[0][1]
                    interaction_type = self.search((interaction[1],identifiers.predicates.type,None))
                    edge = {'triples': [(cd1,rdflib.term.URIRef('http://sbols.org/v2#interaction'),cd2)], 
                                        'weight': 1, 
                                        'display_name': identifiers.external.get_interaction_type_name(interaction_type[0][1])}
                                        
                    interaction_edges.append((cd1,cd2,edge))
                    done_list.append(participant1[2])

        interaction_graph = self._sub_graph(interaction_edges)
        return interaction_graph

    
    def produce_functional_preset(self):
        '''
        Creates a SubGraph from the larger graph that displays 
        FunctionalComponents and ModuleDefinitions.
        :return: Functional SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        # Find all ModuleDefinitions
        functional_edges = []
        module_definitions = self.search((None,None,identifiers.objects.module_definition))
        for module_definition in module_definitions:
            fcs = self.search((module_definition[0],identifiers.predicates.functional_component,None))
            modules = self.search((module_definition[0],identifiers.predicates.module,None))
            for fc in fcs:
                # Find its Definition.
                cd = self.search((fc[1],identifiers.predicates.definition,None))
                # Add An edge between CD and MD with Edge as the FC.
                if cd == []:
                    raise ValueError(f'{fc[1]} Doesnt have a definition.')
                
                edge = {'triples': [(module_definition[0],rdflib.term.URIRef('http://sbols.org/v2#functional'),cd[0][1])], 
                        'weight': 1, 
                        'display_name': "in"}
                functional_edges.append((module_definition[0],cd[0][1],edge))

            for module in modules:
                # Find its Definition (not sure its called definition).
                definition = self.search((module[1],identifiers.predicates.definition,None))
                # Add Edge between MD and MD with Edge as the M
                if definition == []:
                    raise ValueError(f'{module[1]} Doesnt have a definition.')
                
                edge = {'triples': [(module_definition[0],rdflib.term.URIRef('http://sbols.org/v2#functional'),definition[0][1])], 
                        'weight': 1, 
                        'display_name': "inside"}
                functional_edges.append((module_definition[0],definition[0][1],edge))
        functional_graph = self._sub_graph(functional_edges)
        return functional_graph

    def get_sbol_object_role(self,node,obj_type = None, obj_role=None):
        if obj_type is None:
            obj_type = self.search((node,identifiers.predicates.rdf_type,None))
            if obj_type == []:
                raise ValueError(f'{node} does not have a type.')
            obj_type = obj_type[0][1]

        potential_role_predicates = [identifiers.predicates.role,
                                    identifiers.predicates.type,
                                    identifiers.predicates.sequence_constraint_restriction,
                                    ]
        for role in potential_role_predicates:
            if obj_role is None:
                result = self.search((node,role,None))
                if result == []:
                    continue
                result = result[0][1]
            else:
                result = obj_role

            if obj_type == identifiers.objects.component_definition:
                if role == identifiers.predicates.role:
                    cd_type = identifiers.external.get_type_from_role(result)
                    obj_role_name = identifiers.external.get_component_definition_identifier_name(cd_type,result)
                else:
                    obj_role_name = identifiers.external.get_component_definition_identifier_name(result)
            elif obj_type == identifiers.objects.interaction:
                obj_role_name = identifiers.external.get_interaction_type_name(result)
            elif obj_type == identifiers.objects.participation:
                obj_role_name = identifiers.external.get_participant_role_name(result)
            else:
                obj_role_name = result
            
            if obj_role_name == "Unknown":
                raise ValueError(f'Cant find role for: {node}')
            return self._get_name(obj_role_name)
        return None

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', uri)

    def _generate_labels(self):
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            for subject,node,edge in self.graph.edges:
                if "display_name" not in self.nodes[subject].keys():
                    if isinstance(subject,rdflib.URIRef):
                        name = self._get_name(subject)
                    else:
                        name = subject
                    self.graph.nodes[subject]["display_name"] = name

                if isinstance(node,rdflib.URIRef):
                    name = self._get_name(node)
                else:
                    name = node
                self.graph.nodes[node]["display_name"] = name

                if isinstance(edge,rdflib.URIRef):
                    name = self._get_name(edge)
                else:
                    name = edge
                self.graph.edges[subject, node, edge]["display_name"] = name

        elif isinstance(self.graph,nx.classes.graph.Graph):
            for subject,node in self.graph.edges:
                if "display_name" not in self.nodes[subject].keys():
                    if isinstance(subject,rdflib.URIRef):
                        name = self._get_name(subject)
                    else:
                        name = subject
                    self.graph.nodes[subject]["display_name"] = name

                if "display_name" not in self.nodes[node].keys():
                    if isinstance(node,rdflib.URIRef):
                        try:
                            name = self.get_sbol_object_role(subject,obj_type=None,obj_role=node)
                        except ValueError:
                            name = self._get_name(node)
                    else:
                        name = node
                    self.graph.nodes[node]["display_name"] = name

                edge = self.graph.edges[subject,node]
                if "triples" in edge.keys():
                    nx.set_edge_attributes(self.graph,{ (subject,node) : {"display_name" : self._get_name(edge["triples"][0][1]) }})

    def _sub_graph(self, nodes):
        if isinstance(self.graph,nx.classes.multidigraph.MultiDiGraph):
            new_graph = nx.classes.multidigraph.MultiDiGraph()
            new_graph.add_edges_from(nodes)
            for subject,node,edge in new_graph.edges(data=True):
                if "display_name" not in new_graph.nodes[subject].keys():
                    if isinstance(subject,rdflib.URIRef):
                        name = self._get_name(subject)
                    else:
                        name = node
                    new_graph.nodes[subject]["display_name"] = name

                if "display_name" not in new_graph.nodes[node].keys():
                    if isinstance(node,rdflib.URIRef):
                        name = self._get_name(node)
                    else:
                        name = node
                    new_graph.nodes[node]["display_name"] = name
                
                if "display_name" not in edge.keys():
                    if isinstance(edge,rdflib.URIRef):
                        name = self._get_name(edge)
                    else:
                        name = edge
                    new_graph.nodes[node,edge]["display_name"] = name

        elif isinstance(self.graph,nx.classes.graph.Graph):         
            if isinstance(self.graph,nx.classes.digraph.DiGraph):
                new_graph = nx.classes.digraph.DiGraph()
            elif isinstance(self.graph,nx.classes.graph.Graph):
                new_graph = nx.classes.graph.Graph()

            new_graph.add_edges_from(nodes)
            for subject,node in new_graph.edges:
                if "display_name" not in new_graph.nodes[subject].keys():
                    if isinstance(subject,rdflib.URIRef):
                        name = self._get_name(subject)
                    else:
                        name = node
                    new_graph.nodes[subject]["display_name"] = name

                if "display_name" not in new_graph.nodes[node].keys():
                    if isinstance(node,rdflib.URIRef):
                        name = self._get_name(node)
                    else:
                        name = node
                    new_graph.nodes[node]["display_name"] = name

        return new_graph