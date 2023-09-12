"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - `in utero <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/90>`_
         - Something happening in, within, or while inside the uterus.
       * - `in vivo <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/89>`_
         - Something happening or existing inside a living body.
       * - `ex vivo <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/88>`_
         - Something happening or existing outside a living body.
       * - `in vitro <http://uri.interlex.org/tgbugs/uris/readable/technique/inVitro>`_
         - Something happening outside the body in artificial conditions (e.g., in a test tube or culture dish).
       * - `in silico <http://id.nlm.nih.gov/mesh/2018/M0572590>`_
         - Conducted or produced by means of computer modelling or simulation.
       * - `in situ <http://uri.interlex.org/tgbugs/uris/readable/technique/inSitu>`_
         - Something happening or being examined in the original place instead of being moved to another place

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class PreparationType(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - `in utero <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/90>`_
         - Something happening in, within, or while inside the uterus.
       * - `in vivo <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/89>`_
         - Something happening or existing inside a living body.
       * - `ex vivo <http://uri.interlex.org/tgbugs/uris/indexes/ontologies/methods/88>`_
         - Something happening or existing outside a living body.
       * - `in vitro <http://uri.interlex.org/tgbugs/uris/readable/technique/inVitro>`_
         - Something happening outside the body in artificial conditions (e.g., in a test tube or culture dish).
       * - `in silico <http://id.nlm.nih.gov/mesh/2018/M0572590>`_
         - Conducted or produced by means of computer modelling or simulation.
       * - `in situ <http://uri.interlex.org/tgbugs/uris/readable/technique/inSitu>`_
         - Something happening or being examined in the original place instead of being moved to another place

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/PreparationType"]
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
            doc="Word or phrase that constitutes the distinctive designation of the preparation type.",
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
            doc="Longer statement or account giving the characteristics of the preparation type.",
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
            "used_for",
            [
                "openminds.core.ProtocolExecution",
                "openminds.ephys.CellPatching",
                "openminds.ephys.ElectrodePlacement",
                "openminds.ephys.RecordingActivity",
                "openminds.specimenprep.CranialWindowPreparation",
                "openminds.specimenprep.TissueCulturePreparation",
                "openminds.specimenprep.TissueSampleSlicing",
                "openminds.stimulation.StimulationActivity",
            ],
            "^vocab:preparationDesign",
            reverse="preparation_designs",
            multiple=True,
            doc="reverse of 'preparationDesign'",
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
        used_for=None,
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
            used_for=used_for,
        )
