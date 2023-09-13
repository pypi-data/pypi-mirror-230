"""
Type annotations for kendra service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_kendra/type_defs/)

Usage::

    ```python
    from mypy_boto3_kendra.type_defs import AccessControlConfigurationSummaryTypeDef

    data: AccessControlConfigurationSummaryTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AlfrescoEntityType,
    AttributeSuggestionsModeType,
    ConditionOperatorType,
    ConfluenceAttachmentFieldNameType,
    ConfluenceAuthenticationTypeType,
    ConfluenceBlogFieldNameType,
    ConfluencePageFieldNameType,
    ConfluenceSpaceFieldNameType,
    ConfluenceVersionType,
    ContentTypeType,
    DatabaseEngineTypeType,
    DataSourceStatusType,
    DataSourceSyncJobStatusType,
    DataSourceTypeType,
    DocumentAttributeValueTypeType,
    DocumentStatusType,
    EntityTypeType,
    ErrorCodeType,
    ExperienceStatusType,
    FaqFileFormatType,
    FaqStatusType,
    FeaturedResultsSetStatusType,
    HighlightTypeType,
    IndexEditionType,
    IndexStatusType,
    IntervalType,
    IssueSubEntityType,
    KeyLocationType,
    MetricTypeType,
    ModeType,
    OrderType,
    PersonaType,
    PrincipalMappingStatusType,
    PrincipalTypeType,
    QueryIdentifiersEnclosingOptionType,
    QueryResultFormatType,
    QueryResultTypeType,
    QuerySuggestionsBlockListStatusType,
    QuerySuggestionsStatusType,
    ReadAccessTypeType,
    RelevanceTypeType,
    SalesforceChatterFeedIncludeFilterTypeType,
    SalesforceKnowledgeArticleStateType,
    SalesforceStandardObjectNameType,
    ScoreConfidenceType,
    ServiceNowAuthenticationTypeType,
    ServiceNowBuildVersionTypeType,
    SharePointOnlineAuthenticationTypeType,
    SharePointVersionType,
    SlackEntityType,
    SortOrderType,
    SuggestionTypeType,
    ThesaurusStatusType,
    TypeType,
    UserContextPolicyType,
    UserGroupResolutionModeType,
    WebCrawlerModeType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AccessControlConfigurationSummaryTypeDef",
    "AccessControlListConfigurationTypeDef",
    "AclConfigurationTypeDef",
    "DataSourceToIndexFieldMappingTypeDef",
    "DataSourceVpcConfigurationTypeDef",
    "S3PathTypeDef",
    "EntityConfigurationTypeDef",
    "FailedEntityTypeDef",
    "ResponseMetadataTypeDef",
    "EntityPersonaConfigurationTypeDef",
    "SuggestableConfigTypeDef",
    "BasicAuthenticationConfigurationTypeDef",
    "DataSourceSyncJobMetricTargetTypeDef",
    "BatchDeleteDocumentResponseFailedDocumentTypeDef",
    "BatchDeleteFeaturedResultsSetErrorTypeDef",
    "BatchDeleteFeaturedResultsSetRequestRequestTypeDef",
    "BatchGetDocumentStatusResponseErrorTypeDef",
    "StatusTypeDef",
    "BatchPutDocumentResponseFailedDocumentTypeDef",
    "BlobTypeDef",
    "CapacityUnitsConfigurationTypeDef",
    "ClearQuerySuggestionsRequestRequestTypeDef",
    "TimestampTypeDef",
    "ConfluenceAttachmentToIndexFieldMappingTypeDef",
    "ConfluenceBlogToIndexFieldMappingTypeDef",
    "ProxyConfigurationTypeDef",
    "ConfluencePageToIndexFieldMappingTypeDef",
    "ConfluenceSpaceToIndexFieldMappingTypeDef",
    "ConnectionConfigurationTypeDef",
    "ContentSourceConfigurationTypeDef",
    "CorrectionTypeDef",
    "PrincipalTypeDef",
    "TagTypeDef",
    "FeaturedDocumentTypeDef",
    "ServerSideEncryptionConfigurationTypeDef",
    "UserGroupResolutionConfigurationTypeDef",
    "TemplateConfigurationTypeDef",
    "DataSourceGroupTypeDef",
    "DataSourceSummaryTypeDef",
    "DataSourceSyncJobMetricsTypeDef",
    "SqlConfigurationTypeDef",
    "DeleteAccessControlConfigurationRequestRequestTypeDef",
    "DeleteDataSourceRequestRequestTypeDef",
    "DeleteExperienceRequestRequestTypeDef",
    "DeleteFaqRequestRequestTypeDef",
    "DeleteIndexRequestRequestTypeDef",
    "DeletePrincipalMappingRequestRequestTypeDef",
    "DeleteQuerySuggestionsBlockListRequestRequestTypeDef",
    "DeleteThesaurusRequestRequestTypeDef",
    "DescribeAccessControlConfigurationRequestRequestTypeDef",
    "DescribeDataSourceRequestRequestTypeDef",
    "DescribeExperienceRequestRequestTypeDef",
    "ExperienceEndpointTypeDef",
    "DescribeFaqRequestRequestTypeDef",
    "DescribeFeaturedResultsSetRequestRequestTypeDef",
    "FeaturedDocumentMissingTypeDef",
    "FeaturedDocumentWithMetadataTypeDef",
    "DescribeIndexRequestRequestTypeDef",
    "DescribePrincipalMappingRequestRequestTypeDef",
    "GroupOrderingIdSummaryTypeDef",
    "DescribeQuerySuggestionsBlockListRequestRequestTypeDef",
    "DescribeQuerySuggestionsConfigRequestRequestTypeDef",
    "DescribeThesaurusRequestRequestTypeDef",
    "DisassociatePersonasFromEntitiesRequestRequestTypeDef",
    "RelevanceTypeDef",
    "SearchTypeDef",
    "DocumentsMetadataConfigurationTypeDef",
    "EntityDisplayDataTypeDef",
    "UserIdentityConfigurationTypeDef",
    "FacetResultTypeDef",
    "FacetTypeDef",
    "FaqStatisticsTypeDef",
    "FaqSummaryTypeDef",
    "FeaturedResultsSetSummaryTypeDef",
    "GetSnapshotsRequestRequestTypeDef",
    "TimeRangeTypeDef",
    "GitHubDocumentCrawlPropertiesTypeDef",
    "SaaSConfigurationTypeDef",
    "MemberGroupTypeDef",
    "MemberUserTypeDef",
    "GroupSummaryTypeDef",
    "HighlightTypeDef",
    "IndexConfigurationSummaryTypeDef",
    "TextDocumentStatisticsTypeDef",
    "JsonTokenTypeConfigurationTypeDef",
    "JwtTokenTypeConfigurationTypeDef",
    "ListAccessControlConfigurationsRequestRequestTypeDef",
    "ListDataSourcesRequestRequestTypeDef",
    "ListEntityPersonasRequestRequestTypeDef",
    "PersonasSummaryTypeDef",
    "ListExperienceEntitiesRequestRequestTypeDef",
    "ListExperiencesRequestRequestTypeDef",
    "ListFaqsRequestRequestTypeDef",
    "ListFeaturedResultsSetsRequestRequestTypeDef",
    "ListGroupsOlderThanOrderingIdRequestRequestTypeDef",
    "ListIndicesRequestRequestTypeDef",
    "ListQuerySuggestionsBlockListsRequestRequestTypeDef",
    "QuerySuggestionsBlockListSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListThesauriRequestRequestTypeDef",
    "ThesaurusSummaryTypeDef",
    "SortingConfigurationTypeDef",
    "SpellCorrectionConfigurationTypeDef",
    "ScoreAttributesTypeDef",
    "WarningTypeDef",
    "RelevanceFeedbackTypeDef",
    "SeedUrlConfigurationTypeDef",
    "SiteMapsConfigurationTypeDef",
    "StartDataSourceSyncJobRequestRequestTypeDef",
    "StopDataSourceSyncJobRequestRequestTypeDef",
    "SuggestionHighlightTypeDef",
    "TableCellTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "ColumnConfigurationTypeDef",
    "GoogleDriveConfigurationTypeDef",
    "SalesforceChatterFeedConfigurationTypeDef",
    "SalesforceCustomKnowledgeArticleTypeConfigurationTypeDef",
    "SalesforceStandardKnowledgeArticleTypeConfigurationTypeDef",
    "SalesforceStandardObjectAttachmentConfigurationTypeDef",
    "SalesforceStandardObjectConfigurationTypeDef",
    "ServiceNowKnowledgeArticleConfigurationTypeDef",
    "ServiceNowServiceCatalogConfigurationTypeDef",
    "WorkDocsConfigurationTypeDef",
    "BoxConfigurationTypeDef",
    "FsxConfigurationTypeDef",
    "JiraConfigurationTypeDef",
    "QuipConfigurationTypeDef",
    "SlackConfigurationTypeDef",
    "AlfrescoConfigurationTypeDef",
    "OnPremiseConfigurationTypeDef",
    "OneDriveUsersTypeDef",
    "UpdateQuerySuggestionsBlockListRequestRequestTypeDef",
    "UpdateThesaurusRequestRequestTypeDef",
    "AssociateEntitiesToExperienceRequestRequestTypeDef",
    "DisassociateEntitiesFromExperienceRequestRequestTypeDef",
    "AssociateEntitiesToExperienceResponseTypeDef",
    "AssociatePersonasToEntitiesResponseTypeDef",
    "CreateAccessControlConfigurationResponseTypeDef",
    "CreateDataSourceResponseTypeDef",
    "CreateExperienceResponseTypeDef",
    "CreateFaqResponseTypeDef",
    "CreateIndexResponseTypeDef",
    "CreateQuerySuggestionsBlockListResponseTypeDef",
    "CreateThesaurusResponseTypeDef",
    "DescribeFaqResponseTypeDef",
    "DescribeQuerySuggestionsBlockListResponseTypeDef",
    "DescribeThesaurusResponseTypeDef",
    "DisassociateEntitiesFromExperienceResponseTypeDef",
    "DisassociatePersonasFromEntitiesResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListAccessControlConfigurationsResponseTypeDef",
    "StartDataSourceSyncJobResponseTypeDef",
    "AssociatePersonasToEntitiesRequestRequestTypeDef",
    "AttributeSuggestionsDescribeConfigTypeDef",
    "AttributeSuggestionsUpdateConfigTypeDef",
    "AuthenticationConfigurationTypeDef",
    "BatchDeleteDocumentRequestRequestTypeDef",
    "BatchDeleteDocumentResponseTypeDef",
    "BatchDeleteFeaturedResultsSetResponseTypeDef",
    "BatchGetDocumentStatusResponseTypeDef",
    "BatchPutDocumentResponseTypeDef",
    "ClickFeedbackTypeDef",
    "DocumentAttributeValueTypeDef",
    "ConfluenceAttachmentConfigurationTypeDef",
    "ConfluenceBlogConfigurationTypeDef",
    "SharePointConfigurationTypeDef",
    "ConfluencePageConfigurationTypeDef",
    "ConfluenceSpaceConfigurationTypeDef",
    "SpellCorrectedQueryTypeDef",
    "HierarchicalPrincipalTypeDef",
    "CreateFaqRequestRequestTypeDef",
    "CreateQuerySuggestionsBlockListRequestRequestTypeDef",
    "CreateThesaurusRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateFeaturedResultsSetRequestRequestTypeDef",
    "FeaturedResultsSetTypeDef",
    "UpdateFeaturedResultsSetRequestRequestTypeDef",
    "UserContextTypeDef",
    "ListDataSourcesResponseTypeDef",
    "DataSourceSyncJobTypeDef",
    "ExperiencesSummaryTypeDef",
    "DescribeFeaturedResultsSetResponseTypeDef",
    "DescribePrincipalMappingResponseTypeDef",
    "DocumentRelevanceConfigurationTypeDef",
    "DocumentMetadataConfigurationTypeDef",
    "S3DataSourceConfigurationTypeDef",
    "ExperienceEntitiesSummaryTypeDef",
    "ExperienceConfigurationTypeDef",
    "ListFaqsResponseTypeDef",
    "ListFeaturedResultsSetsResponseTypeDef",
    "GetSnapshotsResponseTypeDef",
    "ListDataSourceSyncJobsRequestRequestTypeDef",
    "GroupMembersTypeDef",
    "ListGroupsOlderThanOrderingIdResponseTypeDef",
    "TextWithHighlightsTypeDef",
    "ListIndicesResponseTypeDef",
    "IndexStatisticsTypeDef",
    "UserTokenConfigurationTypeDef",
    "ListEntityPersonasResponseTypeDef",
    "ListQuerySuggestionsBlockListsResponseTypeDef",
    "ListThesauriResponseTypeDef",
    "UrlsTypeDef",
    "SuggestionTextWithHighlightsTypeDef",
    "TableRowTypeDef",
    "DatabaseConfigurationTypeDef",
    "SalesforceKnowledgeArticleConfigurationTypeDef",
    "ServiceNowConfigurationTypeDef",
    "GitHubConfigurationTypeDef",
    "OneDriveConfigurationTypeDef",
    "DescribeQuerySuggestionsConfigResponseTypeDef",
    "UpdateQuerySuggestionsConfigRequestRequestTypeDef",
    "SubmitFeedbackRequestRequestTypeDef",
    "DocumentAttributeConditionTypeDef",
    "DocumentAttributeTargetTypeDef",
    "DocumentAttributeTypeDef",
    "DocumentAttributeValueCountPairTypeDef",
    "ConfluenceConfigurationTypeDef",
    "CreateAccessControlConfigurationRequestRequestTypeDef",
    "DescribeAccessControlConfigurationResponseTypeDef",
    "UpdateAccessControlConfigurationRequestRequestTypeDef",
    "CreateFeaturedResultsSetResponseTypeDef",
    "UpdateFeaturedResultsSetResponseTypeDef",
    "AttributeSuggestionsGetConfigTypeDef",
    "ListDataSourceSyncJobsResponseTypeDef",
    "ListExperiencesResponseTypeDef",
    "QueryRequestRequestTypeDef",
    "RetrieveRequestRequestTypeDef",
    "ListExperienceEntitiesResponseTypeDef",
    "CreateExperienceRequestRequestTypeDef",
    "DescribeExperienceResponseTypeDef",
    "UpdateExperienceRequestRequestTypeDef",
    "PutPrincipalMappingRequestRequestTypeDef",
    "AdditionalResultAttributeValueTypeDef",
    "CreateIndexRequestRequestTypeDef",
    "DescribeIndexResponseTypeDef",
    "UpdateIndexRequestRequestTypeDef",
    "WebCrawlerConfigurationTypeDef",
    "SuggestionValueTypeDef",
    "TableExcerptTypeDef",
    "SalesforceConfigurationTypeDef",
    "HookConfigurationTypeDef",
    "InlineCustomDocumentEnrichmentConfigurationTypeDef",
    "AttributeFilterTypeDef",
    "DocumentInfoTypeDef",
    "DocumentTypeDef",
    "RetrieveResultItemTypeDef",
    "SourceDocumentTypeDef",
    "GetQuerySuggestionsRequestRequestTypeDef",
    "AdditionalResultAttributeTypeDef",
    "DataSourceConfigurationTypeDef",
    "CustomDocumentEnrichmentConfigurationTypeDef",
    "BatchGetDocumentStatusRequestRequestTypeDef",
    "RetrieveResultTypeDef",
    "SuggestionTypeDef",
    "FeaturedResultsItemTypeDef",
    "QueryResultItemTypeDef",
    "BatchPutDocumentRequestRequestTypeDef",
    "CreateDataSourceRequestRequestTypeDef",
    "DescribeDataSourceResponseTypeDef",
    "UpdateDataSourceRequestRequestTypeDef",
    "GetQuerySuggestionsResponseTypeDef",
    "QueryResultTypeDef",
)

AccessControlConfigurationSummaryTypeDef = TypedDict(
    "AccessControlConfigurationSummaryTypeDef",
    {
        "Id": str,
    },
)

AccessControlListConfigurationTypeDef = TypedDict(
    "AccessControlListConfigurationTypeDef",
    {
        "KeyPath": NotRequired[str],
    },
)

AclConfigurationTypeDef = TypedDict(
    "AclConfigurationTypeDef",
    {
        "AllowedGroupsColumnName": str,
    },
)

DataSourceToIndexFieldMappingTypeDef = TypedDict(
    "DataSourceToIndexFieldMappingTypeDef",
    {
        "DataSourceFieldName": str,
        "IndexFieldName": str,
        "DateFieldFormat": NotRequired[str],
    },
)

DataSourceVpcConfigurationTypeDef = TypedDict(
    "DataSourceVpcConfigurationTypeDef",
    {
        "SubnetIds": Sequence[str],
        "SecurityGroupIds": Sequence[str],
    },
)

S3PathTypeDef = TypedDict(
    "S3PathTypeDef",
    {
        "Bucket": str,
        "Key": str,
    },
)

EntityConfigurationTypeDef = TypedDict(
    "EntityConfigurationTypeDef",
    {
        "EntityId": str,
        "EntityType": EntityTypeType,
    },
)

FailedEntityTypeDef = TypedDict(
    "FailedEntityTypeDef",
    {
        "EntityId": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

EntityPersonaConfigurationTypeDef = TypedDict(
    "EntityPersonaConfigurationTypeDef",
    {
        "EntityId": str,
        "Persona": PersonaType,
    },
)

SuggestableConfigTypeDef = TypedDict(
    "SuggestableConfigTypeDef",
    {
        "AttributeName": NotRequired[str],
        "Suggestable": NotRequired[bool],
    },
)

BasicAuthenticationConfigurationTypeDef = TypedDict(
    "BasicAuthenticationConfigurationTypeDef",
    {
        "Host": str,
        "Port": int,
        "Credentials": str,
    },
)

DataSourceSyncJobMetricTargetTypeDef = TypedDict(
    "DataSourceSyncJobMetricTargetTypeDef",
    {
        "DataSourceId": str,
        "DataSourceSyncJobId": NotRequired[str],
    },
)

BatchDeleteDocumentResponseFailedDocumentTypeDef = TypedDict(
    "BatchDeleteDocumentResponseFailedDocumentTypeDef",
    {
        "Id": NotRequired[str],
        "ErrorCode": NotRequired[ErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

BatchDeleteFeaturedResultsSetErrorTypeDef = TypedDict(
    "BatchDeleteFeaturedResultsSetErrorTypeDef",
    {
        "Id": str,
        "ErrorCode": ErrorCodeType,
        "ErrorMessage": str,
    },
)

BatchDeleteFeaturedResultsSetRequestRequestTypeDef = TypedDict(
    "BatchDeleteFeaturedResultsSetRequestRequestTypeDef",
    {
        "IndexId": str,
        "FeaturedResultsSetIds": Sequence[str],
    },
)

BatchGetDocumentStatusResponseErrorTypeDef = TypedDict(
    "BatchGetDocumentStatusResponseErrorTypeDef",
    {
        "DocumentId": NotRequired[str],
        "ErrorCode": NotRequired[ErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

StatusTypeDef = TypedDict(
    "StatusTypeDef",
    {
        "DocumentId": NotRequired[str],
        "DocumentStatus": NotRequired[DocumentStatusType],
        "FailureCode": NotRequired[str],
        "FailureReason": NotRequired[str],
    },
)

BatchPutDocumentResponseFailedDocumentTypeDef = TypedDict(
    "BatchPutDocumentResponseFailedDocumentTypeDef",
    {
        "Id": NotRequired[str],
        "ErrorCode": NotRequired[ErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CapacityUnitsConfigurationTypeDef = TypedDict(
    "CapacityUnitsConfigurationTypeDef",
    {
        "StorageCapacityUnits": int,
        "QueryCapacityUnits": int,
    },
)

ClearQuerySuggestionsRequestRequestTypeDef = TypedDict(
    "ClearQuerySuggestionsRequestRequestTypeDef",
    {
        "IndexId": str,
    },
)

TimestampTypeDef = Union[datetime, str]
ConfluenceAttachmentToIndexFieldMappingTypeDef = TypedDict(
    "ConfluenceAttachmentToIndexFieldMappingTypeDef",
    {
        "DataSourceFieldName": NotRequired[ConfluenceAttachmentFieldNameType],
        "DateFieldFormat": NotRequired[str],
        "IndexFieldName": NotRequired[str],
    },
)

ConfluenceBlogToIndexFieldMappingTypeDef = TypedDict(
    "ConfluenceBlogToIndexFieldMappingTypeDef",
    {
        "DataSourceFieldName": NotRequired[ConfluenceBlogFieldNameType],
        "DateFieldFormat": NotRequired[str],
        "IndexFieldName": NotRequired[str],
    },
)

ProxyConfigurationTypeDef = TypedDict(
    "ProxyConfigurationTypeDef",
    {
        "Host": str,
        "Port": int,
        "Credentials": NotRequired[str],
    },
)

ConfluencePageToIndexFieldMappingTypeDef = TypedDict(
    "ConfluencePageToIndexFieldMappingTypeDef",
    {
        "DataSourceFieldName": NotRequired[ConfluencePageFieldNameType],
        "DateFieldFormat": NotRequired[str],
        "IndexFieldName": NotRequired[str],
    },
)

ConfluenceSpaceToIndexFieldMappingTypeDef = TypedDict(
    "ConfluenceSpaceToIndexFieldMappingTypeDef",
    {
        "DataSourceFieldName": NotRequired[ConfluenceSpaceFieldNameType],
        "DateFieldFormat": NotRequired[str],
        "IndexFieldName": NotRequired[str],
    },
)

ConnectionConfigurationTypeDef = TypedDict(
    "ConnectionConfigurationTypeDef",
    {
        "DatabaseHost": str,
        "DatabasePort": int,
        "DatabaseName": str,
        "TableName": str,
        "SecretArn": str,
    },
)

ContentSourceConfigurationTypeDef = TypedDict(
    "ContentSourceConfigurationTypeDef",
    {
        "DataSourceIds": NotRequired[Sequence[str]],
        "FaqIds": NotRequired[Sequence[str]],
        "DirectPutContent": NotRequired[bool],
    },
)

CorrectionTypeDef = TypedDict(
    "CorrectionTypeDef",
    {
        "BeginOffset": NotRequired[int],
        "EndOffset": NotRequired[int],
        "Term": NotRequired[str],
        "CorrectedTerm": NotRequired[str],
    },
)

PrincipalTypeDef = TypedDict(
    "PrincipalTypeDef",
    {
        "Name": str,
        "Type": PrincipalTypeType,
        "Access": ReadAccessTypeType,
        "DataSourceId": NotRequired[str],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

FeaturedDocumentTypeDef = TypedDict(
    "FeaturedDocumentTypeDef",
    {
        "Id": NotRequired[str],
    },
)

ServerSideEncryptionConfigurationTypeDef = TypedDict(
    "ServerSideEncryptionConfigurationTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)

UserGroupResolutionConfigurationTypeDef = TypedDict(
    "UserGroupResolutionConfigurationTypeDef",
    {
        "UserGroupResolutionMode": UserGroupResolutionModeType,
    },
)

TemplateConfigurationTypeDef = TypedDict(
    "TemplateConfigurationTypeDef",
    {
        "Template": NotRequired[Mapping[str, Any]],
    },
)

DataSourceGroupTypeDef = TypedDict(
    "DataSourceGroupTypeDef",
    {
        "GroupId": str,
        "DataSourceId": str,
    },
)

DataSourceSummaryTypeDef = TypedDict(
    "DataSourceSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Type": NotRequired[DataSourceTypeType],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
        "Status": NotRequired[DataSourceStatusType],
        "LanguageCode": NotRequired[str],
    },
)

DataSourceSyncJobMetricsTypeDef = TypedDict(
    "DataSourceSyncJobMetricsTypeDef",
    {
        "DocumentsAdded": NotRequired[str],
        "DocumentsModified": NotRequired[str],
        "DocumentsDeleted": NotRequired[str],
        "DocumentsFailed": NotRequired[str],
        "DocumentsScanned": NotRequired[str],
    },
)

SqlConfigurationTypeDef = TypedDict(
    "SqlConfigurationTypeDef",
    {
        "QueryIdentifiersEnclosingOption": NotRequired[QueryIdentifiersEnclosingOptionType],
    },
)

DeleteAccessControlConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteAccessControlConfigurationRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
    },
)

DeleteDataSourceRequestRequestTypeDef = TypedDict(
    "DeleteDataSourceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DeleteExperienceRequestRequestTypeDef = TypedDict(
    "DeleteExperienceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DeleteFaqRequestRequestTypeDef = TypedDict(
    "DeleteFaqRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DeleteIndexRequestRequestTypeDef = TypedDict(
    "DeleteIndexRequestRequestTypeDef",
    {
        "Id": str,
    },
)

DeletePrincipalMappingRequestRequestTypeDef = TypedDict(
    "DeletePrincipalMappingRequestRequestTypeDef",
    {
        "IndexId": str,
        "GroupId": str,
        "DataSourceId": NotRequired[str],
        "OrderingId": NotRequired[int],
    },
)

DeleteQuerySuggestionsBlockListRequestRequestTypeDef = TypedDict(
    "DeleteQuerySuggestionsBlockListRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
    },
)

DeleteThesaurusRequestRequestTypeDef = TypedDict(
    "DeleteThesaurusRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DescribeAccessControlConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeAccessControlConfigurationRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
    },
)

DescribeDataSourceRequestRequestTypeDef = TypedDict(
    "DescribeDataSourceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DescribeExperienceRequestRequestTypeDef = TypedDict(
    "DescribeExperienceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

ExperienceEndpointTypeDef = TypedDict(
    "ExperienceEndpointTypeDef",
    {
        "EndpointType": NotRequired[Literal["HOME"]],
        "Endpoint": NotRequired[str],
    },
)

DescribeFaqRequestRequestTypeDef = TypedDict(
    "DescribeFaqRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DescribeFeaturedResultsSetRequestRequestTypeDef = TypedDict(
    "DescribeFeaturedResultsSetRequestRequestTypeDef",
    {
        "IndexId": str,
        "FeaturedResultsSetId": str,
    },
)

FeaturedDocumentMissingTypeDef = TypedDict(
    "FeaturedDocumentMissingTypeDef",
    {
        "Id": NotRequired[str],
    },
)

FeaturedDocumentWithMetadataTypeDef = TypedDict(
    "FeaturedDocumentWithMetadataTypeDef",
    {
        "Id": NotRequired[str],
        "Title": NotRequired[str],
        "URI": NotRequired[str],
    },
)

DescribeIndexRequestRequestTypeDef = TypedDict(
    "DescribeIndexRequestRequestTypeDef",
    {
        "Id": str,
    },
)

DescribePrincipalMappingRequestRequestTypeDef = TypedDict(
    "DescribePrincipalMappingRequestRequestTypeDef",
    {
        "IndexId": str,
        "GroupId": str,
        "DataSourceId": NotRequired[str],
    },
)

GroupOrderingIdSummaryTypeDef = TypedDict(
    "GroupOrderingIdSummaryTypeDef",
    {
        "Status": NotRequired[PrincipalMappingStatusType],
        "LastUpdatedAt": NotRequired[datetime],
        "ReceivedAt": NotRequired[datetime],
        "OrderingId": NotRequired[int],
        "FailureReason": NotRequired[str],
    },
)

DescribeQuerySuggestionsBlockListRequestRequestTypeDef = TypedDict(
    "DescribeQuerySuggestionsBlockListRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
    },
)

DescribeQuerySuggestionsConfigRequestRequestTypeDef = TypedDict(
    "DescribeQuerySuggestionsConfigRequestRequestTypeDef",
    {
        "IndexId": str,
    },
)

DescribeThesaurusRequestRequestTypeDef = TypedDict(
    "DescribeThesaurusRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

DisassociatePersonasFromEntitiesRequestRequestTypeDef = TypedDict(
    "DisassociatePersonasFromEntitiesRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "EntityIds": Sequence[str],
    },
)

RelevanceTypeDef = TypedDict(
    "RelevanceTypeDef",
    {
        "Freshness": NotRequired[bool],
        "Importance": NotRequired[int],
        "Duration": NotRequired[str],
        "RankOrder": NotRequired[OrderType],
        "ValueImportanceMap": NotRequired[Dict[str, int]],
    },
)

SearchTypeDef = TypedDict(
    "SearchTypeDef",
    {
        "Facetable": NotRequired[bool],
        "Searchable": NotRequired[bool],
        "Displayable": NotRequired[bool],
        "Sortable": NotRequired[bool],
    },
)

DocumentsMetadataConfigurationTypeDef = TypedDict(
    "DocumentsMetadataConfigurationTypeDef",
    {
        "S3Prefix": NotRequired[str],
    },
)

EntityDisplayDataTypeDef = TypedDict(
    "EntityDisplayDataTypeDef",
    {
        "UserName": NotRequired[str],
        "GroupName": NotRequired[str],
        "IdentifiedUserName": NotRequired[str],
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
    },
)

UserIdentityConfigurationTypeDef = TypedDict(
    "UserIdentityConfigurationTypeDef",
    {
        "IdentityAttributeName": NotRequired[str],
    },
)

FacetResultTypeDef = TypedDict(
    "FacetResultTypeDef",
    {
        "DocumentAttributeKey": NotRequired[str],
        "DocumentAttributeValueType": NotRequired[DocumentAttributeValueTypeType],
        "DocumentAttributeValueCountPairs": NotRequired[
            List["DocumentAttributeValueCountPairTypeDef"]
        ],
    },
)

FacetTypeDef = TypedDict(
    "FacetTypeDef",
    {
        "DocumentAttributeKey": NotRequired[str],
        "Facets": NotRequired[Sequence[Dict[str, Any]]],
        "MaxResults": NotRequired[int],
    },
)

FaqStatisticsTypeDef = TypedDict(
    "FaqStatisticsTypeDef",
    {
        "IndexedQuestionAnswersCount": int,
    },
)

FaqSummaryTypeDef = TypedDict(
    "FaqSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[FaqStatusType],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
        "FileFormat": NotRequired[FaqFileFormatType],
        "LanguageCode": NotRequired[str],
    },
)

FeaturedResultsSetSummaryTypeDef = TypedDict(
    "FeaturedResultsSetSummaryTypeDef",
    {
        "FeaturedResultsSetId": NotRequired[str],
        "FeaturedResultsSetName": NotRequired[str],
        "Status": NotRequired[FeaturedResultsSetStatusType],
        "LastUpdatedTimestamp": NotRequired[int],
        "CreationTimestamp": NotRequired[int],
    },
)

GetSnapshotsRequestRequestTypeDef = TypedDict(
    "GetSnapshotsRequestRequestTypeDef",
    {
        "IndexId": str,
        "Interval": IntervalType,
        "MetricType": MetricTypeType,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

TimeRangeTypeDef = TypedDict(
    "TimeRangeTypeDef",
    {
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)

GitHubDocumentCrawlPropertiesTypeDef = TypedDict(
    "GitHubDocumentCrawlPropertiesTypeDef",
    {
        "CrawlRepositoryDocuments": NotRequired[bool],
        "CrawlIssue": NotRequired[bool],
        "CrawlIssueComment": NotRequired[bool],
        "CrawlIssueCommentAttachment": NotRequired[bool],
        "CrawlPullRequest": NotRequired[bool],
        "CrawlPullRequestComment": NotRequired[bool],
        "CrawlPullRequestCommentAttachment": NotRequired[bool],
    },
)

SaaSConfigurationTypeDef = TypedDict(
    "SaaSConfigurationTypeDef",
    {
        "OrganizationName": str,
        "HostUrl": str,
    },
)

MemberGroupTypeDef = TypedDict(
    "MemberGroupTypeDef",
    {
        "GroupId": str,
        "DataSourceId": NotRequired[str],
    },
)

MemberUserTypeDef = TypedDict(
    "MemberUserTypeDef",
    {
        "UserId": str,
    },
)

GroupSummaryTypeDef = TypedDict(
    "GroupSummaryTypeDef",
    {
        "GroupId": NotRequired[str],
        "OrderingId": NotRequired[int],
    },
)

HighlightTypeDef = TypedDict(
    "HighlightTypeDef",
    {
        "BeginOffset": int,
        "EndOffset": int,
        "TopAnswer": NotRequired[bool],
        "Type": NotRequired[HighlightTypeType],
    },
)

IndexConfigurationSummaryTypeDef = TypedDict(
    "IndexConfigurationSummaryTypeDef",
    {
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "Status": IndexStatusType,
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Edition": NotRequired[IndexEditionType],
    },
)

TextDocumentStatisticsTypeDef = TypedDict(
    "TextDocumentStatisticsTypeDef",
    {
        "IndexedTextDocumentsCount": int,
        "IndexedTextBytes": int,
    },
)

JsonTokenTypeConfigurationTypeDef = TypedDict(
    "JsonTokenTypeConfigurationTypeDef",
    {
        "UserNameAttributeField": str,
        "GroupAttributeField": str,
    },
)

JwtTokenTypeConfigurationTypeDef = TypedDict(
    "JwtTokenTypeConfigurationTypeDef",
    {
        "KeyLocation": KeyLocationType,
        "URL": NotRequired[str],
        "SecretManagerArn": NotRequired[str],
        "UserNameAttributeField": NotRequired[str],
        "GroupAttributeField": NotRequired[str],
        "Issuer": NotRequired[str],
        "ClaimRegex": NotRequired[str],
    },
)

ListAccessControlConfigurationsRequestRequestTypeDef = TypedDict(
    "ListAccessControlConfigurationsRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListDataSourcesRequestRequestTypeDef = TypedDict(
    "ListDataSourcesRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListEntityPersonasRequestRequestTypeDef = TypedDict(
    "ListEntityPersonasRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

PersonasSummaryTypeDef = TypedDict(
    "PersonasSummaryTypeDef",
    {
        "EntityId": NotRequired[str],
        "Persona": NotRequired[PersonaType],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
    },
)

ListExperienceEntitiesRequestRequestTypeDef = TypedDict(
    "ListExperienceEntitiesRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "NextToken": NotRequired[str],
    },
)

ListExperiencesRequestRequestTypeDef = TypedDict(
    "ListExperiencesRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListFaqsRequestRequestTypeDef = TypedDict(
    "ListFaqsRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListFeaturedResultsSetsRequestRequestTypeDef = TypedDict(
    "ListFeaturedResultsSetsRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListGroupsOlderThanOrderingIdRequestRequestTypeDef = TypedDict(
    "ListGroupsOlderThanOrderingIdRequestRequestTypeDef",
    {
        "IndexId": str,
        "OrderingId": int,
        "DataSourceId": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListIndicesRequestRequestTypeDef = TypedDict(
    "ListIndicesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListQuerySuggestionsBlockListsRequestRequestTypeDef = TypedDict(
    "ListQuerySuggestionsBlockListsRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

QuerySuggestionsBlockListSummaryTypeDef = TypedDict(
    "QuerySuggestionsBlockListSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[QuerySuggestionsBlockListStatusType],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
        "ItemCount": NotRequired[int],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
    },
)

ListThesauriRequestRequestTypeDef = TypedDict(
    "ListThesauriRequestRequestTypeDef",
    {
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ThesaurusSummaryTypeDef = TypedDict(
    "ThesaurusSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[ThesaurusStatusType],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
    },
)

SortingConfigurationTypeDef = TypedDict(
    "SortingConfigurationTypeDef",
    {
        "DocumentAttributeKey": str,
        "SortOrder": SortOrderType,
    },
)

SpellCorrectionConfigurationTypeDef = TypedDict(
    "SpellCorrectionConfigurationTypeDef",
    {
        "IncludeQuerySpellCheckSuggestions": bool,
    },
)

ScoreAttributesTypeDef = TypedDict(
    "ScoreAttributesTypeDef",
    {
        "ScoreConfidence": NotRequired[ScoreConfidenceType],
    },
)

WarningTypeDef = TypedDict(
    "WarningTypeDef",
    {
        "Message": NotRequired[str],
        "Code": NotRequired[Literal["QUERY_LANGUAGE_INVALID_SYNTAX"]],
    },
)

RelevanceFeedbackTypeDef = TypedDict(
    "RelevanceFeedbackTypeDef",
    {
        "ResultId": str,
        "RelevanceValue": RelevanceTypeType,
    },
)

SeedUrlConfigurationTypeDef = TypedDict(
    "SeedUrlConfigurationTypeDef",
    {
        "SeedUrls": Sequence[str],
        "WebCrawlerMode": NotRequired[WebCrawlerModeType],
    },
)

SiteMapsConfigurationTypeDef = TypedDict(
    "SiteMapsConfigurationTypeDef",
    {
        "SiteMaps": Sequence[str],
    },
)

StartDataSourceSyncJobRequestRequestTypeDef = TypedDict(
    "StartDataSourceSyncJobRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

StopDataSourceSyncJobRequestRequestTypeDef = TypedDict(
    "StopDataSourceSyncJobRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
    },
)

SuggestionHighlightTypeDef = TypedDict(
    "SuggestionHighlightTypeDef",
    {
        "BeginOffset": NotRequired[int],
        "EndOffset": NotRequired[int],
    },
)

TableCellTypeDef = TypedDict(
    "TableCellTypeDef",
    {
        "Value": NotRequired[str],
        "TopAnswer": NotRequired[bool],
        "Highlighted": NotRequired[bool],
        "Header": NotRequired[bool],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "TagKeys": Sequence[str],
    },
)

ColumnConfigurationTypeDef = TypedDict(
    "ColumnConfigurationTypeDef",
    {
        "DocumentIdColumnName": str,
        "DocumentDataColumnName": str,
        "ChangeDetectingColumns": Sequence[str],
        "DocumentTitleColumnName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

GoogleDriveConfigurationTypeDef = TypedDict(
    "GoogleDriveConfigurationTypeDef",
    {
        "SecretArn": str,
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "ExcludeMimeTypes": NotRequired[Sequence[str]],
        "ExcludeUserAccounts": NotRequired[Sequence[str]],
        "ExcludeSharedDrives": NotRequired[Sequence[str]],
    },
)

SalesforceChatterFeedConfigurationTypeDef = TypedDict(
    "SalesforceChatterFeedConfigurationTypeDef",
    {
        "DocumentDataFieldName": str,
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "IncludeFilterTypes": NotRequired[Sequence[SalesforceChatterFeedIncludeFilterTypeType]],
    },
)

SalesforceCustomKnowledgeArticleTypeConfigurationTypeDef = TypedDict(
    "SalesforceCustomKnowledgeArticleTypeConfigurationTypeDef",
    {
        "Name": str,
        "DocumentDataFieldName": str,
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

SalesforceStandardKnowledgeArticleTypeConfigurationTypeDef = TypedDict(
    "SalesforceStandardKnowledgeArticleTypeConfigurationTypeDef",
    {
        "DocumentDataFieldName": str,
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

SalesforceStandardObjectAttachmentConfigurationTypeDef = TypedDict(
    "SalesforceStandardObjectAttachmentConfigurationTypeDef",
    {
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

SalesforceStandardObjectConfigurationTypeDef = TypedDict(
    "SalesforceStandardObjectConfigurationTypeDef",
    {
        "Name": SalesforceStandardObjectNameType,
        "DocumentDataFieldName": str,
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

ServiceNowKnowledgeArticleConfigurationTypeDef = TypedDict(
    "ServiceNowKnowledgeArticleConfigurationTypeDef",
    {
        "DocumentDataFieldName": str,
        "CrawlAttachments": NotRequired[bool],
        "IncludeAttachmentFilePatterns": NotRequired[Sequence[str]],
        "ExcludeAttachmentFilePatterns": NotRequired[Sequence[str]],
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "FilterQuery": NotRequired[str],
    },
)

ServiceNowServiceCatalogConfigurationTypeDef = TypedDict(
    "ServiceNowServiceCatalogConfigurationTypeDef",
    {
        "DocumentDataFieldName": str,
        "CrawlAttachments": NotRequired[bool],
        "IncludeAttachmentFilePatterns": NotRequired[Sequence[str]],
        "ExcludeAttachmentFilePatterns": NotRequired[Sequence[str]],
        "DocumentTitleFieldName": NotRequired[str],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

WorkDocsConfigurationTypeDef = TypedDict(
    "WorkDocsConfigurationTypeDef",
    {
        "OrganizationId": str,
        "CrawlComments": NotRequired[bool],
        "UseChangeLog": NotRequired[bool],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

BoxConfigurationTypeDef = TypedDict(
    "BoxConfigurationTypeDef",
    {
        "EnterpriseId": str,
        "SecretArn": str,
        "UseChangeLog": NotRequired[bool],
        "CrawlComments": NotRequired[bool],
        "CrawlTasks": NotRequired[bool],
        "CrawlWebLinks": NotRequired[bool],
        "FileFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "TaskFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "CommentFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "WebLinkFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
    },
)

FsxConfigurationTypeDef = TypedDict(
    "FsxConfigurationTypeDef",
    {
        "FileSystemId": str,
        "FileSystemType": Literal["WINDOWS"],
        "VpcConfiguration": DataSourceVpcConfigurationTypeDef,
        "SecretArn": NotRequired[str],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

JiraConfigurationTypeDef = TypedDict(
    "JiraConfigurationTypeDef",
    {
        "JiraAccountUrl": str,
        "SecretArn": str,
        "UseChangeLog": NotRequired[bool],
        "Project": NotRequired[Sequence[str]],
        "IssueType": NotRequired[Sequence[str]],
        "Status": NotRequired[Sequence[str]],
        "IssueSubEntityFilter": NotRequired[Sequence[IssueSubEntityType]],
        "AttachmentFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "CommentFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "IssueFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "ProjectFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "WorkLogFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
    },
)

QuipConfigurationTypeDef = TypedDict(
    "QuipConfigurationTypeDef",
    {
        "Domain": str,
        "SecretArn": str,
        "CrawlFileComments": NotRequired[bool],
        "CrawlChatRooms": NotRequired[bool],
        "CrawlAttachments": NotRequired[bool],
        "FolderIds": NotRequired[Sequence[str]],
        "ThreadFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "MessageFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "AttachmentFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
    },
)

SlackConfigurationTypeDef = TypedDict(
    "SlackConfigurationTypeDef",
    {
        "TeamId": str,
        "SecretArn": str,
        "SlackEntityList": Sequence[SlackEntityType],
        "SinceCrawlDate": str,
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "UseChangeLog": NotRequired[bool],
        "CrawlBotMessage": NotRequired[bool],
        "ExcludeArchived": NotRequired[bool],
        "LookBackPeriod": NotRequired[int],
        "PrivateChannelFilter": NotRequired[Sequence[str]],
        "PublicChannelFilter": NotRequired[Sequence[str]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
    },
)

AlfrescoConfigurationTypeDef = TypedDict(
    "AlfrescoConfigurationTypeDef",
    {
        "SiteUrl": str,
        "SiteId": str,
        "SecretArn": str,
        "SslCertificateS3Path": S3PathTypeDef,
        "CrawlSystemFolders": NotRequired[bool],
        "CrawlComments": NotRequired[bool],
        "EntityFilter": NotRequired[Sequence[AlfrescoEntityType]],
        "DocumentLibraryFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "BlogFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "WikiFieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
    },
)

OnPremiseConfigurationTypeDef = TypedDict(
    "OnPremiseConfigurationTypeDef",
    {
        "HostUrl": str,
        "OrganizationName": str,
        "SslCertificateS3Path": S3PathTypeDef,
    },
)

OneDriveUsersTypeDef = TypedDict(
    "OneDriveUsersTypeDef",
    {
        "OneDriveUserList": NotRequired[Sequence[str]],
        "OneDriveUserS3Path": NotRequired[S3PathTypeDef],
    },
)

UpdateQuerySuggestionsBlockListRequestRequestTypeDef = TypedDict(
    "UpdateQuerySuggestionsBlockListRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "SourceS3Path": NotRequired[S3PathTypeDef],
        "RoleArn": NotRequired[str],
    },
)

UpdateThesaurusRequestRequestTypeDef = TypedDict(
    "UpdateThesaurusRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "RoleArn": NotRequired[str],
        "SourceS3Path": NotRequired[S3PathTypeDef],
    },
)

AssociateEntitiesToExperienceRequestRequestTypeDef = TypedDict(
    "AssociateEntitiesToExperienceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "EntityList": Sequence[EntityConfigurationTypeDef],
    },
)

DisassociateEntitiesFromExperienceRequestRequestTypeDef = TypedDict(
    "DisassociateEntitiesFromExperienceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "EntityList": Sequence[EntityConfigurationTypeDef],
    },
)

AssociateEntitiesToExperienceResponseTypeDef = TypedDict(
    "AssociateEntitiesToExperienceResponseTypeDef",
    {
        "FailedEntityList": List[FailedEntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociatePersonasToEntitiesResponseTypeDef = TypedDict(
    "AssociatePersonasToEntitiesResponseTypeDef",
    {
        "FailedEntityList": List[FailedEntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAccessControlConfigurationResponseTypeDef = TypedDict(
    "CreateAccessControlConfigurationResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDataSourceResponseTypeDef = TypedDict(
    "CreateDataSourceResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateExperienceResponseTypeDef = TypedDict(
    "CreateExperienceResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFaqResponseTypeDef = TypedDict(
    "CreateFaqResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateIndexResponseTypeDef = TypedDict(
    "CreateIndexResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateQuerySuggestionsBlockListResponseTypeDef = TypedDict(
    "CreateQuerySuggestionsBlockListResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateThesaurusResponseTypeDef = TypedDict(
    "CreateThesaurusResponseTypeDef",
    {
        "Id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFaqResponseTypeDef = TypedDict(
    "DescribeFaqResponseTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": str,
        "Description": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "S3Path": S3PathTypeDef,
        "Status": FaqStatusType,
        "RoleArn": str,
        "ErrorMessage": str,
        "FileFormat": FaqFileFormatType,
        "LanguageCode": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeQuerySuggestionsBlockListResponseTypeDef = TypedDict(
    "DescribeQuerySuggestionsBlockListResponseTypeDef",
    {
        "IndexId": str,
        "Id": str,
        "Name": str,
        "Description": str,
        "Status": QuerySuggestionsBlockListStatusType,
        "ErrorMessage": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "SourceS3Path": S3PathTypeDef,
        "ItemCount": int,
        "FileSizeBytes": int,
        "RoleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeThesaurusResponseTypeDef = TypedDict(
    "DescribeThesaurusResponseTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": str,
        "Description": str,
        "Status": ThesaurusStatusType,
        "ErrorMessage": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "RoleArn": str,
        "SourceS3Path": S3PathTypeDef,
        "FileSizeBytes": int,
        "TermCount": int,
        "SynonymRuleCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateEntitiesFromExperienceResponseTypeDef = TypedDict(
    "DisassociateEntitiesFromExperienceResponseTypeDef",
    {
        "FailedEntityList": List[FailedEntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociatePersonasFromEntitiesResponseTypeDef = TypedDict(
    "DisassociatePersonasFromEntitiesResponseTypeDef",
    {
        "FailedEntityList": List[FailedEntityTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAccessControlConfigurationsResponseTypeDef = TypedDict(
    "ListAccessControlConfigurationsResponseTypeDef",
    {
        "NextToken": str,
        "AccessControlConfigurations": List[AccessControlConfigurationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartDataSourceSyncJobResponseTypeDef = TypedDict(
    "StartDataSourceSyncJobResponseTypeDef",
    {
        "ExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociatePersonasToEntitiesRequestRequestTypeDef = TypedDict(
    "AssociatePersonasToEntitiesRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Personas": Sequence[EntityPersonaConfigurationTypeDef],
    },
)

AttributeSuggestionsDescribeConfigTypeDef = TypedDict(
    "AttributeSuggestionsDescribeConfigTypeDef",
    {
        "SuggestableConfigList": NotRequired[List[SuggestableConfigTypeDef]],
        "AttributeSuggestionsMode": NotRequired[AttributeSuggestionsModeType],
    },
)

AttributeSuggestionsUpdateConfigTypeDef = TypedDict(
    "AttributeSuggestionsUpdateConfigTypeDef",
    {
        "SuggestableConfigList": NotRequired[Sequence[SuggestableConfigTypeDef]],
        "AttributeSuggestionsMode": NotRequired[AttributeSuggestionsModeType],
    },
)

AuthenticationConfigurationTypeDef = TypedDict(
    "AuthenticationConfigurationTypeDef",
    {
        "BasicAuthentication": NotRequired[Sequence[BasicAuthenticationConfigurationTypeDef]],
    },
)

BatchDeleteDocumentRequestRequestTypeDef = TypedDict(
    "BatchDeleteDocumentRequestRequestTypeDef",
    {
        "IndexId": str,
        "DocumentIdList": Sequence[str],
        "DataSourceSyncJobMetricTarget": NotRequired[DataSourceSyncJobMetricTargetTypeDef],
    },
)

BatchDeleteDocumentResponseTypeDef = TypedDict(
    "BatchDeleteDocumentResponseTypeDef",
    {
        "FailedDocuments": List[BatchDeleteDocumentResponseFailedDocumentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDeleteFeaturedResultsSetResponseTypeDef = TypedDict(
    "BatchDeleteFeaturedResultsSetResponseTypeDef",
    {
        "Errors": List[BatchDeleteFeaturedResultsSetErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchGetDocumentStatusResponseTypeDef = TypedDict(
    "BatchGetDocumentStatusResponseTypeDef",
    {
        "Errors": List[BatchGetDocumentStatusResponseErrorTypeDef],
        "DocumentStatusList": List[StatusTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchPutDocumentResponseTypeDef = TypedDict(
    "BatchPutDocumentResponseTypeDef",
    {
        "FailedDocuments": List[BatchPutDocumentResponseFailedDocumentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClickFeedbackTypeDef = TypedDict(
    "ClickFeedbackTypeDef",
    {
        "ResultId": str,
        "ClickTime": TimestampTypeDef,
    },
)

DocumentAttributeValueTypeDef = TypedDict(
    "DocumentAttributeValueTypeDef",
    {
        "StringValue": NotRequired[str],
        "StringListValue": NotRequired[Sequence[str]],
        "LongValue": NotRequired[int],
        "DateValue": NotRequired[TimestampTypeDef],
    },
)

ConfluenceAttachmentConfigurationTypeDef = TypedDict(
    "ConfluenceAttachmentConfigurationTypeDef",
    {
        "CrawlAttachments": NotRequired[bool],
        "AttachmentFieldMappings": NotRequired[
            Sequence[ConfluenceAttachmentToIndexFieldMappingTypeDef]
        ],
    },
)

ConfluenceBlogConfigurationTypeDef = TypedDict(
    "ConfluenceBlogConfigurationTypeDef",
    {
        "BlogFieldMappings": NotRequired[Sequence[ConfluenceBlogToIndexFieldMappingTypeDef]],
    },
)

SharePointConfigurationTypeDef = TypedDict(
    "SharePointConfigurationTypeDef",
    {
        "SharePointVersion": SharePointVersionType,
        "Urls": Sequence[str],
        "SecretArn": str,
        "CrawlAttachments": NotRequired[bool],
        "UseChangeLog": NotRequired[bool],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "DocumentTitleFieldName": NotRequired[str],
        "DisableLocalGroups": NotRequired[bool],
        "SslCertificateS3Path": NotRequired[S3PathTypeDef],
        "AuthenticationType": NotRequired[SharePointOnlineAuthenticationTypeType],
        "ProxyConfiguration": NotRequired[ProxyConfigurationTypeDef],
    },
)

ConfluencePageConfigurationTypeDef = TypedDict(
    "ConfluencePageConfigurationTypeDef",
    {
        "PageFieldMappings": NotRequired[Sequence[ConfluencePageToIndexFieldMappingTypeDef]],
    },
)

ConfluenceSpaceConfigurationTypeDef = TypedDict(
    "ConfluenceSpaceConfigurationTypeDef",
    {
        "CrawlPersonalSpaces": NotRequired[bool],
        "CrawlArchivedSpaces": NotRequired[bool],
        "IncludeSpaces": NotRequired[Sequence[str]],
        "ExcludeSpaces": NotRequired[Sequence[str]],
        "SpaceFieldMappings": NotRequired[Sequence[ConfluenceSpaceToIndexFieldMappingTypeDef]],
    },
)

SpellCorrectedQueryTypeDef = TypedDict(
    "SpellCorrectedQueryTypeDef",
    {
        "SuggestedQueryText": NotRequired[str],
        "Corrections": NotRequired[List[CorrectionTypeDef]],
    },
)

HierarchicalPrincipalTypeDef = TypedDict(
    "HierarchicalPrincipalTypeDef",
    {
        "PrincipalList": Sequence[PrincipalTypeDef],
    },
)

CreateFaqRequestRequestTypeDef = TypedDict(
    "CreateFaqRequestRequestTypeDef",
    {
        "IndexId": str,
        "Name": str,
        "S3Path": S3PathTypeDef,
        "RoleArn": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "FileFormat": NotRequired[FaqFileFormatType],
        "ClientToken": NotRequired[str],
        "LanguageCode": NotRequired[str],
    },
)

CreateQuerySuggestionsBlockListRequestRequestTypeDef = TypedDict(
    "CreateQuerySuggestionsBlockListRequestRequestTypeDef",
    {
        "IndexId": str,
        "Name": str,
        "SourceS3Path": S3PathTypeDef,
        "RoleArn": str,
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateThesaurusRequestRequestTypeDef = TypedDict(
    "CreateThesaurusRequestRequestTypeDef",
    {
        "IndexId": str,
        "Name": str,
        "RoleArn": str,
        "SourceS3Path": S3PathTypeDef,
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ClientToken": NotRequired[str],
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "Tags": Sequence[TagTypeDef],
    },
)

CreateFeaturedResultsSetRequestRequestTypeDef = TypedDict(
    "CreateFeaturedResultsSetRequestRequestTypeDef",
    {
        "IndexId": str,
        "FeaturedResultsSetName": str,
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "Status": NotRequired[FeaturedResultsSetStatusType],
        "QueryTexts": NotRequired[Sequence[str]],
        "FeaturedDocuments": NotRequired[Sequence[FeaturedDocumentTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

FeaturedResultsSetTypeDef = TypedDict(
    "FeaturedResultsSetTypeDef",
    {
        "FeaturedResultsSetId": NotRequired[str],
        "FeaturedResultsSetName": NotRequired[str],
        "Description": NotRequired[str],
        "Status": NotRequired[FeaturedResultsSetStatusType],
        "QueryTexts": NotRequired[List[str]],
        "FeaturedDocuments": NotRequired[List[FeaturedDocumentTypeDef]],
        "LastUpdatedTimestamp": NotRequired[int],
        "CreationTimestamp": NotRequired[int],
    },
)

UpdateFeaturedResultsSetRequestRequestTypeDef = TypedDict(
    "UpdateFeaturedResultsSetRequestRequestTypeDef",
    {
        "IndexId": str,
        "FeaturedResultsSetId": str,
        "FeaturedResultsSetName": NotRequired[str],
        "Description": NotRequired[str],
        "Status": NotRequired[FeaturedResultsSetStatusType],
        "QueryTexts": NotRequired[Sequence[str]],
        "FeaturedDocuments": NotRequired[Sequence[FeaturedDocumentTypeDef]],
    },
)

UserContextTypeDef = TypedDict(
    "UserContextTypeDef",
    {
        "Token": NotRequired[str],
        "UserId": NotRequired[str],
        "Groups": NotRequired[Sequence[str]],
        "DataSourceGroups": NotRequired[Sequence[DataSourceGroupTypeDef]],
    },
)

ListDataSourcesResponseTypeDef = TypedDict(
    "ListDataSourcesResponseTypeDef",
    {
        "SummaryItems": List[DataSourceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DataSourceSyncJobTypeDef = TypedDict(
    "DataSourceSyncJobTypeDef",
    {
        "ExecutionId": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "Status": NotRequired[DataSourceSyncJobStatusType],
        "ErrorMessage": NotRequired[str],
        "ErrorCode": NotRequired[ErrorCodeType],
        "DataSourceErrorCode": NotRequired[str],
        "Metrics": NotRequired[DataSourceSyncJobMetricsTypeDef],
    },
)

ExperiencesSummaryTypeDef = TypedDict(
    "ExperiencesSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Status": NotRequired[ExperienceStatusType],
        "Endpoints": NotRequired[List[ExperienceEndpointTypeDef]],
    },
)

DescribeFeaturedResultsSetResponseTypeDef = TypedDict(
    "DescribeFeaturedResultsSetResponseTypeDef",
    {
        "FeaturedResultsSetId": str,
        "FeaturedResultsSetName": str,
        "Description": str,
        "Status": FeaturedResultsSetStatusType,
        "QueryTexts": List[str],
        "FeaturedDocumentsWithMetadata": List[FeaturedDocumentWithMetadataTypeDef],
        "FeaturedDocumentsMissing": List[FeaturedDocumentMissingTypeDef],
        "LastUpdatedTimestamp": int,
        "CreationTimestamp": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePrincipalMappingResponseTypeDef = TypedDict(
    "DescribePrincipalMappingResponseTypeDef",
    {
        "IndexId": str,
        "DataSourceId": str,
        "GroupId": str,
        "GroupOrderingIdSummaries": List[GroupOrderingIdSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DocumentRelevanceConfigurationTypeDef = TypedDict(
    "DocumentRelevanceConfigurationTypeDef",
    {
        "Name": str,
        "Relevance": RelevanceTypeDef,
    },
)

DocumentMetadataConfigurationTypeDef = TypedDict(
    "DocumentMetadataConfigurationTypeDef",
    {
        "Name": str,
        "Type": DocumentAttributeValueTypeType,
        "Relevance": NotRequired[RelevanceTypeDef],
        "Search": NotRequired[SearchTypeDef],
    },
)

S3DataSourceConfigurationTypeDef = TypedDict(
    "S3DataSourceConfigurationTypeDef",
    {
        "BucketName": str,
        "InclusionPrefixes": NotRequired[Sequence[str]],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "DocumentsMetadataConfiguration": NotRequired[DocumentsMetadataConfigurationTypeDef],
        "AccessControlListConfiguration": NotRequired[AccessControlListConfigurationTypeDef],
    },
)

ExperienceEntitiesSummaryTypeDef = TypedDict(
    "ExperienceEntitiesSummaryTypeDef",
    {
        "EntityId": NotRequired[str],
        "EntityType": NotRequired[EntityTypeType],
        "DisplayData": NotRequired[EntityDisplayDataTypeDef],
    },
)

ExperienceConfigurationTypeDef = TypedDict(
    "ExperienceConfigurationTypeDef",
    {
        "ContentSourceConfiguration": NotRequired[ContentSourceConfigurationTypeDef],
        "UserIdentityConfiguration": NotRequired[UserIdentityConfigurationTypeDef],
    },
)

ListFaqsResponseTypeDef = TypedDict(
    "ListFaqsResponseTypeDef",
    {
        "NextToken": str,
        "FaqSummaryItems": List[FaqSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListFeaturedResultsSetsResponseTypeDef = TypedDict(
    "ListFeaturedResultsSetsResponseTypeDef",
    {
        "FeaturedResultsSetSummaryItems": List[FeaturedResultsSetSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSnapshotsResponseTypeDef = TypedDict(
    "GetSnapshotsResponseTypeDef",
    {
        "SnapShotTimeFilter": TimeRangeTypeDef,
        "SnapshotsDataHeader": List[str],
        "SnapshotsData": List[List[str]],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDataSourceSyncJobsRequestRequestTypeDef = TypedDict(
    "ListDataSourceSyncJobsRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "StartTimeFilter": NotRequired[TimeRangeTypeDef],
        "StatusFilter": NotRequired[DataSourceSyncJobStatusType],
    },
)

GroupMembersTypeDef = TypedDict(
    "GroupMembersTypeDef",
    {
        "MemberGroups": NotRequired[Sequence[MemberGroupTypeDef]],
        "MemberUsers": NotRequired[Sequence[MemberUserTypeDef]],
        "S3PathforGroupMembers": NotRequired[S3PathTypeDef],
    },
)

ListGroupsOlderThanOrderingIdResponseTypeDef = TypedDict(
    "ListGroupsOlderThanOrderingIdResponseTypeDef",
    {
        "GroupsSummaries": List[GroupSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TextWithHighlightsTypeDef = TypedDict(
    "TextWithHighlightsTypeDef",
    {
        "Text": NotRequired[str],
        "Highlights": NotRequired[List[HighlightTypeDef]],
    },
)

ListIndicesResponseTypeDef = TypedDict(
    "ListIndicesResponseTypeDef",
    {
        "IndexConfigurationSummaryItems": List[IndexConfigurationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IndexStatisticsTypeDef = TypedDict(
    "IndexStatisticsTypeDef",
    {
        "FaqStatistics": FaqStatisticsTypeDef,
        "TextDocumentStatistics": TextDocumentStatisticsTypeDef,
    },
)

UserTokenConfigurationTypeDef = TypedDict(
    "UserTokenConfigurationTypeDef",
    {
        "JwtTokenTypeConfiguration": NotRequired[JwtTokenTypeConfigurationTypeDef],
        "JsonTokenTypeConfiguration": NotRequired[JsonTokenTypeConfigurationTypeDef],
    },
)

ListEntityPersonasResponseTypeDef = TypedDict(
    "ListEntityPersonasResponseTypeDef",
    {
        "SummaryItems": List[PersonasSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListQuerySuggestionsBlockListsResponseTypeDef = TypedDict(
    "ListQuerySuggestionsBlockListsResponseTypeDef",
    {
        "BlockListSummaryItems": List[QuerySuggestionsBlockListSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListThesauriResponseTypeDef = TypedDict(
    "ListThesauriResponseTypeDef",
    {
        "NextToken": str,
        "ThesaurusSummaryItems": List[ThesaurusSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UrlsTypeDef = TypedDict(
    "UrlsTypeDef",
    {
        "SeedUrlConfiguration": NotRequired[SeedUrlConfigurationTypeDef],
        "SiteMapsConfiguration": NotRequired[SiteMapsConfigurationTypeDef],
    },
)

SuggestionTextWithHighlightsTypeDef = TypedDict(
    "SuggestionTextWithHighlightsTypeDef",
    {
        "Text": NotRequired[str],
        "Highlights": NotRequired[List[SuggestionHighlightTypeDef]],
    },
)

TableRowTypeDef = TypedDict(
    "TableRowTypeDef",
    {
        "Cells": NotRequired[List[TableCellTypeDef]],
    },
)

DatabaseConfigurationTypeDef = TypedDict(
    "DatabaseConfigurationTypeDef",
    {
        "DatabaseEngineType": DatabaseEngineTypeType,
        "ConnectionConfiguration": ConnectionConfigurationTypeDef,
        "ColumnConfiguration": ColumnConfigurationTypeDef,
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "AclConfiguration": NotRequired[AclConfigurationTypeDef],
        "SqlConfiguration": NotRequired[SqlConfigurationTypeDef],
    },
)

SalesforceKnowledgeArticleConfigurationTypeDef = TypedDict(
    "SalesforceKnowledgeArticleConfigurationTypeDef",
    {
        "IncludedStates": Sequence[SalesforceKnowledgeArticleStateType],
        "StandardKnowledgeArticleTypeConfiguration": NotRequired[
            SalesforceStandardKnowledgeArticleTypeConfigurationTypeDef
        ],
        "CustomKnowledgeArticleTypeConfigurations": NotRequired[
            Sequence[SalesforceCustomKnowledgeArticleTypeConfigurationTypeDef]
        ],
    },
)

ServiceNowConfigurationTypeDef = TypedDict(
    "ServiceNowConfigurationTypeDef",
    {
        "HostUrl": str,
        "SecretArn": str,
        "ServiceNowBuildVersion": ServiceNowBuildVersionTypeType,
        "KnowledgeArticleConfiguration": NotRequired[
            ServiceNowKnowledgeArticleConfigurationTypeDef
        ],
        "ServiceCatalogConfiguration": NotRequired[ServiceNowServiceCatalogConfigurationTypeDef],
        "AuthenticationType": NotRequired[ServiceNowAuthenticationTypeType],
    },
)

GitHubConfigurationTypeDef = TypedDict(
    "GitHubConfigurationTypeDef",
    {
        "SecretArn": str,
        "SaaSConfiguration": NotRequired[SaaSConfigurationTypeDef],
        "OnPremiseConfiguration": NotRequired[OnPremiseConfigurationTypeDef],
        "Type": NotRequired[TypeType],
        "UseChangeLog": NotRequired[bool],
        "GitHubDocumentCrawlProperties": NotRequired[GitHubDocumentCrawlPropertiesTypeDef],
        "RepositoryFilter": NotRequired[Sequence[str]],
        "InclusionFolderNamePatterns": NotRequired[Sequence[str]],
        "InclusionFileTypePatterns": NotRequired[Sequence[str]],
        "InclusionFileNamePatterns": NotRequired[Sequence[str]],
        "ExclusionFolderNamePatterns": NotRequired[Sequence[str]],
        "ExclusionFileTypePatterns": NotRequired[Sequence[str]],
        "ExclusionFileNamePatterns": NotRequired[Sequence[str]],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "GitHubRepositoryConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubCommitConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubIssueDocumentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubIssueCommentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubIssueAttachmentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubPullRequestCommentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubPullRequestDocumentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
        "GitHubPullRequestDocumentAttachmentConfigurationFieldMappings": NotRequired[
            Sequence[DataSourceToIndexFieldMappingTypeDef]
        ],
    },
)

OneDriveConfigurationTypeDef = TypedDict(
    "OneDriveConfigurationTypeDef",
    {
        "TenantDomain": str,
        "SecretArn": str,
        "OneDriveUsers": OneDriveUsersTypeDef,
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "FieldMappings": NotRequired[Sequence[DataSourceToIndexFieldMappingTypeDef]],
        "DisableLocalGroups": NotRequired[bool],
    },
)

DescribeQuerySuggestionsConfigResponseTypeDef = TypedDict(
    "DescribeQuerySuggestionsConfigResponseTypeDef",
    {
        "Mode": ModeType,
        "Status": QuerySuggestionsStatusType,
        "QueryLogLookBackWindowInDays": int,
        "IncludeQueriesWithoutUserInformation": bool,
        "MinimumNumberOfQueryingUsers": int,
        "MinimumQueryCount": int,
        "LastSuggestionsBuildTime": datetime,
        "LastClearTime": datetime,
        "TotalSuggestionsCount": int,
        "AttributeSuggestionsConfig": AttributeSuggestionsDescribeConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateQuerySuggestionsConfigRequestRequestTypeDef = TypedDict(
    "UpdateQuerySuggestionsConfigRequestRequestTypeDef",
    {
        "IndexId": str,
        "Mode": NotRequired[ModeType],
        "QueryLogLookBackWindowInDays": NotRequired[int],
        "IncludeQueriesWithoutUserInformation": NotRequired[bool],
        "MinimumNumberOfQueryingUsers": NotRequired[int],
        "MinimumQueryCount": NotRequired[int],
        "AttributeSuggestionsConfig": NotRequired[AttributeSuggestionsUpdateConfigTypeDef],
    },
)

SubmitFeedbackRequestRequestTypeDef = TypedDict(
    "SubmitFeedbackRequestRequestTypeDef",
    {
        "IndexId": str,
        "QueryId": str,
        "ClickFeedbackItems": NotRequired[Sequence[ClickFeedbackTypeDef]],
        "RelevanceFeedbackItems": NotRequired[Sequence[RelevanceFeedbackTypeDef]],
    },
)

DocumentAttributeConditionTypeDef = TypedDict(
    "DocumentAttributeConditionTypeDef",
    {
        "ConditionDocumentAttributeKey": str,
        "Operator": ConditionOperatorType,
        "ConditionOnValue": NotRequired[DocumentAttributeValueTypeDef],
    },
)

DocumentAttributeTargetTypeDef = TypedDict(
    "DocumentAttributeTargetTypeDef",
    {
        "TargetDocumentAttributeKey": NotRequired[str],
        "TargetDocumentAttributeValueDeletion": NotRequired[bool],
        "TargetDocumentAttributeValue": NotRequired[DocumentAttributeValueTypeDef],
    },
)

DocumentAttributeTypeDef = TypedDict(
    "DocumentAttributeTypeDef",
    {
        "Key": str,
        "Value": DocumentAttributeValueTypeDef,
    },
)

DocumentAttributeValueCountPairTypeDef = TypedDict(
    "DocumentAttributeValueCountPairTypeDef",
    {
        "DocumentAttributeValue": NotRequired[DocumentAttributeValueTypeDef],
        "Count": NotRequired[int],
        "FacetResults": NotRequired[List[Dict[str, Any]]],
    },
)

ConfluenceConfigurationTypeDef = TypedDict(
    "ConfluenceConfigurationTypeDef",
    {
        "ServerUrl": str,
        "SecretArn": str,
        "Version": ConfluenceVersionType,
        "SpaceConfiguration": NotRequired[ConfluenceSpaceConfigurationTypeDef],
        "PageConfiguration": NotRequired[ConfluencePageConfigurationTypeDef],
        "BlogConfiguration": NotRequired[ConfluenceBlogConfigurationTypeDef],
        "AttachmentConfiguration": NotRequired[ConfluenceAttachmentConfigurationTypeDef],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "InclusionPatterns": NotRequired[Sequence[str]],
        "ExclusionPatterns": NotRequired[Sequence[str]],
        "ProxyConfiguration": NotRequired[ProxyConfigurationTypeDef],
        "AuthenticationType": NotRequired[ConfluenceAuthenticationTypeType],
    },
)

CreateAccessControlConfigurationRequestRequestTypeDef = TypedDict(
    "CreateAccessControlConfigurationRequestRequestTypeDef",
    {
        "IndexId": str,
        "Name": str,
        "Description": NotRequired[str],
        "AccessControlList": NotRequired[Sequence[PrincipalTypeDef]],
        "HierarchicalAccessControlList": NotRequired[Sequence[HierarchicalPrincipalTypeDef]],
        "ClientToken": NotRequired[str],
    },
)

DescribeAccessControlConfigurationResponseTypeDef = TypedDict(
    "DescribeAccessControlConfigurationResponseTypeDef",
    {
        "Name": str,
        "Description": str,
        "ErrorMessage": str,
        "AccessControlList": List[PrincipalTypeDef],
        "HierarchicalAccessControlList": List[HierarchicalPrincipalTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAccessControlConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateAccessControlConfigurationRequestRequestTypeDef",
    {
        "IndexId": str,
        "Id": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "AccessControlList": NotRequired[Sequence[PrincipalTypeDef]],
        "HierarchicalAccessControlList": NotRequired[Sequence[HierarchicalPrincipalTypeDef]],
    },
)

CreateFeaturedResultsSetResponseTypeDef = TypedDict(
    "CreateFeaturedResultsSetResponseTypeDef",
    {
        "FeaturedResultsSet": FeaturedResultsSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateFeaturedResultsSetResponseTypeDef = TypedDict(
    "UpdateFeaturedResultsSetResponseTypeDef",
    {
        "FeaturedResultsSet": FeaturedResultsSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AttributeSuggestionsGetConfigTypeDef = TypedDict(
    "AttributeSuggestionsGetConfigTypeDef",
    {
        "SuggestionAttributes": NotRequired[Sequence[str]],
        "AdditionalResponseAttributes": NotRequired[Sequence[str]],
        "AttributeFilter": NotRequired["AttributeFilterTypeDef"],
        "UserContext": NotRequired[UserContextTypeDef],
    },
)

ListDataSourceSyncJobsResponseTypeDef = TypedDict(
    "ListDataSourceSyncJobsResponseTypeDef",
    {
        "History": List[DataSourceSyncJobTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListExperiencesResponseTypeDef = TypedDict(
    "ListExperiencesResponseTypeDef",
    {
        "SummaryItems": List[ExperiencesSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

QueryRequestRequestTypeDef = TypedDict(
    "QueryRequestRequestTypeDef",
    {
        "IndexId": str,
        "QueryText": NotRequired[str],
        "AttributeFilter": NotRequired["AttributeFilterTypeDef"],
        "Facets": NotRequired[Sequence["FacetTypeDef"]],
        "RequestedDocumentAttributes": NotRequired[Sequence[str]],
        "QueryResultTypeFilter": NotRequired[QueryResultTypeType],
        "DocumentRelevanceOverrideConfigurations": NotRequired[
            Sequence[DocumentRelevanceConfigurationTypeDef]
        ],
        "PageNumber": NotRequired[int],
        "PageSize": NotRequired[int],
        "SortingConfiguration": NotRequired[SortingConfigurationTypeDef],
        "UserContext": NotRequired[UserContextTypeDef],
        "VisitorId": NotRequired[str],
        "SpellCorrectionConfiguration": NotRequired[SpellCorrectionConfigurationTypeDef],
    },
)

RetrieveRequestRequestTypeDef = TypedDict(
    "RetrieveRequestRequestTypeDef",
    {
        "IndexId": str,
        "QueryText": str,
        "AttributeFilter": NotRequired["AttributeFilterTypeDef"],
        "RequestedDocumentAttributes": NotRequired[Sequence[str]],
        "DocumentRelevanceOverrideConfigurations": NotRequired[
            Sequence[DocumentRelevanceConfigurationTypeDef]
        ],
        "PageNumber": NotRequired[int],
        "PageSize": NotRequired[int],
        "UserContext": NotRequired[UserContextTypeDef],
    },
)

ListExperienceEntitiesResponseTypeDef = TypedDict(
    "ListExperienceEntitiesResponseTypeDef",
    {
        "SummaryItems": List[ExperienceEntitiesSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateExperienceRequestRequestTypeDef = TypedDict(
    "CreateExperienceRequestRequestTypeDef",
    {
        "Name": str,
        "IndexId": str,
        "RoleArn": NotRequired[str],
        "Configuration": NotRequired[ExperienceConfigurationTypeDef],
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
    },
)

DescribeExperienceResponseTypeDef = TypedDict(
    "DescribeExperienceResponseTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": str,
        "Endpoints": List[ExperienceEndpointTypeDef],
        "Configuration": ExperienceConfigurationTypeDef,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "Description": str,
        "Status": ExperienceStatusType,
        "RoleArn": str,
        "ErrorMessage": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateExperienceRequestRequestTypeDef = TypedDict(
    "UpdateExperienceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Configuration": NotRequired[ExperienceConfigurationTypeDef],
        "Description": NotRequired[str],
    },
)

PutPrincipalMappingRequestRequestTypeDef = TypedDict(
    "PutPrincipalMappingRequestRequestTypeDef",
    {
        "IndexId": str,
        "GroupId": str,
        "GroupMembers": GroupMembersTypeDef,
        "DataSourceId": NotRequired[str],
        "OrderingId": NotRequired[int],
        "RoleArn": NotRequired[str],
    },
)

AdditionalResultAttributeValueTypeDef = TypedDict(
    "AdditionalResultAttributeValueTypeDef",
    {
        "TextWithHighlightsValue": NotRequired[TextWithHighlightsTypeDef],
    },
)

CreateIndexRequestRequestTypeDef = TypedDict(
    "CreateIndexRequestRequestTypeDef",
    {
        "Name": str,
        "RoleArn": str,
        "Edition": NotRequired[IndexEditionType],
        "ServerSideEncryptionConfiguration": NotRequired[ServerSideEncryptionConfigurationTypeDef],
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "UserTokenConfigurations": NotRequired[Sequence[UserTokenConfigurationTypeDef]],
        "UserContextPolicy": NotRequired[UserContextPolicyType],
        "UserGroupResolutionConfiguration": NotRequired[UserGroupResolutionConfigurationTypeDef],
    },
)

DescribeIndexResponseTypeDef = TypedDict(
    "DescribeIndexResponseTypeDef",
    {
        "Name": str,
        "Id": str,
        "Edition": IndexEditionType,
        "RoleArn": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
        "Status": IndexStatusType,
        "Description": str,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "DocumentMetadataConfigurations": List[DocumentMetadataConfigurationTypeDef],
        "IndexStatistics": IndexStatisticsTypeDef,
        "ErrorMessage": str,
        "CapacityUnits": CapacityUnitsConfigurationTypeDef,
        "UserTokenConfigurations": List[UserTokenConfigurationTypeDef],
        "UserContextPolicy": UserContextPolicyType,
        "UserGroupResolutionConfiguration": UserGroupResolutionConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateIndexRequestRequestTypeDef = TypedDict(
    "UpdateIndexRequestRequestTypeDef",
    {
        "Id": str,
        "Name": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "DocumentMetadataConfigurationUpdates": NotRequired[
            Sequence[DocumentMetadataConfigurationTypeDef]
        ],
        "CapacityUnits": NotRequired[CapacityUnitsConfigurationTypeDef],
        "UserTokenConfigurations": NotRequired[Sequence[UserTokenConfigurationTypeDef]],
        "UserContextPolicy": NotRequired[UserContextPolicyType],
        "UserGroupResolutionConfiguration": NotRequired[UserGroupResolutionConfigurationTypeDef],
    },
)

WebCrawlerConfigurationTypeDef = TypedDict(
    "WebCrawlerConfigurationTypeDef",
    {
        "Urls": UrlsTypeDef,
        "CrawlDepth": NotRequired[int],
        "MaxLinksPerPage": NotRequired[int],
        "MaxContentSizePerPageInMegaBytes": NotRequired[float],
        "MaxUrlsPerMinuteCrawlRate": NotRequired[int],
        "UrlInclusionPatterns": NotRequired[Sequence[str]],
        "UrlExclusionPatterns": NotRequired[Sequence[str]],
        "ProxyConfiguration": NotRequired[ProxyConfigurationTypeDef],
        "AuthenticationConfiguration": NotRequired[AuthenticationConfigurationTypeDef],
    },
)

SuggestionValueTypeDef = TypedDict(
    "SuggestionValueTypeDef",
    {
        "Text": NotRequired[SuggestionTextWithHighlightsTypeDef],
    },
)

TableExcerptTypeDef = TypedDict(
    "TableExcerptTypeDef",
    {
        "Rows": NotRequired[List[TableRowTypeDef]],
        "TotalNumberOfRows": NotRequired[int],
    },
)

SalesforceConfigurationTypeDef = TypedDict(
    "SalesforceConfigurationTypeDef",
    {
        "ServerUrl": str,
        "SecretArn": str,
        "StandardObjectConfigurations": NotRequired[
            Sequence[SalesforceStandardObjectConfigurationTypeDef]
        ],
        "KnowledgeArticleConfiguration": NotRequired[
            SalesforceKnowledgeArticleConfigurationTypeDef
        ],
        "ChatterFeedConfiguration": NotRequired[SalesforceChatterFeedConfigurationTypeDef],
        "CrawlAttachments": NotRequired[bool],
        "StandardObjectAttachmentConfiguration": NotRequired[
            SalesforceStandardObjectAttachmentConfigurationTypeDef
        ],
        "IncludeAttachmentFilePatterns": NotRequired[Sequence[str]],
        "ExcludeAttachmentFilePatterns": NotRequired[Sequence[str]],
    },
)

HookConfigurationTypeDef = TypedDict(
    "HookConfigurationTypeDef",
    {
        "LambdaArn": str,
        "S3Bucket": str,
        "InvocationCondition": NotRequired[DocumentAttributeConditionTypeDef],
    },
)

InlineCustomDocumentEnrichmentConfigurationTypeDef = TypedDict(
    "InlineCustomDocumentEnrichmentConfigurationTypeDef",
    {
        "Condition": NotRequired[DocumentAttributeConditionTypeDef],
        "Target": NotRequired[DocumentAttributeTargetTypeDef],
        "DocumentContentDeletion": NotRequired[bool],
    },
)

AttributeFilterTypeDef = TypedDict(
    "AttributeFilterTypeDef",
    {
        "AndAllFilters": NotRequired[Sequence[Dict[str, Any]]],
        "OrAllFilters": NotRequired[Sequence[Dict[str, Any]]],
        "NotFilter": NotRequired[Dict[str, Any]],
        "EqualsTo": NotRequired[DocumentAttributeTypeDef],
        "ContainsAll": NotRequired[DocumentAttributeTypeDef],
        "ContainsAny": NotRequired[DocumentAttributeTypeDef],
        "GreaterThan": NotRequired[DocumentAttributeTypeDef],
        "GreaterThanOrEquals": NotRequired[DocumentAttributeTypeDef],
        "LessThan": NotRequired[DocumentAttributeTypeDef],
        "LessThanOrEquals": NotRequired[DocumentAttributeTypeDef],
    },
)

DocumentInfoTypeDef = TypedDict(
    "DocumentInfoTypeDef",
    {
        "DocumentId": str,
        "Attributes": NotRequired[Sequence[DocumentAttributeTypeDef]],
    },
)

DocumentTypeDef = TypedDict(
    "DocumentTypeDef",
    {
        "Id": str,
        "Title": NotRequired[str],
        "Blob": NotRequired[BlobTypeDef],
        "S3Path": NotRequired[S3PathTypeDef],
        "Attributes": NotRequired[Sequence[DocumentAttributeTypeDef]],
        "AccessControlList": NotRequired[Sequence[PrincipalTypeDef]],
        "HierarchicalAccessControlList": NotRequired[Sequence[HierarchicalPrincipalTypeDef]],
        "ContentType": NotRequired[ContentTypeType],
        "AccessControlConfigurationId": NotRequired[str],
    },
)

RetrieveResultItemTypeDef = TypedDict(
    "RetrieveResultItemTypeDef",
    {
        "Id": NotRequired[str],
        "DocumentId": NotRequired[str],
        "DocumentTitle": NotRequired[str],
        "Content": NotRequired[str],
        "DocumentURI": NotRequired[str],
        "DocumentAttributes": NotRequired[List[DocumentAttributeTypeDef]],
        "ScoreAttributes": NotRequired[ScoreAttributesTypeDef],
    },
)

SourceDocumentTypeDef = TypedDict(
    "SourceDocumentTypeDef",
    {
        "DocumentId": NotRequired[str],
        "SuggestionAttributes": NotRequired[List[str]],
        "AdditionalAttributes": NotRequired[List[DocumentAttributeTypeDef]],
    },
)

GetQuerySuggestionsRequestRequestTypeDef = TypedDict(
    "GetQuerySuggestionsRequestRequestTypeDef",
    {
        "IndexId": str,
        "QueryText": str,
        "MaxSuggestionsCount": NotRequired[int],
        "SuggestionTypes": NotRequired[Sequence[SuggestionTypeType]],
        "AttributeSuggestionsConfig": NotRequired[AttributeSuggestionsGetConfigTypeDef],
    },
)

AdditionalResultAttributeTypeDef = TypedDict(
    "AdditionalResultAttributeTypeDef",
    {
        "Key": str,
        "ValueType": Literal["TEXT_WITH_HIGHLIGHTS_VALUE"],
        "Value": AdditionalResultAttributeValueTypeDef,
    },
)

DataSourceConfigurationTypeDef = TypedDict(
    "DataSourceConfigurationTypeDef",
    {
        "S3Configuration": NotRequired[S3DataSourceConfigurationTypeDef],
        "SharePointConfiguration": NotRequired[SharePointConfigurationTypeDef],
        "DatabaseConfiguration": NotRequired[DatabaseConfigurationTypeDef],
        "SalesforceConfiguration": NotRequired[SalesforceConfigurationTypeDef],
        "OneDriveConfiguration": NotRequired[OneDriveConfigurationTypeDef],
        "ServiceNowConfiguration": NotRequired[ServiceNowConfigurationTypeDef],
        "ConfluenceConfiguration": NotRequired[ConfluenceConfigurationTypeDef],
        "GoogleDriveConfiguration": NotRequired[GoogleDriveConfigurationTypeDef],
        "WebCrawlerConfiguration": NotRequired[WebCrawlerConfigurationTypeDef],
        "WorkDocsConfiguration": NotRequired[WorkDocsConfigurationTypeDef],
        "FsxConfiguration": NotRequired[FsxConfigurationTypeDef],
        "SlackConfiguration": NotRequired[SlackConfigurationTypeDef],
        "BoxConfiguration": NotRequired[BoxConfigurationTypeDef],
        "QuipConfiguration": NotRequired[QuipConfigurationTypeDef],
        "JiraConfiguration": NotRequired[JiraConfigurationTypeDef],
        "GitHubConfiguration": NotRequired[GitHubConfigurationTypeDef],
        "AlfrescoConfiguration": NotRequired[AlfrescoConfigurationTypeDef],
        "TemplateConfiguration": NotRequired[TemplateConfigurationTypeDef],
    },
)

CustomDocumentEnrichmentConfigurationTypeDef = TypedDict(
    "CustomDocumentEnrichmentConfigurationTypeDef",
    {
        "InlineConfigurations": NotRequired[
            Sequence[InlineCustomDocumentEnrichmentConfigurationTypeDef]
        ],
        "PreExtractionHookConfiguration": NotRequired[HookConfigurationTypeDef],
        "PostExtractionHookConfiguration": NotRequired[HookConfigurationTypeDef],
        "RoleArn": NotRequired[str],
    },
)

BatchGetDocumentStatusRequestRequestTypeDef = TypedDict(
    "BatchGetDocumentStatusRequestRequestTypeDef",
    {
        "IndexId": str,
        "DocumentInfoList": Sequence[DocumentInfoTypeDef],
    },
)

RetrieveResultTypeDef = TypedDict(
    "RetrieveResultTypeDef",
    {
        "QueryId": str,
        "ResultItems": List[RetrieveResultItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SuggestionTypeDef = TypedDict(
    "SuggestionTypeDef",
    {
        "Id": NotRequired[str],
        "Value": NotRequired[SuggestionValueTypeDef],
        "SourceDocuments": NotRequired[List[SourceDocumentTypeDef]],
    },
)

FeaturedResultsItemTypeDef = TypedDict(
    "FeaturedResultsItemTypeDef",
    {
        "Id": NotRequired[str],
        "Type": NotRequired[QueryResultTypeType],
        "AdditionalAttributes": NotRequired[List[AdditionalResultAttributeTypeDef]],
        "DocumentId": NotRequired[str],
        "DocumentTitle": NotRequired[TextWithHighlightsTypeDef],
        "DocumentExcerpt": NotRequired[TextWithHighlightsTypeDef],
        "DocumentURI": NotRequired[str],
        "DocumentAttributes": NotRequired[List[DocumentAttributeTypeDef]],
        "FeedbackToken": NotRequired[str],
    },
)

QueryResultItemTypeDef = TypedDict(
    "QueryResultItemTypeDef",
    {
        "Id": NotRequired[str],
        "Type": NotRequired[QueryResultTypeType],
        "Format": NotRequired[QueryResultFormatType],
        "AdditionalAttributes": NotRequired[List[AdditionalResultAttributeTypeDef]],
        "DocumentId": NotRequired[str],
        "DocumentTitle": NotRequired[TextWithHighlightsTypeDef],
        "DocumentExcerpt": NotRequired[TextWithHighlightsTypeDef],
        "DocumentURI": NotRequired[str],
        "DocumentAttributes": NotRequired[List[DocumentAttributeTypeDef]],
        "ScoreAttributes": NotRequired[ScoreAttributesTypeDef],
        "FeedbackToken": NotRequired[str],
        "TableExcerpt": NotRequired[TableExcerptTypeDef],
    },
)

BatchPutDocumentRequestRequestTypeDef = TypedDict(
    "BatchPutDocumentRequestRequestTypeDef",
    {
        "IndexId": str,
        "Documents": Sequence[DocumentTypeDef],
        "RoleArn": NotRequired[str],
        "CustomDocumentEnrichmentConfiguration": NotRequired[
            CustomDocumentEnrichmentConfigurationTypeDef
        ],
    },
)

CreateDataSourceRequestRequestTypeDef = TypedDict(
    "CreateDataSourceRequestRequestTypeDef",
    {
        "Name": str,
        "IndexId": str,
        "Type": DataSourceTypeType,
        "Configuration": NotRequired[DataSourceConfigurationTypeDef],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "Description": NotRequired[str],
        "Schedule": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ClientToken": NotRequired[str],
        "LanguageCode": NotRequired[str],
        "CustomDocumentEnrichmentConfiguration": NotRequired[
            CustomDocumentEnrichmentConfigurationTypeDef
        ],
    },
)

DescribeDataSourceResponseTypeDef = TypedDict(
    "DescribeDataSourceResponseTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": str,
        "Type": DataSourceTypeType,
        "Configuration": DataSourceConfigurationTypeDef,
        "VpcConfiguration": DataSourceVpcConfigurationTypeDef,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "Description": str,
        "Status": DataSourceStatusType,
        "Schedule": str,
        "RoleArn": str,
        "ErrorMessage": str,
        "LanguageCode": str,
        "CustomDocumentEnrichmentConfiguration": CustomDocumentEnrichmentConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDataSourceRequestRequestTypeDef = TypedDict(
    "UpdateDataSourceRequestRequestTypeDef",
    {
        "Id": str,
        "IndexId": str,
        "Name": NotRequired[str],
        "Configuration": NotRequired[DataSourceConfigurationTypeDef],
        "VpcConfiguration": NotRequired[DataSourceVpcConfigurationTypeDef],
        "Description": NotRequired[str],
        "Schedule": NotRequired[str],
        "RoleArn": NotRequired[str],
        "LanguageCode": NotRequired[str],
        "CustomDocumentEnrichmentConfiguration": NotRequired[
            CustomDocumentEnrichmentConfigurationTypeDef
        ],
    },
)

GetQuerySuggestionsResponseTypeDef = TypedDict(
    "GetQuerySuggestionsResponseTypeDef",
    {
        "QuerySuggestionsId": str,
        "Suggestions": List[SuggestionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

QueryResultTypeDef = TypedDict(
    "QueryResultTypeDef",
    {
        "QueryId": str,
        "ResultItems": List[QueryResultItemTypeDef],
        "FacetResults": List["FacetResultTypeDef"],
        "TotalNumberOfResults": int,
        "Warnings": List[WarningTypeDef],
        "SpellCorrectedQueries": List[SpellCorrectedQueryTypeDef],
        "FeaturedResultsItems": List[FeaturedResultsItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
