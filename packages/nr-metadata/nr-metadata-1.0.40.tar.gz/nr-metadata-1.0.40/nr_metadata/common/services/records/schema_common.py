import marshmallow as ma
from edtf import Date as EDTFDate
from marshmallow import validate as ma_validate
from marshmallow_utils.fields import TrimmedString
from oarepo_runtime.i18n.schema import I18nStrField, MultilingualField
from oarepo_runtime.marshmallow import BaseRecordSchema
from oarepo_runtime.validation import CachedMultilayerEDTFValidator

from nr_metadata.common.services.records.schema_datatypes import (
    NRAccessRightsVocabularySchema,
    NRAffiliationVocabularySchema,
    NRAuthorityRoleVocabularySchema,
    NREventSchema,
    NRExternalLocationSchema,
    NRFundingReferenceSchema,
    NRGeoLocationSchema,
    NRLanguageVocabularySchema,
    NRLicenseVocabularySchema,
    NRRelatedItemSchema,
    NRResourceTypeVocabularySchema,
    NRSeriesSchema,
    NRSubjectCategoryVocabularySchema,
    NRSubjectSchema,
)
from nr_metadata.schema.identifiers import (
    NRAuthorityIdentifierSchema,
    NRObjectIdentifierSchema,
    NRSystemIdentifierSchema,
)


class NRCommonRecordSchema(BaseRecordSchema):
    class Meta:
        unknown = ma.RAISE

    metadata = ma.fields.Nested(lambda: NRCommonMetadataSchema())


class NRCommonMetadataSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    abstract = MultilingualField(I18nStrField())

    accessRights = ma.fields.Nested(lambda: NRAccessRightsVocabularySchema())

    accessibility = MultilingualField(I18nStrField())

    additionalTitles = ma.fields.List(
        ma.fields.Nested(lambda: AdditionalTitlesSchema())
    )

    contributors = ma.fields.List(ma.fields.Nested(lambda: NRContributorSchema()))

    creators = ma.fields.List(
        ma.fields.Nested(lambda: NRCreatorSchema()),
        required=True,
        validate=[ma.validate.Length(min=1)],
    )

    dateAvailable = TrimmedString(
        validate=[CachedMultilayerEDTFValidator(types=(EDTFDate,))]
    )

    dateModified = TrimmedString(
        validate=[CachedMultilayerEDTFValidator(types=(EDTFDate,))]
    )

    events = ma.fields.List(ma.fields.Nested(lambda: NREventSchema()))

    externalLocation = ma.fields.Nested(lambda: NRExternalLocationSchema())

    fundingReferences = ma.fields.List(
        ma.fields.Nested(lambda: NRFundingReferenceSchema())
    )

    geoLocations = ma.fields.List(ma.fields.Nested(lambda: NRGeoLocationSchema()))

    languages = ma.fields.List(
        ma.fields.Nested(lambda: NRLanguageVocabularySchema()),
        required=True,
        validate=[ma.validate.Length(min=1)],
    )

    methods = MultilingualField(I18nStrField())

    notes = ma.fields.List(ma.fields.String())

    objectIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRObjectIdentifierSchema())
    )

    originalRecord = ma.fields.String()

    publishers = ma.fields.List(ma.fields.String())

    relatedItems = ma.fields.List(ma.fields.Nested(lambda: NRRelatedItemSchema()))

    resourceType = ma.fields.Nested(
        lambda: NRResourceTypeVocabularySchema(), required=True
    )

    rights = ma.fields.List(ma.fields.Nested(lambda: NRLicenseVocabularySchema()))

    series = ma.fields.List(ma.fields.Nested(lambda: NRSeriesSchema()))

    subjectCategories = ma.fields.List(
        ma.fields.Nested(lambda: NRSubjectCategoryVocabularySchema())
    )

    subjects = ma.fields.List(ma.fields.Nested(lambda: NRSubjectSchema()))

    systemIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRSystemIdentifierSchema())
    )

    technicalInfo = MultilingualField(I18nStrField())

    title = ma.fields.String(required=True)

    version = ma.fields.String()


class AdditionalTitlesSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    title = I18nStrField(required=True)

    titleType = ma.fields.String(
        required=True,
        validate=[
            ma_validate.OneOf(
                ["translatedTitle", "alternativeTitle", "subtitle", "other"]
            )
        ],
    )


class NRContributorSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    affiliations = ma.fields.List(
        ma.fields.Nested(lambda: NRAffiliationVocabularySchema())
    )

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRAuthorityIdentifierSchema())
    )

    fullName = ma.fields.String(required=True)

    nameType = ma.fields.String(
        validate=[ma_validate.OneOf(["Organizational", "Personal"])]
    )

    role = ma.fields.Nested(lambda: NRAuthorityRoleVocabularySchema())


class NRCreatorSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    affiliations = ma.fields.List(
        ma.fields.Nested(lambda: NRAffiliationVocabularySchema())
    )

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRAuthorityIdentifierSchema())
    )

    fullName = ma.fields.String(required=True)

    nameType = ma.fields.String(
        validate=[ma_validate.OneOf(["Organizational", "Personal"])]
    )
