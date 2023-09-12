"""
Structured information on a hash.
"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import EmbeddedMetadata, IRI
from fairgraph.fields import Field


class Hash(EmbeddedMetadata):
    """
    Structured information on a hash.
    """

    type_ = ["https://openminds.ebrains.eu/core/Hash"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field(
            "algorithm",
            str,
            "vocab:algorithm",
            required=True,
            doc="Procedure for solving a mathematical problem in a finite number of steps. Can involve repetition of an operation.",
        ),
        Field("digest", str, "vocab:digest", required=True, doc="Summation or condensation of a body of information."),
    ]

    def __init__(self, algorithm=None, digest=None, id=None, data=None, space=None, scope=None):
        return super().__init__(data=data, algorithm=algorithm, digest=digest)
