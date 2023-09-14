from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as InvenioRecord
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.relations import PIDRelation, RelationsField

from nr_metadata.common.records.dumper import CommonDumper
from nr_metadata.common.records.models import CommonMetadata
from nr_metadata.common.records.multilingual_dumper import MultilingualSearchDumper


class CommonIdProvider(RecordIdProviderV2):
    pid_type = "common"


class CommonRecord(InvenioRecord):
    model_cls = CommonMetadata

    schema = ConstantField("$schema", "local://common-1.0.0.json")

    index = IndexField("common-common-1.0.0")

    pid = PIDField(provider=CommonIdProvider, context_cls=PIDFieldContext, create=True)

    dumper_extensions = [MultilingualSearchDumper()]
    dumper = CommonDumper(extensions=dumper_extensions)

    relations = RelationsField(
        accessRights=PIDRelation(
            "metadata.accessRights",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("access-rights"),
        ),
        affiliations=PIDRelation(
            "metadata.contributors.affiliations",
            keys=["id", "title", "hierarchy"],
            pid_field=Vocabulary.pid.with_type_ctx("institutions"),
        ),
        role=PIDRelation(
            "metadata.contributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-roles"),
        ),
        creators_affiliations=PIDRelation(
            "metadata.creators.affiliations",
            keys=["id", "title", "hierarchy"],
            pid_field=Vocabulary.pid.with_type_ctx("institutions"),
        ),
        country=PIDRelation(
            "metadata.events.eventLocation.country",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("countries"),
        ),
        funder=PIDRelation(
            "metadata.fundingReferences.funder",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("funders"),
        ),
        languages=PIDRelation(
            "metadata.languages",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        itemContributors_affiliations=PIDRelation(
            "metadata.relatedItems.itemContributors.affiliations",
            keys=["id", "title", "hierarchy"],
            pid_field=Vocabulary.pid.with_type_ctx("institutions"),
        ),
        itemContributors_role=PIDRelation(
            "metadata.relatedItems.itemContributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-roles"),
        ),
        itemCreators_affiliations=PIDRelation(
            "metadata.relatedItems.itemCreators.affiliations",
            keys=["id", "title", "hierarchy"],
            pid_field=Vocabulary.pid.with_type_ctx("institutions"),
        ),
        itemRelationType=PIDRelation(
            "metadata.relatedItems.itemRelationType",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("item-relation-types"),
        ),
        itemResourceType=PIDRelation(
            "metadata.relatedItems.itemResourceType",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        resourceType=PIDRelation(
            "metadata.resourceType",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        rights=PIDRelation(
            "metadata.rights",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("licenses"),
        ),
        subjectCategories=PIDRelation(
            "metadata.subjectCategories",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("subject-categories"),
        ),
    )
