"""

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class TissueSampleCollection(KGObject):
    """ """

    default_space = "dataset"
    type_ = ["https://openminds.ebrains.eu/core/TissueSampleCollection"]
    context = {
        "schema": "http://schema.org/",
        "kg": "https://kg.ebrains.eu/api/instances/",
        "vocab": "https://openminds.ebrains.eu/vocab/",
        "terms": "https://openminds.ebrains.eu/controlledTerms/",
        "core": "https://openminds.ebrains.eu/core/",
    }
    fields = [
        Field("lookup_label", str, "vocab:lookupLabel", doc="no description available"),
        Field(
            "additional_remarks",
            str,
            "vocab:additionalRemarks",
            doc="Mention of what deserves additional attention or notice.",
        ),
        Field(
            "anatomical_locations",
            [
                "openminds.controlledterms.CellType",
                "openminds.controlledterms.Organ",
                "openminds.controlledterms.OrganismSubstance",
                "openminds.controlledterms.SubcellularEntity",
                "openminds.controlledterms.UBERONParcellation",
                "openminds.sands.CustomAnatomicalEntity",
                "openminds.sands.ParcellationEntity",
                "openminds.sands.ParcellationEntityVersion",
            ],
            "vocab:anatomicalLocation",
            multiple=True,
            doc="no description available",
        ),
        Field(
            "biological_sex",
            "openminds.controlledterms.BiologicalSex",
            "vocab:biologicalSex",
            multiple=True,
            doc="Differentiation of individuals of most species (animals and plants) based on the type of gametes they produce.",
        ),
        Field(
            "internal_identifier",
            str,
            "vocab:internalIdentifier",
            doc="Term or code that identifies the tissue sample collection within a particular product.",
        ),
        Field(
            "lateralities",
            "openminds.controlledterms.Laterality",
            "vocab:laterality",
            multiple=True,
            doc="Differentiation between a pair of lateral homologous parts of the body.",
        ),
        Field("number_of_tissue_samples", int, "vocab:numberOfTissueSamples", doc="no description available"),
        Field(
            "origins",
            [
                "openminds.controlledterms.CellType",
                "openminds.controlledterms.Organ",
                "openminds.controlledterms.OrganismSubstance",
            ],
            "vocab:origin",
            multiple=True,
            required=True,
            doc="Source at which something begins or rises, or from which something derives.",
        ),
        Field(
            "species",
            ["openminds.controlledterms.Species", "openminds.core.Strain"],
            "vocab:species",
            multiple=True,
            required=True,
            doc="Category of biological classification comprising related organisms or populations potentially capable of interbreeding, and being designated by a binomial that consists of the name of a genus followed by a Latin or latinized uncapitalized noun or adjective.",
        ),
        Field(
            "studied_states",
            "openminds.core.TissueSampleCollectionState",
            "vocab:studiedState",
            multiple=True,
            required=True,
            doc="Reference to a point in time at which the tissue sample collection was studied in a particular mode or condition.",
        ),
        Field(
            "types",
            "openminds.controlledterms.TissueSampleType",
            "vocab:type",
            multiple=True,
            required=True,
            doc="Distinct class to which a group of entities or concepts with similar characteristics or attributes belong to.",
        ),
        Field(
            "has_parts",
            "openminds.core.TissueSample",
            "^vocab:isPartOf",
            reverse="is_part_of",
            multiple=True,
            doc="reverse of 'isPartOf'",
        ),
        Field(
            "has_study_results_in",
            "openminds.core.DatasetVersion",
            "^vocab:studiedSpecimen",
            reverse="studied_specimens",
            multiple=True,
            doc="reverse of 'studiedSpecimen'",
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
            "used_in",
            ["openminds.sands.BrainAtlasVersion", "openminds.sands.CommonCoordinateSpaceVersion"],
            "^vocab:usedSpecimen",
            reverse="used_specimens",
            multiple=True,
            doc="reverse of 'usedSpecimen'",
        ),
    ]
    existence_query_fields = ("lookup_label",)

    def __init__(
        self,
        lookup_label=None,
        additional_remarks=None,
        anatomical_locations=None,
        biological_sex=None,
        internal_identifier=None,
        lateralities=None,
        number_of_tissue_samples=None,
        origins=None,
        species=None,
        studied_states=None,
        types=None,
        has_parts=None,
        has_study_results_in=None,
        is_used_to_group=None,
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
            lookup_label=lookup_label,
            additional_remarks=additional_remarks,
            anatomical_locations=anatomical_locations,
            biological_sex=biological_sex,
            internal_identifier=internal_identifier,
            lateralities=lateralities,
            number_of_tissue_samples=number_of_tissue_samples,
            origins=origins,
            species=species,
            studied_states=studied_states,
            types=types,
            has_parts=has_parts,
            has_study_results_in=has_study_results_in,
            is_used_to_group=is_used_to_group,
            used_in=used_in,
        )
