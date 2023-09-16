"""
Type annotations for connect service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_connect/type_defs/)

Usage::

    ```python
    from mypy_boto3_connect.type_defs import ActionSummaryTypeDef

    data: ActionSummaryTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionTypeType,
    AgentAvailabilityTimerType,
    AgentStatusStateType,
    AgentStatusTypeType,
    BehaviorTypeType,
    ChannelType,
    ContactFlowModuleStateType,
    ContactFlowModuleStatusType,
    ContactFlowStateType,
    ContactFlowTypeType,
    ContactInitiationMethodType,
    ContactStateType,
    CurrentMetricNameType,
    DirectoryTypeType,
    EvaluationFormQuestionTypeType,
    EvaluationFormScoringModeType,
    EvaluationFormScoringStatusType,
    EvaluationFormSingleSelectQuestionDisplayModeType,
    EvaluationFormVersionStatusType,
    EvaluationStatusType,
    EventSourceNameType,
    GroupingType,
    HierarchyGroupMatchTypeType,
    HistoricalMetricNameType,
    HoursOfOperationDaysType,
    InstanceAttributeTypeType,
    InstanceStatusType,
    InstanceStorageResourceTypeType,
    IntegrationTypeType,
    LexVersionType,
    MonitorCapabilityType,
    NumericQuestionPropertyAutomationLabelType,
    ParticipantRoleType,
    ParticipantTimerTypeType,
    PhoneNumberCountryCodeType,
    PhoneNumberTypeType,
    PhoneNumberWorkflowStatusType,
    PhoneTypeType,
    QueueStatusType,
    QueueTypeType,
    QuickConnectTypeType,
    ReferenceStatusType,
    ReferenceTypeType,
    RehydrationTypeType,
    RulePublishStatusType,
    SingleSelectQuestionRuleCategoryAutomationConditionType,
    SortOrderType,
    SourceTypeType,
    StatisticType,
    StorageTypeType,
    StringComparisonTypeType,
    TaskTemplateFieldTypeType,
    TaskTemplateStatusType,
    TimerEligibleParticipantRolesType,
    TrafficDistributionGroupStatusType,
    TrafficTypeType,
    UnitType,
    UseCaseTypeType,
    ViewStatusType,
    ViewTypeType,
    VocabularyLanguageCodeType,
    VocabularyStateType,
    VoiceRecordingTrackType,
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
    "ActionSummaryTypeDef",
    "ActivateEvaluationFormRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "DistributionTypeDef",
    "QueueReferenceTypeDef",
    "AgentInfoTypeDef",
    "AgentStatusReferenceTypeDef",
    "AgentStatusSummaryTypeDef",
    "AgentStatusTypeDef",
    "AnswerMachineDetectionConfigTypeDef",
    "AssociateApprovedOriginRequestRequestTypeDef",
    "LexBotTypeDef",
    "LexV2BotTypeDef",
    "AssociateDefaultVocabularyRequestRequestTypeDef",
    "AssociateLambdaFunctionRequestRequestTypeDef",
    "AssociatePhoneNumberContactFlowRequestRequestTypeDef",
    "AssociateQueueQuickConnectsRequestRequestTypeDef",
    "AssociateSecurityKeyRequestRequestTypeDef",
    "AssociateTrafficDistributionGroupUserRequestRequestTypeDef",
    "AttachmentReferenceTypeDef",
    "AttributeTypeDef",
    "AvailableNumberSummaryTypeDef",
    "ChatMessageTypeDef",
    "ChatStreamingConfigurationTypeDef",
    "ClaimPhoneNumberRequestRequestTypeDef",
    "PhoneNumberStatusTypeDef",
    "ContactFilterTypeDef",
    "ContactFlowModuleSummaryTypeDef",
    "ContactFlowModuleTypeDef",
    "ContactFlowSummaryTypeDef",
    "ContactFlowTypeDef",
    "QueueInfoTypeDef",
    "WisdomInfoTypeDef",
    "TagConditionTypeDef",
    "CreateAgentStatusRequestRequestTypeDef",
    "CreateContactFlowModuleRequestRequestTypeDef",
    "CreateContactFlowRequestRequestTypeDef",
    "EvaluationFormScoringStrategyTypeDef",
    "CreateInstanceRequestRequestTypeDef",
    "CreateIntegrationAssociationRequestRequestTypeDef",
    "ParticipantDetailsToAddTypeDef",
    "ParticipantTokenCredentialsTypeDef",
    "CreatePromptRequestRequestTypeDef",
    "OutboundCallerConfigTypeDef",
    "RuleTriggerEventSourceTypeDef",
    "CreateSecurityProfileRequestRequestTypeDef",
    "CreateTrafficDistributionGroupRequestRequestTypeDef",
    "CreateUseCaseRequestRequestTypeDef",
    "CreateUserHierarchyGroupRequestRequestTypeDef",
    "UserIdentityInfoTypeDef",
    "UserPhoneConfigTypeDef",
    "ViewInputContentTypeDef",
    "CreateViewVersionRequestRequestTypeDef",
    "CreateVocabularyRequestRequestTypeDef",
    "CredentialsTypeDef",
    "CrossChannelBehaviorTypeDef",
    "CurrentMetricTypeDef",
    "CurrentMetricSortCriteriaTypeDef",
    "DateReferenceTypeDef",
    "DeactivateEvaluationFormRequestRequestTypeDef",
    "DefaultVocabularyTypeDef",
    "DeleteContactEvaluationRequestRequestTypeDef",
    "DeleteContactFlowModuleRequestRequestTypeDef",
    "DeleteContactFlowRequestRequestTypeDef",
    "DeleteEvaluationFormRequestRequestTypeDef",
    "DeleteHoursOfOperationRequestRequestTypeDef",
    "DeleteInstanceRequestRequestTypeDef",
    "DeleteIntegrationAssociationRequestRequestTypeDef",
    "DeletePromptRequestRequestTypeDef",
    "DeleteQueueRequestRequestTypeDef",
    "DeleteQuickConnectRequestRequestTypeDef",
    "DeleteRoutingProfileRequestRequestTypeDef",
    "DeleteRuleRequestRequestTypeDef",
    "DeleteSecurityProfileRequestRequestTypeDef",
    "DeleteTaskTemplateRequestRequestTypeDef",
    "DeleteTrafficDistributionGroupRequestRequestTypeDef",
    "DeleteUseCaseRequestRequestTypeDef",
    "DeleteUserHierarchyGroupRequestRequestTypeDef",
    "DeleteUserRequestRequestTypeDef",
    "DeleteViewRequestRequestTypeDef",
    "DeleteViewVersionRequestRequestTypeDef",
    "DeleteVocabularyRequestRequestTypeDef",
    "DescribeAgentStatusRequestRequestTypeDef",
    "DescribeContactEvaluationRequestRequestTypeDef",
    "DescribeContactFlowModuleRequestRequestTypeDef",
    "DescribeContactFlowRequestRequestTypeDef",
    "DescribeContactRequestRequestTypeDef",
    "DescribeEvaluationFormRequestRequestTypeDef",
    "DescribeHoursOfOperationRequestRequestTypeDef",
    "DescribeInstanceAttributeRequestRequestTypeDef",
    "DescribeInstanceRequestRequestTypeDef",
    "DescribeInstanceStorageConfigRequestRequestTypeDef",
    "DescribePhoneNumberRequestRequestTypeDef",
    "DescribePromptRequestRequestTypeDef",
    "PromptTypeDef",
    "DescribeQueueRequestRequestTypeDef",
    "DescribeQuickConnectRequestRequestTypeDef",
    "DescribeRoutingProfileRequestRequestTypeDef",
    "DescribeRuleRequestRequestTypeDef",
    "DescribeSecurityProfileRequestRequestTypeDef",
    "SecurityProfileTypeDef",
    "DescribeTrafficDistributionGroupRequestRequestTypeDef",
    "TrafficDistributionGroupTypeDef",
    "DescribeUserHierarchyGroupRequestRequestTypeDef",
    "DescribeUserHierarchyStructureRequestRequestTypeDef",
    "DescribeUserRequestRequestTypeDef",
    "DescribeViewRequestRequestTypeDef",
    "DescribeVocabularyRequestRequestTypeDef",
    "VocabularyTypeDef",
    "RoutingProfileReferenceTypeDef",
    "DisassociateApprovedOriginRequestRequestTypeDef",
    "DisassociateInstanceStorageConfigRequestRequestTypeDef",
    "DisassociateLambdaFunctionRequestRequestTypeDef",
    "DisassociateLexBotRequestRequestTypeDef",
    "DisassociatePhoneNumberContactFlowRequestRequestTypeDef",
    "DisassociateQueueQuickConnectsRequestRequestTypeDef",
    "RoutingProfileQueueReferenceTypeDef",
    "DisassociateSecurityKeyRequestRequestTypeDef",
    "DisassociateTrafficDistributionGroupUserRequestRequestTypeDef",
    "DismissUserContactRequestRequestTypeDef",
    "EmailReferenceTypeDef",
    "EncryptionConfigTypeDef",
    "EvaluationAnswerDataTypeDef",
    "NumericQuestionPropertyValueAutomationTypeDef",
    "EvaluationFormNumericQuestionOptionTypeDef",
    "EvaluationFormSectionTypeDef",
    "SingleSelectQuestionRuleCategoryAutomationTypeDef",
    "EvaluationFormSingleSelectQuestionOptionTypeDef",
    "EvaluationFormSummaryTypeDef",
    "EvaluationFormVersionSummaryTypeDef",
    "EvaluationScoreTypeDef",
    "EvaluationNoteTypeDef",
    "EventBridgeActionDefinitionTypeDef",
    "FilterV2TypeDef",
    "FiltersTypeDef",
    "GetContactAttributesRequestRequestTypeDef",
    "GetFederationTokenRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "TimestampTypeDef",
    "GetPromptFileRequestRequestTypeDef",
    "GetTaskTemplateRequestRequestTypeDef",
    "GetTrafficDistributionRequestRequestTypeDef",
    "HierarchyGroupConditionTypeDef",
    "HierarchyGroupSummaryReferenceTypeDef",
    "HierarchyGroupSummaryTypeDef",
    "HierarchyLevelTypeDef",
    "HierarchyLevelUpdateTypeDef",
    "ThresholdTypeDef",
    "HoursOfOperationTimeSliceTypeDef",
    "StringConditionTypeDef",
    "HoursOfOperationSummaryTypeDef",
    "InstanceStatusReasonTypeDef",
    "KinesisFirehoseConfigTypeDef",
    "KinesisStreamConfigTypeDef",
    "InstanceSummaryTypeDef",
    "IntegrationAssociationSummaryTypeDef",
    "TaskTemplateFieldIdentifierTypeDef",
    "ListAgentStatusRequestRequestTypeDef",
    "ListApprovedOriginsRequestRequestTypeDef",
    "ListBotsRequestRequestTypeDef",
    "ListContactEvaluationsRequestRequestTypeDef",
    "ListContactFlowModulesRequestRequestTypeDef",
    "ListContactFlowsRequestRequestTypeDef",
    "ListContactReferencesRequestRequestTypeDef",
    "ListDefaultVocabulariesRequestRequestTypeDef",
    "ListEvaluationFormVersionsRequestRequestTypeDef",
    "ListEvaluationFormsRequestRequestTypeDef",
    "ListHoursOfOperationsRequestRequestTypeDef",
    "ListInstanceAttributesRequestRequestTypeDef",
    "ListInstanceStorageConfigsRequestRequestTypeDef",
    "ListInstancesRequestRequestTypeDef",
    "ListIntegrationAssociationsRequestRequestTypeDef",
    "ListLambdaFunctionsRequestRequestTypeDef",
    "ListLexBotsRequestRequestTypeDef",
    "ListPhoneNumbersRequestRequestTypeDef",
    "PhoneNumberSummaryTypeDef",
    "ListPhoneNumbersSummaryTypeDef",
    "ListPhoneNumbersV2RequestRequestTypeDef",
    "ListPromptsRequestRequestTypeDef",
    "PromptSummaryTypeDef",
    "ListQueueQuickConnectsRequestRequestTypeDef",
    "QuickConnectSummaryTypeDef",
    "ListQueuesRequestRequestTypeDef",
    "QueueSummaryTypeDef",
    "ListQuickConnectsRequestRequestTypeDef",
    "ListRoutingProfileQueuesRequestRequestTypeDef",
    "RoutingProfileQueueConfigSummaryTypeDef",
    "ListRoutingProfilesRequestRequestTypeDef",
    "RoutingProfileSummaryTypeDef",
    "ListRulesRequestRequestTypeDef",
    "ListSecurityKeysRequestRequestTypeDef",
    "SecurityKeyTypeDef",
    "ListSecurityProfilePermissionsRequestRequestTypeDef",
    "ListSecurityProfilesRequestRequestTypeDef",
    "SecurityProfileSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTaskTemplatesRequestRequestTypeDef",
    "TaskTemplateMetadataTypeDef",
    "ListTrafficDistributionGroupUsersRequestRequestTypeDef",
    "TrafficDistributionGroupUserSummaryTypeDef",
    "ListTrafficDistributionGroupsRequestRequestTypeDef",
    "TrafficDistributionGroupSummaryTypeDef",
    "ListUseCasesRequestRequestTypeDef",
    "UseCaseTypeDef",
    "ListUserHierarchyGroupsRequestRequestTypeDef",
    "ListUsersRequestRequestTypeDef",
    "UserSummaryTypeDef",
    "ListViewVersionsRequestRequestTypeDef",
    "ViewVersionSummaryTypeDef",
    "ListViewsRequestRequestTypeDef",
    "ViewSummaryTypeDef",
    "MetricFilterV2TypeDef",
    "ThresholdV2TypeDef",
    "MonitorContactRequestRequestTypeDef",
    "NotificationRecipientTypeTypeDef",
    "NumberReferenceTypeDef",
    "ParticipantDetailsTypeDef",
    "ParticipantTimerValueTypeDef",
    "PersistentChatTypeDef",
    "PhoneNumberQuickConnectConfigTypeDef",
    "PutUserStatusRequestRequestTypeDef",
    "QueueQuickConnectConfigTypeDef",
    "UserQuickConnectConfigTypeDef",
    "StringReferenceTypeDef",
    "UrlReferenceTypeDef",
    "ReferenceTypeDef",
    "ReleasePhoneNumberRequestRequestTypeDef",
    "ReplicateInstanceRequestRequestTypeDef",
    "TagSearchConditionTypeDef",
    "ResumeContactRecordingRequestRequestTypeDef",
    "SearchAvailablePhoneNumbersRequestRequestTypeDef",
    "TagSetTypeDef",
    "SecurityProfileSearchSummaryTypeDef",
    "SearchVocabulariesRequestRequestTypeDef",
    "VocabularySummaryTypeDef",
    "SignInDistributionTypeDef",
    "StartContactEvaluationRequestRequestTypeDef",
    "VoiceRecordingConfigurationTypeDef",
    "StopContactRecordingRequestRequestTypeDef",
    "StopContactRequestRequestTypeDef",
    "StopContactStreamingRequestRequestTypeDef",
    "SuspendContactRecordingRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TransferContactRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAgentStatusRequestRequestTypeDef",
    "UpdateContactAttributesRequestRequestTypeDef",
    "UpdateContactFlowContentRequestRequestTypeDef",
    "UpdateContactFlowMetadataRequestRequestTypeDef",
    "UpdateContactFlowModuleContentRequestRequestTypeDef",
    "UpdateContactFlowModuleMetadataRequestRequestTypeDef",
    "UpdateContactFlowNameRequestRequestTypeDef",
    "UpdateInstanceAttributeRequestRequestTypeDef",
    "UpdatePhoneNumberRequestRequestTypeDef",
    "UpdatePromptRequestRequestTypeDef",
    "UpdateQueueHoursOfOperationRequestRequestTypeDef",
    "UpdateQueueMaxContactsRequestRequestTypeDef",
    "UpdateQueueNameRequestRequestTypeDef",
    "UpdateQueueStatusRequestRequestTypeDef",
    "UpdateQuickConnectNameRequestRequestTypeDef",
    "UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef",
    "UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef",
    "UpdateRoutingProfileNameRequestRequestTypeDef",
    "UpdateSecurityProfileRequestRequestTypeDef",
    "UpdateUserHierarchyGroupNameRequestRequestTypeDef",
    "UpdateUserHierarchyRequestRequestTypeDef",
    "UpdateUserRoutingProfileRequestRequestTypeDef",
    "UpdateUserSecurityProfilesRequestRequestTypeDef",
    "UpdateViewMetadataRequestRequestTypeDef",
    "UserReferenceTypeDef",
    "UserIdentityInfoLiteTypeDef",
    "ViewContentTypeDef",
    "RuleSummaryTypeDef",
    "ActivateEvaluationFormResponseTypeDef",
    "AssociateInstanceStorageConfigResponseTypeDef",
    "AssociateSecurityKeyResponseTypeDef",
    "ClaimPhoneNumberResponseTypeDef",
    "CreateAgentStatusResponseTypeDef",
    "CreateContactFlowModuleResponseTypeDef",
    "CreateContactFlowResponseTypeDef",
    "CreateEvaluationFormResponseTypeDef",
    "CreateHoursOfOperationResponseTypeDef",
    "CreateInstanceResponseTypeDef",
    "CreateIntegrationAssociationResponseTypeDef",
    "CreatePromptResponseTypeDef",
    "CreateQueueResponseTypeDef",
    "CreateQuickConnectResponseTypeDef",
    "CreateRoutingProfileResponseTypeDef",
    "CreateRuleResponseTypeDef",
    "CreateSecurityProfileResponseTypeDef",
    "CreateTaskTemplateResponseTypeDef",
    "CreateTrafficDistributionGroupResponseTypeDef",
    "CreateUseCaseResponseTypeDef",
    "CreateUserHierarchyGroupResponseTypeDef",
    "CreateUserResponseTypeDef",
    "CreateVocabularyResponseTypeDef",
    "DeactivateEvaluationFormResponseTypeDef",
    "DeleteVocabularyResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetContactAttributesResponseTypeDef",
    "GetPromptFileResponseTypeDef",
    "ListApprovedOriginsResponseTypeDef",
    "ListLambdaFunctionsResponseTypeDef",
    "ListSecurityProfilePermissionsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "MonitorContactResponseTypeDef",
    "ReplicateInstanceResponseTypeDef",
    "StartChatContactResponseTypeDef",
    "StartContactEvaluationResponseTypeDef",
    "StartContactStreamingResponseTypeDef",
    "StartOutboundVoiceContactResponseTypeDef",
    "StartTaskContactResponseTypeDef",
    "SubmitContactEvaluationResponseTypeDef",
    "TransferContactResponseTypeDef",
    "UpdateContactEvaluationResponseTypeDef",
    "UpdateEvaluationFormResponseTypeDef",
    "UpdatePhoneNumberResponseTypeDef",
    "UpdatePromptResponseTypeDef",
    "AgentConfigTypeDef",
    "TelephonyConfigTypeDef",
    "AgentContactReferenceTypeDef",
    "ListAgentStatusResponseTypeDef",
    "DescribeAgentStatusResponseTypeDef",
    "StartOutboundVoiceContactRequestRequestTypeDef",
    "AssociateLexBotRequestRequestTypeDef",
    "ListLexBotsResponseTypeDef",
    "AssociateBotRequestRequestTypeDef",
    "DisassociateBotRequestRequestTypeDef",
    "LexBotConfigTypeDef",
    "DescribeInstanceAttributeResponseTypeDef",
    "ListInstanceAttributesResponseTypeDef",
    "SearchAvailablePhoneNumbersResponseTypeDef",
    "StartContactStreamingRequestRequestTypeDef",
    "ClaimedPhoneNumberSummaryTypeDef",
    "UserDataFiltersTypeDef",
    "ListContactFlowModulesResponseTypeDef",
    "DescribeContactFlowModuleResponseTypeDef",
    "ListContactFlowsResponseTypeDef",
    "DescribeContactFlowResponseTypeDef",
    "ContactTypeDef",
    "ControlPlaneTagFilterTypeDef",
    "CreateEvaluationFormRequestRequestTypeDef",
    "EvaluationFormContentTypeDef",
    "EvaluationFormTypeDef",
    "UpdateEvaluationFormRequestRequestTypeDef",
    "CreateParticipantRequestRequestTypeDef",
    "CreateParticipantResponseTypeDef",
    "CreateQueueRequestRequestTypeDef",
    "QueueTypeDef",
    "UpdateQueueOutboundCallerConfigRequestRequestTypeDef",
    "UpdateUserIdentityInfoRequestRequestTypeDef",
    "CreateUserRequestRequestTypeDef",
    "UpdateUserPhoneConfigRequestRequestTypeDef",
    "UserTypeDef",
    "CreateViewRequestRequestTypeDef",
    "UpdateViewContentRequestRequestTypeDef",
    "GetFederationTokenResponseTypeDef",
    "MediaConcurrencyTypeDef",
    "CurrentMetricDataTypeDef",
    "ListDefaultVocabulariesResponseTypeDef",
    "DescribePromptResponseTypeDef",
    "SearchPromptsResponseTypeDef",
    "DescribeSecurityProfileResponseTypeDef",
    "DescribeTrafficDistributionGroupResponseTypeDef",
    "DescribeVocabularyResponseTypeDef",
    "DimensionsTypeDef",
    "DisassociateRoutingProfileQueuesRequestRequestTypeDef",
    "RoutingProfileQueueConfigTypeDef",
    "KinesisVideoStreamConfigTypeDef",
    "S3ConfigTypeDef",
    "EvaluationAnswerInputTypeDef",
    "EvaluationAnswerOutputTypeDef",
    "EvaluationFormNumericQuestionAutomationTypeDef",
    "EvaluationFormSingleSelectQuestionAutomationOptionTypeDef",
    "ListEvaluationFormsResponseTypeDef",
    "ListEvaluationFormVersionsResponseTypeDef",
    "EvaluationMetadataTypeDef",
    "EvaluationSummaryTypeDef",
    "GetCurrentMetricDataRequestRequestTypeDef",
    "ListAgentStatusRequestListAgentStatusesPaginateTypeDef",
    "ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef",
    "ListBotsRequestListBotsPaginateTypeDef",
    "ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef",
    "ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef",
    "ListContactFlowsRequestListContactFlowsPaginateTypeDef",
    "ListContactReferencesRequestListContactReferencesPaginateTypeDef",
    "ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef",
    "ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef",
    "ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef",
    "ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef",
    "ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef",
    "ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef",
    "ListInstancesRequestListInstancesPaginateTypeDef",
    "ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef",
    "ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef",
    "ListLexBotsRequestListLexBotsPaginateTypeDef",
    "ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef",
    "ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef",
    "ListPromptsRequestListPromptsPaginateTypeDef",
    "ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef",
    "ListQueuesRequestListQueuesPaginateTypeDef",
    "ListQuickConnectsRequestListQuickConnectsPaginateTypeDef",
    "ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef",
    "ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef",
    "ListRulesRequestListRulesPaginateTypeDef",
    "ListSecurityKeysRequestListSecurityKeysPaginateTypeDef",
    "ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef",
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    "ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef",
    "ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef",
    "ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef",
    "ListUseCasesRequestListUseCasesPaginateTypeDef",
    "ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef",
    "ListUsersRequestListUsersPaginateTypeDef",
    "ListViewVersionsRequestListViewVersionsPaginateTypeDef",
    "ListViewsRequestListViewsPaginateTypeDef",
    "SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef",
    "SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef",
    "UpdateContactScheduleRequestRequestTypeDef",
    "HierarchyPathReferenceTypeDef",
    "HierarchyPathTypeDef",
    "ListUserHierarchyGroupsResponseTypeDef",
    "HierarchyStructureTypeDef",
    "HierarchyStructureUpdateTypeDef",
    "HistoricalMetricTypeDef",
    "HoursOfOperationConfigTypeDef",
    "HoursOfOperationSearchCriteriaTypeDef",
    "PromptSearchCriteriaTypeDef",
    "QueueSearchCriteriaTypeDef",
    "QuickConnectSearchCriteriaTypeDef",
    "RoutingProfileSearchCriteriaTypeDef",
    "SecurityProfileSearchCriteriaTypeDef",
    "UserSearchCriteriaTypeDef",
    "ListHoursOfOperationsResponseTypeDef",
    "InstanceTypeDef",
    "ListInstancesResponseTypeDef",
    "ListIntegrationAssociationsResponseTypeDef",
    "InvisibleFieldInfoTypeDef",
    "ReadOnlyFieldInfoTypeDef",
    "RequiredFieldInfoTypeDef",
    "TaskTemplateDefaultFieldValueTypeDef",
    "TaskTemplateFieldTypeDef",
    "ListPhoneNumbersResponseTypeDef",
    "ListPhoneNumbersV2ResponseTypeDef",
    "ListPromptsResponseTypeDef",
    "ListQueueQuickConnectsResponseTypeDef",
    "ListQuickConnectsResponseTypeDef",
    "ListQueuesResponseTypeDef",
    "ListRoutingProfileQueuesResponseTypeDef",
    "ListRoutingProfilesResponseTypeDef",
    "ListSecurityKeysResponseTypeDef",
    "ListSecurityProfilesResponseTypeDef",
    "ListTaskTemplatesResponseTypeDef",
    "ListTrafficDistributionGroupUsersResponseTypeDef",
    "ListTrafficDistributionGroupsResponseTypeDef",
    "ListUseCasesResponseTypeDef",
    "ListUsersResponseTypeDef",
    "ListViewVersionsResponseTypeDef",
    "ListViewsResponseTypeDef",
    "MetricV2TypeDef",
    "SendNotificationActionDefinitionTypeDef",
    "ParticipantTimerConfigurationTypeDef",
    "StartChatContactRequestRequestTypeDef",
    "QuickConnectConfigTypeDef",
    "ReferenceSummaryTypeDef",
    "StartTaskContactRequestRequestTypeDef",
    "TaskActionDefinitionTypeDef",
    "UpdateContactRequestRequestTypeDef",
    "ResourceTagsSearchCriteriaTypeDef",
    "SearchResourceTagsResponseTypeDef",
    "SearchSecurityProfilesResponseTypeDef",
    "SearchVocabulariesResponseTypeDef",
    "SignInConfigTypeDef",
    "StartContactRecordingRequestRequestTypeDef",
    "UserSearchSummaryTypeDef",
    "ViewTypeDef",
    "ListRulesResponseTypeDef",
    "ListBotsResponseTypeDef",
    "DescribePhoneNumberResponseTypeDef",
    "GetCurrentUserDataRequestRequestTypeDef",
    "DescribeContactResponseTypeDef",
    "HoursOfOperationSearchFilterTypeDef",
    "PromptSearchFilterTypeDef",
    "QueueSearchFilterTypeDef",
    "QuickConnectSearchFilterTypeDef",
    "RoutingProfileSearchFilterTypeDef",
    "SecurityProfilesSearchFilterTypeDef",
    "UserSearchFilterTypeDef",
    "DescribeEvaluationFormResponseTypeDef",
    "DescribeQueueResponseTypeDef",
    "SearchQueuesResponseTypeDef",
    "DescribeUserResponseTypeDef",
    "RoutingProfileTypeDef",
    "UpdateRoutingProfileConcurrencyRequestRequestTypeDef",
    "CurrentMetricResultTypeDef",
    "AssociateRoutingProfileQueuesRequestRequestTypeDef",
    "CreateRoutingProfileRequestRequestTypeDef",
    "UpdateRoutingProfileQueuesRequestRequestTypeDef",
    "InstanceStorageConfigTypeDef",
    "SubmitContactEvaluationRequestRequestTypeDef",
    "UpdateContactEvaluationRequestRequestTypeDef",
    "EvaluationFormNumericQuestionPropertiesTypeDef",
    "EvaluationFormSingleSelectQuestionAutomationTypeDef",
    "EvaluationTypeDef",
    "ListContactEvaluationsResponseTypeDef",
    "UserDataTypeDef",
    "HierarchyGroupTypeDef",
    "DescribeUserHierarchyStructureResponseTypeDef",
    "UpdateUserHierarchyStructureRequestRequestTypeDef",
    "GetMetricDataRequestGetMetricDataPaginateTypeDef",
    "GetMetricDataRequestRequestTypeDef",
    "HistoricalMetricDataTypeDef",
    "CreateHoursOfOperationRequestRequestTypeDef",
    "HoursOfOperationTypeDef",
    "UpdateHoursOfOperationRequestRequestTypeDef",
    "DescribeInstanceResponseTypeDef",
    "TaskTemplateConstraintsTypeDef",
    "TaskTemplateDefaultsTypeDef",
    "GetMetricDataV2RequestRequestTypeDef",
    "MetricDataV2TypeDef",
    "ChatParticipantRoleConfigTypeDef",
    "CreateQuickConnectRequestRequestTypeDef",
    "QuickConnectTypeDef",
    "UpdateQuickConnectConfigRequestRequestTypeDef",
    "ListContactReferencesResponseTypeDef",
    "RuleActionTypeDef",
    "SearchResourceTagsRequestRequestTypeDef",
    "SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef",
    "GetTrafficDistributionResponseTypeDef",
    "UpdateTrafficDistributionRequestRequestTypeDef",
    "SearchUsersResponseTypeDef",
    "CreateViewResponseTypeDef",
    "CreateViewVersionResponseTypeDef",
    "DescribeViewResponseTypeDef",
    "UpdateViewContentResponseTypeDef",
    "SearchHoursOfOperationsRequestRequestTypeDef",
    "SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef",
    "SearchPromptsRequestRequestTypeDef",
    "SearchPromptsRequestSearchPromptsPaginateTypeDef",
    "SearchQueuesRequestRequestTypeDef",
    "SearchQueuesRequestSearchQueuesPaginateTypeDef",
    "SearchQuickConnectsRequestRequestTypeDef",
    "SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef",
    "SearchRoutingProfilesRequestRequestTypeDef",
    "SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef",
    "SearchSecurityProfilesRequestRequestTypeDef",
    "SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef",
    "SearchUsersRequestRequestTypeDef",
    "SearchUsersRequestSearchUsersPaginateTypeDef",
    "DescribeRoutingProfileResponseTypeDef",
    "SearchRoutingProfilesResponseTypeDef",
    "GetCurrentMetricDataResponseTypeDef",
    "AssociateInstanceStorageConfigRequestRequestTypeDef",
    "DescribeInstanceStorageConfigResponseTypeDef",
    "ListInstanceStorageConfigsResponseTypeDef",
    "UpdateInstanceStorageConfigRequestRequestTypeDef",
    "EvaluationFormSingleSelectQuestionPropertiesTypeDef",
    "DescribeContactEvaluationResponseTypeDef",
    "GetCurrentUserDataResponseTypeDef",
    "DescribeUserHierarchyGroupResponseTypeDef",
    "HistoricalMetricResultTypeDef",
    "DescribeHoursOfOperationResponseTypeDef",
    "SearchHoursOfOperationsResponseTypeDef",
    "CreateTaskTemplateRequestRequestTypeDef",
    "GetTaskTemplateResponseTypeDef",
    "UpdateTaskTemplateRequestRequestTypeDef",
    "UpdateTaskTemplateResponseTypeDef",
    "MetricResultV2TypeDef",
    "UpdateParticipantRoleConfigChannelInfoTypeDef",
    "DescribeQuickConnectResponseTypeDef",
    "SearchQuickConnectsResponseTypeDef",
    "CreateRuleRequestRequestTypeDef",
    "RuleTypeDef",
    "UpdateRuleRequestRequestTypeDef",
    "EvaluationFormQuestionTypePropertiesTypeDef",
    "GetMetricDataResponseTypeDef",
    "GetMetricDataV2ResponseTypeDef",
    "UpdateParticipantRoleConfigRequestRequestTypeDef",
    "DescribeRuleResponseTypeDef",
    "EvaluationFormQuestionTypeDef",
    "EvaluationFormItemTypeDef",
)

ActionSummaryTypeDef = TypedDict(
    "ActionSummaryTypeDef",
    {
        "ActionType": ActionTypeType,
    },
)

ActivateEvaluationFormRequestRequestTypeDef = TypedDict(
    "ActivateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
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

DistributionTypeDef = TypedDict(
    "DistributionTypeDef",
    {
        "Region": str,
        "Percentage": int,
    },
)

QueueReferenceTypeDef = TypedDict(
    "QueueReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)

AgentInfoTypeDef = TypedDict(
    "AgentInfoTypeDef",
    {
        "Id": NotRequired[str],
        "ConnectedToAgentTimestamp": NotRequired[datetime],
    },
)

AgentStatusReferenceTypeDef = TypedDict(
    "AgentStatusReferenceTypeDef",
    {
        "StatusStartTimestamp": NotRequired[datetime],
        "StatusArn": NotRequired[str],
        "StatusName": NotRequired[str],
    },
)

AgentStatusSummaryTypeDef = TypedDict(
    "AgentStatusSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[AgentStatusTypeType],
    },
)

AgentStatusTypeDef = TypedDict(
    "AgentStatusTypeDef",
    {
        "AgentStatusARN": NotRequired[str],
        "AgentStatusId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Type": NotRequired[AgentStatusTypeType],
        "DisplayOrder": NotRequired[int],
        "State": NotRequired[AgentStatusStateType],
        "Tags": NotRequired[Dict[str, str]],
    },
)

AnswerMachineDetectionConfigTypeDef = TypedDict(
    "AnswerMachineDetectionConfigTypeDef",
    {
        "EnableAnswerMachineDetection": NotRequired[bool],
        "AwaitAnswerMachinePrompt": NotRequired[bool],
    },
)

AssociateApprovedOriginRequestRequestTypeDef = TypedDict(
    "AssociateApprovedOriginRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Origin": str,
    },
)

LexBotTypeDef = TypedDict(
    "LexBotTypeDef",
    {
        "Name": str,
        "LexRegion": str,
    },
)

LexV2BotTypeDef = TypedDict(
    "LexV2BotTypeDef",
    {
        "AliasArn": NotRequired[str],
    },
)

AssociateDefaultVocabularyRequestRequestTypeDef = TypedDict(
    "AssociateDefaultVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "VocabularyId": NotRequired[str],
    },
)

AssociateLambdaFunctionRequestRequestTypeDef = TypedDict(
    "AssociateLambdaFunctionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FunctionArn": str,
    },
)

AssociatePhoneNumberContactFlowRequestRequestTypeDef = TypedDict(
    "AssociatePhoneNumberContactFlowRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "InstanceId": str,
        "ContactFlowId": str,
    },
)

AssociateQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "AssociateQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "QuickConnectIds": Sequence[str],
    },
)

AssociateSecurityKeyRequestRequestTypeDef = TypedDict(
    "AssociateSecurityKeyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Key": str,
    },
)

AssociateTrafficDistributionGroupUserRequestRequestTypeDef = TypedDict(
    "AssociateTrafficDistributionGroupUserRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "UserId": str,
        "InstanceId": str,
    },
)

AttachmentReferenceTypeDef = TypedDict(
    "AttachmentReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
        "Status": NotRequired[ReferenceStatusType],
    },
)

AttributeTypeDef = TypedDict(
    "AttributeTypeDef",
    {
        "AttributeType": NotRequired[InstanceAttributeTypeType],
        "Value": NotRequired[str],
    },
)

AvailableNumberSummaryTypeDef = TypedDict(
    "AvailableNumberSummaryTypeDef",
    {
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
    },
)

ChatMessageTypeDef = TypedDict(
    "ChatMessageTypeDef",
    {
        "ContentType": str,
        "Content": str,
    },
)

ChatStreamingConfigurationTypeDef = TypedDict(
    "ChatStreamingConfigurationTypeDef",
    {
        "StreamingEndpointArn": str,
    },
)

ClaimPhoneNumberRequestRequestTypeDef = TypedDict(
    "ClaimPhoneNumberRequestRequestTypeDef",
    {
        "TargetArn": str,
        "PhoneNumber": str,
        "PhoneNumberDescription": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
    },
)

PhoneNumberStatusTypeDef = TypedDict(
    "PhoneNumberStatusTypeDef",
    {
        "Status": NotRequired[PhoneNumberWorkflowStatusType],
        "Message": NotRequired[str],
    },
)

ContactFilterTypeDef = TypedDict(
    "ContactFilterTypeDef",
    {
        "ContactStates": NotRequired[Sequence[ContactStateType]],
    },
)

ContactFlowModuleSummaryTypeDef = TypedDict(
    "ContactFlowModuleSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
    },
)

ContactFlowModuleTypeDef = TypedDict(
    "ContactFlowModuleTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Content": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
        "Status": NotRequired[ContactFlowModuleStatusType],
        "Tags": NotRequired[Dict[str, str]],
    },
)

ContactFlowSummaryTypeDef = TypedDict(
    "ContactFlowSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "ContactFlowType": NotRequired[ContactFlowTypeType],
        "ContactFlowState": NotRequired[ContactFlowStateType],
    },
)

ContactFlowTypeDef = TypedDict(
    "ContactFlowTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ContactFlowTypeType],
        "State": NotRequired[ContactFlowStateType],
        "Description": NotRequired[str],
        "Content": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)

QueueInfoTypeDef = TypedDict(
    "QueueInfoTypeDef",
    {
        "Id": NotRequired[str],
        "EnqueueTimestamp": NotRequired[datetime],
    },
)

WisdomInfoTypeDef = TypedDict(
    "WisdomInfoTypeDef",
    {
        "SessionArn": NotRequired[str],
    },
)

TagConditionTypeDef = TypedDict(
    "TagConditionTypeDef",
    {
        "TagKey": NotRequired[str],
        "TagValue": NotRequired[str],
    },
)

CreateAgentStatusRequestRequestTypeDef = TypedDict(
    "CreateAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "State": AgentStatusStateType,
        "Description": NotRequired[str],
        "DisplayOrder": NotRequired[int],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

CreateContactFlowModuleRequestRequestTypeDef = TypedDict(
    "CreateContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Content": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
    },
)

CreateContactFlowRequestRequestTypeDef = TypedDict(
    "CreateContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Type": ContactFlowTypeType,
        "Content": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

EvaluationFormScoringStrategyTypeDef = TypedDict(
    "EvaluationFormScoringStrategyTypeDef",
    {
        "Mode": EvaluationFormScoringModeType,
        "Status": EvaluationFormScoringStatusType,
    },
)

CreateInstanceRequestRequestTypeDef = TypedDict(
    "CreateInstanceRequestRequestTypeDef",
    {
        "IdentityManagementType": DirectoryTypeType,
        "InboundCallsEnabled": bool,
        "OutboundCallsEnabled": bool,
        "ClientToken": NotRequired[str],
        "InstanceAlias": NotRequired[str],
        "DirectoryId": NotRequired[str],
    },
)

CreateIntegrationAssociationRequestRequestTypeDef = TypedDict(
    "CreateIntegrationAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": IntegrationTypeType,
        "IntegrationArn": str,
        "SourceApplicationUrl": NotRequired[str],
        "SourceApplicationName": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

ParticipantDetailsToAddTypeDef = TypedDict(
    "ParticipantDetailsToAddTypeDef",
    {
        "ParticipantRole": NotRequired[ParticipantRoleType],
        "DisplayName": NotRequired[str],
    },
)

ParticipantTokenCredentialsTypeDef = TypedDict(
    "ParticipantTokenCredentialsTypeDef",
    {
        "ParticipantToken": NotRequired[str],
        "Expiry": NotRequired[str],
    },
)

CreatePromptRequestRequestTypeDef = TypedDict(
    "CreatePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "S3Uri": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

OutboundCallerConfigTypeDef = TypedDict(
    "OutboundCallerConfigTypeDef",
    {
        "OutboundCallerIdName": NotRequired[str],
        "OutboundCallerIdNumberId": NotRequired[str],
        "OutboundFlowId": NotRequired[str],
    },
)

RuleTriggerEventSourceTypeDef = TypedDict(
    "RuleTriggerEventSourceTypeDef",
    {
        "EventSourceName": EventSourceNameType,
        "IntegrationAssociationId": NotRequired[str],
    },
)

CreateSecurityProfileRequestRequestTypeDef = TypedDict(
    "CreateSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileName": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "Permissions": NotRequired[Sequence[str]],
        "Tags": NotRequired[Mapping[str, str]],
        "AllowedAccessControlTags": NotRequired[Mapping[str, str]],
        "TagRestrictedResources": NotRequired[Sequence[str]],
    },
)

CreateTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "CreateTrafficDistributionGroupRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

CreateUseCaseRequestRequestTypeDef = TypedDict(
    "CreateUseCaseRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "UseCaseType": UseCaseTypeType,
        "Tags": NotRequired[Mapping[str, str]],
    },
)

CreateUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "CreateUserHierarchyGroupRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceId": str,
        "ParentGroupId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

UserIdentityInfoTypeDef = TypedDict(
    "UserIdentityInfoTypeDef",
    {
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
        "Email": NotRequired[str],
        "SecondaryEmail": NotRequired[str],
        "Mobile": NotRequired[str],
    },
)

UserPhoneConfigTypeDef = TypedDict(
    "UserPhoneConfigTypeDef",
    {
        "PhoneType": PhoneTypeType,
        "AutoAccept": NotRequired[bool],
        "AfterContactWorkTimeLimit": NotRequired[int],
        "DeskPhoneNumber": NotRequired[str],
    },
)

ViewInputContentTypeDef = TypedDict(
    "ViewInputContentTypeDef",
    {
        "Template": NotRequired[str],
        "Actions": NotRequired[Sequence[str]],
    },
)

CreateViewVersionRequestRequestTypeDef = TypedDict(
    "CreateViewVersionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "VersionDescription": NotRequired[str],
        "ViewContentSha256": NotRequired[str],
    },
)

CreateVocabularyRequestRequestTypeDef = TypedDict(
    "CreateVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyName": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "Content": str,
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

CredentialsTypeDef = TypedDict(
    "CredentialsTypeDef",
    {
        "AccessToken": NotRequired[str],
        "AccessTokenExpiration": NotRequired[datetime],
        "RefreshToken": NotRequired[str],
        "RefreshTokenExpiration": NotRequired[datetime],
    },
)

CrossChannelBehaviorTypeDef = TypedDict(
    "CrossChannelBehaviorTypeDef",
    {
        "BehaviorType": BehaviorTypeType,
    },
)

CurrentMetricTypeDef = TypedDict(
    "CurrentMetricTypeDef",
    {
        "Name": NotRequired[CurrentMetricNameType],
        "Unit": NotRequired[UnitType],
    },
)

CurrentMetricSortCriteriaTypeDef = TypedDict(
    "CurrentMetricSortCriteriaTypeDef",
    {
        "SortByMetric": NotRequired[CurrentMetricNameType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

DateReferenceTypeDef = TypedDict(
    "DateReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)

DeactivateEvaluationFormRequestRequestTypeDef = TypedDict(
    "DeactivateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
    },
)

DefaultVocabularyTypeDef = TypedDict(
    "DefaultVocabularyTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "VocabularyId": str,
        "VocabularyName": str,
    },
)

DeleteContactEvaluationRequestRequestTypeDef = TypedDict(
    "DeleteContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
    },
)

DeleteContactFlowModuleRequestRequestTypeDef = TypedDict(
    "DeleteContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
    },
)

DeleteContactFlowRequestRequestTypeDef = TypedDict(
    "DeleteContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
    },
)

DeleteEvaluationFormRequestRequestTypeDef = TypedDict(
    "DeleteEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": NotRequired[int],
    },
)

DeleteHoursOfOperationRequestRequestTypeDef = TypedDict(
    "DeleteHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
    },
)

DeleteInstanceRequestRequestTypeDef = TypedDict(
    "DeleteInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)

DeleteIntegrationAssociationRequestRequestTypeDef = TypedDict(
    "DeleteIntegrationAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
    },
)

DeletePromptRequestRequestTypeDef = TypedDict(
    "DeletePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)

DeleteQueueRequestRequestTypeDef = TypedDict(
    "DeleteQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
    },
)

DeleteQuickConnectRequestRequestTypeDef = TypedDict(
    "DeleteQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
    },
)

DeleteRoutingProfileRequestRequestTypeDef = TypedDict(
    "DeleteRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
    },
)

DeleteRuleRequestRequestTypeDef = TypedDict(
    "DeleteRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RuleId": str,
    },
)

DeleteSecurityProfileRequestRequestTypeDef = TypedDict(
    "DeleteSecurityProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "SecurityProfileId": str,
    },
)

DeleteTaskTemplateRequestRequestTypeDef = TypedDict(
    "DeleteTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "TaskTemplateId": str,
    },
)

DeleteTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "DeleteTrafficDistributionGroupRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
    },
)

DeleteUseCaseRequestRequestTypeDef = TypedDict(
    "DeleteUseCaseRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "UseCaseId": str,
    },
)

DeleteUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "DeleteUserHierarchyGroupRequestRequestTypeDef",
    {
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)

DeleteUserRequestRequestTypeDef = TypedDict(
    "DeleteUserRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
    },
)

DeleteViewRequestRequestTypeDef = TypedDict(
    "DeleteViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
    },
)

DeleteViewVersionRequestRequestTypeDef = TypedDict(
    "DeleteViewVersionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "ViewVersion": int,
    },
)

DeleteVocabularyRequestRequestTypeDef = TypedDict(
    "DeleteVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyId": str,
    },
)

DescribeAgentStatusRequestRequestTypeDef = TypedDict(
    "DescribeAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AgentStatusId": str,
    },
)

DescribeContactEvaluationRequestRequestTypeDef = TypedDict(
    "DescribeContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
    },
)

DescribeContactFlowModuleRequestRequestTypeDef = TypedDict(
    "DescribeContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
    },
)

DescribeContactFlowRequestRequestTypeDef = TypedDict(
    "DescribeContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
    },
)

DescribeContactRequestRequestTypeDef = TypedDict(
    "DescribeContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
    },
)

DescribeEvaluationFormRequestRequestTypeDef = TypedDict(
    "DescribeEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": NotRequired[int],
    },
)

DescribeHoursOfOperationRequestRequestTypeDef = TypedDict(
    "DescribeHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
    },
)

DescribeInstanceAttributeRequestRequestTypeDef = TypedDict(
    "DescribeInstanceAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AttributeType": InstanceAttributeTypeType,
    },
)

DescribeInstanceRequestRequestTypeDef = TypedDict(
    "DescribeInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)

DescribeInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "DescribeInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
    },
)

DescribePhoneNumberRequestRequestTypeDef = TypedDict(
    "DescribePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
    },
)

DescribePromptRequestRequestTypeDef = TypedDict(
    "DescribePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)

PromptTypeDef = TypedDict(
    "PromptTypeDef",
    {
        "PromptARN": NotRequired[str],
        "PromptId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)

DescribeQueueRequestRequestTypeDef = TypedDict(
    "DescribeQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
    },
)

DescribeQuickConnectRequestRequestTypeDef = TypedDict(
    "DescribeQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
    },
)

DescribeRoutingProfileRequestRequestTypeDef = TypedDict(
    "DescribeRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
    },
)

DescribeRuleRequestRequestTypeDef = TypedDict(
    "DescribeRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RuleId": str,
    },
)

DescribeSecurityProfileRequestRequestTypeDef = TypedDict(
    "DescribeSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
    },
)

SecurityProfileTypeDef = TypedDict(
    "SecurityProfileTypeDef",
    {
        "Id": NotRequired[str],
        "OrganizationResourceId": NotRequired[str],
        "Arn": NotRequired[str],
        "SecurityProfileName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "AllowedAccessControlTags": NotRequired[Dict[str, str]],
        "TagRestrictedResources": NotRequired[List[str]],
    },
)

DescribeTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "DescribeTrafficDistributionGroupRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
    },
)

TrafficDistributionGroupTypeDef = TypedDict(
    "TrafficDistributionGroupTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "InstanceArn": NotRequired[str],
        "Status": NotRequired[TrafficDistributionGroupStatusType],
        "Tags": NotRequired[Dict[str, str]],
        "IsDefault": NotRequired[bool],
    },
)

DescribeUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "DescribeUserHierarchyGroupRequestRequestTypeDef",
    {
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)

DescribeUserHierarchyStructureRequestRequestTypeDef = TypedDict(
    "DescribeUserHierarchyStructureRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)

DescribeUserRequestRequestTypeDef = TypedDict(
    "DescribeUserRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
    },
)

DescribeViewRequestRequestTypeDef = TypedDict(
    "DescribeViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
    },
)

DescribeVocabularyRequestRequestTypeDef = TypedDict(
    "DescribeVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyId": str,
    },
)

VocabularyTypeDef = TypedDict(
    "VocabularyTypeDef",
    {
        "Name": str,
        "Id": str,
        "Arn": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "State": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": NotRequired[str],
        "Content": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)

RoutingProfileReferenceTypeDef = TypedDict(
    "RoutingProfileReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)

DisassociateApprovedOriginRequestRequestTypeDef = TypedDict(
    "DisassociateApprovedOriginRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Origin": str,
    },
)

DisassociateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "DisassociateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
    },
)

DisassociateLambdaFunctionRequestRequestTypeDef = TypedDict(
    "DisassociateLambdaFunctionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FunctionArn": str,
    },
)

DisassociateLexBotRequestRequestTypeDef = TypedDict(
    "DisassociateLexBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "BotName": str,
        "LexRegion": str,
    },
)

DisassociatePhoneNumberContactFlowRequestRequestTypeDef = TypedDict(
    "DisassociatePhoneNumberContactFlowRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "InstanceId": str,
    },
)

DisassociateQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "DisassociateQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "QuickConnectIds": Sequence[str],
    },
)

RoutingProfileQueueReferenceTypeDef = TypedDict(
    "RoutingProfileQueueReferenceTypeDef",
    {
        "QueueId": str,
        "Channel": ChannelType,
    },
)

DisassociateSecurityKeyRequestRequestTypeDef = TypedDict(
    "DisassociateSecurityKeyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
    },
)

DisassociateTrafficDistributionGroupUserRequestRequestTypeDef = TypedDict(
    "DisassociateTrafficDistributionGroupUserRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "UserId": str,
        "InstanceId": str,
    },
)

DismissUserContactRequestRequestTypeDef = TypedDict(
    "DismissUserContactRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "ContactId": str,
    },
)

EmailReferenceTypeDef = TypedDict(
    "EmailReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)

EncryptionConfigTypeDef = TypedDict(
    "EncryptionConfigTypeDef",
    {
        "EncryptionType": Literal["KMS"],
        "KeyId": str,
    },
)

EvaluationAnswerDataTypeDef = TypedDict(
    "EvaluationAnswerDataTypeDef",
    {
        "StringValue": NotRequired[str],
        "NumericValue": NotRequired[float],
        "NotApplicable": NotRequired[bool],
    },
)

NumericQuestionPropertyValueAutomationTypeDef = TypedDict(
    "NumericQuestionPropertyValueAutomationTypeDef",
    {
        "Label": NumericQuestionPropertyAutomationLabelType,
    },
)

EvaluationFormNumericQuestionOptionTypeDef = TypedDict(
    "EvaluationFormNumericQuestionOptionTypeDef",
    {
        "MinValue": int,
        "MaxValue": int,
        "Score": NotRequired[int],
        "AutomaticFail": NotRequired[bool],
    },
)

EvaluationFormSectionTypeDef = TypedDict(
    "EvaluationFormSectionTypeDef",
    {
        "Title": str,
        "RefId": str,
        "Items": Sequence["EvaluationFormItemTypeDef"],
        "Instructions": NotRequired[str],
        "Weight": NotRequired[float],
    },
)

SingleSelectQuestionRuleCategoryAutomationTypeDef = TypedDict(
    "SingleSelectQuestionRuleCategoryAutomationTypeDef",
    {
        "Category": str,
        "Condition": SingleSelectQuestionRuleCategoryAutomationConditionType,
        "OptionRefId": str,
    },
)

EvaluationFormSingleSelectQuestionOptionTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionOptionTypeDef",
    {
        "RefId": str,
        "Text": str,
        "Score": NotRequired[int],
        "AutomaticFail": NotRequired[bool],
    },
)

EvaluationFormSummaryTypeDef = TypedDict(
    "EvaluationFormSummaryTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "Title": str,
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
        "LatestVersion": int,
        "LastActivatedTime": NotRequired[datetime],
        "LastActivatedBy": NotRequired[str],
        "ActiveVersion": NotRequired[int],
    },
)

EvaluationFormVersionSummaryTypeDef = TypedDict(
    "EvaluationFormVersionSummaryTypeDef",
    {
        "EvaluationFormArn": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Locked": bool,
        "Status": EvaluationFormVersionStatusType,
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
    },
)

EvaluationScoreTypeDef = TypedDict(
    "EvaluationScoreTypeDef",
    {
        "Percentage": NotRequired[float],
        "NotApplicable": NotRequired[bool],
        "AutomaticFail": NotRequired[bool],
    },
)

EvaluationNoteTypeDef = TypedDict(
    "EvaluationNoteTypeDef",
    {
        "Value": NotRequired[str],
    },
)

EventBridgeActionDefinitionTypeDef = TypedDict(
    "EventBridgeActionDefinitionTypeDef",
    {
        "Name": str,
    },
)

FilterV2TypeDef = TypedDict(
    "FilterV2TypeDef",
    {
        "FilterKey": NotRequired[str],
        "FilterValues": NotRequired[Sequence[str]],
    },
)

FiltersTypeDef = TypedDict(
    "FiltersTypeDef",
    {
        "Queues": NotRequired[Sequence[str]],
        "Channels": NotRequired[Sequence[ChannelType]],
        "RoutingProfiles": NotRequired[Sequence[str]],
    },
)

GetContactAttributesRequestRequestTypeDef = TypedDict(
    "GetContactAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "InitialContactId": str,
    },
)

GetFederationTokenRequestRequestTypeDef = TypedDict(
    "GetFederationTokenRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)

TimestampTypeDef = Union[datetime, str]
GetPromptFileRequestRequestTypeDef = TypedDict(
    "GetPromptFileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)

GetTaskTemplateRequestRequestTypeDef = TypedDict(
    "GetTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "TaskTemplateId": str,
        "SnapshotVersion": NotRequired[str],
    },
)

GetTrafficDistributionRequestRequestTypeDef = TypedDict(
    "GetTrafficDistributionRequestRequestTypeDef",
    {
        "Id": str,
    },
)

HierarchyGroupConditionTypeDef = TypedDict(
    "HierarchyGroupConditionTypeDef",
    {
        "Value": NotRequired[str],
        "HierarchyGroupMatchType": NotRequired[HierarchyGroupMatchTypeType],
    },
)

HierarchyGroupSummaryReferenceTypeDef = TypedDict(
    "HierarchyGroupSummaryReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)

HierarchyGroupSummaryTypeDef = TypedDict(
    "HierarchyGroupSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

HierarchyLevelTypeDef = TypedDict(
    "HierarchyLevelTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

HierarchyLevelUpdateTypeDef = TypedDict(
    "HierarchyLevelUpdateTypeDef",
    {
        "Name": str,
    },
)

ThresholdTypeDef = TypedDict(
    "ThresholdTypeDef",
    {
        "Comparison": NotRequired[Literal["LT"]],
        "ThresholdValue": NotRequired[float],
    },
)

HoursOfOperationTimeSliceTypeDef = TypedDict(
    "HoursOfOperationTimeSliceTypeDef",
    {
        "Hours": int,
        "Minutes": int,
    },
)

StringConditionTypeDef = TypedDict(
    "StringConditionTypeDef",
    {
        "FieldName": NotRequired[str],
        "Value": NotRequired[str],
        "ComparisonType": NotRequired[StringComparisonTypeType],
    },
)

HoursOfOperationSummaryTypeDef = TypedDict(
    "HoursOfOperationSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

InstanceStatusReasonTypeDef = TypedDict(
    "InstanceStatusReasonTypeDef",
    {
        "Message": NotRequired[str],
    },
)

KinesisFirehoseConfigTypeDef = TypedDict(
    "KinesisFirehoseConfigTypeDef",
    {
        "FirehoseArn": str,
    },
)

KinesisStreamConfigTypeDef = TypedDict(
    "KinesisStreamConfigTypeDef",
    {
        "StreamArn": str,
    },
)

InstanceSummaryTypeDef = TypedDict(
    "InstanceSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "IdentityManagementType": NotRequired[DirectoryTypeType],
        "InstanceAlias": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "ServiceRole": NotRequired[str],
        "InstanceStatus": NotRequired[InstanceStatusType],
        "InboundCallsEnabled": NotRequired[bool],
        "OutboundCallsEnabled": NotRequired[bool],
        "InstanceAccessUrl": NotRequired[str],
    },
)

IntegrationAssociationSummaryTypeDef = TypedDict(
    "IntegrationAssociationSummaryTypeDef",
    {
        "IntegrationAssociationId": NotRequired[str],
        "IntegrationAssociationArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "IntegrationType": NotRequired[IntegrationTypeType],
        "IntegrationArn": NotRequired[str],
        "SourceApplicationUrl": NotRequired[str],
        "SourceApplicationName": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
    },
)

TaskTemplateFieldIdentifierTypeDef = TypedDict(
    "TaskTemplateFieldIdentifierTypeDef",
    {
        "Name": NotRequired[str],
    },
)

ListAgentStatusRequestRequestTypeDef = TypedDict(
    "ListAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "AgentStatusTypes": NotRequired[Sequence[AgentStatusTypeType]],
    },
)

ListApprovedOriginsRequestRequestTypeDef = TypedDict(
    "ListApprovedOriginsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListBotsRequestRequestTypeDef = TypedDict(
    "ListBotsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexVersion": LexVersionType,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListContactEvaluationsRequestRequestTypeDef = TypedDict(
    "ListContactEvaluationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "NextToken": NotRequired[str],
    },
)

ListContactFlowModulesRequestRequestTypeDef = TypedDict(
    "ListContactFlowModulesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ContactFlowModuleState": NotRequired[ContactFlowModuleStateType],
    },
)

ListContactFlowsRequestRequestTypeDef = TypedDict(
    "ListContactFlowsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowTypes": NotRequired[Sequence[ContactFlowTypeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListContactReferencesRequestRequestTypeDef = TypedDict(
    "ListContactReferencesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ReferenceTypes": Sequence[ReferenceTypeType],
        "NextToken": NotRequired[str],
    },
)

ListDefaultVocabulariesRequestRequestTypeDef = TypedDict(
    "ListDefaultVocabulariesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListEvaluationFormVersionsRequestRequestTypeDef = TypedDict(
    "ListEvaluationFormVersionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListEvaluationFormsRequestRequestTypeDef = TypedDict(
    "ListEvaluationFormsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListHoursOfOperationsRequestRequestTypeDef = TypedDict(
    "ListHoursOfOperationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInstanceAttributesRequestRequestTypeDef = TypedDict(
    "ListInstanceAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInstanceStorageConfigsRequestRequestTypeDef = TypedDict(
    "ListInstanceStorageConfigsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInstancesRequestRequestTypeDef = TypedDict(
    "ListInstancesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListIntegrationAssociationsRequestRequestTypeDef = TypedDict(
    "ListIntegrationAssociationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": NotRequired[IntegrationTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListLambdaFunctionsRequestRequestTypeDef = TypedDict(
    "ListLambdaFunctionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListLexBotsRequestRequestTypeDef = TypedDict(
    "ListLexBotsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListPhoneNumbersRequestRequestTypeDef = TypedDict(
    "ListPhoneNumbersRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

PhoneNumberSummaryTypeDef = TypedDict(
    "PhoneNumberSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
    },
)

ListPhoneNumbersSummaryTypeDef = TypedDict(
    "ListPhoneNumbersSummaryTypeDef",
    {
        "PhoneNumberId": NotRequired[str],
        "PhoneNumberArn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "TargetArn": NotRequired[str],
    },
)

ListPhoneNumbersV2RequestRequestTypeDef = TypedDict(
    "ListPhoneNumbersV2RequestRequestTypeDef",
    {
        "TargetArn": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberPrefix": NotRequired[str],
    },
)

ListPromptsRequestRequestTypeDef = TypedDict(
    "ListPromptsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

PromptSummaryTypeDef = TypedDict(
    "PromptSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

ListQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "ListQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

QuickConnectSummaryTypeDef = TypedDict(
    "QuickConnectSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "QuickConnectType": NotRequired[QuickConnectTypeType],
    },
)

ListQueuesRequestRequestTypeDef = TypedDict(
    "ListQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueTypes": NotRequired[Sequence[QueueTypeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

QueueSummaryTypeDef = TypedDict(
    "QueueSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "QueueType": NotRequired[QueueTypeType],
    },
)

ListQuickConnectsRequestRequestTypeDef = TypedDict(
    "ListQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "QuickConnectTypes": NotRequired[Sequence[QuickConnectTypeType]],
    },
)

ListRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "ListRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

RoutingProfileQueueConfigSummaryTypeDef = TypedDict(
    "RoutingProfileQueueConfigSummaryTypeDef",
    {
        "QueueId": str,
        "QueueArn": str,
        "QueueName": str,
        "Priority": int,
        "Delay": int,
        "Channel": ChannelType,
    },
)

ListRoutingProfilesRequestRequestTypeDef = TypedDict(
    "ListRoutingProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

RoutingProfileSummaryTypeDef = TypedDict(
    "RoutingProfileSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

ListRulesRequestRequestTypeDef = TypedDict(
    "ListRulesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PublishStatus": NotRequired[RulePublishStatusType],
        "EventSourceName": NotRequired[EventSourceNameType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListSecurityKeysRequestRequestTypeDef = TypedDict(
    "ListSecurityKeysRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

SecurityKeyTypeDef = TypedDict(
    "SecurityKeyTypeDef",
    {
        "AssociationId": NotRequired[str],
        "Key": NotRequired[str],
        "CreationTime": NotRequired[datetime],
    },
)

ListSecurityProfilePermissionsRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilePermissionsRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListSecurityProfilesRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

SecurityProfileSummaryTypeDef = TypedDict(
    "SecurityProfileSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ListTaskTemplatesRequestRequestTypeDef = TypedDict(
    "ListTaskTemplatesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "Status": NotRequired[TaskTemplateStatusType],
        "Name": NotRequired[str],
    },
)

TaskTemplateMetadataTypeDef = TypedDict(
    "TaskTemplateMetadataTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Status": NotRequired[TaskTemplateStatusType],
        "LastModifiedTime": NotRequired[datetime],
        "CreatedTime": NotRequired[datetime],
    },
)

ListTrafficDistributionGroupUsersRequestRequestTypeDef = TypedDict(
    "ListTrafficDistributionGroupUsersRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

TrafficDistributionGroupUserSummaryTypeDef = TypedDict(
    "TrafficDistributionGroupUserSummaryTypeDef",
    {
        "UserId": NotRequired[str],
    },
)

ListTrafficDistributionGroupsRequestRequestTypeDef = TypedDict(
    "ListTrafficDistributionGroupsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "InstanceId": NotRequired[str],
    },
)

TrafficDistributionGroupSummaryTypeDef = TypedDict(
    "TrafficDistributionGroupSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "InstanceArn": NotRequired[str],
        "Status": NotRequired[TrafficDistributionGroupStatusType],
        "IsDefault": NotRequired[bool],
    },
)

ListUseCasesRequestRequestTypeDef = TypedDict(
    "ListUseCasesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

UseCaseTypeDef = TypedDict(
    "UseCaseTypeDef",
    {
        "UseCaseId": NotRequired[str],
        "UseCaseArn": NotRequired[str],
        "UseCaseType": NotRequired[UseCaseTypeType],
    },
)

ListUserHierarchyGroupsRequestRequestTypeDef = TypedDict(
    "ListUserHierarchyGroupsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListUsersRequestRequestTypeDef = TypedDict(
    "ListUsersRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

UserSummaryTypeDef = TypedDict(
    "UserSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Username": NotRequired[str],
    },
)

ListViewVersionsRequestRequestTypeDef = TypedDict(
    "ListViewVersionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ViewVersionSummaryTypeDef = TypedDict(
    "ViewVersionSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Description": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ViewTypeType],
        "Version": NotRequired[int],
        "VersionDescription": NotRequired[str],
    },
)

ListViewsRequestRequestTypeDef = TypedDict(
    "ListViewsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Type": NotRequired[ViewTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ViewSummaryTypeDef = TypedDict(
    "ViewSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ViewTypeType],
        "Status": NotRequired[ViewStatusType],
        "Description": NotRequired[str],
    },
)

MetricFilterV2TypeDef = TypedDict(
    "MetricFilterV2TypeDef",
    {
        "MetricFilterKey": NotRequired[str],
        "MetricFilterValues": NotRequired[Sequence[str]],
    },
)

ThresholdV2TypeDef = TypedDict(
    "ThresholdV2TypeDef",
    {
        "Comparison": NotRequired[str],
        "ThresholdValue": NotRequired[float],
    },
)

MonitorContactRequestRequestTypeDef = TypedDict(
    "MonitorContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "UserId": str,
        "AllowedMonitorCapabilities": NotRequired[Sequence[MonitorCapabilityType]],
        "ClientToken": NotRequired[str],
    },
)

NotificationRecipientTypeTypeDef = TypedDict(
    "NotificationRecipientTypeTypeDef",
    {
        "UserTags": NotRequired[Mapping[str, str]],
        "UserIds": NotRequired[Sequence[str]],
    },
)

NumberReferenceTypeDef = TypedDict(
    "NumberReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)

ParticipantDetailsTypeDef = TypedDict(
    "ParticipantDetailsTypeDef",
    {
        "DisplayName": str,
    },
)

ParticipantTimerValueTypeDef = TypedDict(
    "ParticipantTimerValueTypeDef",
    {
        "ParticipantTimerAction": NotRequired[Literal["Unset"]],
        "ParticipantTimerDurationInMinutes": NotRequired[int],
    },
)

PersistentChatTypeDef = TypedDict(
    "PersistentChatTypeDef",
    {
        "RehydrationType": NotRequired[RehydrationTypeType],
        "SourceContactId": NotRequired[str],
    },
)

PhoneNumberQuickConnectConfigTypeDef = TypedDict(
    "PhoneNumberQuickConnectConfigTypeDef",
    {
        "PhoneNumber": str,
    },
)

PutUserStatusRequestRequestTypeDef = TypedDict(
    "PutUserStatusRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "AgentStatusId": str,
    },
)

QueueQuickConnectConfigTypeDef = TypedDict(
    "QueueQuickConnectConfigTypeDef",
    {
        "QueueId": str,
        "ContactFlowId": str,
    },
)

UserQuickConnectConfigTypeDef = TypedDict(
    "UserQuickConnectConfigTypeDef",
    {
        "UserId": str,
        "ContactFlowId": str,
    },
)

StringReferenceTypeDef = TypedDict(
    "StringReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)

UrlReferenceTypeDef = TypedDict(
    "UrlReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)

ReferenceTypeDef = TypedDict(
    "ReferenceTypeDef",
    {
        "Value": str,
        "Type": ReferenceTypeType,
    },
)

ReleasePhoneNumberRequestRequestTypeDef = TypedDict(
    "ReleasePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "ClientToken": NotRequired[str],
    },
)

ReplicateInstanceRequestRequestTypeDef = TypedDict(
    "ReplicateInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ReplicaRegion": str,
        "ReplicaAlias": str,
        "ClientToken": NotRequired[str],
    },
)

TagSearchConditionTypeDef = TypedDict(
    "TagSearchConditionTypeDef",
    {
        "tagKey": NotRequired[str],
        "tagValue": NotRequired[str],
        "tagKeyComparisonType": NotRequired[StringComparisonTypeType],
        "tagValueComparisonType": NotRequired[StringComparisonTypeType],
    },
)

ResumeContactRecordingRequestRequestTypeDef = TypedDict(
    "ResumeContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)

SearchAvailablePhoneNumbersRequestRequestTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersRequestRequestTypeDef",
    {
        "TargetArn": str,
        "PhoneNumberCountryCode": PhoneNumberCountryCodeType,
        "PhoneNumberType": PhoneNumberTypeType,
        "PhoneNumberPrefix": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

TagSetTypeDef = TypedDict(
    "TagSetTypeDef",
    {
        "key": NotRequired[str],
        "value": NotRequired[str],
    },
)

SecurityProfileSearchSummaryTypeDef = TypedDict(
    "SecurityProfileSearchSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "OrganizationResourceId": NotRequired[str],
        "Arn": NotRequired[str],
        "SecurityProfileName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)

SearchVocabulariesRequestRequestTypeDef = TypedDict(
    "SearchVocabulariesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "State": NotRequired[VocabularyStateType],
        "NameStartsWith": NotRequired[str],
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
    },
)

VocabularySummaryTypeDef = TypedDict(
    "VocabularySummaryTypeDef",
    {
        "Name": str,
        "Id": str,
        "Arn": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "State": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": NotRequired[str],
    },
)

SignInDistributionTypeDef = TypedDict(
    "SignInDistributionTypeDef",
    {
        "Region": str,
        "Enabled": bool,
    },
)

StartContactEvaluationRequestRequestTypeDef = TypedDict(
    "StartContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "EvaluationFormId": str,
        "ClientToken": NotRequired[str],
    },
)

VoiceRecordingConfigurationTypeDef = TypedDict(
    "VoiceRecordingConfigurationTypeDef",
    {
        "VoiceRecordingTrack": NotRequired[VoiceRecordingTrackType],
    },
)

StopContactRecordingRequestRequestTypeDef = TypedDict(
    "StopContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)

StopContactRequestRequestTypeDef = TypedDict(
    "StopContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
    },
)

StopContactStreamingRequestRequestTypeDef = TypedDict(
    "StopContactStreamingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "StreamingId": str,
    },
)

SuspendContactRecordingRequestRequestTypeDef = TypedDict(
    "SuspendContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

TransferContactRequestRequestTypeDef = TypedDict(
    "TransferContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ContactFlowId": str,
        "QueueId": NotRequired[str],
        "UserId": NotRequired[str],
        "ClientToken": NotRequired[str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

UpdateAgentStatusRequestRequestTypeDef = TypedDict(
    "UpdateAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AgentStatusId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[AgentStatusStateType],
        "DisplayOrder": NotRequired[int],
        "ResetOrderNumber": NotRequired[bool],
    },
)

UpdateContactAttributesRequestRequestTypeDef = TypedDict(
    "UpdateContactAttributesRequestRequestTypeDef",
    {
        "InitialContactId": str,
        "InstanceId": str,
        "Attributes": Mapping[str, str],
    },
)

UpdateContactFlowContentRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Content": str,
    },
)

UpdateContactFlowMetadataRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "ContactFlowState": NotRequired[ContactFlowStateType],
    },
)

UpdateContactFlowModuleContentRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowModuleContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
        "Content": str,
    },
)

UpdateContactFlowModuleMetadataRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowModuleMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
    },
)

UpdateContactFlowNameRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UpdateInstanceAttributeRequestRequestTypeDef = TypedDict(
    "UpdateInstanceAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AttributeType": InstanceAttributeTypeType,
        "Value": str,
    },
)

UpdatePhoneNumberRequestRequestTypeDef = TypedDict(
    "UpdatePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "TargetArn": str,
        "ClientToken": NotRequired[str],
    },
)

UpdatePromptRequestRequestTypeDef = TypedDict(
    "UpdatePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "S3Uri": NotRequired[str],
    },
)

UpdateQueueHoursOfOperationRequestRequestTypeDef = TypedDict(
    "UpdateQueueHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "HoursOfOperationId": str,
    },
)

UpdateQueueMaxContactsRequestRequestTypeDef = TypedDict(
    "UpdateQueueMaxContactsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "MaxContacts": NotRequired[int],
    },
)

UpdateQueueNameRequestRequestTypeDef = TypedDict(
    "UpdateQueueNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UpdateQueueStatusRequestRequestTypeDef = TypedDict(
    "UpdateQueueStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "Status": QueueStatusType,
    },
)

UpdateQuickConnectNameRequestRequestTypeDef = TypedDict(
    "UpdateQuickConnectNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "AgentAvailabilityTimer": AgentAvailabilityTimerType,
    },
)

UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "DefaultOutboundQueueId": str,
    },
)

UpdateRoutingProfileNameRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UpdateSecurityProfileRequestRequestTypeDef = TypedDict(
    "UpdateSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "Permissions": NotRequired[Sequence[str]],
        "AllowedAccessControlTags": NotRequired[Mapping[str, str]],
        "TagRestrictedResources": NotRequired[Sequence[str]],
    },
)

UpdateUserHierarchyGroupNameRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyGroupNameRequestRequestTypeDef",
    {
        "Name": str,
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)

UpdateUserHierarchyRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "HierarchyGroupId": NotRequired[str],
    },
)

UpdateUserRoutingProfileRequestRequestTypeDef = TypedDict(
    "UpdateUserRoutingProfileRequestRequestTypeDef",
    {
        "RoutingProfileId": str,
        "UserId": str,
        "InstanceId": str,
    },
)

UpdateUserSecurityProfilesRequestRequestTypeDef = TypedDict(
    "UpdateUserSecurityProfilesRequestRequestTypeDef",
    {
        "SecurityProfileIds": Sequence[str],
        "UserId": str,
        "InstanceId": str,
    },
)

UpdateViewMetadataRequestRequestTypeDef = TypedDict(
    "UpdateViewMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UserReferenceTypeDef = TypedDict(
    "UserReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)

UserIdentityInfoLiteTypeDef = TypedDict(
    "UserIdentityInfoLiteTypeDef",
    {
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
    },
)

ViewContentTypeDef = TypedDict(
    "ViewContentTypeDef",
    {
        "InputSchema": NotRequired[str],
        "Template": NotRequired[str],
        "Actions": NotRequired[List[str]],
    },
)

RuleSummaryTypeDef = TypedDict(
    "RuleSummaryTypeDef",
    {
        "Name": str,
        "RuleId": str,
        "RuleArn": str,
        "EventSourceName": EventSourceNameType,
        "PublishStatus": RulePublishStatusType,
        "ActionSummaries": List[ActionSummaryTypeDef],
        "CreatedTime": datetime,
        "LastUpdatedTime": datetime,
    },
)

ActivateEvaluationFormResponseTypeDef = TypedDict(
    "ActivateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateInstanceStorageConfigResponseTypeDef = TypedDict(
    "AssociateInstanceStorageConfigResponseTypeDef",
    {
        "AssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateSecurityKeyResponseTypeDef = TypedDict(
    "AssociateSecurityKeyResponseTypeDef",
    {
        "AssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ClaimPhoneNumberResponseTypeDef = TypedDict(
    "ClaimPhoneNumberResponseTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAgentStatusResponseTypeDef = TypedDict(
    "CreateAgentStatusResponseTypeDef",
    {
        "AgentStatusARN": str,
        "AgentStatusId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContactFlowModuleResponseTypeDef = TypedDict(
    "CreateContactFlowModuleResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContactFlowResponseTypeDef = TypedDict(
    "CreateContactFlowResponseTypeDef",
    {
        "ContactFlowId": str,
        "ContactFlowArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEvaluationFormResponseTypeDef = TypedDict(
    "CreateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateHoursOfOperationResponseTypeDef = TypedDict(
    "CreateHoursOfOperationResponseTypeDef",
    {
        "HoursOfOperationId": str,
        "HoursOfOperationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInstanceResponseTypeDef = TypedDict(
    "CreateInstanceResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateIntegrationAssociationResponseTypeDef = TypedDict(
    "CreateIntegrationAssociationResponseTypeDef",
    {
        "IntegrationAssociationId": str,
        "IntegrationAssociationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePromptResponseTypeDef = TypedDict(
    "CreatePromptResponseTypeDef",
    {
        "PromptARN": str,
        "PromptId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateQueueResponseTypeDef = TypedDict(
    "CreateQueueResponseTypeDef",
    {
        "QueueArn": str,
        "QueueId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateQuickConnectResponseTypeDef = TypedDict(
    "CreateQuickConnectResponseTypeDef",
    {
        "QuickConnectARN": str,
        "QuickConnectId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRoutingProfileResponseTypeDef = TypedDict(
    "CreateRoutingProfileResponseTypeDef",
    {
        "RoutingProfileArn": str,
        "RoutingProfileId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRuleResponseTypeDef = TypedDict(
    "CreateRuleResponseTypeDef",
    {
        "RuleArn": str,
        "RuleId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSecurityProfileResponseTypeDef = TypedDict(
    "CreateSecurityProfileResponseTypeDef",
    {
        "SecurityProfileId": str,
        "SecurityProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTaskTemplateResponseTypeDef = TypedDict(
    "CreateTaskTemplateResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrafficDistributionGroupResponseTypeDef = TypedDict(
    "CreateTrafficDistributionGroupResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUseCaseResponseTypeDef = TypedDict(
    "CreateUseCaseResponseTypeDef",
    {
        "UseCaseId": str,
        "UseCaseArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUserHierarchyGroupResponseTypeDef = TypedDict(
    "CreateUserHierarchyGroupResponseTypeDef",
    {
        "HierarchyGroupId": str,
        "HierarchyGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUserResponseTypeDef = TypedDict(
    "CreateUserResponseTypeDef",
    {
        "UserId": str,
        "UserArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateVocabularyResponseTypeDef = TypedDict(
    "CreateVocabularyResponseTypeDef",
    {
        "VocabularyArn": str,
        "VocabularyId": str,
        "State": VocabularyStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeactivateEvaluationFormResponseTypeDef = TypedDict(
    "DeactivateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteVocabularyResponseTypeDef = TypedDict(
    "DeleteVocabularyResponseTypeDef",
    {
        "VocabularyArn": str,
        "VocabularyId": str,
        "State": VocabularyStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetContactAttributesResponseTypeDef = TypedDict(
    "GetContactAttributesResponseTypeDef",
    {
        "Attributes": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetPromptFileResponseTypeDef = TypedDict(
    "GetPromptFileResponseTypeDef",
    {
        "PromptPresignedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListApprovedOriginsResponseTypeDef = TypedDict(
    "ListApprovedOriginsResponseTypeDef",
    {
        "Origins": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListLambdaFunctionsResponseTypeDef = TypedDict(
    "ListLambdaFunctionsResponseTypeDef",
    {
        "LambdaFunctions": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSecurityProfilePermissionsResponseTypeDef = TypedDict(
    "ListSecurityProfilePermissionsResponseTypeDef",
    {
        "Permissions": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MonitorContactResponseTypeDef = TypedDict(
    "MonitorContactResponseTypeDef",
    {
        "ContactId": str,
        "ContactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplicateInstanceResponseTypeDef = TypedDict(
    "ReplicateInstanceResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartChatContactResponseTypeDef = TypedDict(
    "StartChatContactResponseTypeDef",
    {
        "ContactId": str,
        "ParticipantId": str,
        "ParticipantToken": str,
        "ContinuedFromContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartContactEvaluationResponseTypeDef = TypedDict(
    "StartContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartContactStreamingResponseTypeDef = TypedDict(
    "StartContactStreamingResponseTypeDef",
    {
        "StreamingId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartOutboundVoiceContactResponseTypeDef = TypedDict(
    "StartOutboundVoiceContactResponseTypeDef",
    {
        "ContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartTaskContactResponseTypeDef = TypedDict(
    "StartTaskContactResponseTypeDef",
    {
        "ContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SubmitContactEvaluationResponseTypeDef = TypedDict(
    "SubmitContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TransferContactResponseTypeDef = TypedDict(
    "TransferContactResponseTypeDef",
    {
        "ContactId": str,
        "ContactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateContactEvaluationResponseTypeDef = TypedDict(
    "UpdateContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEvaluationFormResponseTypeDef = TypedDict(
    "UpdateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdatePhoneNumberResponseTypeDef = TypedDict(
    "UpdatePhoneNumberResponseTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdatePromptResponseTypeDef = TypedDict(
    "UpdatePromptResponseTypeDef",
    {
        "PromptARN": str,
        "PromptId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AgentConfigTypeDef = TypedDict(
    "AgentConfigTypeDef",
    {
        "Distributions": List[DistributionTypeDef],
    },
)

TelephonyConfigTypeDef = TypedDict(
    "TelephonyConfigTypeDef",
    {
        "Distributions": List[DistributionTypeDef],
    },
)

AgentContactReferenceTypeDef = TypedDict(
    "AgentContactReferenceTypeDef",
    {
        "ContactId": NotRequired[str],
        "Channel": NotRequired[ChannelType],
        "InitiationMethod": NotRequired[ContactInitiationMethodType],
        "AgentContactState": NotRequired[ContactStateType],
        "StateStartTimestamp": NotRequired[datetime],
        "ConnectedToAgentTimestamp": NotRequired[datetime],
        "Queue": NotRequired[QueueReferenceTypeDef],
    },
)

ListAgentStatusResponseTypeDef = TypedDict(
    "ListAgentStatusResponseTypeDef",
    {
        "NextToken": str,
        "AgentStatusSummaryList": List[AgentStatusSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAgentStatusResponseTypeDef = TypedDict(
    "DescribeAgentStatusResponseTypeDef",
    {
        "AgentStatus": AgentStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartOutboundVoiceContactRequestRequestTypeDef = TypedDict(
    "StartOutboundVoiceContactRequestRequestTypeDef",
    {
        "DestinationPhoneNumber": str,
        "ContactFlowId": str,
        "InstanceId": str,
        "ClientToken": NotRequired[str],
        "SourcePhoneNumber": NotRequired[str],
        "QueueId": NotRequired[str],
        "Attributes": NotRequired[Mapping[str, str]],
        "AnswerMachineDetectionConfig": NotRequired[AnswerMachineDetectionConfigTypeDef],
        "CampaignId": NotRequired[str],
        "TrafficType": NotRequired[TrafficTypeType],
    },
)

AssociateLexBotRequestRequestTypeDef = TypedDict(
    "AssociateLexBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": LexBotTypeDef,
    },
)

ListLexBotsResponseTypeDef = TypedDict(
    "ListLexBotsResponseTypeDef",
    {
        "LexBots": List[LexBotTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateBotRequestRequestTypeDef = TypedDict(
    "AssociateBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)

DisassociateBotRequestRequestTypeDef = TypedDict(
    "DisassociateBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)

LexBotConfigTypeDef = TypedDict(
    "LexBotConfigTypeDef",
    {
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)

DescribeInstanceAttributeResponseTypeDef = TypedDict(
    "DescribeInstanceAttributeResponseTypeDef",
    {
        "Attribute": AttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListInstanceAttributesResponseTypeDef = TypedDict(
    "ListInstanceAttributesResponseTypeDef",
    {
        "Attributes": List[AttributeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchAvailablePhoneNumbersResponseTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersResponseTypeDef",
    {
        "NextToken": str,
        "AvailableNumbersList": List[AvailableNumberSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartContactStreamingRequestRequestTypeDef = TypedDict(
    "StartContactStreamingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ChatStreamingConfiguration": ChatStreamingConfigurationTypeDef,
        "ClientToken": str,
    },
)

ClaimedPhoneNumberSummaryTypeDef = TypedDict(
    "ClaimedPhoneNumberSummaryTypeDef",
    {
        "PhoneNumberId": NotRequired[str],
        "PhoneNumberArn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "PhoneNumberDescription": NotRequired[str],
        "TargetArn": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "PhoneNumberStatus": NotRequired[PhoneNumberStatusTypeDef],
    },
)

UserDataFiltersTypeDef = TypedDict(
    "UserDataFiltersTypeDef",
    {
        "Queues": NotRequired[Sequence[str]],
        "ContactFilter": NotRequired[ContactFilterTypeDef],
        "RoutingProfiles": NotRequired[Sequence[str]],
        "Agents": NotRequired[Sequence[str]],
        "UserHierarchyGroups": NotRequired[Sequence[str]],
    },
)

ListContactFlowModulesResponseTypeDef = TypedDict(
    "ListContactFlowModulesResponseTypeDef",
    {
        "ContactFlowModulesSummaryList": List[ContactFlowModuleSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeContactFlowModuleResponseTypeDef = TypedDict(
    "DescribeContactFlowModuleResponseTypeDef",
    {
        "ContactFlowModule": ContactFlowModuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListContactFlowsResponseTypeDef = TypedDict(
    "ListContactFlowsResponseTypeDef",
    {
        "ContactFlowSummaryList": List[ContactFlowSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeContactFlowResponseTypeDef = TypedDict(
    "DescribeContactFlowResponseTypeDef",
    {
        "ContactFlow": ContactFlowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ContactTypeDef = TypedDict(
    "ContactTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "InitialContactId": NotRequired[str],
        "PreviousContactId": NotRequired[str],
        "InitiationMethod": NotRequired[ContactInitiationMethodType],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Channel": NotRequired[ChannelType],
        "QueueInfo": NotRequired[QueueInfoTypeDef],
        "AgentInfo": NotRequired[AgentInfoTypeDef],
        "InitiationTimestamp": NotRequired[datetime],
        "DisconnectTimestamp": NotRequired[datetime],
        "LastUpdateTimestamp": NotRequired[datetime],
        "ScheduledTimestamp": NotRequired[datetime],
        "RelatedContactId": NotRequired[str],
        "WisdomInfo": NotRequired[WisdomInfoTypeDef],
    },
)

ControlPlaneTagFilterTypeDef = TypedDict(
    "ControlPlaneTagFilterTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Sequence[TagConditionTypeDef]]],
        "AndConditions": NotRequired[Sequence[TagConditionTypeDef]],
        "TagCondition": NotRequired[TagConditionTypeDef],
    },
)

CreateEvaluationFormRequestRequestTypeDef = TypedDict(
    "CreateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Title": str,
        "Items": Sequence["EvaluationFormItemTypeDef"],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "ClientToken": NotRequired[str],
    },
)

EvaluationFormContentTypeDef = TypedDict(
    "EvaluationFormContentTypeDef",
    {
        "EvaluationFormVersion": int,
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "Title": str,
        "Items": List["EvaluationFormItemTypeDef"],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
    },
)

EvaluationFormTypeDef = TypedDict(
    "EvaluationFormTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Locked": bool,
        "EvaluationFormArn": str,
        "Title": str,
        "Status": EvaluationFormVersionStatusType,
        "Items": List["EvaluationFormItemTypeDef"],
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "Tags": NotRequired[Dict[str, str]],
    },
)

UpdateEvaluationFormRequestRequestTypeDef = TypedDict(
    "UpdateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Title": str,
        "Items": Sequence["EvaluationFormItemTypeDef"],
        "CreateNewVersion": NotRequired[bool],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "ClientToken": NotRequired[str],
    },
)

CreateParticipantRequestRequestTypeDef = TypedDict(
    "CreateParticipantRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ParticipantDetails": ParticipantDetailsToAddTypeDef,
        "ClientToken": NotRequired[str],
    },
)

CreateParticipantResponseTypeDef = TypedDict(
    "CreateParticipantResponseTypeDef",
    {
        "ParticipantCredentials": ParticipantTokenCredentialsTypeDef,
        "ParticipantId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateQueueRequestRequestTypeDef = TypedDict(
    "CreateQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "HoursOfOperationId": str,
        "Description": NotRequired[str],
        "OutboundCallerConfig": NotRequired[OutboundCallerConfigTypeDef],
        "MaxContacts": NotRequired[int],
        "QuickConnectIds": NotRequired[Sequence[str]],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

QueueTypeDef = TypedDict(
    "QueueTypeDef",
    {
        "Name": NotRequired[str],
        "QueueArn": NotRequired[str],
        "QueueId": NotRequired[str],
        "Description": NotRequired[str],
        "OutboundCallerConfig": NotRequired[OutboundCallerConfigTypeDef],
        "HoursOfOperationId": NotRequired[str],
        "MaxContacts": NotRequired[int],
        "Status": NotRequired[QueueStatusType],
        "Tags": NotRequired[Dict[str, str]],
    },
)

UpdateQueueOutboundCallerConfigRequestRequestTypeDef = TypedDict(
    "UpdateQueueOutboundCallerConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "OutboundCallerConfig": OutboundCallerConfigTypeDef,
    },
)

UpdateUserIdentityInfoRequestRequestTypeDef = TypedDict(
    "UpdateUserIdentityInfoRequestRequestTypeDef",
    {
        "IdentityInfo": UserIdentityInfoTypeDef,
        "UserId": str,
        "InstanceId": str,
    },
)

CreateUserRequestRequestTypeDef = TypedDict(
    "CreateUserRequestRequestTypeDef",
    {
        "Username": str,
        "PhoneConfig": UserPhoneConfigTypeDef,
        "SecurityProfileIds": Sequence[str],
        "RoutingProfileId": str,
        "InstanceId": str,
        "Password": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoTypeDef],
        "DirectoryUserId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

UpdateUserPhoneConfigRequestRequestTypeDef = TypedDict(
    "UpdateUserPhoneConfigRequestRequestTypeDef",
    {
        "PhoneConfig": UserPhoneConfigTypeDef,
        "UserId": str,
        "InstanceId": str,
    },
)

UserTypeDef = TypedDict(
    "UserTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Username": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoTypeDef],
        "PhoneConfig": NotRequired[UserPhoneConfigTypeDef],
        "DirectoryUserId": NotRequired[str],
        "SecurityProfileIds": NotRequired[List[str]],
        "RoutingProfileId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)

CreateViewRequestRequestTypeDef = TypedDict(
    "CreateViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Status": ViewStatusType,
        "Content": ViewInputContentTypeDef,
        "Name": str,
        "ClientToken": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

UpdateViewContentRequestRequestTypeDef = TypedDict(
    "UpdateViewContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "Status": ViewStatusType,
        "Content": ViewInputContentTypeDef,
    },
)

GetFederationTokenResponseTypeDef = TypedDict(
    "GetFederationTokenResponseTypeDef",
    {
        "Credentials": CredentialsTypeDef,
        "SignInUrl": str,
        "UserArn": str,
        "UserId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MediaConcurrencyTypeDef = TypedDict(
    "MediaConcurrencyTypeDef",
    {
        "Channel": ChannelType,
        "Concurrency": int,
        "CrossChannelBehavior": NotRequired[CrossChannelBehaviorTypeDef],
    },
)

CurrentMetricDataTypeDef = TypedDict(
    "CurrentMetricDataTypeDef",
    {
        "Metric": NotRequired[CurrentMetricTypeDef],
        "Value": NotRequired[float],
    },
)

ListDefaultVocabulariesResponseTypeDef = TypedDict(
    "ListDefaultVocabulariesResponseTypeDef",
    {
        "DefaultVocabularyList": List[DefaultVocabularyTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePromptResponseTypeDef = TypedDict(
    "DescribePromptResponseTypeDef",
    {
        "Prompt": PromptTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchPromptsResponseTypeDef = TypedDict(
    "SearchPromptsResponseTypeDef",
    {
        "Prompts": List[PromptTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSecurityProfileResponseTypeDef = TypedDict(
    "DescribeSecurityProfileResponseTypeDef",
    {
        "SecurityProfile": SecurityProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrafficDistributionGroupResponseTypeDef = TypedDict(
    "DescribeTrafficDistributionGroupResponseTypeDef",
    {
        "TrafficDistributionGroup": TrafficDistributionGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeVocabularyResponseTypeDef = TypedDict(
    "DescribeVocabularyResponseTypeDef",
    {
        "Vocabulary": VocabularyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DimensionsTypeDef = TypedDict(
    "DimensionsTypeDef",
    {
        "Queue": NotRequired[QueueReferenceTypeDef],
        "Channel": NotRequired[ChannelType],
        "RoutingProfile": NotRequired[RoutingProfileReferenceTypeDef],
    },
)

DisassociateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "DisassociateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueReferences": Sequence[RoutingProfileQueueReferenceTypeDef],
    },
)

RoutingProfileQueueConfigTypeDef = TypedDict(
    "RoutingProfileQueueConfigTypeDef",
    {
        "QueueReference": RoutingProfileQueueReferenceTypeDef,
        "Priority": int,
        "Delay": int,
    },
)

KinesisVideoStreamConfigTypeDef = TypedDict(
    "KinesisVideoStreamConfigTypeDef",
    {
        "Prefix": str,
        "RetentionPeriodHours": int,
        "EncryptionConfig": EncryptionConfigTypeDef,
    },
)

S3ConfigTypeDef = TypedDict(
    "S3ConfigTypeDef",
    {
        "BucketName": str,
        "BucketPrefix": str,
        "EncryptionConfig": NotRequired[EncryptionConfigTypeDef],
    },
)

EvaluationAnswerInputTypeDef = TypedDict(
    "EvaluationAnswerInputTypeDef",
    {
        "Value": NotRequired[EvaluationAnswerDataTypeDef],
    },
)

EvaluationAnswerOutputTypeDef = TypedDict(
    "EvaluationAnswerOutputTypeDef",
    {
        "Value": NotRequired[EvaluationAnswerDataTypeDef],
        "SystemSuggestedValue": NotRequired[EvaluationAnswerDataTypeDef],
    },
)

EvaluationFormNumericQuestionAutomationTypeDef = TypedDict(
    "EvaluationFormNumericQuestionAutomationTypeDef",
    {
        "PropertyValue": NotRequired[NumericQuestionPropertyValueAutomationTypeDef],
    },
)

EvaluationFormSingleSelectQuestionAutomationOptionTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionAutomationOptionTypeDef",
    {
        "RuleCategory": NotRequired[SingleSelectQuestionRuleCategoryAutomationTypeDef],
    },
)

ListEvaluationFormsResponseTypeDef = TypedDict(
    "ListEvaluationFormsResponseTypeDef",
    {
        "EvaluationFormSummaryList": List[EvaluationFormSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEvaluationFormVersionsResponseTypeDef = TypedDict(
    "ListEvaluationFormVersionsResponseTypeDef",
    {
        "EvaluationFormVersionSummaryList": List[EvaluationFormVersionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EvaluationMetadataTypeDef = TypedDict(
    "EvaluationMetadataTypeDef",
    {
        "ContactId": str,
        "EvaluatorArn": str,
        "ContactAgentId": NotRequired[str],
        "Score": NotRequired[EvaluationScoreTypeDef],
    },
)

EvaluationSummaryTypeDef = TypedDict(
    "EvaluationSummaryTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "EvaluationFormTitle": str,
        "EvaluationFormId": str,
        "Status": EvaluationStatusType,
        "EvaluatorArn": str,
        "CreatedTime": datetime,
        "LastModifiedTime": datetime,
        "Score": NotRequired[EvaluationScoreTypeDef],
    },
)

GetCurrentMetricDataRequestRequestTypeDef = TypedDict(
    "GetCurrentMetricDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Filters": FiltersTypeDef,
        "CurrentMetrics": Sequence[CurrentMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortCriteria": NotRequired[Sequence[CurrentMetricSortCriteriaTypeDef]],
    },
)

ListAgentStatusRequestListAgentStatusesPaginateTypeDef = TypedDict(
    "ListAgentStatusRequestListAgentStatusesPaginateTypeDef",
    {
        "InstanceId": str,
        "AgentStatusTypes": NotRequired[Sequence[AgentStatusTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef = TypedDict(
    "ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListBotsRequestListBotsPaginateTypeDef = TypedDict(
    "ListBotsRequestListBotsPaginateTypeDef",
    {
        "InstanceId": str,
        "LexVersion": LexVersionType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef = TypedDict(
    "ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef = TypedDict(
    "ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleState": NotRequired[ContactFlowModuleStateType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListContactFlowsRequestListContactFlowsPaginateTypeDef = TypedDict(
    "ListContactFlowsRequestListContactFlowsPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactFlowTypes": NotRequired[Sequence[ContactFlowTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListContactReferencesRequestListContactReferencesPaginateTypeDef = TypedDict(
    "ListContactReferencesRequestListContactReferencesPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ReferenceTypes": Sequence[ReferenceTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef = TypedDict(
    "ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef = TypedDict(
    "ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef = TypedDict(
    "ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef = TypedDict(
    "ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef = TypedDict(
    "ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef = TypedDict(
    "ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInstancesRequestListInstancesPaginateTypeDef = TypedDict(
    "ListInstancesRequestListInstancesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef = TypedDict(
    "ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": NotRequired[IntegrationTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef = TypedDict(
    "ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLexBotsRequestListLexBotsPaginateTypeDef = TypedDict(
    "ListLexBotsRequestListLexBotsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef = TypedDict(
    "ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef",
    {
        "InstanceId": str,
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef = TypedDict(
    "ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef",
    {
        "TargetArn": NotRequired[str],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberPrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPromptsRequestListPromptsPaginateTypeDef = TypedDict(
    "ListPromptsRequestListPromptsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef = TypedDict(
    "ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListQueuesRequestListQueuesPaginateTypeDef = TypedDict(
    "ListQueuesRequestListQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "QueueTypes": NotRequired[Sequence[QueueTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListQuickConnectsRequestListQuickConnectsPaginateTypeDef = TypedDict(
    "ListQuickConnectsRequestListQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "QuickConnectTypes": NotRequired[Sequence[QuickConnectTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef = TypedDict(
    "ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef = TypedDict(
    "ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListRulesRequestListRulesPaginateTypeDef = TypedDict(
    "ListRulesRequestListRulesPaginateTypeDef",
    {
        "InstanceId": str,
        "PublishStatus": NotRequired[RulePublishStatusType],
        "EventSourceName": NotRequired[EventSourceNameType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSecurityKeysRequestListSecurityKeysPaginateTypeDef = TypedDict(
    "ListSecurityKeysRequestListSecurityKeysPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef = TypedDict(
    "ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef = TypedDict(
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef = TypedDict(
    "ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef",
    {
        "InstanceId": str,
        "Status": NotRequired[TaskTemplateStatusType],
        "Name": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef = (
    TypedDict(
        "ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef",
        {
            "TrafficDistributionGroupId": str,
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)

ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef = TypedDict(
    "ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef",
    {
        "InstanceId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListUseCasesRequestListUseCasesPaginateTypeDef = TypedDict(
    "ListUseCasesRequestListUseCasesPaginateTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef = TypedDict(
    "ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListUsersRequestListUsersPaginateTypeDef = TypedDict(
    "ListUsersRequestListUsersPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListViewVersionsRequestListViewVersionsPaginateTypeDef = TypedDict(
    "ListViewVersionsRequestListViewVersionsPaginateTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListViewsRequestListViewsPaginateTypeDef = TypedDict(
    "ListViewsRequestListViewsPaginateTypeDef",
    {
        "InstanceId": str,
        "Type": NotRequired[ViewTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef",
    {
        "TargetArn": str,
        "PhoneNumberCountryCode": PhoneNumberCountryCodeType,
        "PhoneNumberType": PhoneNumberTypeType,
        "PhoneNumberPrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef = TypedDict(
    "SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef",
    {
        "InstanceId": str,
        "State": NotRequired[VocabularyStateType],
        "NameStartsWith": NotRequired[str],
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

UpdateContactScheduleRequestRequestTypeDef = TypedDict(
    "UpdateContactScheduleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ScheduledTime": TimestampTypeDef,
    },
)

HierarchyPathReferenceTypeDef = TypedDict(
    "HierarchyPathReferenceTypeDef",
    {
        "LevelOne": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelTwo": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelThree": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelFour": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelFive": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
    },
)

HierarchyPathTypeDef = TypedDict(
    "HierarchyPathTypeDef",
    {
        "LevelOne": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelTwo": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelThree": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelFour": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelFive": NotRequired[HierarchyGroupSummaryTypeDef],
    },
)

ListUserHierarchyGroupsResponseTypeDef = TypedDict(
    "ListUserHierarchyGroupsResponseTypeDef",
    {
        "UserHierarchyGroupSummaryList": List[HierarchyGroupSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HierarchyStructureTypeDef = TypedDict(
    "HierarchyStructureTypeDef",
    {
        "LevelOne": NotRequired[HierarchyLevelTypeDef],
        "LevelTwo": NotRequired[HierarchyLevelTypeDef],
        "LevelThree": NotRequired[HierarchyLevelTypeDef],
        "LevelFour": NotRequired[HierarchyLevelTypeDef],
        "LevelFive": NotRequired[HierarchyLevelTypeDef],
    },
)

HierarchyStructureUpdateTypeDef = TypedDict(
    "HierarchyStructureUpdateTypeDef",
    {
        "LevelOne": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelTwo": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelThree": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelFour": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelFive": NotRequired[HierarchyLevelUpdateTypeDef],
    },
)

HistoricalMetricTypeDef = TypedDict(
    "HistoricalMetricTypeDef",
    {
        "Name": NotRequired[HistoricalMetricNameType],
        "Threshold": NotRequired[ThresholdTypeDef],
        "Statistic": NotRequired[StatisticType],
        "Unit": NotRequired[UnitType],
    },
)

HoursOfOperationConfigTypeDef = TypedDict(
    "HoursOfOperationConfigTypeDef",
    {
        "Day": HoursOfOperationDaysType,
        "StartTime": HoursOfOperationTimeSliceTypeDef,
        "EndTime": HoursOfOperationTimeSliceTypeDef,
    },
)

HoursOfOperationSearchCriteriaTypeDef = TypedDict(
    "HoursOfOperationSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)

PromptSearchCriteriaTypeDef = TypedDict(
    "PromptSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)

QueueSearchCriteriaTypeDef = TypedDict(
    "QueueSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
        "QueueTypeCondition": NotRequired[Literal["STANDARD"]],
    },
)

QuickConnectSearchCriteriaTypeDef = TypedDict(
    "QuickConnectSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)

RoutingProfileSearchCriteriaTypeDef = TypedDict(
    "RoutingProfileSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)

SecurityProfileSearchCriteriaTypeDef = TypedDict(
    "SecurityProfileSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)

UserSearchCriteriaTypeDef = TypedDict(
    "UserSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
        "HierarchyGroupCondition": NotRequired[HierarchyGroupConditionTypeDef],
    },
)

ListHoursOfOperationsResponseTypeDef = TypedDict(
    "ListHoursOfOperationsResponseTypeDef",
    {
        "HoursOfOperationSummaryList": List[HoursOfOperationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InstanceTypeDef = TypedDict(
    "InstanceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "IdentityManagementType": NotRequired[DirectoryTypeType],
        "InstanceAlias": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "ServiceRole": NotRequired[str],
        "InstanceStatus": NotRequired[InstanceStatusType],
        "StatusReason": NotRequired[InstanceStatusReasonTypeDef],
        "InboundCallsEnabled": NotRequired[bool],
        "OutboundCallsEnabled": NotRequired[bool],
        "InstanceAccessUrl": NotRequired[str],
    },
)

ListInstancesResponseTypeDef = TypedDict(
    "ListInstancesResponseTypeDef",
    {
        "InstanceSummaryList": List[InstanceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListIntegrationAssociationsResponseTypeDef = TypedDict(
    "ListIntegrationAssociationsResponseTypeDef",
    {
        "IntegrationAssociationSummaryList": List[IntegrationAssociationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InvisibleFieldInfoTypeDef = TypedDict(
    "InvisibleFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)

ReadOnlyFieldInfoTypeDef = TypedDict(
    "ReadOnlyFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)

RequiredFieldInfoTypeDef = TypedDict(
    "RequiredFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)

TaskTemplateDefaultFieldValueTypeDef = TypedDict(
    "TaskTemplateDefaultFieldValueTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
        "DefaultValue": NotRequired[str],
    },
)

TaskTemplateFieldTypeDef = TypedDict(
    "TaskTemplateFieldTypeDef",
    {
        "Id": TaskTemplateFieldIdentifierTypeDef,
        "Description": NotRequired[str],
        "Type": NotRequired[TaskTemplateFieldTypeType],
        "SingleSelectOptions": NotRequired[Sequence[str]],
    },
)

ListPhoneNumbersResponseTypeDef = TypedDict(
    "ListPhoneNumbersResponseTypeDef",
    {
        "PhoneNumberSummaryList": List[PhoneNumberSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPhoneNumbersV2ResponseTypeDef = TypedDict(
    "ListPhoneNumbersV2ResponseTypeDef",
    {
        "NextToken": str,
        "ListPhoneNumbersSummaryList": List[ListPhoneNumbersSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPromptsResponseTypeDef = TypedDict(
    "ListPromptsResponseTypeDef",
    {
        "PromptSummaryList": List[PromptSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListQueueQuickConnectsResponseTypeDef = TypedDict(
    "ListQueueQuickConnectsResponseTypeDef",
    {
        "NextToken": str,
        "QuickConnectSummaryList": List[QuickConnectSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListQuickConnectsResponseTypeDef = TypedDict(
    "ListQuickConnectsResponseTypeDef",
    {
        "QuickConnectSummaryList": List[QuickConnectSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListQueuesResponseTypeDef = TypedDict(
    "ListQueuesResponseTypeDef",
    {
        "QueueSummaryList": List[QueueSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRoutingProfileQueuesResponseTypeDef = TypedDict(
    "ListRoutingProfileQueuesResponseTypeDef",
    {
        "NextToken": str,
        "RoutingProfileQueueConfigSummaryList": List[RoutingProfileQueueConfigSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRoutingProfilesResponseTypeDef = TypedDict(
    "ListRoutingProfilesResponseTypeDef",
    {
        "RoutingProfileSummaryList": List[RoutingProfileSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSecurityKeysResponseTypeDef = TypedDict(
    "ListSecurityKeysResponseTypeDef",
    {
        "SecurityKeys": List[SecurityKeyTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSecurityProfilesResponseTypeDef = TypedDict(
    "ListSecurityProfilesResponseTypeDef",
    {
        "SecurityProfileSummaryList": List[SecurityProfileSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTaskTemplatesResponseTypeDef = TypedDict(
    "ListTaskTemplatesResponseTypeDef",
    {
        "TaskTemplates": List[TaskTemplateMetadataTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTrafficDistributionGroupUsersResponseTypeDef = TypedDict(
    "ListTrafficDistributionGroupUsersResponseTypeDef",
    {
        "NextToken": str,
        "TrafficDistributionGroupUserSummaryList": List[TrafficDistributionGroupUserSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTrafficDistributionGroupsResponseTypeDef = TypedDict(
    "ListTrafficDistributionGroupsResponseTypeDef",
    {
        "NextToken": str,
        "TrafficDistributionGroupSummaryList": List[TrafficDistributionGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListUseCasesResponseTypeDef = TypedDict(
    "ListUseCasesResponseTypeDef",
    {
        "UseCaseSummaryList": List[UseCaseTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListUsersResponseTypeDef = TypedDict(
    "ListUsersResponseTypeDef",
    {
        "UserSummaryList": List[UserSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListViewVersionsResponseTypeDef = TypedDict(
    "ListViewVersionsResponseTypeDef",
    {
        "ViewVersionSummaryList": List[ViewVersionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListViewsResponseTypeDef = TypedDict(
    "ListViewsResponseTypeDef",
    {
        "ViewsSummaryList": List[ViewSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MetricV2TypeDef = TypedDict(
    "MetricV2TypeDef",
    {
        "Name": NotRequired[str],
        "Threshold": NotRequired[Sequence[ThresholdV2TypeDef]],
        "MetricFilters": NotRequired[Sequence[MetricFilterV2TypeDef]],
    },
)

SendNotificationActionDefinitionTypeDef = TypedDict(
    "SendNotificationActionDefinitionTypeDef",
    {
        "DeliveryMethod": Literal["EMAIL"],
        "Content": str,
        "ContentType": Literal["PLAIN_TEXT"],
        "Recipient": NotificationRecipientTypeTypeDef,
        "Subject": NotRequired[str],
    },
)

ParticipantTimerConfigurationTypeDef = TypedDict(
    "ParticipantTimerConfigurationTypeDef",
    {
        "ParticipantRole": TimerEligibleParticipantRolesType,
        "TimerType": ParticipantTimerTypeType,
        "TimerValue": ParticipantTimerValueTypeDef,
    },
)

StartChatContactRequestRequestTypeDef = TypedDict(
    "StartChatContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "ParticipantDetails": ParticipantDetailsTypeDef,
        "Attributes": NotRequired[Mapping[str, str]],
        "InitialMessage": NotRequired[ChatMessageTypeDef],
        "ClientToken": NotRequired[str],
        "ChatDurationInMinutes": NotRequired[int],
        "SupportedMessagingContentTypes": NotRequired[Sequence[str]],
        "PersistentChat": NotRequired[PersistentChatTypeDef],
        "RelatedContactId": NotRequired[str],
    },
)

QuickConnectConfigTypeDef = TypedDict(
    "QuickConnectConfigTypeDef",
    {
        "QuickConnectType": QuickConnectTypeType,
        "UserConfig": NotRequired[UserQuickConnectConfigTypeDef],
        "QueueConfig": NotRequired[QueueQuickConnectConfigTypeDef],
        "PhoneConfig": NotRequired[PhoneNumberQuickConnectConfigTypeDef],
    },
)

ReferenceSummaryTypeDef = TypedDict(
    "ReferenceSummaryTypeDef",
    {
        "Url": NotRequired[UrlReferenceTypeDef],
        "Attachment": NotRequired[AttachmentReferenceTypeDef],
        "String": NotRequired[StringReferenceTypeDef],
        "Number": NotRequired[NumberReferenceTypeDef],
        "Date": NotRequired[DateReferenceTypeDef],
        "Email": NotRequired[EmailReferenceTypeDef],
    },
)

StartTaskContactRequestRequestTypeDef = TypedDict(
    "StartTaskContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "PreviousContactId": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Attributes": NotRequired[Mapping[str, str]],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "ScheduledTime": NotRequired[TimestampTypeDef],
        "TaskTemplateId": NotRequired[str],
        "QuickConnectId": NotRequired[str],
        "RelatedContactId": NotRequired[str],
    },
)

TaskActionDefinitionTypeDef = TypedDict(
    "TaskActionDefinitionTypeDef",
    {
        "Name": str,
        "ContactFlowId": str,
        "Description": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
    },
)

UpdateContactRequestRequestTypeDef = TypedDict(
    "UpdateContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
    },
)

ResourceTagsSearchCriteriaTypeDef = TypedDict(
    "ResourceTagsSearchCriteriaTypeDef",
    {
        "TagSearchCondition": NotRequired[TagSearchConditionTypeDef],
    },
)

SearchResourceTagsResponseTypeDef = TypedDict(
    "SearchResourceTagsResponseTypeDef",
    {
        "Tags": List[TagSetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchSecurityProfilesResponseTypeDef = TypedDict(
    "SearchSecurityProfilesResponseTypeDef",
    {
        "SecurityProfiles": List[SecurityProfileSearchSummaryTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchVocabulariesResponseTypeDef = TypedDict(
    "SearchVocabulariesResponseTypeDef",
    {
        "VocabularySummaryList": List[VocabularySummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SignInConfigTypeDef = TypedDict(
    "SignInConfigTypeDef",
    {
        "Distributions": List[SignInDistributionTypeDef],
    },
)

StartContactRecordingRequestRequestTypeDef = TypedDict(
    "StartContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
        "VoiceRecordingConfiguration": VoiceRecordingConfigurationTypeDef,
    },
)

UserSearchSummaryTypeDef = TypedDict(
    "UserSearchSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "DirectoryUserId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Id": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoLiteTypeDef],
        "PhoneConfig": NotRequired[UserPhoneConfigTypeDef],
        "RoutingProfileId": NotRequired[str],
        "SecurityProfileIds": NotRequired[List[str]],
        "Tags": NotRequired[Dict[str, str]],
        "Username": NotRequired[str],
    },
)

ViewTypeDef = TypedDict(
    "ViewTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[ViewStatusType],
        "Type": NotRequired[ViewTypeType],
        "Description": NotRequired[str],
        "Version": NotRequired[int],
        "VersionDescription": NotRequired[str],
        "Content": NotRequired[ViewContentTypeDef],
        "Tags": NotRequired[Dict[str, str]],
        "CreatedTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "ViewContentSha256": NotRequired[str],
    },
)

ListRulesResponseTypeDef = TypedDict(
    "ListRulesResponseTypeDef",
    {
        "RuleSummaryList": List[RuleSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListBotsResponseTypeDef = TypedDict(
    "ListBotsResponseTypeDef",
    {
        "LexBots": List[LexBotConfigTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePhoneNumberResponseTypeDef = TypedDict(
    "DescribePhoneNumberResponseTypeDef",
    {
        "ClaimedPhoneNumberSummary": ClaimedPhoneNumberSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCurrentUserDataRequestRequestTypeDef = TypedDict(
    "GetCurrentUserDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Filters": UserDataFiltersTypeDef,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

DescribeContactResponseTypeDef = TypedDict(
    "DescribeContactResponseTypeDef",
    {
        "Contact": ContactTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HoursOfOperationSearchFilterTypeDef = TypedDict(
    "HoursOfOperationSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

PromptSearchFilterTypeDef = TypedDict(
    "PromptSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

QueueSearchFilterTypeDef = TypedDict(
    "QueueSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

QuickConnectSearchFilterTypeDef = TypedDict(
    "QuickConnectSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

RoutingProfileSearchFilterTypeDef = TypedDict(
    "RoutingProfileSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

SecurityProfilesSearchFilterTypeDef = TypedDict(
    "SecurityProfilesSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

UserSearchFilterTypeDef = TypedDict(
    "UserSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)

DescribeEvaluationFormResponseTypeDef = TypedDict(
    "DescribeEvaluationFormResponseTypeDef",
    {
        "EvaluationForm": EvaluationFormTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeQueueResponseTypeDef = TypedDict(
    "DescribeQueueResponseTypeDef",
    {
        "Queue": QueueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchQueuesResponseTypeDef = TypedDict(
    "SearchQueuesResponseTypeDef",
    {
        "Queues": List[QueueTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeUserResponseTypeDef = TypedDict(
    "DescribeUserResponseTypeDef",
    {
        "User": UserTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RoutingProfileTypeDef = TypedDict(
    "RoutingProfileTypeDef",
    {
        "InstanceId": NotRequired[str],
        "Name": NotRequired[str],
        "RoutingProfileArn": NotRequired[str],
        "RoutingProfileId": NotRequired[str],
        "Description": NotRequired[str],
        "MediaConcurrencies": NotRequired[List[MediaConcurrencyTypeDef]],
        "DefaultOutboundQueueId": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "NumberOfAssociatedQueues": NotRequired[int],
        "NumberOfAssociatedUsers": NotRequired[int],
        "AgentAvailabilityTimer": NotRequired[AgentAvailabilityTimerType],
    },
)

UpdateRoutingProfileConcurrencyRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileConcurrencyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "MediaConcurrencies": Sequence[MediaConcurrencyTypeDef],
    },
)

CurrentMetricResultTypeDef = TypedDict(
    "CurrentMetricResultTypeDef",
    {
        "Dimensions": NotRequired[DimensionsTypeDef],
        "Collections": NotRequired[List[CurrentMetricDataTypeDef]],
    },
)

AssociateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "AssociateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueConfigs": Sequence[RoutingProfileQueueConfigTypeDef],
    },
)

CreateRoutingProfileRequestRequestTypeDef = TypedDict(
    "CreateRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Description": str,
        "DefaultOutboundQueueId": str,
        "MediaConcurrencies": Sequence[MediaConcurrencyTypeDef],
        "QueueConfigs": NotRequired[Sequence[RoutingProfileQueueConfigTypeDef]],
        "Tags": NotRequired[Mapping[str, str]],
        "AgentAvailabilityTimer": NotRequired[AgentAvailabilityTimerType],
    },
)

UpdateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueConfigs": Sequence[RoutingProfileQueueConfigTypeDef],
    },
)

InstanceStorageConfigTypeDef = TypedDict(
    "InstanceStorageConfigTypeDef",
    {
        "StorageType": StorageTypeType,
        "AssociationId": NotRequired[str],
        "S3Config": NotRequired[S3ConfigTypeDef],
        "KinesisVideoStreamConfig": NotRequired[KinesisVideoStreamConfigTypeDef],
        "KinesisStreamConfig": NotRequired[KinesisStreamConfigTypeDef],
        "KinesisFirehoseConfig": NotRequired[KinesisFirehoseConfigTypeDef],
    },
)

SubmitContactEvaluationRequestRequestTypeDef = TypedDict(
    "SubmitContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
        "Answers": NotRequired[Mapping[str, EvaluationAnswerInputTypeDef]],
        "Notes": NotRequired[Mapping[str, EvaluationNoteTypeDef]],
    },
)

UpdateContactEvaluationRequestRequestTypeDef = TypedDict(
    "UpdateContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
        "Answers": NotRequired[Mapping[str, EvaluationAnswerInputTypeDef]],
        "Notes": NotRequired[Mapping[str, EvaluationNoteTypeDef]],
    },
)

EvaluationFormNumericQuestionPropertiesTypeDef = TypedDict(
    "EvaluationFormNumericQuestionPropertiesTypeDef",
    {
        "MinValue": int,
        "MaxValue": int,
        "Options": NotRequired[Sequence[EvaluationFormNumericQuestionOptionTypeDef]],
        "Automation": NotRequired[EvaluationFormNumericQuestionAutomationTypeDef],
    },
)

EvaluationFormSingleSelectQuestionAutomationTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionAutomationTypeDef",
    {
        "Options": Sequence[EvaluationFormSingleSelectQuestionAutomationOptionTypeDef],
        "DefaultOptionRefId": NotRequired[str],
    },
)

EvaluationTypeDef = TypedDict(
    "EvaluationTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "Metadata": EvaluationMetadataTypeDef,
        "Answers": Dict[str, EvaluationAnswerOutputTypeDef],
        "Notes": Dict[str, EvaluationNoteTypeDef],
        "Status": EvaluationStatusType,
        "CreatedTime": datetime,
        "LastModifiedTime": datetime,
        "Scores": NotRequired[Dict[str, EvaluationScoreTypeDef]],
        "Tags": NotRequired[Dict[str, str]],
    },
)

ListContactEvaluationsResponseTypeDef = TypedDict(
    "ListContactEvaluationsResponseTypeDef",
    {
        "EvaluationSummaryList": List[EvaluationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserDataTypeDef = TypedDict(
    "UserDataTypeDef",
    {
        "User": NotRequired[UserReferenceTypeDef],
        "RoutingProfile": NotRequired[RoutingProfileReferenceTypeDef],
        "HierarchyPath": NotRequired[HierarchyPathReferenceTypeDef],
        "Status": NotRequired[AgentStatusReferenceTypeDef],
        "AvailableSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "MaxSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "ActiveSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "Contacts": NotRequired[List[AgentContactReferenceTypeDef]],
        "NextStatus": NotRequired[str],
    },
)

HierarchyGroupTypeDef = TypedDict(
    "HierarchyGroupTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LevelId": NotRequired[str],
        "HierarchyPath": NotRequired[HierarchyPathTypeDef],
        "Tags": NotRequired[Dict[str, str]],
    },
)

DescribeUserHierarchyStructureResponseTypeDef = TypedDict(
    "DescribeUserHierarchyStructureResponseTypeDef",
    {
        "HierarchyStructure": HierarchyStructureTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateUserHierarchyStructureRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyStructureRequestRequestTypeDef",
    {
        "HierarchyStructure": HierarchyStructureUpdateTypeDef,
        "InstanceId": str,
    },
)

GetMetricDataRequestGetMetricDataPaginateTypeDef = TypedDict(
    "GetMetricDataRequestGetMetricDataPaginateTypeDef",
    {
        "InstanceId": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": FiltersTypeDef,
        "HistoricalMetrics": Sequence[HistoricalMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

GetMetricDataRequestRequestTypeDef = TypedDict(
    "GetMetricDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": FiltersTypeDef,
        "HistoricalMetrics": Sequence[HistoricalMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

HistoricalMetricDataTypeDef = TypedDict(
    "HistoricalMetricDataTypeDef",
    {
        "Metric": NotRequired[HistoricalMetricTypeDef],
        "Value": NotRequired[float],
    },
)

CreateHoursOfOperationRequestRequestTypeDef = TypedDict(
    "CreateHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "TimeZone": str,
        "Config": Sequence[HoursOfOperationConfigTypeDef],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

HoursOfOperationTypeDef = TypedDict(
    "HoursOfOperationTypeDef",
    {
        "HoursOfOperationId": NotRequired[str],
        "HoursOfOperationArn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "TimeZone": NotRequired[str],
        "Config": NotRequired[List[HoursOfOperationConfigTypeDef]],
        "Tags": NotRequired[Dict[str, str]],
    },
)

UpdateHoursOfOperationRequestRequestTypeDef = TypedDict(
    "UpdateHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "TimeZone": NotRequired[str],
        "Config": NotRequired[Sequence[HoursOfOperationConfigTypeDef]],
    },
)

DescribeInstanceResponseTypeDef = TypedDict(
    "DescribeInstanceResponseTypeDef",
    {
        "Instance": InstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TaskTemplateConstraintsTypeDef = TypedDict(
    "TaskTemplateConstraintsTypeDef",
    {
        "RequiredFields": NotRequired[Sequence[RequiredFieldInfoTypeDef]],
        "ReadOnlyFields": NotRequired[Sequence[ReadOnlyFieldInfoTypeDef]],
        "InvisibleFields": NotRequired[Sequence[InvisibleFieldInfoTypeDef]],
    },
)

TaskTemplateDefaultsTypeDef = TypedDict(
    "TaskTemplateDefaultsTypeDef",
    {
        "DefaultFieldValues": NotRequired[Sequence[TaskTemplateDefaultFieldValueTypeDef]],
    },
)

GetMetricDataV2RequestRequestTypeDef = TypedDict(
    "GetMetricDataV2RequestRequestTypeDef",
    {
        "ResourceArn": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": Sequence[FilterV2TypeDef],
        "Metrics": Sequence[MetricV2TypeDef],
        "Groupings": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

MetricDataV2TypeDef = TypedDict(
    "MetricDataV2TypeDef",
    {
        "Metric": NotRequired[MetricV2TypeDef],
        "Value": NotRequired[float],
    },
)

ChatParticipantRoleConfigTypeDef = TypedDict(
    "ChatParticipantRoleConfigTypeDef",
    {
        "ParticipantTimerConfigList": Sequence[ParticipantTimerConfigurationTypeDef],
    },
)

CreateQuickConnectRequestRequestTypeDef = TypedDict(
    "CreateQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "QuickConnectConfig": QuickConnectConfigTypeDef,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

QuickConnectTypeDef = TypedDict(
    "QuickConnectTypeDef",
    {
        "QuickConnectARN": NotRequired[str],
        "QuickConnectId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "QuickConnectConfig": NotRequired[QuickConnectConfigTypeDef],
        "Tags": NotRequired[Dict[str, str]],
    },
)

UpdateQuickConnectConfigRequestRequestTypeDef = TypedDict(
    "UpdateQuickConnectConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
        "QuickConnectConfig": QuickConnectConfigTypeDef,
    },
)

ListContactReferencesResponseTypeDef = TypedDict(
    "ListContactReferencesResponseTypeDef",
    {
        "ReferenceSummaryList": List[ReferenceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RuleActionTypeDef = TypedDict(
    "RuleActionTypeDef",
    {
        "ActionType": ActionTypeType,
        "TaskAction": NotRequired[TaskActionDefinitionTypeDef],
        "EventBridgeAction": NotRequired[EventBridgeActionDefinitionTypeDef],
        "AssignContactCategoryAction": NotRequired[Mapping[str, Any]],
        "SendNotificationAction": NotRequired[SendNotificationActionDefinitionTypeDef],
    },
)

SearchResourceTagsRequestRequestTypeDef = TypedDict(
    "SearchResourceTagsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceTypes": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchCriteria": NotRequired[ResourceTagsSearchCriteriaTypeDef],
    },
)

SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef = TypedDict(
    "SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef",
    {
        "InstanceId": str,
        "ResourceTypes": NotRequired[Sequence[str]],
        "SearchCriteria": NotRequired[ResourceTagsSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

GetTrafficDistributionResponseTypeDef = TypedDict(
    "GetTrafficDistributionResponseTypeDef",
    {
        "TelephonyConfig": TelephonyConfigTypeDef,
        "Id": str,
        "Arn": str,
        "SignInConfig": SignInConfigTypeDef,
        "AgentConfig": AgentConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTrafficDistributionRequestRequestTypeDef = TypedDict(
    "UpdateTrafficDistributionRequestRequestTypeDef",
    {
        "Id": str,
        "TelephonyConfig": NotRequired[TelephonyConfigTypeDef],
        "SignInConfig": NotRequired[SignInConfigTypeDef],
        "AgentConfig": NotRequired[AgentConfigTypeDef],
    },
)

SearchUsersResponseTypeDef = TypedDict(
    "SearchUsersResponseTypeDef",
    {
        "Users": List[UserSearchSummaryTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateViewResponseTypeDef = TypedDict(
    "CreateViewResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateViewVersionResponseTypeDef = TypedDict(
    "CreateViewVersionResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeViewResponseTypeDef = TypedDict(
    "DescribeViewResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateViewContentResponseTypeDef = TypedDict(
    "UpdateViewContentResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchHoursOfOperationsRequestRequestTypeDef = TypedDict(
    "SearchHoursOfOperationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[HoursOfOperationSearchFilterTypeDef],
        "SearchCriteria": NotRequired["HoursOfOperationSearchCriteriaTypeDef"],
    },
)

SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef = TypedDict(
    "SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[HoursOfOperationSearchFilterTypeDef],
        "SearchCriteria": NotRequired[HoursOfOperationSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchPromptsRequestRequestTypeDef = TypedDict(
    "SearchPromptsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[PromptSearchFilterTypeDef],
        "SearchCriteria": NotRequired["PromptSearchCriteriaTypeDef"],
    },
)

SearchPromptsRequestSearchPromptsPaginateTypeDef = TypedDict(
    "SearchPromptsRequestSearchPromptsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[PromptSearchFilterTypeDef],
        "SearchCriteria": NotRequired[PromptSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchQueuesRequestRequestTypeDef = TypedDict(
    "SearchQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[QueueSearchFilterTypeDef],
        "SearchCriteria": NotRequired["QueueSearchCriteriaTypeDef"],
    },
)

SearchQueuesRequestSearchQueuesPaginateTypeDef = TypedDict(
    "SearchQueuesRequestSearchQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[QueueSearchFilterTypeDef],
        "SearchCriteria": NotRequired[QueueSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchQuickConnectsRequestRequestTypeDef = TypedDict(
    "SearchQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[QuickConnectSearchFilterTypeDef],
        "SearchCriteria": NotRequired["QuickConnectSearchCriteriaTypeDef"],
    },
)

SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef = TypedDict(
    "SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[QuickConnectSearchFilterTypeDef],
        "SearchCriteria": NotRequired[QuickConnectSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchRoutingProfilesRequestRequestTypeDef = TypedDict(
    "SearchRoutingProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[RoutingProfileSearchFilterTypeDef],
        "SearchCriteria": NotRequired["RoutingProfileSearchCriteriaTypeDef"],
    },
)

SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef = TypedDict(
    "SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[RoutingProfileSearchFilterTypeDef],
        "SearchCriteria": NotRequired[RoutingProfileSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchSecurityProfilesRequestRequestTypeDef = TypedDict(
    "SearchSecurityProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchCriteria": NotRequired["SecurityProfileSearchCriteriaTypeDef"],
        "SearchFilter": NotRequired[SecurityProfilesSearchFilterTypeDef],
    },
)

SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef = TypedDict(
    "SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchCriteria": NotRequired[SecurityProfileSearchCriteriaTypeDef],
        "SearchFilter": NotRequired[SecurityProfilesSearchFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

SearchUsersRequestRequestTypeDef = TypedDict(
    "SearchUsersRequestRequestTypeDef",
    {
        "InstanceId": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[UserSearchFilterTypeDef],
        "SearchCriteria": NotRequired["UserSearchCriteriaTypeDef"],
    },
)

SearchUsersRequestSearchUsersPaginateTypeDef = TypedDict(
    "SearchUsersRequestSearchUsersPaginateTypeDef",
    {
        "InstanceId": NotRequired[str],
        "SearchFilter": NotRequired[UserSearchFilterTypeDef],
        "SearchCriteria": NotRequired[UserSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeRoutingProfileResponseTypeDef = TypedDict(
    "DescribeRoutingProfileResponseTypeDef",
    {
        "RoutingProfile": RoutingProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchRoutingProfilesResponseTypeDef = TypedDict(
    "SearchRoutingProfilesResponseTypeDef",
    {
        "RoutingProfiles": List[RoutingProfileTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCurrentMetricDataResponseTypeDef = TypedDict(
    "GetCurrentMetricDataResponseTypeDef",
    {
        "NextToken": str,
        "MetricResults": List[CurrentMetricResultTypeDef],
        "DataSnapshotTime": datetime,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "AssociateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "StorageConfig": InstanceStorageConfigTypeDef,
    },
)

DescribeInstanceStorageConfigResponseTypeDef = TypedDict(
    "DescribeInstanceStorageConfigResponseTypeDef",
    {
        "StorageConfig": InstanceStorageConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListInstanceStorageConfigsResponseTypeDef = TypedDict(
    "ListInstanceStorageConfigsResponseTypeDef",
    {
        "StorageConfigs": List[InstanceStorageConfigTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "UpdateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "StorageConfig": InstanceStorageConfigTypeDef,
    },
)

EvaluationFormSingleSelectQuestionPropertiesTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionPropertiesTypeDef",
    {
        "Options": Sequence[EvaluationFormSingleSelectQuestionOptionTypeDef],
        "DisplayAs": NotRequired[EvaluationFormSingleSelectQuestionDisplayModeType],
        "Automation": NotRequired[EvaluationFormSingleSelectQuestionAutomationTypeDef],
    },
)

DescribeContactEvaluationResponseTypeDef = TypedDict(
    "DescribeContactEvaluationResponseTypeDef",
    {
        "Evaluation": EvaluationTypeDef,
        "EvaluationForm": EvaluationFormContentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetCurrentUserDataResponseTypeDef = TypedDict(
    "GetCurrentUserDataResponseTypeDef",
    {
        "NextToken": str,
        "UserDataList": List[UserDataTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeUserHierarchyGroupResponseTypeDef = TypedDict(
    "DescribeUserHierarchyGroupResponseTypeDef",
    {
        "HierarchyGroup": HierarchyGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HistoricalMetricResultTypeDef = TypedDict(
    "HistoricalMetricResultTypeDef",
    {
        "Dimensions": NotRequired[DimensionsTypeDef],
        "Collections": NotRequired[List[HistoricalMetricDataTypeDef]],
    },
)

DescribeHoursOfOperationResponseTypeDef = TypedDict(
    "DescribeHoursOfOperationResponseTypeDef",
    {
        "HoursOfOperation": HoursOfOperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchHoursOfOperationsResponseTypeDef = TypedDict(
    "SearchHoursOfOperationsResponseTypeDef",
    {
        "HoursOfOperations": List[HoursOfOperationTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTaskTemplateRequestRequestTypeDef = TypedDict(
    "CreateTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Fields": Sequence[TaskTemplateFieldTypeDef],
        "Description": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Constraints": NotRequired[TaskTemplateConstraintsTypeDef],
        "Defaults": NotRequired[TaskTemplateDefaultsTypeDef],
        "Status": NotRequired[TaskTemplateStatusType],
        "ClientToken": NotRequired[str],
    },
)

GetTaskTemplateResponseTypeDef = TypedDict(
    "GetTaskTemplateResponseTypeDef",
    {
        "InstanceId": str,
        "Id": str,
        "Arn": str,
        "Name": str,
        "Description": str,
        "ContactFlowId": str,
        "Constraints": TaskTemplateConstraintsTypeDef,
        "Defaults": TaskTemplateDefaultsTypeDef,
        "Fields": List[TaskTemplateFieldTypeDef],
        "Status": TaskTemplateStatusType,
        "LastModifiedTime": datetime,
        "CreatedTime": datetime,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTaskTemplateRequestRequestTypeDef = TypedDict(
    "UpdateTaskTemplateRequestRequestTypeDef",
    {
        "TaskTemplateId": str,
        "InstanceId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Constraints": NotRequired[TaskTemplateConstraintsTypeDef],
        "Defaults": NotRequired[TaskTemplateDefaultsTypeDef],
        "Status": NotRequired[TaskTemplateStatusType],
        "Fields": NotRequired[Sequence[TaskTemplateFieldTypeDef]],
    },
)

UpdateTaskTemplateResponseTypeDef = TypedDict(
    "UpdateTaskTemplateResponseTypeDef",
    {
        "InstanceId": str,
        "Id": str,
        "Arn": str,
        "Name": str,
        "Description": str,
        "ContactFlowId": str,
        "Constraints": TaskTemplateConstraintsTypeDef,
        "Defaults": TaskTemplateDefaultsTypeDef,
        "Fields": List[TaskTemplateFieldTypeDef],
        "Status": TaskTemplateStatusType,
        "LastModifiedTime": datetime,
        "CreatedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MetricResultV2TypeDef = TypedDict(
    "MetricResultV2TypeDef",
    {
        "Dimensions": NotRequired[Dict[str, str]],
        "Collections": NotRequired[List[MetricDataV2TypeDef]],
    },
)

UpdateParticipantRoleConfigChannelInfoTypeDef = TypedDict(
    "UpdateParticipantRoleConfigChannelInfoTypeDef",
    {
        "Chat": NotRequired[ChatParticipantRoleConfigTypeDef],
    },
)

DescribeQuickConnectResponseTypeDef = TypedDict(
    "DescribeQuickConnectResponseTypeDef",
    {
        "QuickConnect": QuickConnectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchQuickConnectsResponseTypeDef = TypedDict(
    "SearchQuickConnectsResponseTypeDef",
    {
        "QuickConnects": List[QuickConnectTypeDef],
        "NextToken": str,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRuleRequestRequestTypeDef = TypedDict(
    "CreateRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "TriggerEventSource": RuleTriggerEventSourceTypeDef,
        "Function": str,
        "Actions": Sequence[RuleActionTypeDef],
        "PublishStatus": RulePublishStatusType,
        "ClientToken": NotRequired[str],
    },
)

RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "Name": str,
        "RuleId": str,
        "RuleArn": str,
        "TriggerEventSource": RuleTriggerEventSourceTypeDef,
        "Function": str,
        "Actions": List[RuleActionTypeDef],
        "PublishStatus": RulePublishStatusType,
        "CreatedTime": datetime,
        "LastUpdatedTime": datetime,
        "LastUpdatedBy": str,
        "Tags": NotRequired[Dict[str, str]],
    },
)

UpdateRuleRequestRequestTypeDef = TypedDict(
    "UpdateRuleRequestRequestTypeDef",
    {
        "RuleId": str,
        "InstanceId": str,
        "Name": str,
        "Function": str,
        "Actions": Sequence[RuleActionTypeDef],
        "PublishStatus": RulePublishStatusType,
    },
)

EvaluationFormQuestionTypePropertiesTypeDef = TypedDict(
    "EvaluationFormQuestionTypePropertiesTypeDef",
    {
        "Numeric": NotRequired[EvaluationFormNumericQuestionPropertiesTypeDef],
        "SingleSelect": NotRequired[EvaluationFormSingleSelectQuestionPropertiesTypeDef],
    },
)

GetMetricDataResponseTypeDef = TypedDict(
    "GetMetricDataResponseTypeDef",
    {
        "NextToken": str,
        "MetricResults": List[HistoricalMetricResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetMetricDataV2ResponseTypeDef = TypedDict(
    "GetMetricDataV2ResponseTypeDef",
    {
        "NextToken": str,
        "MetricResults": List[MetricResultV2TypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateParticipantRoleConfigRequestRequestTypeDef = TypedDict(
    "UpdateParticipantRoleConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ChannelConfiguration": UpdateParticipantRoleConfigChannelInfoTypeDef,
    },
)

DescribeRuleResponseTypeDef = TypedDict(
    "DescribeRuleResponseTypeDef",
    {
        "Rule": RuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EvaluationFormQuestionTypeDef = TypedDict(
    "EvaluationFormQuestionTypeDef",
    {
        "Title": str,
        "RefId": str,
        "QuestionType": EvaluationFormQuestionTypeType,
        "Instructions": NotRequired[str],
        "NotApplicableEnabled": NotRequired[bool],
        "QuestionTypeProperties": NotRequired[EvaluationFormQuestionTypePropertiesTypeDef],
        "Weight": NotRequired[float],
    },
)

EvaluationFormItemTypeDef = TypedDict(
    "EvaluationFormItemTypeDef",
    {
        "Section": NotRequired[Dict[str, Any]],
        "Question": NotRequired[EvaluationFormQuestionTypeDef],
    },
)
