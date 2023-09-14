import marshmallow as ma
from oarepo_runtime.ui import marshmallow as l10n
from oarepo_runtime.ui.marshmallow import InvenioUISchema
from oarepo_vocabularies.services.ui_schema import (
    HierarchyUISchema,
    VocabularyI18nStrUIField,
)

import nr_metadata.common.services.records.ui_schema_common
import nr_metadata.common.services.records.ui_schema_datatypes
import nr_metadata.ui_schema.identifiers
from nr_metadata.ui_schema.subjects import NRSubjectListField


class NRDocumentRecordUISchema(InvenioUISchema):
    class Meta:
        unknown = ma.RAISE

    metadata = ma.fields.Nested(lambda: NRDocumentMetadataUISchema())

    syntheticFields = ma.fields.Nested(lambda: NRDocumentSyntheticFieldsUISchema())


class NRDocumentMetadataUISchema(
    nr_metadata.common.services.records.ui_schema_common.NRCommonMetadataUISchema
):
    class Meta:
        unknown = ma.RAISE

    additionalTitles = ma.fields.List(
        ma.fields.Nested(lambda: AdditionalTitlesItemUISchema())
    )

    collection = ma.fields.String()

    contributors = ma.fields.List(ma.fields.Nested(lambda: ContributorsItemUISchema()))

    creators = ma.fields.List(
        ma.fields.Nested(lambda: CreatorsItemUISchema()), required=True
    )

    events = ma.fields.List(ma.fields.Nested(lambda: EventsItemUISchema()))

    externalLocation = ma.fields.Nested(lambda: ExternalLocationUISchema())

    fundingReferences = ma.fields.List(
        ma.fields.Nested(lambda: FundingReferencesItemUISchema())
    )

    geoLocations = ma.fields.List(ma.fields.Nested(lambda: GeoLocationsItemUISchema()))

    objectIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: ObjectIdentifiersItemUISchema())
    )

    relatedItems = ma.fields.List(ma.fields.Nested(lambda: RelatedItemsItemUISchema()))

    series = ma.fields.List(ma.fields.Nested(lambda: SeriesItemUISchema()))

    subjects = NRSubjectListField(ma.fields.Nested(lambda: SubjectsItemUISchema()))

    systemIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: SystemIdentifiersItemUISchema())
    )

    thesis = ma.fields.Nested(lambda: NRThesisUISchema())


class RelatedItemsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRRelatedItemUISchema
):
    class Meta:
        unknown = ma.RAISE

    itemContributors = ma.fields.List(
        ma.fields.Nested(lambda: ItemContributorsItemUISchema())
    )

    itemCreators = ma.fields.List(ma.fields.Nested(lambda: ItemCreatorsItemUISchema()))

    itemPIDs = ma.fields.List(ma.fields.Nested(lambda: ObjectIdentifiersItemUISchema()))


class ContributorsItemUISchema(
    nr_metadata.common.services.records.ui_schema_common.NRContributorUISchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemUISchema())
    )


class CreatorsItemUISchema(
    nr_metadata.common.services.records.ui_schema_common.NRCreatorUISchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemUISchema())
    )


class EventsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NREventUISchema
):
    class Meta:
        unknown = ma.RAISE

    eventLocation = ma.fields.Nested(lambda: EventLocationUISchema(), required=True)


class GeoLocationsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRGeoLocationUISchema
):
    class Meta:
        unknown = ma.RAISE

    geoLocationPoint = ma.fields.Nested(lambda: GeoLocationPointUISchema())


class ItemContributorsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRRelatedItemContributorUISchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemUISchema())
    )


class ItemCreatorsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRRelatedItemCreatorUISchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemUISchema())
    )


class NRThesisUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    dateDefended = l10n.LocalizedDate()

    defended = ma.fields.Boolean()

    degreeGrantors = ma.fields.List(ma.fields.Nested(lambda: NRDegreeGrantorUISchema()))

    studyFields = ma.fields.List(ma.fields.String())


class AccessRightsUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRAccessRightsVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class AdditionalTitlesItemUISchema(
    nr_metadata.common.services.records.ui_schema_common.AdditionalTitlesUISchema
):
    class Meta:
        unknown = ma.RAISE


class AffiliationsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRAffiliationVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchyUISchema())

    title = VocabularyI18nStrUIField()


class AuthorityIdentifiersItemUISchema(
    nr_metadata.ui_schema.identifiers.NRAuthorityIdentifierUISchema
):
    class Meta:
        unknown = ma.RAISE


class CountryUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRCountryVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class EventLocationUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRLocationUISchema
):
    class Meta:
        unknown = ma.RAISE


class ExternalLocationUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRExternalLocationUISchema
):
    class Meta:
        unknown = ma.RAISE


class FunderUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRFunderVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class FundingReferencesItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRFundingReferenceUISchema
):
    class Meta:
        unknown = ma.RAISE


class GeoLocationPointUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRGeoLocationPointUISchema
):
    class Meta:
        unknown = ma.RAISE


class ItemRelationTypeUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRItemRelationTypeVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class ItemResourceTypeUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRResourceTypeVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class LanguagesItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRLanguageVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRDegreeGrantorUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchyUISchema())

    title = VocabularyI18nStrUIField()


class NRDocumentSyntheticFieldsUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    institutions = ma.fields.String()

    keywords_cs = ma.fields.String()

    keywords_en = ma.fields.String()

    person = ma.fields.String()


class ObjectIdentifiersItemUISchema(
    nr_metadata.ui_schema.identifiers.NRObjectIdentifierUISchema
):
    class Meta:
        unknown = ma.RAISE


class RightsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRLicenseVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class RoleUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRAuthorityRoleVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class SeriesItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRSeriesUISchema
):
    class Meta:
        unknown = ma.RAISE


class SubjectCategoriesItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRSubjectCategoryVocabularyUISchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class SubjectsItemUISchema(
    nr_metadata.common.services.records.ui_schema_datatypes.NRSubjectUISchema
):
    class Meta:
        unknown = ma.RAISE


class SystemIdentifiersItemUISchema(
    nr_metadata.ui_schema.identifiers.NRSystemIdentifierUISchema
):
    class Meta:
        unknown = ma.RAISE
