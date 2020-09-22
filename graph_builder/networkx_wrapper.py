import os
import sys
import re
import copy
import rdflib
import networkx as nx
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from sbol_rdflib_identifiers import identifiers
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_graph, rdflib_to_networkx_digraph

default_prune_nodes = [identifiers.objects.sequence]
default_prune_edges = [
    identifiers.predicates.version,
    identifiers.predicates.display_id,
    identifiers.predicates.persistent_identity,
    identifiers.predicates.access,
    identifiers.predicates.direction,
    identifiers.predicates.sequence,
    identifiers.predicates.encoding,
    identifiers.predicates.elements]

potential_role_predicates = [
    identifiers.predicates.role,
    identifiers.predicates.type]  

whitelist_sbol_objects = [
    identifiers.objects.component_definition,
    identifiers.objects.participation,
    identifiers.objects.interaction]

rec = re.compile('#|\/|:') 

class NetworkXGraphWrapper:
    def __init__(self, graph = None, graph_type = "directed", prune=False):
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
        if prune:
            self.prune_graph()

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
    
    def get_connected_nodes(self,node):
        return nx.node_connected_component(self.graph, node)

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
                if ((subject == s or not s or (isinstance(s,list) and subject in s)) and 
                   (edge == p or not p or (isinstance(p,list) and edge in p)) and 
                   (node == o or not o or (isinstance(o,list) and node in o))):
                        matches.append((subject,node,edge))

        elif isinstance(self.graph,nx.classes.graph.Graph):                
            for subject,node in self.graph.edges:
                edge = self.graph.edges[subject,node]
                triple = edge["triples"][0]

                if ((triple[0] == s or not s or (isinstance(s,list) and triple[0] in s)) and 
                (triple[1] == p or not p or (isinstance(p,list) and triple[1] in p)) and 
                (triple[2] == o or not o or (isinstance(o,list) and triple[2] in o))):
                    matches.append((triple[0],triple[2],edge))
        return matches

    def retrieve_node(self,node,edge_name):
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            pass

        elif isinstance(self.graph,nx.classes.graph.Graph):
            edges = self.graph.edges(node,data=True)
            for e in edges:
                if e[2]["triples"][0][1] == edge_name:
                    return e[2]["triples"][0][2]
            return None

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
            prune_edges = default_prune_edges
        elif isinstance(prune_edges,(list,set,tuple)):
            pass
        else:
            prune_edges = [prune_edges]

        if prune_nodes is None:
            prune_nodes = default_prune_nodes
        elif isinstance(prune_nodes,(list,set,tuple)):
            pass
        else:
            prune_nodes = [prune_nodes]

        to_prune_edges = []
        to_prune_nodes = []
        if isinstance(self.graph,nx.classes.multidigraph.MultiDiGraph):
            for n1,n2,edge in self.graph.edges:
                if edge in prune_edges:
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
                elif "triples" in edge.keys():
                    if edge["triples"][0][1] in prune_edges:
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
    
    def get_graph(self):
        return self.graph
        
    def produce_components_preset(self):
        '''
        Creates a SubGraph from the larger graph that displays 
        ComponentDefs and said CD's as subparts of other CD's
        :return: Interaction SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        components = self.search((None,identifiers.predicates.component,None))
        cd_edges = []
        for s,p,o in components:
            subject_type = self.retrieve_node(s,identifiers.predicates.rdf_type)
            if subject_type != identifiers.objects.component_definition:
                continue
            cd = self.retrieve_node(p,identifiers.predicates.definition)
            if cd is None:
                raise ValueError(f'{p} is a component with no definition')
            cd_edges.append((s,cd,o))
        parts_graph = self._sub_graph(cd_edges)
        return parts_graph
        
    def produce_parts_preset(self):
        '''
        Creates a SubGraph from the larger graph that displays 
        ComponentDefs and said CD's as subparts of other CD's
        :return: Interaction SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        components = self.search((None,[identifiers.predicates.component,identifiers.predicates.functional_component],None))
        cd_edges = []
        for s,p,o in components:
            subject_type = self.retrieve_node(s,identifiers.predicates.rdf_type)
            if subject_type != identifiers.objects.component_definition and subject_type != identifiers.objects.module_definition:
                continue
            cd = self.retrieve_node(p,identifiers.predicates.definition)

            if cd is None:
                raise ValueError(f'{p} is a component with no definition')

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
        part_mapping = {identifiers.external.participant_inhibitor : "in",
                        identifiers.external.participant_inhibited : "out",
                        identifiers.external.participant_stimulator : "in",
                        identifiers.external.participant_stimulated : "out",
                        identifiers.external.participant_modifier : "in",
                        identifiers.external.participant_modified : "out",
                        identifiers.external.participant_product : "out",
                        identifiers.external.participant_reactant : "out",
                        identifiers.external.participant_participation_promoter : "in",
                        identifiers.external.participant_template : "in"}
        interaction_edges = []
        interactions = self.search((None,identifiers.predicates.interaction,None))
        for interaction in interactions:
            done_list = []
            participants = self.search((interaction[1],identifiers.predicates.participation,None))
            for participant1 in participants:
                participant1_type = self.retrieve_node(participant1[1],identifiers.predicates.role)
                try:
                    particiant_1_mapping = part_mapping[participant1_type]
                except KeyError:
                    particiant_1_mapping = "in"

                for participant2 in participants:
                    if participant1 == participant2 or participant1[2] in done_list or participant2[2] in done_list:
                        continue
                    fc1 = self.retrieve_node(participant1[1],identifiers.predicates.participant)
                    fc2 = self.retrieve_node(participant2[1],identifiers.predicates.participant)
                    if fc1 is None:
                        raise ValueError(f'{participant1[1]} is a participant with no component')
                    if fc2 is None:
                        raise ValueError(f'{participant2[1]} is a participant with no component')

                    cd1 = self.retrieve_node(fc1,identifiers.predicates.definition)
                    if cd1 is None:
                        raise ValueError(f'{fc1} is a component with no definition')

                    cd2 = self.retrieve_node(fc2,identifiers.predicates.definition)
                    if cd2 is None:
                        raise ValueError(f'{fc2} is a component with no definition')

                    interaction_type = self.retrieve_node(interaction[1],identifiers.predicates.type)
                    participant2_type = self.retrieve_node(participant2[1],identifiers.predicates.role)

                    try:
                        particiant_2_mapping = part_mapping[participant2_type]
                    except KeyError:
                        particiant_2_mapping = "out"
                    interaction_type_name = identifiers.external.get_interaction_type_name(interaction_type)
                    if particiant_1_mapping == "in" and particiant_2_mapping == "out":
                        in_part = cd1
                        out_part = cd2
                    elif particiant_2_mapping == "in" and particiant_1_mapping == "out":
                        in_part = cd2
                        out_part = cd1
                    else:
                        in_part = cd1
                        out_part = cd2
                        edge = {'triples': [(out_part,interaction_type_name,in_part)], 
                        'weight': 1, 
                        'display_name': interaction_type_name}
                        interaction_edges.append((out_part,in_part,edge))


                    edge = {'triples': [(cd1,interaction_type_name,cd2)], 
                                        'weight': 1, 
                                        'display_name': interaction_type_name}
                                        
                    interaction_edges.append((in_part,out_part,edge))
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
                cd = self.retrieve_node(fc[1],identifiers.predicates.definition)
                # Add An edge between CD and MD with Edge as the FC.
                if cd is None:
                    raise ValueError(f'{fc[1]} Doesnt have a definition.')
                
                edge = {'triples': [(module_definition[0],rdflib.term.URIRef('http://sbols.org/v2#functional'),cd)], 
                        'weight': 1, 
                        'display_name': "in"}
                functional_edges.append((module_definition[0],cd,edge))

            for module in modules:
                # Find its Definition (not sure its called definition).
                definition = self.retrieve_node(module[1],identifiers.predicates.definition)
                # Add Edge between MD and MD with Edge as the M
                if definition is None:
                    raise ValueError(f'{module[1]} Doesnt have a definition.')
                
                edge = {'triples': [(module_definition[0],rdflib.term.URIRef('http://sbols.org/v2#functional'),definition)], 
                        'weight': 1, 
                        'display_name': "inside"}
                functional_edges.append((module_definition[0],definition,edge))
        functional_graph = self._sub_graph(functional_edges)
        return functional_graph

    def produce_parent_preset(self):
        # A parent is essentially a triple child - parent - edge
        # If a node doesnt have a parent don't add it as it will already be present.

        def inner_search(pattern,triplepack):
            (s,p,o) = pattern
            for triple in triplepack:
                triple = triple[0]
                if ((triple[0] == s or not s) and (triple[1] == p or not p) and (triple[2] == o or not o)):
                    return triple
            return None

        parent_edges_graph = []
        for node in self.graph.nodes:
            edges = [[e for e in edge[2]["triples"]] for edge in self.graph.edges(node,data=True)]
            node_type = inner_search((node,identifiers.predicates.rdf_type,None),edges)
            if node_type is None:
                continue
            node_type = node_type[2]
            child = None
            predicate = None
            for edge in edges:
                edge = edge[0]
                if edge[1] in identifiers.predicates.ownership_predicates and edge[0] == node:
                    child = edge[2]
                    predicate = edge[1]
                elif edge[1] == identifiers.predicates.component and edge[0] == node:
                    parent_edges = [[e for e in edge[2]["triples"]] for edge in self.graph.edges(edge[0],data=True)]
                    potential_parent_type = inner_search((edge[0],identifiers.predicates.rdf_type,None),parent_edges)
                    print(potential_parent_type)
                    if identifiers.objects.component_definition == potential_parent_type[2]:
                        child = potential_parent_type[2]
                        predicate = edge[1]
                    else:
                        # A sequenceAnnotation will be handled in its own iteration.
                        continue
                else:
                    #All the other triples that aren't parential.
                    continue

                if child is not None and predicate is not None:
                    new_edge = {'triples': [(node,predicate,child)], 
                            'weight': 1, 
                            'display_name': self._get_name(str(predicate))}

                    parent_edges_graph.append((node,child,new_edge))

        parent_graph = self._sub_graph(parent_edges_graph)
        return parent_graph


    def get_sbol_object_role(self,node,obj_type = None, obj_role=None):
        if obj_type is None:
            obj_type = self.retrieve_node(node,identifiers.predicates.rdf_type)
            if obj_type is None:
                return None
        if obj_type not in whitelist_sbol_objects:
            return None

        for role in potential_role_predicates:
            if obj_role is None:
                result = self.retrieve_node(node,role)
                if result is None:
                    continue
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
                return None
            return self._get_name(obj_role_name)
        return None

    def translate_role(self,subject,role):
        translators = [
            identifiers.external.get_component_definition_identifier_name(identifiers.external.get_type_from_role(role),role),
            identifiers.external.get_interaction_type_name(role),
            identifiers.external.get_participant_role_name(role)
            ]

        for translated in translators:
            if translated != "Unknown":
                return translated
        return None

    def triplepack_search(self,pattern,triplepack):
        (s,p,o) = pattern
        for triple in triplepack:
            triple = triple[0]
            if ((triple[0] == s or not s) and (triple[1] == p or not p) and (triple[2] == o or not o)):
                return triple
        return None

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return rec.split(uri)

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
                        # This is a little hacky, basically leveraging the 
                        # knowledge of the SBOL data model to reduce execution time.
                        name = self.translate_role(subject,node)
                        if name is None:
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

    def _get_parent(self,node,node_edges,graph_edges):
        for edge in node_edges:
            edge = edge[0]
            if edge[1] in identifiers.predicates.ownership_predicates and edge[2] == node:
                return edge[0]
            elif edge[1] == identifiers.predicates.component and edge[2] == node:
                parent_edges = [[e for e in edge[2]["triples"]] for edge in graph_edges(edge[0],data=True)]
                potential_parent_type = self.triplepack_search((edge[0],identifiers.predicates.rdf_type,None),parent_edges)
                if identifiers.objects.component_definition == potential_parent_type[2]:
                    return potential_parent_type[0]
                else:
                    # A sequenceAnnotation will be handled in its own iteration.
                    pass
            else:
                #All the other triples that aren't parential.
                pass
        return None


