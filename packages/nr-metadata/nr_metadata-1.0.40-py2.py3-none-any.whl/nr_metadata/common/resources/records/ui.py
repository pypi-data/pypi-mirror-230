from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from nr_metadata.common.services.records.ui_schema_common import NRCommonRecordUISchema


class CommonUIJSONSerializer(MarshmallowSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=NRCommonRecordUISchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
