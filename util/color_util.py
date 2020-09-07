import enum
import sys,os
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"util")))
from sbol_rdflib_identifiers import identifiers

class SBOLTypeColors(enum.Enum):
    ComponentDefinition = (0,0,0.255)
    Component = (0,0.255,0)
    ModuleDefinition = (0.255,0,0)
    Range = (0,0.255,0.255)
    Cut = (0.255,0,0.255)
    Sequence = (0.255,0.255,0)
    
    CombinatorialDerivation = (0,0,0.128)
    Experiment = (0,0.128,0)
    ExperimentalData = (0.128,0,0)
    FunctionalComponent = (0,0.128,0.128)
    Implementation = (0.128,0,0.128)
    Interaction = (0.128,0.128,0)
    GenericLocation = (0,0,0.64)
    MapsTo = (0,0.64,0)
    Module = (0.64,0,0)
    Model = (0,0.64,0.64)
    Attachment = (0.64,0,0.64)
    Collection = (0.64,0.64,0)
    SequenceAnnotation = (0,0,0.32)
    Participation = (0,0.32,0)
    SequenceConstraint = (0.32,0,0)
    default = (0,0.32,0.32)


class SBOLPredicateColors(enum.Enum):

    rdf_type = (0,0,0.255)
    displayId = (0,0.255,0)
    persistentIdentity = (0.255,0,0)
    version = (0,0.255,0.255)
    title = (0.255,0,0.255)
    description = (0.255,0.255,0)
    component = (0,0,0.128)
    functionalComponent = (0,0.128,0)
    sequenceAnnotation = (0.128,0,0)
    sequenceConstraint = (0,0.128,0.128)
    location = (0.128,0,0.128)
    sequence = (0.128,0.128,0)
    cut = (0,0,0.64)
    at = (0,0.64,0)
    definition = (0.64,0,0)
    restriction = (0,0.64,0.64)
    subject = (0.64,0,0.64)
    object = (0.64,0.64,0)
    type = (0,0,0.32)
    role = (0,0.32,0)
    start = (0.32,0,0)
    end = (0,0.32,0.32)
    interaction = (0.32,0,0.32)
    participation = (0.32,0.32,0)
    elements = (0,0,0.16)
    participant = (0,0.16,0)
    encoding = (0.16,0,0)
    direction = (0,0.16,0.16)
    access = (0.16,0,0.16)
    orientation = (0.16,0.16,0)
    framework = (0,0,0.8)
    language = (0,0.8,0)
    source = (0.8,0,0)
    local = (0,0.8,0.8)
    remote = (0.8,0,0.8)
    module = (0.8,0.8,0)



def calculate_next_color(curr_color):
    curr_color = list(curr_color)
    if curr_color[0] != 0 and curr_color[1] == 0 and curr_color[2] == 0:
        curr_color[1] = curr_color[0]
        curr_color[0] = 0
    elif curr_color[0] == 0 and curr_color[1] != 0 and curr_color[2] == 0:
        curr_color[2] = curr_color[1]
        curr_color[1] = 0
    elif curr_color[0] == 0 and curr_color[1] == 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[2]
        curr_color[1] = curr_color[2]
        curr_color[2] = 0
    elif curr_color[0] != 0 and curr_color[1] != 0 and curr_color[2] == 0:
        curr_color[2] = curr_color[1]
        curr_color[0] = 0
    elif curr_color[0] == 0 and curr_color[1] != 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[1]
        curr_color[1] = 0
    elif curr_color[0] != 0 and curr_color[1] == 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[0] / 2
        curr_color[1] = 0
        curr_color[2] = 0
    else:
        raise ValueError(curr_color)
    return tuple(curr_color)

def calculate_role_color(node_color,curr_mapping):
    role_color = [0,0,0]
    for index,e in enumerate(node_color):
        if e != 0:
            role_color[index] = 0
        else:
            for inner_e in node_color:
                if inner_e != 0:
                    role_color[index] = inner_e
    if tuple(role_color) in curr_mapping.values():
        # Index of elements that need to change
        to_change_elements = [index for index,e in enumerate(role_color) if e != 0]
        while tuple(role_color) in curr_mapping.values():
            # Get the values of the elements that need to change.
            curr_col = [e for index,e in enumerate(role_color) if index in to_change_elements]
            # Calculate updated Colors.
            colors = calculate_next_color_role(curr_col,max(role_color))
            # Get the new color value in the list if the index 
            role_color = [colors.pop() if index in to_change_elements else 0 for index,x in enumerate(role_color)]
    return tuple(role_color)


def calculate_next_color_role(color,not_zero_color):
    curr_color = color.copy()
    if len(curr_color) == 1:
        curr_color[0] = not_zero_color * 0.75

    elif len(curr_color) == 2:   
        if curr_color[0] != 0 and curr_color[1] != 0:
            curr_color[1] = curr_color[0]
            curr_color[0] = 0

        elif curr_color[0] == 0 and curr_color[1] != 0:
            curr_color[0] = curr_color[1]
            curr_color[1] = 0

        elif curr_color[0] != 0 and curr_color[1] == 0:
            curr_color[0] = curr_color[0] * 0.75
            curr_color[1] = curr_color[0] * 0.75
        else:
            raise ValueError(f'{curr_color}')
    else:
        return calculate_next_color(curr_color)

    return curr_color