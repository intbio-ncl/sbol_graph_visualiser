import rdflib


class SBOLIdentifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.objects = Objects(self.namespaces)
        self.predicates = Predicates(self.namespaces)
        self.external = ExternalIdentifiers(self.namespaces)
    

class Namespace:
    def __init__(self):
        self.sbol = rdflib.URIRef('http://sbols.org/v2#')
        identifiers = rdflib.URIRef('http://identifiers.org/')
        self.sequence_ontology = rdflib.URIRef(identifiers + 'so/SO:')
        self.sbo_biomodels = rdflib.URIRef(identifiers + 'biomodels.sbo/SBO:')
        self.identifier_edam = rdflib.URIRef(identifiers + 'edam/')

        self.biopax = rdflib.URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = rdflib.URIRef('http://purl.org/dc/terms/')
        self.edam = rdflib.URIRef('http://edamontology.org/format')
        self.owl = rdflib.URIRef('http://www.w3.org/2002/07/owl#')
        self.prov = rdflib.URIRef('https://www.w3.org/ns/prov#')

class Objects:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.component_definition = rdflib.term.URIRef(self.namespaces.sbol + 'ComponentDefinition')
        self.component = rdflib.term.URIRef(self.namespaces.sbol + 'Component')
        self.module_definition = rdflib.term.URIRef(self.namespaces.sbol + 'ModuleDefinition')
        self.range = rdflib.term.URIRef(self.namespaces.sbol + 'Range')
        self.cut = rdflib.term.URIRef(self.namespaces.sbol + 'Cut')
        self.sequence = rdflib.term.URIRef(self.namespaces.sbol + "Sequence")
        self.combinatorial_derivation = rdflib.term.URIRef(self.namespaces.sbol + "CombinatorialDerivation")
        self.experiment = rdflib.term.URIRef(self.namespaces.sbol + "Experiment")
        self.experimental_data = rdflib.term.URIRef(self.namespaces.sbol + "ExperimentalData")
        self.functional_component = rdflib.term.URIRef(self.namespaces.sbol + "FunctionalComponent")
        self.implementation = rdflib.term.URIRef(self.namespaces.sbol + "Implementation")
        self.interaction = rdflib.term.URIRef(self.namespaces.sbol + "Interaction")
        self.generic_location = rdflib.term.URIRef(self.namespaces.sbol + "GenericLocation")
        self.mapsTo = rdflib.term.URIRef(self.namespaces.sbol + "MapsTo")
        self.module = rdflib.term.URIRef(self.namespaces.sbol + "Module")
        self.model = rdflib.term.URIRef(self.namespaces.sbol + "Model")
        self.attachment = rdflib.term.URIRef(self.namespaces.sbol + "Attachment")
        self.collection = rdflib.term.URIRef(self.namespaces.sbol + "Collection")
        self.sequence_annotation = rdflib.term.URIRef(self.namespaces.sbol + "SequenceAnnotation")
        self.participation = rdflib.term.URIRef(self.namespaces.sbol + "Participation")
        self.sequence_constraint = rdflib.term.URIRef(self.namespaces.sbol + "SequenceConstraint")

        self.top_levels = {rdflib.URIRef(self.namespaces.sbol + name) for name in
                            ['Sequence',
                            'ComponentDefinition',
                            'ModuleDefinition',
                            'Model',
                            'Collection',
                            'GenericTopLevel',
                            'Attachment',
                            'Activity',
                            'Agent',
                            'Plan',
                            'Implementation',
                            'CombinatorialDerivation',
                            'Experiment',
                            'ExperimentalData']}

class Predicates:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.rdf_type = rdflib.URIRef(rdflib.RDF.type)

        self.display_id = rdflib.term.URIRef(self.namespaces.sbol + 'displayId')
        self.persistent_identity = rdflib.term.URIRef(self.namespaces.sbol + 'persistentIdentity')
        self.version = rdflib.term.URIRef(self.namespaces.sbol + 'version')
        self.title = rdflib.term.URIRef(self.namespaces.dc + 'title')
        self.description = rdflib.term.URIRef(self.namespaces.dc + 'description')


        self.component = rdflib.term.URIRef(self.namespaces.sbol + 'component')
        self.functional_component = rdflib.term.URIRef(self.namespaces.sbol + 'functionalComponent')
        self.sequence_annotation = rdflib.term.URIRef(self.namespaces.sbol + 'sequenceAnnotation')
        self.sequence_constraint = rdflib.term.URIRef(self.namespaces.sbol + 'sequenceConstraint')
        self.location = rdflib.term.URIRef(self.namespaces.sbol + 'location')
        self.sequence = rdflib.term.URIRef(self.namespaces.sbol + 'sequence')
        self.cut = rdflib.term.URIRef(self.namespaces.sbol + 'cut')
        self.at = rdflib.term.URIRef(self.namespaces.sbol + 'at')

        self.definition = rdflib.term.URIRef(self.namespaces.sbol + 'definition')
        self.sequence_constraint_restriction = rdflib.term.URIRef(self.namespaces.sbol + 'restriction')
        self.sequence_constraint_subject = rdflib.term.URIRef(self.namespaces.sbol + 'subject')
        self.sequence_constraint_object = rdflib.term.URIRef(self.namespaces.sbol + 'object')
        self.type = rdflib.term.URIRef(self.namespaces.sbol + 'type')
        self.role = rdflib.term.URIRef(self.namespaces.sbol + 'role')
        self.start = rdflib.term.URIRef(self.namespaces.sbol + 'start')
        self.end = rdflib.term.URIRef(self.namespaces.sbol + 'end')

        self.interaction = rdflib.term.URIRef(self.namespaces.sbol + 'interaction')
        self.participation = rdflib.term.URIRef(self.namespaces.sbol + 'participation')
        self.elements = rdflib.term.URIRef(self.namespaces.sbol + 'elements')
        self.participant = rdflib.term.URIRef(self.namespaces.sbol + 'participant')
        self.encoding = rdflib.term.URIRef(self.namespaces.sbol + 'encoding')
        self.direction = rdflib.term.URIRef(self.namespaces.sbol + 'direction')
        self.access = rdflib.term.URIRef(self.namespaces.sbol + 'access')
        self.orientation = rdflib.term.URIRef(self.namespaces.sbol + 'orientation')

        self.framework = rdflib.term.URIRef(self.namespaces.sbol + 'framework')
        self.language = rdflib.term.URIRef(self.namespaces.sbol + 'language')
        self.source = rdflib.term.URIRef(self.namespaces.sbol + 'source')

        self.local = rdflib.term.URIRef(self.namespaces.sbol + 'local')
        self.remote = rdflib.term.URIRef(self.namespaces.sbol + 'remote')

        self.module = rdflib.term.URIRef(self.namespaces.sbol + "module")
        self.ownership_predicates = {rdflib.URIRef(self.namespaces.sbol + predicate) for predicate in
                                ['module',
                                'mapsTo',
                                'interaction',
                                'participation',
                                'functionalComponent',
                                'sequenceConstraint',
                                'location',
                                'sequenceAnnotation',
                                'variableComponent']}  

class ExternalIdentifiers:
    def __init__(self, namespaces):
        self.namespaces = namespaces

        self.component_definition_DNA = rdflib.URIRef(self.namespaces.biopax + "Dna")
        self.component_definition_DNARegion = rdflib.URIRef(self.namespaces.biopax + "DnaRegion")
        self.component_definition_RNA = rdflib.URIRef(self.namespaces.biopax + "Rna")
        self.component_definition_RNARegion = rdflib.URIRef(self.namespaces.biopax + "RnaRegion")
        self.component_definition_protein = rdflib.URIRef(self.namespaces.biopax + "Protein")
        self.component_definition_smallMolecule = rdflib.URIRef(self.namespaces.biopax + "SmallMolecule")
        self.component_definition_complex = rdflib.URIRef(self.namespaces.biopax + "Complex")

        self.component_definition_promoter       = rdflib.URIRef(self.namespaces.sequence_ontology + "0000167")
        self.component_definition_rbs            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000139")
        self.component_definition_cds            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000316")
        self.component_definition_terminator     = rdflib.URIRef(self.namespaces.sequence_ontology + "0000141")
        self.component_definition_gene           = rdflib.URIRef(self.namespaces.sequence_ontology + "0000704")
        self.component_definition_operator       = rdflib.URIRef(self.namespaces.sequence_ontology + "0000057")
        self.component_definition_engineeredGene = rdflib.URIRef(self.namespaces.sequence_ontology + "0000280")
        self.component_definition_mRNA           = rdflib.URIRef(self.namespaces.sequence_ontology + "0000234")
        self.component_definition_engineeredRegion = rdflib.URIRef(self.namespaces.sequence_ontology + "0000804")
        self.component_definition_nonCovBindingSite = rdflib.URIRef(self.namespaces.sequence_ontology + "0001091")
        self.component_definition_effector       = rdflib.URIRef("http://identifiers.org/chebi/CHEBI:35224") 
        self.component_definition_startCodon     = rdflib.URIRef(self.namespaces.sequence_ontology + "0000318")
        self.component_definition_tag            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000324")
        self.component_definition_engineeredTag  = rdflib.URIRef(self.namespaces.sequence_ontology + "0000807")
        self.component_definition_sgRNA          = rdflib.URIRef(self.namespaces.sequence_ontology + "0001998")
        self.component_definition_transcriptionFactor = rdflib.URIRef("ttp://identifiers.org/go/GO:0003700")

        self.interaction_inhibition = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000169")
        self.interaction_stimulation = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000170")
        self.interaction_biochemical_reaction = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000176")
        self.interaction_noncovalent_bonding = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000177")
        self.interaction_degradation = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000179")
        self.interaction_genetic_production = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000589")
        self.interaction_control = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000168")

        self.participant_inhibitor = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000020")
        self.participant_inhibited = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000642")
        self.participant_stimulator =  rdflib.URIRef(self.namespaces.sbo_biomodels + "0000459")
        self.participant_stimulated = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000643")
        self.participant_modifier = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000019")
        self.participant_modified = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000644")
        self.participant_product = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000011")
        self.participant_reactant = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000010")
        self.participant_participation_promoter = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000598") 
        self.participant_template = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000645")

        self.location_orientation_inline = rdflib.URIRef(self.namespaces.sbol + "inline")
        self.location_orientation_reverseComplement = rdflib.URIRef(self.namespaces.sbol + "reverseComplement")

        self.functional_component_direction_in = rdflib.URIRef(self.namespaces.sbol + "in")
        self.functional_component_direction_out = rdflib.URIRef(self.namespaces.sbol + "out")
        self.functional_component_direction_inout = rdflib.URIRef(self.namespaces.sbol + "inout") 
        self.functional_component_direction_none = rdflib.URIRef(self.namespaces.sbol + "none")

        self.component_instance_acess_public = rdflib.URIRef(self.namespaces.sbol + "public")
        self.component_instance_acess_private = rdflib.URIRef(self.namespaces.sbol + "private")

        self.sequence_encoding_iupacDNA = rdflib.URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacRNA = rdflib.URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacProtein = rdflib.URIRef("http://www.chem.qmul.ac.uk/iupac/AminoAcid/")
        self.sequence_encoding_opensmilesSMILES = rdflib.URIRef("http://www.opensmiles.org/opensmiles.html")

        self.sequence_constraint_restriction_precedes = rdflib.URIRef(self.namespaces.sbol + "precedes")
        self.sequence_constraint_restriction_sameOrientationAs = rdflib.URIRef(self.namespaces.sbol + "sameOrientationAs")
        self.sequence_constraint_restriction_oppositeOrientationAs = rdflib.URIRef(self.namespaces.sbol + "oppositeOrientationAs")
        self.sequence_constraint_restriction_differentFrom = rdflib.URIRef(self.namespaces.sbol + "differentFrom")

        self.model_language_SBML = rdflib.URIRef(self.namespaces.identifier_edam + "format_2585")
        self.model_language_CellML = rdflib.URIRef(self.namespaces.identifier_edam + "format_3240")
        self.model_language_BioPAX = rdflib.URIRef(self.namespaces.identifier_edam + "format_3156")

        self.model_framework_continuous =  rdflib.URIRef(self.namespaces.sbo_biomodels + "0000062")
        self.model_framework_discrete = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000063")

        self.mapsTo_refinement_useRemote = rdflib.URIRef(self.namespaces.sbol + "useRemote")
        self.mapsTo_refinement_useLocal = rdflib.URIRef(self.namespaces.sbol + "useLocal") 
        self.mapsTo_refinement_verifyIdentical  = rdflib.URIRef(self.namespaces.sbol + "verifyIdentical")
        self.mapsTo_refinement_merge = rdflib.URIRef(self.namespaces.sbol + "merge") 

        self.variable_component_cardinality_zeroOrOne = rdflib.URIRef(self.namespaces.sbol + "zeroOrOne") 
        self.variable_component_cardinality_one = rdflib.URIRef(self.namespaces.sbol + "one")
        self.variable_component_cardinality_zeroOrMore = rdflib.URIRef(self.namespaces.sbol + "zeroOrMore")
        self.variable_component_cardinality_oneOrMore = rdflib.URIRef(self.namespaces.sbol + "oneOrMore")

        self.dna_roles = {self.component_definition_promoter : "Promoter",
                        self.component_definition_rbs : "RBS",
                        self.component_definition_cds : "CDS",
                        self.component_definition_terminator : "Terminator",
                        self.component_definition_engineeredRegion : "Engineered Region",
                        self.component_definition_engineeredRegion : "Engineered Region",
                        self.component_definition_operator : "Operator",
                        self.component_definition_gene : "Gene"}
        self.rna_roles = {self.component_definition_mRNA : "mRNA",
                         self.component_definition_sgRNA : "sgRNA",
                         self.component_definition_cds : "CDS RNA"}
        self.protein_roles = {self.component_definition_transcriptionFactor : "Transcriptional Factor"}
        self.small_molecule_roles = {self.component_definition_effector : "Effector"}
        self.complex_roles = {}

    def get_component_definition_identifier_name(self, type,role = None):
        '''
        Reverse method that when you know the URI's return a descriptive name for said ComponentDefinition
        '''
        if type == self.component_definition_DNA or type == self.component_definition_DNARegion:
            try:
                return self.dna_roles[role]
            except KeyError:
                return "DNA"

        elif type == self.component_definition_RNA or type == self.component_definition_RNARegion:
            try:
                return self.rna_roles[role]
            except KeyError:
                return "RNA"

        elif type == self.component_definition_protein:
            try:
                return self.protein_roles[role]
            except KeyError:
                return "Protein"

        elif type == self.component_definition_smallMolecule:
            try:
                return self.small_molecule_roles[role]
            except KeyError:
                return "Small Molecule"

        elif type == self.component_definition_complex:
            try:
                return self.complex_roles[role]
            except KeyError:
                return "Complex"

        else:
            return "Unknown"
        return "Unknown"
    
    def get_type_from_role(self,role):
        if role in self.dna_roles:
            return self.component_definition_DNA
        if role in self.rna_roles:
            return self.component_definition_RNA
        if role in self.protein_roles:
            return self.component_definition_protein
        if role in self.small_molecule_roles:
            return self.component_definition_smallMolecule
        if role in self.complex_roles:
            return self.component_definition_complex

    def get_participant_role_name(self,role):
        if role == self.participant_inhibitor:
            return "Inhibitor"
        if role == self.participant_inhibited:
            return "Inhibited"
        if role == self.participant_stimulator:
            return "Stimulator"
        if role == self.participant_stimulated:
            return "Stimulated"
        if role == self.participant_modifier:
            return "Modifier"
        if role == self.participant_modified:
            return "Modified"
        if role == self.participant_product:
            return "Product"
        if role == self.participant_reactant:
            return "Reactant"
        if role == self.participant_participation_promoter:
            return "Promoter"
        if role == self.participant_template:
            return "Template"
        return "Unknown"

    def get_interaction_type_name(self,int_type):
        if int_type == self.interaction_inhibition:
            return "Inhibition"
        if int_type == self.interaction_stimulation:
            return "Stimulation"
        if int_type == self.interaction_biochemical_reaction:
            return "Biochemical reaction"
        if int_type == self.interaction_noncovalent_bonding:
            return "Noncovalent bonding"
        if int_type == self.interaction_degradation:
            return "Degradation"
        if int_type == self.interaction_genetic_production:
            return "Genetic production"
        if int_type == self.interaction_control:
            return "Control"
        return "Unknown"
    
    def get_location_orientation_name(self,orientation):
        if orientation == self.location_orientation_inline:
            return "Inline"
        if orientation == self.location_orientation_reverseComplement:
            return "Reverse Complement"

    def get_model_framework_name(self,framework):
        if framework == self.model_framework_continuous:
            return "Continuous"
        if framework == self.model_framework_discrete:
            return "Discrete"
        return "Unknown Framework"

    def get_model_language_name(self,language):
        if language == self.model_language_SBML:
            return "SBML"
        if language == self.model_language_CellML:
            return "CellML"
        if language == self.model_language_BioPAX:
            return "BioPAX"
        return "Unknown Language"

identifiers = SBOLIdentifiers()