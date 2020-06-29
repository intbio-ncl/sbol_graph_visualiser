import rdflib
import re
from sbol_rdflib_identifiers import identifiers


prune_list = [identifiers.predicates.version,identifiers.predicates.display_id,identifiers.predicates.persistent_identity]
def get_name(subject):

    split_subject = split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def split(uri):
    return re.split('#|\/|:', uri)


