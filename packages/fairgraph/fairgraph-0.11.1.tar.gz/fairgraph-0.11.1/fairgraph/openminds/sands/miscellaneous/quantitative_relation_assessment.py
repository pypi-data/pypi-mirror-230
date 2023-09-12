"""

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import EmbeddedMetadata, IRI
from fairgraph.fields import Field


class QuantitativeRelationAssessment(EmbeddedMetadata):
    """ """

    type_ = ["https://openminds.ebrains.eu/sands/QuantitativeRelationAssessment"]
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
            "openminds.sands.ParcellationEntityVersion",
            "vocab:inRelationTo",
            required=True,
            doc="Reference to a related element.",
        ),
        Field(
            "quantitative_overlap",
            ["openminds.core.QuantitativeValue", "openminds.core.QuantitativeValueRange"],
            "vocab:quantitativeOverlap",
            required=True,
            doc="Numerical characterization of how much two things occupy the same space.",
        ),
    ]

    def __init__(
        self, criteria=None, in_relation_to=None, quantitative_overlap=None, id=None, data=None, space=None, scope=None
    ):
        return super().__init__(
            data=data, criteria=criteria, in_relation_to=in_relation_to, quantitative_overlap=quantitative_overlap
        )
