from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from invenio_records_resources.services.records.components import DataComponent
from oarepo_runtime.config.service import PermissionsPresetsConfigMixin

from nr_metadata.documents.records.api import DocumentsRecord
from nr_metadata.documents.services.records.permissions import DocumentsPermissionPolicy
from nr_metadata.documents.services.records.schema import NRDocumentRecordSchema
from nr_metadata.documents.services.records.search import DocumentsSearchOptions


class DocumentsServiceConfig(PermissionsPresetsConfigMixin, InvenioRecordServiceConfig):
    """DocumentsRecord service config."""

    PERMISSIONS_PRESETS = ["everyone"]

    url_prefix = "/nr-metadata-documents/"

    base_permission_policy_cls = DocumentsPermissionPolicy

    schema = NRDocumentRecordSchema

    search = DocumentsSearchOptions

    record_cls = DocumentsRecord

    service_id = "documents"

    components = [
        *PermissionsPresetsConfigMixin.components,
        *InvenioRecordServiceConfig.components,
        DataComponent,
    ]

    model = "nr_metadata.documents"

    @property
    def links_item(self):
        return {
            "self": RecordLink("{self.url_prefix}{id}"),
        }

    @property
    def links_search(self):
        return {
            **pagination_links("{self.url_prefix}{?args*}"),
        }
