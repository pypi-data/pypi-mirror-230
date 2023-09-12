"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - autism spectrum disorder model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal autism sprectrum disorder.
       * - Alzheimer's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Alzheimer's disease.
       * - Huntington's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Huntington's disease.
       * - fragile X syndrome model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal fragile X syndrome.
       * - Williams-Beuren syndrome model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Williams-Beuren syndrome.
       * - stroke model
         - An animal or cell displaying all or some of the pathological processes that are observed during stroke in humans or animals.
       * - Parkinson's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Parkinson's disease.
       * - epilepsy model
         - An animal or cell displaying all or some of the pathological processes that are observed for epilepsy in humans or animals.

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class DiseaseModel(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - autism spectrum disorder model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal autism sprectrum disorder.
       * - Alzheimer's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Alzheimer's disease.
       * - Huntington's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Huntington's disease.
       * - fragile X syndrome model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal fragile X syndrome.
       * - Williams-Beuren syndrome model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Williams-Beuren syndrome.
       * - stroke model
         - An animal or cell displaying all or some of the pathological processes that are observed during stroke in humans or animals.
       * - Parkinson's disease model
         - An animal or cell displaying all or some of the pathological processes that are observed in the actual human or animal Parkinson's disease.
       * - epilepsy model
         - An animal or cell displaying all or some of the pathological processes that are observed for epilepsy in humans or animals.

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/DiseaseModel"]
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
            doc="Word or phrase that constitutes the distinctive designation of the disease model.",
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
            doc="Longer statement or account giving the characteristics of the disease model.",
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
            "is_modeled_by",
            "openminds.core.Strain",
            "^vocab:diseaseModel",
            reverse="disease_models",
            multiple=True,
            doc="reverse of 'diseaseModel'",
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
            "specimen_states",
            [
                "openminds.core.SubjectGroupState",
                "openminds.core.SubjectState",
                "openminds.core.TissueSampleCollectionState",
                "openminds.core.TissueSampleState",
            ],
            "^vocab:pathology",
            reverse="pathologies",
            multiple=True,
            doc="reverse of 'pathology'",
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
        is_modeled_by=None,
        is_used_to_group=None,
        specimen_states=None,
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
            is_modeled_by=is_modeled_by,
            is_used_to_group=is_used_to_group,
            specimen_states=specimen_states,
            studied_in=studied_in,
        )
