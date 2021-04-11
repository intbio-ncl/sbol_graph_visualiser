import re
import networkx as nx
from rdflib import URIRef,Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph

from util.sbol_identifiers import identifiers

class GraphWrapper:
    def __init__(self,graph,prune=False):
        if isinstance(graph,nx.DiGraph):
            self._graph = graph
        else:
            _graph = Graph()
            _graph.load(graph)
            self._graph = rdflib_to_networkx_digraph(_graph)
            self._generate_labels()
        if prune:
            self._prune_graph()        
       

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

    @property
    def adjacency(self):
        return self._graph.adjacency()

    def in_edges(self,node = None):
        return self.graph.in_edges(node)
    
    def out_edges(self,node = None):
        return self.graph.out_edges(node)

    def search(self,pattern,graph=None):
        matches = []
        (s, p, o) = pattern
        if graph is None:
            graph = self._graph
        for subject,node in graph.edges:
            edge = graph.edges[subject,node]
            triple = edge["triples"][0]
            if ((triple[0] == s or not s or (isinstance(s,list) and triple[0] in s)) and 
                (triple[1] == p or not p or (isinstance(p,list) and triple[1] in p)) and 
                (triple[2] == o or not o or (isinstance(o,list) and triple[2] in o))):
                matches.append((triple[0],triple[2],edge))
        return matches

    def retrieve_node(self,node,edge_name):
        edges = self._graph.edges(node,data=True)
        for edge in edges:
            for e in edge[2]["triples"]:
                if edge_name == e[1]:
                    return e[2]
        return None

    def retrieve_nodes(self,node,edge_names):
        if not isinstance(edge_names,(list,set,tuple)):
            edge_names = [edge_names]
        matches = []
        edges = self._graph.edges(node,data=True)
        for edge in edges:
            for e in edge[2]["triples"]:
                if e[1] in edge_names:
                    matches.append(e[2])
        return matches

    def add(self,edges):
        self._graph.add_edges_from(edges)
    
    def get_tree(self):
        tree_edges = []
        node_attrs = {}
        seen = []
        for n,v,e in self._graph.edges(data=True):
            node_attrs[v] = self.nodes[v]
            node_attrs[n] = self.nodes[n]
            v_copy = v
            if v in seen:
                v = URIRef(n[0:-2] + "/" + self._get_name(str(v)) + "/1")
                node_attrs[v] = self.nodes[v_copy]
            seen.append(v)
            e = {'triples': [(n,e["triples"][0][1],v)], 
                'weight': 1, 
                'display_name': e["display_name"]}
            tree_edges.append((n,v,e))       
        tree_graph = self.sub_graph(tree_edges,node_attrs)
        return tree_graph

    def get_network(self):
        return self
        
    def sub_graph(self,nodes,node_attrs = {}):
        new_graph = nx.DiGraph()
        new_graph.add_edges_from(nodes)

        for subject,node in new_graph.edges:
            try:
                new_graph.nodes[subject].update(node_attrs[subject])
            except (KeyError,ValueError):
                pass
            if "display_name" not in new_graph.nodes[subject].keys():
                if isinstance(subject,URIRef):
                    name = self._get_name(subject)
                else:
                    name = node
                new_graph.nodes[subject]["display_name"] = name

            try:
                new_graph.nodes[node].update(node_attrs[node])
            except (KeyError,ValueError):
                pass
            if "display_name" not in new_graph.nodes[node].keys():
                if isinstance(node,URIRef):
                    name = self._get_name(node)
                else:
                    name = node
                new_graph.nodes[node]["display_name"] = name
        new_graph = GraphWrapper(new_graph)
        return new_graph

    def triplepack_search(self,pattern,triplepack):
        (s,p,o) = pattern
        for triple in triplepack:
            triple = triple[0]
            if ((triple[0] == s or not s) and (triple[1] == p or not p) and (triple[2] == o or not o)):
                return triple
        return None

    def _generate_labels(self):
        for subject,node in self._graph.edges:
            if "display_name" not in self.nodes[subject].keys():
                if isinstance(subject,URIRef):
                    name = self._get_name(subject)
                else:
                    name = subject
                self._graph.nodes[subject]["display_name"] = name

            if "display_name" not in self.nodes[node].keys():
                if isinstance(node,URIRef):
                    # This is a little hacky, basically leveraging the 
                    # knowledge of the SBOL data model to reduce execution time.
                    name = identifiers.translate_role(node)
                    if name is None:
                        name = self._get_name(node)
                else:
                    name = node
                self._graph.nodes[node]["display_name"] = name

            edge = self._graph.edges[subject,node]
            if "triples" in edge.keys():
                nx.set_edge_attributes(self._graph,{(subject,node) : {"display_name" : self._get_name(edge["triples"][0][1])}})

    def _prune_graph(self):
        prune_edges = identifiers.predicates.default_prune_edges
        prune_nodes = identifiers.objects.default_prune_nodes

        to_prune_edges = []
        to_prune_nodes = []
        for n1,n2,edge in self._graph.edges(data=True):
            if n1 in prune_nodes:
                to_prune_nodes.append(n1)
            if n2 in prune_nodes:
                to_prune_nodes.append(n2)
            # edge = self._graph.edges[n1,n2]
            if "display_name" in edge.keys():
                if edge["display_name"] in [self._get_name(p) for p in prune_edges]:
                    to_prune_edges.append((n1,n2))
            elif "triples" in edge.keys():
                for index,triple in enumerate(edge["triples"]):
                    if triple[1] in prune_edges:
                        del edge["triples"][index]
                if len(edge["triples"]) == 0:
                    to_prune_edges.append((n1,n2))

        self._graph.remove_nodes_from(to_prune_nodes)
        self._graph.remove_edges_from(to_prune_edges)
        self._graph.remove_nodes_from(list(nx.isolates(self._graph)))

    def _create_edge_dict(self,s,p,o,weight=1):
        edge = {'triples': [(s,p,o)], 
                'weight': weight, 
                'display_name': self._get_name(str(p))}
        return edge

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', uri)