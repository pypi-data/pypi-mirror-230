import marshmallow as ma
from marshmallow import validate as ma_validate
from oarepo_runtime.i18n.ui_schema import (
    I18nStrUIField,
    MultilingualLocalizedUIField,
    MultilingualUIField,
)
from oarepo_runtime.ui import marshmallow as l10n
from oarepo_runtime.ui.marshmallow import InvenioUISchema

from nr_metadata.common.services.records.ui_schema_datatypes import (
    NRAccessRightsVocabularyUISchema,
    NRAffiliationVocabularyUISchema,
    NRAuthorityRoleVocabularyUISchema,
    NREventUISchema,
    NRExternalLocationUISchema,
    NRFundingReferenceUISchema,
    NRGeoLocationUISchema,
    NRLanguageVocabularyUISchema,
    NRLicenseVocabularyUISchema,
    NRRelatedItemUISchema,
    NRResourceTypeVocabularyUISchema,
    NRSeriesUISchema,
    NRSubjectCategoryVocabularyUISchema,
    NRSubjectUISchema,
)
from nr_metadata.ui_schema.identifiers import (
    NRAuthorityIdentifierUISchema,
    NRObjectIdentifierUISchema,
    NRSystemIdentifierUISchema,
)
from nr_metadata.ui_schema.subjects import NRSubjectListField


class NRCommonRecordUISchema(InvenioUISchema):
    class Meta:
        unknown = ma.RAISE

    metadata = ma.fields.Nested(lambda: NRCommonMetadataUISchema())


class NRCommonMetadataUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    abstract = MultilingualUIField(I18nStrUIField())

    accessRights = ma.fields.Nested(lambda: NRAccessRightsVocabularyUISchema())

    accessibility = MultilingualLocalizedUIField(I18nStrUIField())

    additionalTitles = ma.fields.List(
        ma.fields.Nested(lambda: AdditionalTitlesUISchema())
    )

    contributors = ma.fields.List(ma.fields.Nested(lambda: NRContributorUISchema()))

    creators = ma.fields.List(
        ma.fields.Nested(lambda: NRCreatorUISchema()), required=True
    )

    dateAvailable = l10n.LocalizedEDTF()

    dateModified = l10n.LocalizedEDTF()

    events = ma.fields.List(ma.fields.Nested(lambda: NREventUISchema()))

    externalLocation = ma.fields.Nested(lambda: NRExternalLocationUISchema())

    fundingReferences = ma.fields.List(
        ma.fields.Nested(lambda: NRFundingReferenceUISchema())
    )

    geoLocations = ma.fields.List(ma.fields.Nested(lambda: NRGeoLocationUISchema()))

    languages = ma.fields.List(
        ma.fields.Nested(lambda: NRLanguageVocabularyUISchema()), required=True
    )

    methods = MultilingualUIField(I18nStrUIField())

    notes = ma.fields.List(ma.fields.String())

    objectIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRObjectIdentifierUISchema())
    )

    originalRecord = ma.fields.String()

    publishers = ma.fields.List(ma.fields.String())

    relatedItems = ma.fields.List(ma.fields.Nested(lambda: NRRelatedItemUISchema()))

    resourceType = ma.fields.Nested(
        lambda: NRResourceTypeVocabularyUISchema(), required=True
    )

    rights = ma.fields.List(ma.fields.Nested(lambda: NRLicenseVocabularyUISchema()))

    series = ma.fields.List(ma.fields.Nested(lambda: NRSeriesUISchema()))

    subjectCategories = ma.fields.List(
        ma.fields.Nested(lambda: NRSubjectCategoryVocabularyUISchema())
    )

    subjects = NRSubjectListField(ma.fields.Nested(lambda: NRSubjectUISchema()))

    systemIdentifiers = ma.fields.List(
        ma.fields.Nested(lambda: NRSystemIdentifierUISchema())
    )

    technicalInfo = MultilingualUIField(I18nStrUIField())

    title = ma.fields.String(required=True)

    version = ma.fields.String()


class AdditionalTitlesUISchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    title = I18nStrUIField(required=True)

    titleType = ma.fields.String(
        required=True,
        validate=[
            ma_validate.OneOf(
                ["translatedTitle", "alternativeTitle", "subtitle", "other"]
            )
        ],
    )


class NRContributorUISchema(ma.Schema):
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


class NRCreatorUISchema(ma.Schema):
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
