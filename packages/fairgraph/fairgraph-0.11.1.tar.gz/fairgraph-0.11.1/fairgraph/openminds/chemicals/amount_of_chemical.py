"""
Structured information about the amount of a given chemical that was used.
"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import EmbeddedMetadata, IRI
from fairgraph.fields import Field


class AmountOfChemical(EmbeddedMetadata):
    """
    Structured information about the amount of a given chemical that was used.
    """

    type_ = ["https://openminds.ebrains.eu/chemicals/AmountOfChemical"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field("amount", "openminds.core.QuantitativeValue", "vocab:amount", doc="no description available"),
        Field(
            "chemical_product",
            [
                "openminds.chemicals.ChemicalMixture",
                "openminds.chemicals.ChemicalSubstance",
                "openminds.controlledterms.MolecularEntity",
            ],
            "vocab:chemicalProduct",
            required=True,
            doc="no description available",
        ),
    ]

    def __init__(self, amount=None, chemical_product=None, id=None, data=None, space=None, scope=None):
        return super().__init__(data=data, amount=amount, chemical_product=chemical_product)
