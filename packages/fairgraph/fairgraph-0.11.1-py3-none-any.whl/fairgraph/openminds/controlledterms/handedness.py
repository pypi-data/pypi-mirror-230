"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - ambilevous handedness
         - Handedness where the organism exhibits equally poor dexterity in the use of right or left hand or foot in the performance of tasks that require one (dominant) hand or foot.
       * - ambidextrous handedness
         - Handedness where the organism exhibits no overall dominance in the use of right or left hand or foot in the performance of tasks that require one (dominant) hand or foot.
       * - left handedness
         - Handedness where the organism preferentially uses the left hand or foot for tasks requiring the use of a single hand or foot.
       * - right handedness
         - Handedness where the organism preferentially uses the right hand or foot for tasks requiring the use of a single hand or foot.
       * - mixed handedness
         - Handedness where the organism exhibits dominance in the use of right or left hand or foot differently in the performance of different tasks that require one (dominant) hand or foot.

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class Handedness(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - ambilevous handedness
         - Handedness where the organism exhibits equally poor dexterity in the use of right or left hand or foot in the performance of tasks that require one (dominant) hand or foot.
       * - ambidextrous handedness
         - Handedness where the organism exhibits no overall dominance in the use of right or left hand or foot in the performance of tasks that require one (dominant) hand or foot.
       * - left handedness
         - Handedness where the organism preferentially uses the left hand or foot for tasks requiring the use of a single hand or foot.
       * - right handedness
         - Handedness where the organism preferentially uses the right hand or foot for tasks requiring the use of a single hand or foot.
       * - mixed handedness
         - Handedness where the organism exhibits dominance in the use of right or left hand or foot differently in the performance of different tasks that require one (dominant) hand or foot.

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/Handedness"]
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
            doc="Word or phrase that constitutes the distinctive designation of the handedness.",
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
            doc="Longer statement or account giving the characteristics of the handedness.",
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
        Field(
            "subject_states",
            ["openminds.core.SubjectGroupState", "openminds.core.SubjectState"],
            "^vocab:handedness",
            reverse="handedness",
            multiple=True,
            doc="reverse of 'handedness'",
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
        is_used_to_group=None,
        studied_in=None,
        subject_states=None,
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
            is_used_to_group=is_used_to_group,
            studied_in=studied_in,
            subject_states=subject_states,
        )
