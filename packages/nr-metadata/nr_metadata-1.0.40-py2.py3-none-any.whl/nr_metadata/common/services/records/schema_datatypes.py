import marshmallow as ma
from edtf import Interval as EDTFInterval
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import validate as ma_validate
from marshmallow_utils.fields import TrimmedString
from oarepo_runtime.i18n.schema import I18nStrField, MultilingualField
from oarepo_runtime.validation import CachedMultilayerEDTFValidator
from oarepo_vocabularies.services.schema import HierarchySchema

from nr_metadata.schema.identifiers import (
    NRAuthorityIdentifierSchema,
    NRObjectIdentifierSchema,
)


class NREventSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    eventDate = TrimmedString(
        required=True, validate=[CachedMultilayerEDTFValidator(types=(EDTFInterval,))]
    )

    eventLocation = ma.fields.Nested(lambda: NRLocationSchema(), required=True)

    eventNameAlternate = ma.fields.List(ma.fields.String())

    eventNameOriginal = ma.fields.String(required=True)


class NRRelatedItemSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    itemContributors = ma.fields.List(
        ma.fields.Nested(lambda: NRRelatedItemContributorSchema())
    )

    itemCreators = ma.fields.List(
        ma.fields.Nested(lambda: NRRelatedItemCreatorSchema())
    )

    itemEndPage = ma.fields.String()

    itemIssue = ma.fields.String()

    itemPIDs = ma.fields.List(ma.fields.Nested(lambda: NRObjectIdentifierSchema()))

    itemPublisher = ma.fields.String()

    itemRelationType = ma.fields.Nested(lambda: NRItemRelationTypeVocabularySchema())

    itemResourceType = ma.fields.Nested(lambda: NRResourceTypeVocabularySchema())

    itemStartPage = ma.fields.String()

    itemTitle = ma.fields.String(required=True)

    itemURL = ma.fields.String()

    itemVolume = ma.fields.String()

    itemYear = ma.fields.Integer()


class NRFundingReferenceSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    funder = ma.fields.Nested(lambda: NRFunderVocabularySchema())

    fundingProgram = ma.fields.String()

    projectID = ma.fields.String(required=True)

    projectName = ma.fields.String()


class NRGeoLocationSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    geoLocationPlace = ma.fields.String(required=True)

    geoLocationPoint = ma.fields.Nested(lambda: NRGeoLocationPointSchema())


class NRLocationSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    country = ma.fields.Nested(lambda: NRCountryVocabularySchema())

    place = ma.fields.String(required=True)


class NRRelatedItemContributorSchema(ma.Schema):
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


class NRRelatedItemCreatorSchema(ma.Schema):
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


class NRAccessRightsVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRAffiliationVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchySchema())

    title = i18n_strings


class NRAuthorityRoleVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRCountryVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRExternalLocationSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    externalLocationNote = ma.fields.String()

    externalLocationURL = ma.fields.String(required=True)


class NRFunderVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRGeoLocationPointSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    pointLatitude = ma.fields.Float(
        required=True, validate=[ma.validate.Range(min=-90.0, max=90.0)]
    )

    pointLongitude = ma.fields.Float(
        required=True, validate=[ma.validate.Range(min=-180.0, max=180.0)]
    )


class NRItemRelationTypeVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRLanguageVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRLicenseVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRResourceTypeVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRSeriesSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    seriesTitle = ma.fields.String(required=True)

    seriesVolume = ma.fields.String()


class NRSubjectCategoryVocabularySchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = i18n_strings


class NRSubjectSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    classificationCode = ma.fields.String()

    subject = MultilingualField(I18nStrField(), required=True)

    subjectScheme = ma.fields.String()

    valueURI = ma.fields.String()
