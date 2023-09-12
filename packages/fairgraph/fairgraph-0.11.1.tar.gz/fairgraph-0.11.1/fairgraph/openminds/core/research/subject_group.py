"""

"""

# this file was auto-generated

from datetime import date, datetime
from fairgraph import KGObject, IRI
from fairgraph.fields import Field


class SubjectGroup(KGObject):
    """ """

    default_space = "dataset"
    type_ = ["https://openminds.ebrains.eu/core/SubjectGroup"]
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
            doc="Term or code that identifies the subject group within a particular product.",
        ),
        Field("number_of_subjects", int, "vocab:numberOfSubjects", doc="no description available"),
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
            "openminds.core.SubjectGroupState",
            "vocab:studiedState",
            multiple=True,
            required=True,
            doc="Reference to a point in time at which the subject group was studied in a particular mode or condition.",
        ),
        Field(
            "has_parts",
            "openminds.core.Subject",
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
        biological_sex=None,
        internal_identifier=None,
        number_of_subjects=None,
        species=None,
        studied_states=None,
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
            biological_sex=biological_sex,
            internal_identifier=internal_identifier,
            number_of_subjects=number_of_subjects,
            species=species,
            studied_states=studied_states,
            has_parts=has_parts,
            has_study_results_in=has_study_results_in,
            is_used_to_group=is_used_to_group,
            used_in=used_in,
        )
