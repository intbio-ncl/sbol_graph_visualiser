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


participant_type_mapping = {identifiers.external.participant_inhibitor : "in",
                            identifiers.external.participant_inhibited : "out",
                            identifiers.external.participant_stimulator : "in",
                            identifiers.external.participant_stimulated : "out",
                            identifiers.external.participant_modifier : "in",
                            identifiers.external.participant_modified : "out",
                            identifiers.external.participant_product : "out",
                            identifiers.external.participant_reactant : "in",
                            identifiers.external.participant_participation_promoter : "in",
                            identifiers.external.participant_template : "in"}

rec = re.compile('#|\/|:') 

class NetworkXGraphWrapper:
    def __init__(self, graph = None, graph_type = "directed", prune=False):
        if isinstance(graph,nx.classes.digraph.DiGraph):
            self.graph = graph
        else:
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
        return self.graph.adjacency()
    
    @property
    def degree(self):
        return self.graph.degree
    
    def in_edges(self,node = None):
        if not isinstance(self.graph,nx.classes.digraph.DiGraph):
            raise ValueError(f'Graph is not direted.')   
        return self.graph.in_edges(node)
    
    def out_edges(self,node = None):
        if not isinstance(self.graph,nx.classes.digraph.DiGraph):
            raise ValueError(f'Graph is not direted.')   
        return self.graph.out_edges(node)

    def has_node(self,node):
        return self.graph.has_node(node)

    def triangles(self,graph = None,nodes=None):
        '''
        Finds the number of triangles that include a node as one node.
        '''
        if graph is None:
            graph = self.graph
        return nx.triangles(graph,nodes=nodes)

    def transitivity(self,graph = None):
        '''
        Compute graph transitivity i.e. fraction of all possible triangles present in G.
        Possible triangles are identified by the number of 
        “triads” (two edges with a shared vertex).
        '''
        if graph is None:
            graph = self.graph
        return nx.transitivity(graph)

    def clustering_coeficients(self,graph=None,nodes=None,weight=None):
        '''
        Compute the clustering coefficient for nodes.
        Clustering coefficient is a measure of the degree to which nodes 
        in a graph tend to cluster together
        '''
        if graph is None:
            graph = self.graph
        return nx.clustering(graph,nodes=nodes,weight=weight)

    def average_clustering(self,graph=None,**kwargs):
        '''
        Compute the average clustering coefficient for the graph G.
        Clustering coefficient is a measure of the degree to which nodes 
        in a graph tend to cluster together
        '''
        if graph is None:
            graph = self.graph
        return nx.average_clustering(graph, **kwargs)

    def square_clustering(self,graph=None,nodes=None):
        '''
        Compute the squares clustering coefficient for nodes.
        For each node return the fraction of possible squares that exist at the node
        Clustering coefficient is a measure of the degree to which nodes 
        in a graph tend to cluster together
        '''
        if graph is None:
            graph = self.graph
        return nx.square_clustering(graph, nodes=nodes)

    def generalized_degree(self,graph=None,nodes=None):
        '''
        Compute the generalized degree for nodes.
        For each node, the generalized degree shows how many edges of given triangle multiplicity the node is connected to
        '''
        if graph is None:
            graph = self.graph
        return nx.generalized_degree(graph, nodes=nodes)

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

    def search(self,pattern,graph=None):
        '''
        Given a tuple of size 3 search the graph for the related edge.
        provide None in the index where the search is to be made. 
        :return: list of matches
        :rtype: list
        '''
        matches = []
        (s, p, o) = pattern
        if graph is None:
            graph = self.graph
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            for subject,node,edge in graph.edges:
                if ((subject == s or not s or (isinstance(s,list) and subject in s)) and 
                   (edge == p or not p or (isinstance(p,list) and edge in p)) and 
                   (node == o or not o or (isinstance(o,list) and node in o))):
                        matches.append((subject,node,edge))

        elif isinstance(self.graph,nx.classes.graph.Graph):                
            for subject,node in graph.edges:
                edge = graph.edges[subject,node]
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

    def retrieve_nodes(self,node,edge_names):
        if not isinstance(edge_names,(list,set,tuple)):
            edge_names = [edge_names]
        
        matches = []
        if isinstance(self.graph, nx.classes.multidigraph.MultiDiGraph):
            pass

        elif isinstance(self.graph,nx.classes.graph.Graph):
            edges = self.graph.edges(node,data=True)
            for e in edges:
                if e[2]["triples"][0][1] in edge_names:
                    matches.append(e[2]["triples"][0][2])
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
        return self
    
    def get_tree(self):
        tree_edges = []
        node_attrs = {}
        seen = []
        for n,v,e in self.graph.edges(data=True):
            node_attrs[v] = self.nodes[v]
            node_attrs[n] = self.nodes[n]
            v_copy = v
            if v in seen:
                v = rdflib.URIRef(n[0:-2] + "/" + self._get_name(str(v)) + "/1")
                node_attrs[v] = self.nodes[v_copy]
            seen.append(v)
            e = {'triples': [(n,e["triples"][0][1],v)], 
                'weight': 1, 
                'display_name': e["display_name"]}
            tree_edges.append((n,v,e))       


        tree_graph = self._sub_graph(tree_edges,node_attrs)
        return tree_graph

    def _sub_graph(self, nodes,node_attrs = {}):
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
                try:
                    new_graph.nodes[subject].update(node_attrs[subject])
                except KeyError:
                    pass
                if "display_name" not in new_graph.nodes[subject].keys():
                    if isinstance(subject,rdflib.URIRef):
                        name = self._get_name(subject)
                    else:
                        name = node
                    new_graph.nodes[subject]["display_name"] = name

                try:
                    new_graph.nodes[node].update(node_attrs[node])
                except KeyError:
                    pass
                if "display_name" not in new_graph.nodes[node].keys():
                    if isinstance(node,rdflib.URIRef):
                        name = self._get_name(node)
                    else:
                        name = node
                    new_graph.nodes[node]["display_name"] = name

        new_graph = NetworkXGraphWrapper(new_graph)
        return new_graph
        
    def produce_full_graph(self):
        return self.get_graph()
        
    def produce_components_graph(self):
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
        
    def produce_parts_graph(self):
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
        interaction_edges = []
        interactions = self.search((None,identifiers.predicates.interaction,None))
        for interaction in interactions:
            done_list = []
            participants = self.search((interaction[1],identifiers.predicates.participation,None))
            for participant1 in participants:
                cd1 = self._get_cd_from_part(participant1[1])
                participant1_type = self.retrieve_node(participant1[1],identifiers.predicates.role)

                for participant2 in participants:
                    if participant1 == participant2 or participant1[2] in done_list or participant2[2] in done_list:
                        continue
                    
                    cd2 = self._get_cd_from_part(participant2[1])
                    interaction_type = self.retrieve_node(interaction[1],identifiers.predicates.type)
                    participant2_type = self.retrieve_node(participant2[1],identifiers.predicates.role)

                    interaction_type_name = identifiers.external.get_interaction_type_name(interaction_type)
                    interaction_edges = interaction_edges + self._get_in_out_participants(cd1,cd2,participant1_type,participant2_type,interaction_type_name)

                    done_list.append(participant1[2])

        interaction_graph = self._sub_graph(interaction_edges)
        return interaction_graph
    
    def produce_protein_protein_interaction_graph(self):
        '''
        Creates a SubGraph from the larger graph that displays a graph of 
        interacting proteins within the provided graph.
        :return: PPI SubGraph 
        :rtype: nx.classes.graph.Graph
        '''
        ppi_edges = []
        interactions = self.search((None,identifiers.predicates.interaction,None))
        for interaction in interactions:
            done_list = []
            participants = self.search((interaction[1],identifiers.predicates.participation,None))
            for participant1 in participants:
                atleast_one = False
                cd1 = self._get_cd_from_part(participant1[1])
                cd1_type = self.retrieve_node(cd1,identifiers.predicates.type)
                participant1_type = self.retrieve_node(participant1[1],identifiers.predicates.role)
                if cd1_type != identifiers.external.component_definition_protein:
                    continue
                interaction_type = self.retrieve_node(interaction[1],identifiers.predicates.type)
                interaction_type_name = identifiers.external.get_interaction_type_name(interaction_type)
                if len(participants) > 1 :
                    for participant2 in participants:
                        if participant1 == participant2 or participant1[2] in done_list or participant2[2] in done_list:
                            atleast_one = True
                            continue

                        cd2 = self._get_cd_from_part(participant2[1])
                        cd2_type = self.retrieve_node(cd2,identifiers.predicates.type)
                        if cd2_type != identifiers.external.component_definition_protein:
                            continue

                        participant2_type = self.retrieve_node(participant2[1],identifiers.predicates.role)
                        ppi_edges = ppi_edges + self._get_in_out_participants(cd1,cd2,participant1_type,participant2_type,interaction_type_name)

                        done_list.append(participant1[2])
                        atleast_one = True

                if not atleast_one:
                    edge = self._create_edge_dict(cd1,interaction_type_name,cd1)
                    ppi_edges.append((cd1,cd1,edge))
        ppi_network = self._sub_graph(ppi_edges)
        return ppi_network

    def produce_functional_graph(self):
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

    def produce_parent_graph(self):
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
                    new_edge = self._create_edge_dict(node,predicate,child)
                    parent_edges_graph.append((node,child,new_edge))

        parent_graph = self._sub_graph(parent_edges_graph)
        return parent_graph

    def produce_set_combinatorial_derivation_graph(self):
        cd_edges_graph = []
        comb_der = self.search((None,None,identifiers.objects.combinatorial_derivation))
        for cd in comb_der:
            strategy = self.retrieve_node(cd[0],identifiers.predicates.strategy)
            if strategy is not None:
                strat_edge = self._create_edge_dict(cd[0],identifiers.predicates.strategy,strategy)
                cd_edges_graph.append((cd[0],strategy,strat_edge)) 

            variable_components = self.retrieve_nodes(cd[0],identifiers.predicates.variable_component)
            for vc in variable_components:
                vc_edge = self._create_edge_dict(cd[0],identifiers.predicates.variable_component,vc)
                cd_edges_graph.append((cd[0],vc,vc_edge))

                variable = self.retrieve_node(vc,identifiers.predicates.variable)
                if variable is None:
                    raise ValueError(f'{vc} doesnt have a variable.')
                
                operator = self.retrieve_node(vc,identifiers.predicates.operator)
                if operator is None:
                    raise ValueError(f'{vc} doesnt have a operator')
                

                variable_edge = self._create_edge_dict(vc,identifiers.predicates.variable,variable)
                cd_edges_graph.append((vc,variable,variable_edge))
                operator_edge = self._create_edge_dict(vc,identifiers.predicates.operator,operator)
                cd_edges_graph.append((vc,operator,operator_edge))

                variants = self.retrieve_nodes(vc,identifiers.predicates.variant)
                for variant in variants:
                    variant_edge = self._create_edge_dict(vc,identifiers.predicates.variant,variant)
                    cd_edges_graph.append((vc,variant,variant_edge))

                variant_collections = self.retrieve_nodes(vc,identifiers.predicates.variant_collection)
                for variant_c in variant_collections:
                    members = self.retrieve_nodes(variant_c,identifiers.predicates.member)
                    for member in members:
                        member_type = self.retrieve_node(member,identifiers.predicates.rdf_type)
                        if member_type == identifiers.objects.component_definition:
                            member_edge = self._create_edge_dict(vc,identifiers.predicates.variant,member)
                            cd_edges_graph.append((vc,member,member_edge))

        cd_graph = self._sub_graph(cd_edges_graph)
        return cd_graph
    
    def produce_sequence_preset(self):
        sequence_edges = []
        component_definitions = self.search((None,None,identifiers.objects.component_definition))
        for cd in component_definitions:
            cd_name = cd[0]
            sequence_locations = []
            # Get all the information (SA and SC)
            sequence_annotations = self.retrieve_nodes(cd_name,identifiers.predicates.sequence_annotation)
            sequence_constraints = self.retrieve_nodes(cd_name,identifiers.predicates.sequence_constraint)

            for sa in sequence_annotations:

                sa_edge = self._create_edge_dict(cd_name,identifiers.predicates.sequence_annotation,sa)
                sequence_edges.append((cd_name,sa,sa_edge))
                component = self.retrieve_node(sa,identifiers.predicates.component)
                definition = self.retrieve_node(component,identifiers.predicates.definition)
                d_type = self.retrieve_node(definition,identifiers.predicates.type)
                d_role = self.retrieve_node(definition,identifiers.predicates.role)
                d_role_name = identifiers.external.get_component_definition_identifier_name(d_type,d_role)

                locations = self.retrieve_nodes(sa,identifiers.predicates.location)
                for location in locations:
                    location_type = self.retrieve_node(location,identifiers.predicates.rdf_type)
                    if location_type == identifiers.objects.range:
                        start = self.retrieve_node(location,identifiers.predicates.start)
                        end = self.retrieve_node(location,identifiers.predicates.end)
                    elif location_type == identifiers.objects.cut:
                        start = self.retrieve_node(location,identifiers.predicates.at)
                        end = start
                    else:
                        pass # Generic Location??
                    print(location)
                    print(start,end)
                    sequence_locations.append((location,d_role_name,(int(start),int(end))))

            # Need to order
            ordered_locations = []  
            for index,sl in enumerate(sequence_locations):
                sl_1_loc = sl[2]
                if index == 0:
                    ordered_locations.append(sl)
                    continue
                for ordered_index,sl_2 in enumerate(ordered_locations):
                    if sl_2[0] == sl[0]:
                        continue
                    sl_2_loc = sl_2[2]
                    if sl_1_loc[0] < sl_2_loc[0]:
                        ordered_locations.insert(ordered_index,sl)
                        break

            print("Finished Ordering")
            for sl in ordered_locations:
                print(sl)
    
            # add connections between ordered locations.



        sequence_graph = self._sub_graph(sequence_edges)
        return sequence_graph

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

    def _get_cd_from_part(self,participant):
        fc1 = self.retrieve_node(participant,identifiers.predicates.participant)
        if fc1 is None:
            raise ValueError(f'{participant} is a participant with no component')

        cd1 = self.retrieve_node(fc1,identifiers.predicates.definition)
        if cd1 is None:
            raise ValueError(f'{fc1} is a component with no definition')
        
        return cd1

    def _get_in_out_participants(self,cd1,cd2,participant1_type,participant2_type,interaction_type_name):
        interaction_edges = []
        try:
            particiant_1_mapping = participant_type_mapping[participant1_type]
        except KeyError:
            particiant_1_mapping = "in"
        try:
            particiant_2_mapping = participant_type_mapping[participant2_type]
        except KeyError:
            particiant_2_mapping = "out"
        
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
        return interaction_edges

    def _create_edge_dict(self,s,p,o,weight=1):
        edge = {'triples': [(s,p,o)], 
                'weight': weight, 
                'display_name': self._get_name(str(p))}
        return edge