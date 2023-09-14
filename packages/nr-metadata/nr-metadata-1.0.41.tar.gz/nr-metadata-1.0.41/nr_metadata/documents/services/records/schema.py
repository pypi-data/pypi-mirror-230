import marshmallow as ma
from invenio_vocabularies.services.schema import i18n_strings
from oarepo_runtime.marshmallow import BaseRecordSchema
from oarepo_runtime.validation import validate_date
from oarepo_vocabularies.services.schema import HierarchySchema

import nr_metadata.common.services.records.schema_common
import nr_metadata.common.services.records.schema_datatypes
import nr_metadata.schema.identifiers


class NRDocumentRecordSchema(BaseRecordSchema):
    class Meta:
        unknown = ma.RAISE

    metadata = ma.fields.Nested(lambda: NRDocumentMetadataSchema())

    syntheticFields = ma.fields.Nested(lambda: NRDocumentSyntheticFieldsSchema())


class NRDocumentMetadataSchema(
    nr_metadata.common.services.records.schema_common.NRCommonMetadataSchema
):
    class Meta:
        unknown = ma.RAISE

    additionalTitles = ma.fields.List(
        ma.fields.Nested(lambda: AdditionalTitlesItemSchema())
    )

    collection = ma.fields.String()

    contributors = ma.fields.List(ma.fields.Nested(lambda: ContributorsItemSchema()))

    creators = ma.fields.List(
        ma.fields.Nested(lambda: CreatorsItemSchema()),
        required=True,
        validate=[ma.validate.Length(min=1)],
    )

    events = ma.fields.List(ma.fields.Nested(lambda: EventsItemSchema()))

    externalLocation = ma.fields.Nested(lambda: ExternalLocationSchema())

    fundingReferences = ma.fields.List(
        ma.fields.Nested(lambda: FundingReferencesItemSchema())
    )

    geoLocations = ma.fields.List(ma.fields.Nested(lambda: GeoLocationsItemSchema()))

    objectIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: ObjectIdentifiersItemSchema())
    )

    relatedItems = ma.fields.List(ma.fields.Nested(lambda: RelatedItemsItemSchema()))

    series = ma.fields.List(ma.fields.Nested(lambda: SeriesItemSchema()))

    subjects = ma.fields.List(ma.fields.Nested(lambda: SubjectsItemSchema()))

    systemIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: SystemIdentifiersItemSchema())
    )

    thesis = ma.fields.Nested(lambda: NRThesisSchema())


class RelatedItemsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRRelatedItemSchema
):
    class Meta:
        unknown = ma.RAISE

    itemContributors = ma.fields.List(
        ma.fields.Nested(lambda: ItemContributorsItemSchema())
    )

    itemCreators = ma.fields.List(ma.fields.Nested(lambda: ItemCreatorsItemSchema()))

    itemPIDs = ma.fields.List(ma.fields.Nested(lambda: ObjectIdentifiersItemSchema()))


class ContributorsItemSchema(
    nr_metadata.common.services.records.schema_common.NRContributorSchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemSchema())
    )


class CreatorsItemSchema(
    nr_metadata.common.services.records.schema_common.NRCreatorSchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemSchema())
    )


class EventsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NREventSchema
):
    class Meta:
        unknown = ma.RAISE

    eventLocation = ma.fields.Nested(lambda: EventLocationSchema(), required=True)


class GeoLocationsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRGeoLocationSchema
):
    class Meta:
        unknown = ma.RAISE

    geoLocationPoint = ma.fields.Nested(lambda: GeoLocationPointSchema())


class ItemContributorsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRRelatedItemContributorSchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemSchema())
    )


class ItemCreatorsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRRelatedItemCreatorSchema
):
    class Meta:
        unknown = ma.RAISE

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: AuthorityIdentifiersItemSchema())
    )


class NRThesisSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    dateDefended = ma.fields.String(validate=[validate_date("%Y-%m-%d")])

    defended = ma.fields.Boolean()

    degreeGrantors = ma.fields.List(ma.fields.Nested(lambda: NRDegreeGrantorSchema()))

    studyFields = ma.fields.List(ma.fields.String())


class AccessRightsSchema(
    nr_metadata.common.services.records.schema_datatypes.NRAccessRightsVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class AdditionalTitlesItemSchema(
    nr_metadata.common.services.records.schema_common.AdditionalTitlesSchema
):
    class Meta:
        unknown = ma.RAISE


class AffiliationsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRAffiliationVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchySchema())

    title = i18n_strings


class AuthorityIdentifiersItemSchema(
    nr_metadata.schema.identifiers.NRAuthorityIdentifierSchema
):
    class Meta:
        unknown = ma.RAISE


class CountrySchema(
    nr_metadata.common.services.records.schema_datatypes.NRCountryVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class EventLocationSchema(
    nr_metadata.common.services.records.schema_datatypes.NRLocationSchema
):
    class Meta:
        unknown = ma.RAISE


class ExternalLocationSchema(
    nr_metadata.common.services.records.schema_datatypes.NRExternalLocationSchema
):
    class Meta:
        unknown = ma.RAISE


class FunderSchema(
    nr_metadata.common.services.records.schema_datatypes.NRFunderVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class FundingReferencesItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRFundingReferenceSchema
):
    class Meta:
        unknown = ma.RAISE


class GeoLocationPointSchema(
    nr_metadata.common.services.records.schema_datatypes.NRGeoLocationPointSchema
):
    class Meta:
        unknown = ma.RAISE


class ItemRelationTypeSchema(
    nr_metadata.common.services.records.schema_datatypes.NRItemRelationTypeVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class ItemResourceTypeSchema(
    nr_metadata.common.services.records.schema_datatypes.NRResourceTypeVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class LanguagesItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRLanguageVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRDegreeGrantorSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchySchema())

    title = i18n_strings


class NRDocumentSyntheticFieldsSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE


class ObjectIdentifiersItemSchema(
    nr_metadata.schema.identifiers.NRObjectIdentifierSchema
):
    class Meta:
        unknown = ma.RAISE


class RightsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRLicenseVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class RoleSchema(
    nr_metadata.common.services.records.schema_datatypes.NRAuthorityRoleVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class SeriesItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRSeriesSchema
):
    class Meta:
        unknown = ma.RAISE


class SubjectCategoriesItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRSubjectCategoryVocabularySchema
):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class SubjectsItemSchema(
    nr_metadata.common.services.records.schema_datatypes.NRSubjectSchema
):
    class Meta:
        unknown = ma.RAISE


class SystemIdentifiersItemSchema(
    nr_metadata.schema.identifiers.NRSystemIdentifierSchema
):
    class Meta:
        unknown = ma.RAISE
