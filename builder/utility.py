import re

from util.sbol_identifiers import identifiers

_rec = re.compile('#|\/|:') 

default_prune_nodes = [
    identifiers.objects.sequence]

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


def get_sbol_object_role(graph,node,obj_type = None, obj_role=None):
    if obj_type is None:
        obj_type = graph.get_rdf_type(node)
        if obj_type is None:
            return None
    if obj_type not in whitelist_sbol_objects:
        return None

    for role in potential_role_predicates:
        if obj_role is None:
            result = graph.get_role(node)
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
        return get_name(obj_role_name)
    return None

def translate_role(subject,role):
    translators = [
        identifiers.external.get_component_definition_identifier_name(identifiers.external.get_type_from_role(role),role),
        identifiers.external.get_interaction_type_name(role),
        identifiers.external.get_participant_role_name(role)]

    for translated in translators:
        if translated != "Unknown":
            return translated
    return None

def valid_participant_types(p1,p2):
    input_participants = [identifiers.external.participant_reactant]
    if p1 in input_participants and p2 in input_participants:
        return False
    return True

def participation_direction(cd1,cd2,p1_type,p2_type,interaction_type):
    interaction_edges = []
    interaction_type_name = identifiers.external.get_interaction_type_name(interaction_type)
    try:
        particiant_1_mapping = participant_type_mapping[p1_type]
    except KeyError:
        particiant_1_mapping = "in"
    try:
        particiant_2_mapping = participant_type_mapping[p2_type]
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
        edge = {'triples': [(out_part,interaction_type,in_part)], 
                'weight': 1, 
                'display_name': interaction_type_name}
        interaction_edges.append((out_part,in_part,edge))

    edge = {'triples': [(cd1,interaction_type,cd2)], 
                        'weight': 1, 
                        'display_name': interaction_type_name}
                        
    interaction_edges.append((in_part,out_part,edge))
    return interaction_edges

def get_parent(graph,node,node_edges,graph_edges):
    for edge in node_edges:
        edge = edge[0]
        if edge[1] in identifiers.predicates.ownership_predicates and edge[2] == node:
            return edge[0]
        elif edge[1] == identifiers.predicates.component and edge[2] == node:
            parent_edges = [[e for e in edge[2]["triples"]] for edge in graph_edges(edge[0],data=True)]
            potential_parent_type = graph.triplepack_search((edge[0],identifiers.predicates.rdf_type,None),parent_edges)
            if identifiers.objects.component_definition == potential_parent_type[2]:
                return potential_parent_type[0]
            else:
                # A sequenceAnnotation will be handled in its own iteration.
                pass
        else:
            #All the other triples that aren't parential.
            pass
    return None

def get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return _rec.split(uri)