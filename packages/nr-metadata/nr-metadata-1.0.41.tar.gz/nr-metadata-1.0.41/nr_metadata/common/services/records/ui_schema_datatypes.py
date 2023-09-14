import marshmallow as ma
from marshmallow import validate as ma_validate
from oarepo_runtime.i18n.ui_schema import I18nStrUIField
from oarepo_runtime.ui import marshmallow as l10n
from oarepo_vocabularies.services.ui_schema import (
    HierarchyUISchema,
    VocabularyI18nStrUIField,
)

from nr_metadata.ui_schema.identifiers import (
    NRAuthorityIdentifierUISchema,
    NRObjectIdentifierUISchema,
)


class NREventUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    eventDate = l10n.LocalizedEDTFInterval(required=True)

    eventLocation = ma.fields.Nested(lambda: NRLocationUISchema(), required=True)

    eventNameAlternate = ma.fields.List(ma.fields.String())

    eventNameOriginal = ma.fields.String(required=True)


class NRRelatedItemUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    itemContributors = ma.fields.List(
        ma.fields.Nested(lambda: NRRelatedItemContributorUISchema())
    )

    itemCreators = ma.fields.List(
        ma.fields.Nested(lambda: NRRelatedItemCreatorUISchema())
    )

    itemEndPage = ma.fields.String()

    itemIssue = ma.fields.String()

    itemPIDs = ma.fields.List(ma.fields.Nested(lambda: NRObjectIdentifierUISchema()))

    itemPublisher = ma.fields.String()

    itemRelationType = ma.fields.Nested(lambda: NRItemRelationTypeVocabularyUISchema())

    itemResourceType = ma.fields.Nested(lambda: NRResourceTypeVocabularyUISchema())

    itemStartPage = ma.fields.String()

    itemTitle = ma.fields.String(required=True)

    itemURL = ma.fields.String()

    itemVolume = ma.fields.String()

    itemYear = ma.fields.Integer()


class NRFundingReferenceUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    funder = ma.fields.Nested(lambda: NRFunderVocabularyUISchema())

    fundingProgram = ma.fields.String()

    projectID = ma.fields.String(required=True)

    projectName = ma.fields.String()


class NRGeoLocationUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    geoLocationPlace = ma.fields.String(required=True)

    geoLocationPoint = ma.fields.Nested(lambda: NRGeoLocationPointUISchema())


class NRLocationUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    country = ma.fields.Nested(lambda: NRCountryVocabularyUISchema())

    place = ma.fields.String(required=True)


class NRRelatedItemContributorUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    affiliations = ma.fields.List(
        ma.fields.Nested(lambda: NRAffiliationVocabularyUISchema())
    )

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRAuthorityIdentifierUISchema())
    )

    fullName = ma.fields.String(required=True)

    nameType = ma.fields.String(
        validate=[ma_validate.OneOf(["Organizational", "Personal"])]
    )

    role = ma.fields.Nested(lambda: NRAuthorityRoleVocabularyUISchema())


class NRRelatedItemCreatorUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    affiliations = ma.fields.List(
        ma.fields.Nested(lambda: NRAffiliationVocabularyUISchema())
    )

    authorityIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRAuthorityIdentifierUISchema())
    )

    fullName = ma.fields.String(required=True)

    nameType = ma.fields.String(
        validate=[ma_validate.OneOf(["Organizational", "Personal"])]
    )


class NRAccessRightsVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRAffiliationVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    hierarchy = ma.fields.Nested(lambda: HierarchyUISchema())

    title = VocabularyI18nStrUIField()


class NRAuthorityRoleVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRCountryVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRExternalLocationUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    externalLocationNote = ma.fields.String()

    externalLocationURL = ma.fields.String(required=True)


class NRFunderVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRGeoLocationPointUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    pointLatitude = ma.fields.Float(required=True)

    pointLongitude = ma.fields.Float(required=True)


class NRItemRelationTypeVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRLanguageVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRLicenseVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRResourceTypeVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRSeriesUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    seriesTitle = ma.fields.String(required=True)

    seriesVolume = ma.fields.String()


class NRSubjectCategoryVocabularyUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    _id = ma.fields.String(data_key="id", attribute="id")

    _version = ma.fields.String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()


class NRSubjectUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    classificationCode = ma.fields.String()

    subject = I18nStrUIField()

    subjectScheme = ma.fields.String()

    valueURI = ma.fields.String()
