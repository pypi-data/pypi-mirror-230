"""

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import EmbeddedMetadata, IRI
from fairgraph.fields import Field


class QualitativeRelationAssessment(EmbeddedMetadata):
    """ """

    type_ = ["https://openminds.ebrains.eu/sands/QualitativeRelationAssessment"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field(
            "criteria",
            "openminds.core.ProtocolExecution",
            "vocab:criteria",
            doc="Aspects or standards on which a judgement or decision is based.",
        ),
        Field(
            "in_relation_to",
            [
                "openminds.sands.CustomAnatomicalEntity",
                "openminds.sands.ParcellationEntity",
                "openminds.sands.ParcellationEntityVersion",
            ],
            "vocab:inRelationTo",
            required=True,
            doc="Reference to a related element.",
        ),
        Field(
            "qualitative_overlap",
            "openminds.controlledterms.QualitativeOverlap",
            "vocab:qualitativeOverlap",
            required=True,
            doc="Semantic characterization of how much two things occupy the same space.",
        ),
    ]

    def __init__(
        self, criteria=None, in_relation_to=None, qualitative_overlap=None, id=None, data=None, space=None, scope=None
    ):
        return super().__init__(
            data=data, criteria=criteria, in_relation_to=in_relation_to, qualitative_overlap=qualitative_overlap
        )
