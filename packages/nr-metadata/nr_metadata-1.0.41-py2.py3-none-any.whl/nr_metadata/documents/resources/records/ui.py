from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from nr_metadata.documents.services.records.ui_schema import NRDocumentRecordUISchema


class DocumentsUIJSONSerializer(MarshmallowSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=NRDocumentRecordUISchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
