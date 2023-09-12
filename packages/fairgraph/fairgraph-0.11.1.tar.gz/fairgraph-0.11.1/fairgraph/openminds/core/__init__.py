import sys
import inspect
from fairgraph.kgobject import KGObject
from fairgraph.embedded import EmbeddedMetadata

from .research.subject_group import SubjectGroup
from .research.protocol_execution import ProtocolExecution
from .research.behavioral_protocol import BehavioralProtocol
from .research.string_property import StringProperty
from .research.custom_property_set import CustomPropertySet
from .research.subject import Subject
from .research.strain import Strain
from .research.tissue_sample_collection import TissueSampleCollection
from .research.configuration import Configuration
from .research.tissue_sample_state import TissueSampleState
from .research.subject_state import SubjectState
from .research.tissue_sample import TissueSample
from .research.tissue_sample_collection_state import TissueSampleCollectionState
from .research.protocol import Protocol
from .research.subject_group_state import SubjectGroupState
from .research.property_value_list import PropertyValueList
from .research.numerical_property import NumericalProperty
from .products.dataset import Dataset
from .products.project import Project
from .products.software_version import SoftwareVersion
from .products.dataset_version import DatasetVersion
from .products.meta_data_model_version import MetaDataModelVersion
from .products.setup import Setup
from .products.model import Model
from .products.software import Software
from .products.meta_data_model import MetaDataModel
from .products.web_service_version import WebServiceVersion
from .products.model_version import ModelVersion
from .products.web_service import WebService
from .digitalIdentifier.doi import DOI
from .digitalIdentifier.rorid import RORID
from .digitalIdentifier.issn import ISSN
from .digitalIdentifier.identifiers_dot_org_id import IdentifiersDotOrgID
from .digitalIdentifier.isbn import ISBN
from .digitalIdentifier.rrid import RRID
from .digitalIdentifier.orcid import ORCID
from .digitalIdentifier.gridid import GRIDID
from .digitalIdentifier.stock_number import StockNumber
from .digitalIdentifier.handle import HANDLE
from .digitalIdentifier.swhid import SWHID
from .miscellaneous.research_product_group import ResearchProductGroup
from .miscellaneous.quantitative_value import QuantitativeValue
from .miscellaneous.funding import Funding
from .miscellaneous.web_resource import WebResource
from .miscellaneous.comment import Comment
from .miscellaneous.quantitative_value_range import QuantitativeValueRange
from .miscellaneous.quantitative_value_array import QuantitativeValueArray
from .actors.account_information import AccountInformation
from .actors.contribution import Contribution
from .actors.consortium import Consortium
from .actors.organization import Organization
from .actors.contact_information import ContactInformation
from .actors.affiliation import Affiliation
from .actors.person import Person
from .data.service_link import ServiceLink
from .data.copyright import Copyright
from .data.content_type_pattern import ContentTypePattern
from .data.file_repository import FileRepository
from .data.license import License
from .data.file import File
from .data.hash import Hash
from .data.file_archive import FileArchive
from .data.file_path_pattern import FilePathPattern
from .data.content_type import ContentType
from .data.file_repository_structure import FileRepositoryStructure
from .data.file_bundle import FileBundle
from .data.measurement import Measurement


def list_kg_classes():
    """List all KG classes defined in this module"""
    return [
        obj
        for name, obj in inspect.getmembers(sys.modules[__name__])
        if inspect.isclass(obj) and issubclass(obj, KGObject) and obj.__module__.startswith(__name__)
    ]


def list_embedded_metadata_classes():
    """List all embedded metadata classes defined in this module"""
    return [
        obj
        for name, obj in inspect.getmembers(sys.modules[__name__])
        if inspect.isclass(obj) and issubclass(obj, EmbeddedMetadata) and obj.__module__.startswith(__name__)
    ]


def set_error_handling(value):
    """
    Control validation for all classes in this module.

    Args:
        value (str): action to follow when there is a validation failure.
            (e.g. if a required field is not provided).
            Possible values: "error", "warning", "log", None
    """
    for cls in list_kg_classes() + list_embedded_metadata_classes():
        cls.set_error_handling(value)
