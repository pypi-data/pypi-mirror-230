"""

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - longitudinal plane
         - The 'longitudinal plane' is always perpendicular to the axial and frontal plane of an organism, extremity or organ, running parallel to the 'median plane' and dividing it into a left and right part.
       * - axial plane
         - An anatomical plane which divides the body into cranial and caudal (head and tail) parts.
       * - frontal plane
         - The 'frontal plane' is always perpendicular to the axial and longitudinal plane of an organism, extremity or organ, dividing it into an anterior, rostral or front part, and a posterior, caudal or back part.
       * - sagittal plane
         - An anatomical plane which divides the body into right and left parts.
       * - coronal plane
         - An anatomical plane which divides the body into divides the body into dorsal and ventral (back and front, or posterior and anterior) parts.
       * - axial plane
         - The 'axial plane' is always perpendicular to the longitudinal and the frontal plane of an organism, extremity or organ, dividing it into a dorsal, superior, above or top part, and a ventral, inferior, below or bottom part.

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class AnatomicalPlane(KGObject):
    """

    .. list-table:: **Possible values**
       :widths: 20 80
       :header-rows: 0

       * - longitudinal plane
         - The 'longitudinal plane' is always perpendicular to the axial and frontal plane of an organism, extremity or organ, running parallel to the 'median plane' and dividing it into a left and right part.
       * - axial plane
         - An anatomical plane which divides the body into cranial and caudal (head and tail) parts.
       * - frontal plane
         - The 'frontal plane' is always perpendicular to the axial and longitudinal plane of an organism, extremity or organ, dividing it into an anterior, rostral or front part, and a posterior, caudal or back part.
       * - sagittal plane
         - An anatomical plane which divides the body into right and left parts.
       * - coronal plane
         - An anatomical plane which divides the body into divides the body into dorsal and ventral (back and front, or posterior and anterior) parts.
       * - axial plane
         - The 'axial plane' is always perpendicular to the longitudinal and the frontal plane of an organism, extremity or organ, dividing it into a dorsal, superior, above or top part, and a ventral, inferior, below or bottom part.

    """

    default_space = "controlled"
    type_ = ["https://openminds.ebrains.eu/controlledTerms/AnatomicalPlane"]
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
            doc="Word or phrase that constitutes the distinctive designation of the anatomical plane.",
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
            doc="Longer statement or account giving the characteristics of the anatomical plane.",
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
            "used_in",
            "openminds.specimenprep.SlicingDeviceUsage",
            "^vocab:slicingPlane",
            reverse="slicing_planes",
            multiple=True,
            doc="reverse of 'slicingPlane'",
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
        used_in=None,
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
            used_in=used_in,
        )
