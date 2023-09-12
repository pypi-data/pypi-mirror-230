"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - `arterial blood <http://purl.obolibrary.org/obo/UBERON_0013755>`_
         - 'Arterial blood' is the oxygenated portion of blood which occupies the pulmonary vein, the left chambers of the heart, and the arteries of the circulatory system.
       * - `venous blood <http://purl.obolibrary.org/obo/UBERON_0013756>`_
         - 'Venous blood' is deoxygenated blood which travels from the peripheral vessels, through the venous system into the right atrium of the heart.
       * - `blood <http://purl.obolibrary.org/obo/UBERON_0000178>`_
         - ''Blood' is a body fluid in the circulatory system of vertebrates that transports substances to and from cells (e.g. nutrients, oxygen or metabolic waste products). [[adapted from Wikipedia](https://en.wikipedia.org/wiki/Blood)]

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class OrganismSubstance(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - `arterial blood <http://purl.obolibrary.org/obo/UBERON_0013755>`_
         - 'Arterial blood' is the oxygenated portion of blood which occupies the pulmonary vein, the left chambers of the heart, and the arteries of the circulatory system.
       * - `venous blood <http://purl.obolibrary.org/obo/UBERON_0013756>`_
         - 'Venous blood' is deoxygenated blood which travels from the peripheral vessels, through the venous system into the right atrium of the heart.
       * - `blood <http://purl.obolibrary.org/obo/UBERON_0000178>`_
         - ''Blood' is a body fluid in the circulatory system of vertebrates that transports substances to and from cells (e.g. nutrients, oxygen or metabolic waste products). [[adapted from Wikipedia](https://en.wikipedia.org/wiki/Blood)]

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/OrganismSubstance"]
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
            doc="Word or phrase that constitutes the distinctive designation of the organism substance.",
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
            doc="Longer statement or account giving the characteristics of the organism substance.",
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
            "is_location_of",
            ["openminds.ephys.ElectrodeArrayUsage", "openminds.ephys.ElectrodeUsage", "openminds.ephys.PipetteUsage"],
            ["^vocab:anatomicalLocation", "^vocab:anatomicalLocationOfElectrodes"],
            reverse=["anatomical_locations", "anatomical_location_of_electrodes"],
            multiple=True,
            doc="reverse of anatomicalLocation, anatomicalLocationOfElectrodes",
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
            "samples",
            ["openminds.core.TissueSample", "openminds.core.TissueSampleCollection"],
            "^vocab:origin",
            reverse="origins",
            multiple=True,
            doc="reverse of 'origin'",
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
        is_location_of=None,
        is_used_to_group=None,
        samples=None,
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
            is_location_of=is_location_of,
            is_used_to_group=is_used_to_group,
            samples=samples,
            studied_in=studied_in,
        )
