"""

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import EmbeddedMetadata, IRI
from fairgraph.fields import Field


class Rectangle(EmbeddedMetadata):
    """ """

    type_ = ["https://openminds.ebrains.eu/sands/Rectangle"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field(
            "length", "openminds.core.QuantitativeValue", "vocab:length", required=True, doc="no description available"
        ),
        Field(
            "width", "openminds.core.QuantitativeValue", "vocab:width", required=True, doc="no description available"
        ),
    ]

    def __init__(self, length=None, width=None, id=None, data=None, space=None, scope=None):
        return super().__init__(data=data, length=length, width=width)
