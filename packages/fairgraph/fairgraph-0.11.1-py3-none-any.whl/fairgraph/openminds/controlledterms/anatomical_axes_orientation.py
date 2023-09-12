"""
Structured information on the anatomical directions of the X, Y, and Z axis.
    Here we show the first 20 possible values, an additional 28 values are not shown.

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - RSA
         - X, Y, Z axes are oriented towards right, superior and anterior, respectively.
       * - SAL
         - X, Y, Z axes are oriented towards superior, anterior and left, respectively.
       * - RIP
         - X, Y, Z axes are oriented towards right, inferior and posterior, respectively.
       * - SRA
         - X, Y, Z axes are oriented towards superior, right and anterior, respectively.
       * - ALI
         - X, Y, Z axes are oriented towards anterior, left and inferior, respectively.
       * - ILA
         - X, Y, Z axes are oriented towards inferior, left and anterior, respectively.
       * - SAR
         - X, Y, Z axes are oriented towards superior, anterior and right, respectively.
       * - ILP
         - X, Y, Z axes are oriented towards inferior, left and posterior, respectively.
       * - RSP
         - X, Y, Z axes are oriented towards right, superior and posterior, respectively.
       * - ASR
         - X, Y, Z axes are oriented towards anterior, superior and right, respectively.
       * - IPR
         - X, Y, Z axes are oriented towards inferior, posterior and right, respectively.
       * - IPL
         - X, Y, Z axes are oriented towards inferior, posterior and left, respectively.
       * - RPS
         - X, Y, Z axes are oriented towards right, posterior and superior, respectively.
       * - SPL
         - X, Y, Z axes are oriented towards superior, posterior and left, respectively.
       * - SPR
         - X, Y, Z axes are oriented towards superior, posterior and right, respectively.
       * - AIL
         - X, Y, Z axes are oriented towards anterior, inferior and left, respectively.
       * - LIA
         - X, Y, Z axes are oriented towards left, inferior and anterior, respectively.
       * - RAS
         - X, Y, Z axes are oriented towards right, anterior and superior, respectively.
       * - IAR
         - X, Y, Z axes are oriented towards inferior, anterior and right, respectively.
       * - PSL
         - X, Y, Z axes are oriented towards posterior, superior and left, respectively.

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class AnatomicalAxesOrientation(KGObject):
    """
    Structured information on the anatomical directions of the X, Y, and Z axis.
    Here we show the first 20 possible values, an additional 28 values are not shown.

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - RSA
         - X, Y, Z axes are oriented towards right, superior and anterior, respectively.
       * - SAL
         - X, Y, Z axes are oriented towards superior, anterior and left, respectively.
       * - RIP
         - X, Y, Z axes are oriented towards right, inferior and posterior, respectively.
       * - SRA
         - X, Y, Z axes are oriented towards superior, right and anterior, respectively.
       * - ALI
         - X, Y, Z axes are oriented towards anterior, left and inferior, respectively.
       * - ILA
         - X, Y, Z axes are oriented towards inferior, left and anterior, respectively.
       * - SAR
         - X, Y, Z axes are oriented towards superior, anterior and right, respectively.
       * - ILP
         - X, Y, Z axes are oriented towards inferior, left and posterior, respectively.
       * - RSP
         - X, Y, Z axes are oriented towards right, superior and posterior, respectively.
       * - ASR
         - X, Y, Z axes are oriented towards anterior, superior and right, respectively.
       * - IPR
         - X, Y, Z axes are oriented towards inferior, posterior and right, respectively.
       * - IPL
         - X, Y, Z axes are oriented towards inferior, posterior and left, respectively.
       * - RPS
         - X, Y, Z axes are oriented towards right, posterior and superior, respectively.
       * - SPL
         - X, Y, Z axes are oriented towards superior, posterior and left, respectively.
       * - SPR
         - X, Y, Z axes are oriented towards superior, posterior and right, respectively.
       * - AIL
         - X, Y, Z axes are oriented towards anterior, inferior and left, respectively.
       * - LIA
         - X, Y, Z axes are oriented towards left, inferior and anterior, respectively.
       * - RAS
         - X, Y, Z axes are oriented towards right, anterior and superior, respectively.
       * - IAR
         - X, Y, Z axes are oriented towards inferior, anterior and right, respectively.
       * - PSL
         - X, Y, Z axes are oriented towards posterior, superior and left, respectively.

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/AnatomicalAxesOrientation"]
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
            doc="Word or phrase that constitutes the distinctive designation of the anatomical axes orientation.",
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
            doc="Longer statement or account giving the characteristics of the anatomical axes orientation.",
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
            "is_orientation_of",
            "openminds.sands.CustomCoordinateSpace",
            "^vocab:anatomicalAxesOrientation",
            reverse="anatomical_axes_orientations",
            multiple=True,
            doc="reverse of 'anatomicalAxesOrientation'",
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
        is_orientation_of=None,
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
            is_orientation_of=is_orientation_of,
        )
