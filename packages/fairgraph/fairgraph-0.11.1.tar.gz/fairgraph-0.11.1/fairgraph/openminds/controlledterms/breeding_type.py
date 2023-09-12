"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - outbred
         - 'Outbred' breeding (or outbreeding) is the production of offspring from mating organisms that belong to two different background breeds.
       * - coisogenic
         - 'Coisogenic' breeding  is a type of inbreeding where the offspring differs at only a single locus through a mutation occurring in the original inbred strain.
       * - selective inbred
         - 'Selective inbred' breeding (or selective inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed) and have been selected based on a particular phenotype.
       * - congenic
         - 'Congenic' breeding is the production of offspring from repeated backcrossing into an inbred (background) strain, with selection for a particular marker, ideally a single gene from another strain.
       * - hybrid
         - A 'hybrid' is an organism that resulted from special outbreeding of two species (normally within the same genus).
       * - inbred
         - 'Inbred' breeding (or inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed).

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class BreedingType(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - outbred
         - 'Outbred' breeding (or outbreeding) is the production of offspring from mating organisms that belong to two different background breeds.
       * - coisogenic
         - 'Coisogenic' breeding  is a type of inbreeding where the offspring differs at only a single locus through a mutation occurring in the original inbred strain.
       * - selective inbred
         - 'Selective inbred' breeding (or selective inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed) and have been selected based on a particular phenotype.
       * - congenic
         - 'Congenic' breeding is the production of offspring from repeated backcrossing into an inbred (background) strain, with selection for a particular marker, ideally a single gene from another strain.
       * - hybrid
         - A 'hybrid' is an organism that resulted from special outbreeding of two species (normally within the same genus).
       * - inbred
         - 'Inbred' breeding (or inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed).

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/BreedingType"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field(
            "name",
            str,
            "vocab:name",
            required=True,
            doc="Word or phrase that constitutes the distinctive designation of the breeding type.",
        ),
        Field(
            "definition",
            str,
            "vocab:definition",
            doc="Short, but precise statement of the meaning of a word, word group, sign or a symbol.",
        ),
        Field(
            "description",
            str,
            "vocab:description",
            doc="Longer statement or account giving the characteristics of the breeding type.",
        ),
        Field(
            "interlex_identifier",
            IRI,
            "vocab:interlexIdentifier",
            doc="Persistent identifier for a term registered in the InterLex project.",
        ),
        Field(
            "knowledge_space_link",
            IRI,
            "vocab:knowledgeSpaceLink",
            doc="Persistent link to an encyclopedia entry in the Knowledge Space project.",
        ),
        Field(
            "preferred_ontology_identifier",
            IRI,
            "vocab:preferredOntologyIdentifier",
            doc="Persistent identifier of a preferred ontological term.",
        ),
        Field(
            "synonyms",
            str,
            "vocab:synonym",
            multiple=True,
            doc="Words or expressions used in the same language that have the same or nearly the same meaning in some or all senses.",
        ),
        Field(
            "describes",
            [
                "openminds.computation.ValidationTestVersion",
                "openminds.computation.WorkflowRecipeVersion",
                "openminds.core.DatasetVersion",
                "openminds.core.MetaDataModelVersion",
                "openminds.core.ModelVersion",
                "openminds.core.SoftwareVersion",
                "openminds.core.WebServiceVersion",
                "openminds.publications.Book",
                "openminds.publications.Chapter",
                "openminds.publications.LearningResource",
                "openminds.publications.LivePaperVersion",
                "openminds.publications.ScholarlyArticle",
                "openminds.sands.BrainAtlasVersion",
                "openminds.sands.CommonCoordinateSpaceVersion",
            ],
            "^vocab:keyword",
            reverse="keywords",
            multiple=True,
            doc="reverse of 'keyword'",
        ),
        Field(
            "is_breeding_type_of",
            "openminds.core.Strain",
            "^vocab:breedingType",
            reverse="breeding_types",
            multiple=True,
            doc="reverse of 'breedingType'",
        ),
        Field(
            "is_used_to_group",
            "openminds.core.FileBundle",
            "^vocab:groupedBy",
            reverse="grouped_by",
            multiple=True,
            doc="reverse of 'groupedBy'",
        ),
        Field(
            "studied_in",
            [
                "openminds.computation.DataAnalysis",
                "openminds.computation.DataCopy",
                "openminds.computation.GenericComputation",
                "openminds.computation.ModelValidation",
                "openminds.computation.Optimization",
                "openminds.computation.Simulation",
                "openminds.computation.ValidationTest",
                "openminds.computation.Visualization",
                "openminds.core.Model",
                "openminds.core.ProtocolExecution",
                "openminds.ephys.CellPatching",
                "openminds.ephys.ElectrodePlacement",
                "openminds.ephys.RecordingActivity",
                "openminds.specimenprep.CranialWindowPreparation",
                "openminds.specimenprep.TissueCulturePreparation",
                "openminds.specimenprep.TissueSampleSlicing",
                "openminds.stimulation.StimulationActivity",
            ],
            "^vocab:studyTarget",
            reverse="study_targets",
            multiple=True,
            doc="reverse of 'studyTarget'",
        ),
    ]
    existence_query_fields = ("name",)

    def __init__(
        self,
        name=None,
        definition=None,
        description=None,
        interlex_identifier=None,
        knowledge_space_link=None,
        preferred_ontology_identifier=None,
        synonyms=None,
        describes=None,
        is_breeding_type_of=None,
        is_used_to_group=None,
        studied_in=None,
        id=None,
        data=None,
        space=None,
        scope=None,
    ):
        return super().__init__(
            id=id,
            space=space,
            scope=scope,
            data=data,
            name=name,
            definition=definition,
            description=description,
            interlex_identifier=interlex_identifier,
            knowledge_space_link=knowledge_space_link,
            preferred_ontology_identifier=preferred_ontology_identifier,
            synonyms=synonyms,
            describes=describes,
            is_breeding_type_of=is_breeding_type_of,
            is_used_to_group=is_used_to_group,
            studied_in=studied_in,
        )
