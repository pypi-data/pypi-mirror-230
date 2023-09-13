"""
Type annotations for events service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_events/type_defs/)

Usage::

    ```python
    from mypy_boto3_events.type_defs import ActivateEventSourceRequestRequestTypeDef

    data: ActivateEventSourceRequestRequestTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    ApiDestinationHttpMethodType,
    ApiDestinationStateType,
    ArchiveStateType,
    AssignPublicIpType,
    ConnectionAuthorizationTypeType,
    ConnectionOAuthHttpMethodType,
    ConnectionStateType,
    EndpointStateType,
    EventSourceStateType,
    LaunchTypeType,
    PlacementConstraintTypeType,
    PlacementStrategyTypeType,
    ReplayStateType,
    ReplicationStateType,
    RuleStateType,
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
    "ActivateEventSourceRequestRequestTypeDef",
    "ApiDestinationTypeDef",
    "ArchiveTypeDef",
    "AwsVpcConfigurationTypeDef",
    "BatchArrayPropertiesTypeDef",
    "BatchRetryStrategyTypeDef",
    "CancelReplayRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "CapacityProviderStrategyItemTypeDef",
    "ConditionTypeDef",
    "ConnectionApiKeyAuthResponseParametersTypeDef",
    "ConnectionBasicAuthResponseParametersTypeDef",
    "ConnectionBodyParameterTypeDef",
    "ConnectionHeaderParameterTypeDef",
    "ConnectionQueryStringParameterTypeDef",
    "ConnectionOAuthClientResponseParametersTypeDef",
    "ConnectionTypeDef",
    "CreateApiDestinationRequestRequestTypeDef",
    "CreateArchiveRequestRequestTypeDef",
    "CreateConnectionApiKeyAuthRequestParametersTypeDef",
    "CreateConnectionBasicAuthRequestParametersTypeDef",
    "CreateConnectionOAuthClientRequestParametersTypeDef",
    "EndpointEventBusTypeDef",
    "ReplicationConfigTypeDef",
    "TagTypeDef",
    "CreatePartnerEventSourceRequestRequestTypeDef",
    "DeactivateEventSourceRequestRequestTypeDef",
    "DeadLetterConfigTypeDef",
    "DeauthorizeConnectionRequestRequestTypeDef",
    "DeleteApiDestinationRequestRequestTypeDef",
    "DeleteArchiveRequestRequestTypeDef",
    "DeleteConnectionRequestRequestTypeDef",
    "DeleteEndpointRequestRequestTypeDef",
    "DeleteEventBusRequestRequestTypeDef",
    "DeletePartnerEventSourceRequestRequestTypeDef",
    "DeleteRuleRequestRequestTypeDef",
    "DescribeApiDestinationRequestRequestTypeDef",
    "DescribeArchiveRequestRequestTypeDef",
    "DescribeConnectionRequestRequestTypeDef",
    "DescribeEndpointRequestRequestTypeDef",
    "DescribeEventBusRequestRequestTypeDef",
    "DescribeEventSourceRequestRequestTypeDef",
    "DescribePartnerEventSourceRequestRequestTypeDef",
    "DescribeReplayRequestRequestTypeDef",
    "ReplayDestinationTypeDef",
    "DescribeRuleRequestRequestTypeDef",
    "DisableRuleRequestRequestTypeDef",
    "PlacementConstraintTypeDef",
    "PlacementStrategyTypeDef",
    "EnableRuleRequestRequestTypeDef",
    "EventBusTypeDef",
    "EventSourceTypeDef",
    "PrimaryTypeDef",
    "SecondaryTypeDef",
    "HttpParametersTypeDef",
    "InputTransformerTypeDef",
    "KinesisParametersTypeDef",
    "ListApiDestinationsRequestRequestTypeDef",
    "ListArchivesRequestRequestTypeDef",
    "ListConnectionsRequestRequestTypeDef",
    "ListEndpointsRequestRequestTypeDef",
    "ListEventBusesRequestRequestTypeDef",
    "ListEventSourcesRequestRequestTypeDef",
    "ListPartnerEventSourceAccountsRequestRequestTypeDef",
    "PartnerEventSourceAccountTypeDef",
    "ListPartnerEventSourcesRequestRequestTypeDef",
    "PartnerEventSourceTypeDef",
    "ListReplaysRequestRequestTypeDef",
    "ReplayTypeDef",
    "PaginatorConfigTypeDef",
    "ListRuleNamesByTargetRequestRequestTypeDef",
    "ListRulesRequestRequestTypeDef",
    "RuleTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTargetsByRuleRequestRequestTypeDef",
    "TimestampTypeDef",
    "PutEventsResultEntryTypeDef",
    "PutPartnerEventsResultEntryTypeDef",
    "PutTargetsResultEntryTypeDef",
    "RedshiftDataParametersTypeDef",
    "RemovePermissionRequestRequestTypeDef",
    "RemoveTargetsRequestRequestTypeDef",
    "RemoveTargetsResultEntryTypeDef",
    "RetryPolicyTypeDef",
    "RunCommandTargetTypeDef",
    "SageMakerPipelineParameterTypeDef",
    "SqsParametersTypeDef",
    "TestEventPatternRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateApiDestinationRequestRequestTypeDef",
    "UpdateArchiveRequestRequestTypeDef",
    "UpdateConnectionApiKeyAuthRequestParametersTypeDef",
    "UpdateConnectionBasicAuthRequestParametersTypeDef",
    "UpdateConnectionOAuthClientRequestParametersTypeDef",
    "NetworkConfigurationTypeDef",
    "BatchParametersTypeDef",
    "CancelReplayResponseTypeDef",
    "CreateApiDestinationResponseTypeDef",
    "CreateArchiveResponseTypeDef",
    "CreateConnectionResponseTypeDef",
    "CreateEventBusResponseTypeDef",
    "CreatePartnerEventSourceResponseTypeDef",
    "DeauthorizeConnectionResponseTypeDef",
    "DeleteConnectionResponseTypeDef",
    "DescribeApiDestinationResponseTypeDef",
    "DescribeArchiveResponseTypeDef",
    "DescribeEventBusResponseTypeDef",
    "DescribeEventSourceResponseTypeDef",
    "DescribePartnerEventSourceResponseTypeDef",
    "DescribeRuleResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ListApiDestinationsResponseTypeDef",
    "ListArchivesResponseTypeDef",
    "ListRuleNamesByTargetResponseTypeDef",
    "PutRuleResponseTypeDef",
    "StartReplayResponseTypeDef",
    "TestEventPatternResponseTypeDef",
    "UpdateApiDestinationResponseTypeDef",
    "UpdateArchiveResponseTypeDef",
    "UpdateConnectionResponseTypeDef",
    "PutPermissionRequestRequestTypeDef",
    "ConnectionHttpParametersTypeDef",
    "ListConnectionsResponseTypeDef",
    "CreateEventBusRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "PutRuleRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "DescribeReplayResponseTypeDef",
    "ListEventBusesResponseTypeDef",
    "ListEventSourcesResponseTypeDef",
    "FailoverConfigTypeDef",
    "ListPartnerEventSourceAccountsResponseTypeDef",
    "ListPartnerEventSourcesResponseTypeDef",
    "ListReplaysResponseTypeDef",
    "ListRuleNamesByTargetRequestListRuleNamesByTargetPaginateTypeDef",
    "ListRulesRequestListRulesPaginateTypeDef",
    "ListTargetsByRuleRequestListTargetsByRulePaginateTypeDef",
    "ListRulesResponseTypeDef",
    "PutEventsRequestEntryTypeDef",
    "PutPartnerEventsRequestEntryTypeDef",
    "StartReplayRequestRequestTypeDef",
    "PutEventsResponseTypeDef",
    "PutPartnerEventsResponseTypeDef",
    "PutTargetsResponseTypeDef",
    "RemoveTargetsResponseTypeDef",
    "RunCommandParametersTypeDef",
    "SageMakerPipelineParametersTypeDef",
    "EcsParametersTypeDef",
    "ConnectionOAuthResponseParametersTypeDef",
    "CreateConnectionOAuthRequestParametersTypeDef",
    "UpdateConnectionOAuthRequestParametersTypeDef",
    "RoutingConfigTypeDef",
    "PutEventsRequestRequestTypeDef",
    "PutPartnerEventsRequestRequestTypeDef",
    "TargetTypeDef",
    "ConnectionAuthResponseParametersTypeDef",
    "CreateConnectionAuthRequestParametersTypeDef",
    "UpdateConnectionAuthRequestParametersTypeDef",
    "CreateEndpointRequestRequestTypeDef",
    "CreateEndpointResponseTypeDef",
    "DescribeEndpointResponseTypeDef",
    "EndpointTypeDef",
    "UpdateEndpointRequestRequestTypeDef",
    "UpdateEndpointResponseTypeDef",
    "ListTargetsByRuleResponseTypeDef",
    "PutTargetsRequestRequestTypeDef",
    "DescribeConnectionResponseTypeDef",
    "CreateConnectionRequestRequestTypeDef",
    "UpdateConnectionRequestRequestTypeDef",
    "ListEndpointsResponseTypeDef",
)

ActivateEventSourceRequestRequestTypeDef = TypedDict(
    "ActivateEventSourceRequestRequestTypeDef",
    {
        "Name": str,
    },
)

ApiDestinationTypeDef = TypedDict(
    "ApiDestinationTypeDef",
    {
        "ApiDestinationArn": NotRequired[str],
        "Name": NotRequired[str],
        "ApiDestinationState": NotRequired[ApiDestinationStateType],
        "ConnectionArn": NotRequired[str],
        "InvocationEndpoint": NotRequired[str],
        "HttpMethod": NotRequired[ApiDestinationHttpMethodType],
        "InvocationRateLimitPerSecond": NotRequired[int],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

ArchiveTypeDef = TypedDict(
    "ArchiveTypeDef",
    {
        "ArchiveName": NotRequired[str],
        "EventSourceArn": NotRequired[str],
        "State": NotRequired[ArchiveStateType],
        "StateReason": NotRequired[str],
        "RetentionDays": NotRequired[int],
        "SizeBytes": NotRequired[int],
        "EventCount": NotRequired[int],
        "CreationTime": NotRequired[datetime],
    },
)

AwsVpcConfigurationTypeDef = TypedDict(
    "AwsVpcConfigurationTypeDef",
    {
        "Subnets": List[str],
        "SecurityGroups": NotRequired[List[str]],
        "AssignPublicIp": NotRequired[AssignPublicIpType],
    },
)

BatchArrayPropertiesTypeDef = TypedDict(
    "BatchArrayPropertiesTypeDef",
    {
        "Size": NotRequired[int],
    },
)

BatchRetryStrategyTypeDef = TypedDict(
    "BatchRetryStrategyTypeDef",
    {
        "Attempts": NotRequired[int],
    },
)

CancelReplayRequestRequestTypeDef = TypedDict(
    "CancelReplayRequestRequestTypeDef",
    {
        "ReplayName": str,
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

CapacityProviderStrategyItemTypeDef = TypedDict(
    "CapacityProviderStrategyItemTypeDef",
    {
        "capacityProvider": str,
        "weight": NotRequired[int],
        "base": NotRequired[int],
    },
)

ConditionTypeDef = TypedDict(
    "ConditionTypeDef",
    {
        "Type": str,
        "Key": str,
        "Value": str,
    },
)

ConnectionApiKeyAuthResponseParametersTypeDef = TypedDict(
    "ConnectionApiKeyAuthResponseParametersTypeDef",
    {
        "ApiKeyName": NotRequired[str],
    },
)

ConnectionBasicAuthResponseParametersTypeDef = TypedDict(
    "ConnectionBasicAuthResponseParametersTypeDef",
    {
        "Username": NotRequired[str],
    },
)

ConnectionBodyParameterTypeDef = TypedDict(
    "ConnectionBodyParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
        "IsValueSecret": NotRequired[bool],
    },
)

ConnectionHeaderParameterTypeDef = TypedDict(
    "ConnectionHeaderParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
        "IsValueSecret": NotRequired[bool],
    },
)

ConnectionQueryStringParameterTypeDef = TypedDict(
    "ConnectionQueryStringParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
        "IsValueSecret": NotRequired[bool],
    },
)

ConnectionOAuthClientResponseParametersTypeDef = TypedDict(
    "ConnectionOAuthClientResponseParametersTypeDef",
    {
        "ClientID": NotRequired[str],
    },
)

ConnectionTypeDef = TypedDict(
    "ConnectionTypeDef",
    {
        "ConnectionArn": NotRequired[str],
        "Name": NotRequired[str],
        "ConnectionState": NotRequired[ConnectionStateType],
        "StateReason": NotRequired[str],
        "AuthorizationType": NotRequired[ConnectionAuthorizationTypeType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastAuthorizedTime": NotRequired[datetime],
    },
)

CreateApiDestinationRequestRequestTypeDef = TypedDict(
    "CreateApiDestinationRequestRequestTypeDef",
    {
        "Name": str,
        "ConnectionArn": str,
        "InvocationEndpoint": str,
        "HttpMethod": ApiDestinationHttpMethodType,
        "Description": NotRequired[str],
        "InvocationRateLimitPerSecond": NotRequired[int],
    },
)

CreateArchiveRequestRequestTypeDef = TypedDict(
    "CreateArchiveRequestRequestTypeDef",
    {
        "ArchiveName": str,
        "EventSourceArn": str,
        "Description": NotRequired[str],
        "EventPattern": NotRequired[str],
        "RetentionDays": NotRequired[int],
    },
)

CreateConnectionApiKeyAuthRequestParametersTypeDef = TypedDict(
    "CreateConnectionApiKeyAuthRequestParametersTypeDef",
    {
        "ApiKeyName": str,
        "ApiKeyValue": str,
    },
)

CreateConnectionBasicAuthRequestParametersTypeDef = TypedDict(
    "CreateConnectionBasicAuthRequestParametersTypeDef",
    {
        "Username": str,
        "Password": str,
    },
)

CreateConnectionOAuthClientRequestParametersTypeDef = TypedDict(
    "CreateConnectionOAuthClientRequestParametersTypeDef",
    {
        "ClientID": str,
        "ClientSecret": str,
    },
)

EndpointEventBusTypeDef = TypedDict(
    "EndpointEventBusTypeDef",
    {
        "EventBusArn": str,
    },
)

ReplicationConfigTypeDef = TypedDict(
    "ReplicationConfigTypeDef",
    {
        "State": NotRequired[ReplicationStateType],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

CreatePartnerEventSourceRequestRequestTypeDef = TypedDict(
    "CreatePartnerEventSourceRequestRequestTypeDef",
    {
        "Name": str,
        "Account": str,
    },
)

DeactivateEventSourceRequestRequestTypeDef = TypedDict(
    "DeactivateEventSourceRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeadLetterConfigTypeDef = TypedDict(
    "DeadLetterConfigTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

DeauthorizeConnectionRequestRequestTypeDef = TypedDict(
    "DeauthorizeConnectionRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteApiDestinationRequestRequestTypeDef = TypedDict(
    "DeleteApiDestinationRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteArchiveRequestRequestTypeDef = TypedDict(
    "DeleteArchiveRequestRequestTypeDef",
    {
        "ArchiveName": str,
    },
)

DeleteConnectionRequestRequestTypeDef = TypedDict(
    "DeleteConnectionRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteEndpointRequestRequestTypeDef = TypedDict(
    "DeleteEndpointRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteEventBusRequestRequestTypeDef = TypedDict(
    "DeleteEventBusRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeletePartnerEventSourceRequestRequestTypeDef = TypedDict(
    "DeletePartnerEventSourceRequestRequestTypeDef",
    {
        "Name": str,
        "Account": str,
    },
)

DeleteRuleRequestRequestTypeDef = TypedDict(
    "DeleteRuleRequestRequestTypeDef",
    {
        "Name": str,
        "EventBusName": NotRequired[str],
        "Force": NotRequired[bool],
    },
)

DescribeApiDestinationRequestRequestTypeDef = TypedDict(
    "DescribeApiDestinationRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DescribeArchiveRequestRequestTypeDef = TypedDict(
    "DescribeArchiveRequestRequestTypeDef",
    {
        "ArchiveName": str,
    },
)

DescribeConnectionRequestRequestTypeDef = TypedDict(
    "DescribeConnectionRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DescribeEndpointRequestRequestTypeDef = TypedDict(
    "DescribeEndpointRequestRequestTypeDef",
    {
        "Name": str,
        "HomeRegion": NotRequired[str],
    },
)

DescribeEventBusRequestRequestTypeDef = TypedDict(
    "DescribeEventBusRequestRequestTypeDef",
    {
        "Name": NotRequired[str],
    },
)

DescribeEventSourceRequestRequestTypeDef = TypedDict(
    "DescribeEventSourceRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DescribePartnerEventSourceRequestRequestTypeDef = TypedDict(
    "DescribePartnerEventSourceRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DescribeReplayRequestRequestTypeDef = TypedDict(
    "DescribeReplayRequestRequestTypeDef",
    {
        "ReplayName": str,
    },
)

ReplayDestinationTypeDef = TypedDict(
    "ReplayDestinationTypeDef",
    {
        "Arn": str,
        "FilterArns": NotRequired[List[str]],
    },
)

DescribeRuleRequestRequestTypeDef = TypedDict(
    "DescribeRuleRequestRequestTypeDef",
    {
        "Name": str,
        "EventBusName": NotRequired[str],
    },
)

DisableRuleRequestRequestTypeDef = TypedDict(
    "DisableRuleRequestRequestTypeDef",
    {
        "Name": str,
        "EventBusName": NotRequired[str],
    },
)

PlacementConstraintTypeDef = TypedDict(
    "PlacementConstraintTypeDef",
    {
        "type": NotRequired[PlacementConstraintTypeType],
        "expression": NotRequired[str],
    },
)

PlacementStrategyTypeDef = TypedDict(
    "PlacementStrategyTypeDef",
    {
        "type": NotRequired[PlacementStrategyTypeType],
        "field": NotRequired[str],
    },
)

EnableRuleRequestRequestTypeDef = TypedDict(
    "EnableRuleRequestRequestTypeDef",
    {
        "Name": str,
        "EventBusName": NotRequired[str],
    },
)

EventBusTypeDef = TypedDict(
    "EventBusTypeDef",
    {
        "Name": NotRequired[str],
        "Arn": NotRequired[str],
        "Policy": NotRequired[str],
    },
)

EventSourceTypeDef = TypedDict(
    "EventSourceTypeDef",
    {
        "Arn": NotRequired[str],
        "CreatedBy": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "ExpirationTime": NotRequired[datetime],
        "Name": NotRequired[str],
        "State": NotRequired[EventSourceStateType],
    },
)

PrimaryTypeDef = TypedDict(
    "PrimaryTypeDef",
    {
        "HealthCheck": str,
    },
)

SecondaryTypeDef = TypedDict(
    "SecondaryTypeDef",
    {
        "Route": str,
    },
)

HttpParametersTypeDef = TypedDict(
    "HttpParametersTypeDef",
    {
        "PathParameterValues": NotRequired[List[str]],
        "HeaderParameters": NotRequired[Dict[str, str]],
        "QueryStringParameters": NotRequired[Dict[str, str]],
    },
)

InputTransformerTypeDef = TypedDict(
    "InputTransformerTypeDef",
    {
        "InputTemplate": str,
        "InputPathsMap": NotRequired[Dict[str, str]],
    },
)

KinesisParametersTypeDef = TypedDict(
    "KinesisParametersTypeDef",
    {
        "PartitionKeyPath": str,
    },
)

ListApiDestinationsRequestRequestTypeDef = TypedDict(
    "ListApiDestinationsRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "ConnectionArn": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListArchivesRequestRequestTypeDef = TypedDict(
    "ListArchivesRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "EventSourceArn": NotRequired[str],
        "State": NotRequired[ArchiveStateType],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListConnectionsRequestRequestTypeDef = TypedDict(
    "ListConnectionsRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "ConnectionState": NotRequired[ConnectionStateType],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListEndpointsRequestRequestTypeDef = TypedDict(
    "ListEndpointsRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "HomeRegion": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListEventBusesRequestRequestTypeDef = TypedDict(
    "ListEventBusesRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListEventSourcesRequestRequestTypeDef = TypedDict(
    "ListEventSourcesRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListPartnerEventSourceAccountsRequestRequestTypeDef = TypedDict(
    "ListPartnerEventSourceAccountsRequestRequestTypeDef",
    {
        "EventSourceName": str,
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

PartnerEventSourceAccountTypeDef = TypedDict(
    "PartnerEventSourceAccountTypeDef",
    {
        "Account": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "ExpirationTime": NotRequired[datetime],
        "State": NotRequired[EventSourceStateType],
    },
)

ListPartnerEventSourcesRequestRequestTypeDef = TypedDict(
    "ListPartnerEventSourcesRequestRequestTypeDef",
    {
        "NamePrefix": str,
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

PartnerEventSourceTypeDef = TypedDict(
    "PartnerEventSourceTypeDef",
    {
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
    },
)

ListReplaysRequestRequestTypeDef = TypedDict(
    "ListReplaysRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "State": NotRequired[ReplayStateType],
        "EventSourceArn": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ReplayTypeDef = TypedDict(
    "ReplayTypeDef",
    {
        "ReplayName": NotRequired[str],
        "EventSourceArn": NotRequired[str],
        "State": NotRequired[ReplayStateType],
        "StateReason": NotRequired[str],
        "EventStartTime": NotRequired[datetime],
        "EventEndTime": NotRequired[datetime],
        "EventLastReplayedTime": NotRequired[datetime],
        "ReplayStartTime": NotRequired[datetime],
        "ReplayEndTime": NotRequired[datetime],
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

ListRuleNamesByTargetRequestRequestTypeDef = TypedDict(
    "ListRuleNamesByTargetRequestRequestTypeDef",
    {
        "TargetArn": str,
        "EventBusName": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

ListRulesRequestRequestTypeDef = TypedDict(
    "ListRulesRequestRequestTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "EventBusName": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "Name": NotRequired[str],
        "Arn": NotRequired[str],
        "EventPattern": NotRequired[str],
        "State": NotRequired[RuleStateType],
        "Description": NotRequired[str],
        "ScheduleExpression": NotRequired[str],
        "RoleArn": NotRequired[str],
        "ManagedBy": NotRequired[str],
        "EventBusName": NotRequired[str],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
    },
)

ListTargetsByRuleRequestRequestTypeDef = TypedDict(
    "ListTargetsByRuleRequestRequestTypeDef",
    {
        "Rule": str,
        "EventBusName": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

TimestampTypeDef = Union[datetime, str]
PutEventsResultEntryTypeDef = TypedDict(
    "PutEventsResultEntryTypeDef",
    {
        "EventId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

PutPartnerEventsResultEntryTypeDef = TypedDict(
    "PutPartnerEventsResultEntryTypeDef",
    {
        "EventId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

PutTargetsResultEntryTypeDef = TypedDict(
    "PutTargetsResultEntryTypeDef",
    {
        "TargetId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

RedshiftDataParametersTypeDef = TypedDict(
    "RedshiftDataParametersTypeDef",
    {
        "Database": str,
        "SecretManagerArn": NotRequired[str],
        "DbUser": NotRequired[str],
        "Sql": NotRequired[str],
        "StatementName": NotRequired[str],
        "WithEvent": NotRequired[bool],
        "Sqls": NotRequired[List[str]],
    },
)

RemovePermissionRequestRequestTypeDef = TypedDict(
    "RemovePermissionRequestRequestTypeDef",
    {
        "StatementId": NotRequired[str],
        "RemoveAllPermissions": NotRequired[bool],
        "EventBusName": NotRequired[str],
    },
)

RemoveTargetsRequestRequestTypeDef = TypedDict(
    "RemoveTargetsRequestRequestTypeDef",
    {
        "Rule": str,
        "Ids": Sequence[str],
        "EventBusName": NotRequired[str],
        "Force": NotRequired[bool],
    },
)

RemoveTargetsResultEntryTypeDef = TypedDict(
    "RemoveTargetsResultEntryTypeDef",
    {
        "TargetId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

RetryPolicyTypeDef = TypedDict(
    "RetryPolicyTypeDef",
    {
        "MaximumRetryAttempts": NotRequired[int],
        "MaximumEventAgeInSeconds": NotRequired[int],
    },
)

RunCommandTargetTypeDef = TypedDict(
    "RunCommandTargetTypeDef",
    {
        "Key": str,
        "Values": List[str],
    },
)

SageMakerPipelineParameterTypeDef = TypedDict(
    "SageMakerPipelineParameterTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)

SqsParametersTypeDef = TypedDict(
    "SqsParametersTypeDef",
    {
        "MessageGroupId": NotRequired[str],
    },
)

TestEventPatternRequestRequestTypeDef = TypedDict(
    "TestEventPatternRequestRequestTypeDef",
    {
        "EventPattern": str,
        "Event": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "TagKeys": Sequence[str],
    },
)

UpdateApiDestinationRequestRequestTypeDef = TypedDict(
    "UpdateApiDestinationRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "ConnectionArn": NotRequired[str],
        "InvocationEndpoint": NotRequired[str],
        "HttpMethod": NotRequired[ApiDestinationHttpMethodType],
        "InvocationRateLimitPerSecond": NotRequired[int],
    },
)

UpdateArchiveRequestRequestTypeDef = TypedDict(
    "UpdateArchiveRequestRequestTypeDef",
    {
        "ArchiveName": str,
        "Description": NotRequired[str],
        "EventPattern": NotRequired[str],
        "RetentionDays": NotRequired[int],
    },
)

UpdateConnectionApiKeyAuthRequestParametersTypeDef = TypedDict(
    "UpdateConnectionApiKeyAuthRequestParametersTypeDef",
    {
        "ApiKeyName": NotRequired[str],
        "ApiKeyValue": NotRequired[str],
    },
)

UpdateConnectionBasicAuthRequestParametersTypeDef = TypedDict(
    "UpdateConnectionBasicAuthRequestParametersTypeDef",
    {
        "Username": NotRequired[str],
        "Password": NotRequired[str],
    },
)

UpdateConnectionOAuthClientRequestParametersTypeDef = TypedDict(
    "UpdateConnectionOAuthClientRequestParametersTypeDef",
    {
        "ClientID": NotRequired[str],
        "ClientSecret": NotRequired[str],
    },
)

NetworkConfigurationTypeDef = TypedDict(
    "NetworkConfigurationTypeDef",
    {
        "awsvpcConfiguration": NotRequired[AwsVpcConfigurationTypeDef],
    },
)

BatchParametersTypeDef = TypedDict(
    "BatchParametersTypeDef",
    {
        "JobDefinition": str,
        "JobName": str,
        "ArrayProperties": NotRequired[BatchArrayPropertiesTypeDef],
        "RetryStrategy": NotRequired[BatchRetryStrategyTypeDef],
    },
)

CancelReplayResponseTypeDef = TypedDict(
    "CancelReplayResponseTypeDef",
    {
        "ReplayArn": str,
        "State": ReplayStateType,
        "StateReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateApiDestinationResponseTypeDef = TypedDict(
    "CreateApiDestinationResponseTypeDef",
    {
        "ApiDestinationArn": str,
        "ApiDestinationState": ApiDestinationStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateArchiveResponseTypeDef = TypedDict(
    "CreateArchiveResponseTypeDef",
    {
        "ArchiveArn": str,
        "State": ArchiveStateType,
        "StateReason": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateConnectionResponseTypeDef = TypedDict(
    "CreateConnectionResponseTypeDef",
    {
        "ConnectionArn": str,
        "ConnectionState": ConnectionStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEventBusResponseTypeDef = TypedDict(
    "CreateEventBusResponseTypeDef",
    {
        "EventBusArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePartnerEventSourceResponseTypeDef = TypedDict(
    "CreatePartnerEventSourceResponseTypeDef",
    {
        "EventSourceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeauthorizeConnectionResponseTypeDef = TypedDict(
    "DeauthorizeConnectionResponseTypeDef",
    {
        "ConnectionArn": str,
        "ConnectionState": ConnectionStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastAuthorizedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteConnectionResponseTypeDef = TypedDict(
    "DeleteConnectionResponseTypeDef",
    {
        "ConnectionArn": str,
        "ConnectionState": ConnectionStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastAuthorizedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeApiDestinationResponseTypeDef = TypedDict(
    "DescribeApiDestinationResponseTypeDef",
    {
        "ApiDestinationArn": str,
        "Name": str,
        "Description": str,
        "ApiDestinationState": ApiDestinationStateType,
        "ConnectionArn": str,
        "InvocationEndpoint": str,
        "HttpMethod": ApiDestinationHttpMethodType,
        "InvocationRateLimitPerSecond": int,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeArchiveResponseTypeDef = TypedDict(
    "DescribeArchiveResponseTypeDef",
    {
        "ArchiveArn": str,
        "ArchiveName": str,
        "EventSourceArn": str,
        "Description": str,
        "EventPattern": str,
        "State": ArchiveStateType,
        "StateReason": str,
        "RetentionDays": int,
        "SizeBytes": int,
        "EventCount": int,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEventBusResponseTypeDef = TypedDict(
    "DescribeEventBusResponseTypeDef",
    {
        "Name": str,
        "Arn": str,
        "Policy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEventSourceResponseTypeDef = TypedDict(
    "DescribeEventSourceResponseTypeDef",
    {
        "Arn": str,
        "CreatedBy": str,
        "CreationTime": datetime,
        "ExpirationTime": datetime,
        "Name": str,
        "State": EventSourceStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePartnerEventSourceResponseTypeDef = TypedDict(
    "DescribePartnerEventSourceResponseTypeDef",
    {
        "Arn": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRuleResponseTypeDef = TypedDict(
    "DescribeRuleResponseTypeDef",
    {
        "Name": str,
        "Arn": str,
        "EventPattern": str,
        "ScheduleExpression": str,
        "State": RuleStateType,
        "Description": str,
        "RoleArn": str,
        "ManagedBy": str,
        "EventBusName": str,
        "CreatedBy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListApiDestinationsResponseTypeDef = TypedDict(
    "ListApiDestinationsResponseTypeDef",
    {
        "ApiDestinations": List[ApiDestinationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListArchivesResponseTypeDef = TypedDict(
    "ListArchivesResponseTypeDef",
    {
        "Archives": List[ArchiveTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRuleNamesByTargetResponseTypeDef = TypedDict(
    "ListRuleNamesByTargetResponseTypeDef",
    {
        "RuleNames": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutRuleResponseTypeDef = TypedDict(
    "PutRuleResponseTypeDef",
    {
        "RuleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartReplayResponseTypeDef = TypedDict(
    "StartReplayResponseTypeDef",
    {
        "ReplayArn": str,
        "State": ReplayStateType,
        "StateReason": str,
        "ReplayStartTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TestEventPatternResponseTypeDef = TypedDict(
    "TestEventPatternResponseTypeDef",
    {
        "Result": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateApiDestinationResponseTypeDef = TypedDict(
    "UpdateApiDestinationResponseTypeDef",
    {
        "ApiDestinationArn": str,
        "ApiDestinationState": ApiDestinationStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateArchiveResponseTypeDef = TypedDict(
    "UpdateArchiveResponseTypeDef",
    {
        "ArchiveArn": str,
        "State": ArchiveStateType,
        "StateReason": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateConnectionResponseTypeDef = TypedDict(
    "UpdateConnectionResponseTypeDef",
    {
        "ConnectionArn": str,
        "ConnectionState": ConnectionStateType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastAuthorizedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutPermissionRequestRequestTypeDef = TypedDict(
    "PutPermissionRequestRequestTypeDef",
    {
        "EventBusName": NotRequired[str],
        "Action": NotRequired[str],
        "Principal": NotRequired[str],
        "StatementId": NotRequired[str],
        "Condition": NotRequired[ConditionTypeDef],
        "Policy": NotRequired[str],
    },
)

ConnectionHttpParametersTypeDef = TypedDict(
    "ConnectionHttpParametersTypeDef",
    {
        "HeaderParameters": NotRequired[Sequence[ConnectionHeaderParameterTypeDef]],
        "QueryStringParameters": NotRequired[Sequence[ConnectionQueryStringParameterTypeDef]],
        "BodyParameters": NotRequired[Sequence[ConnectionBodyParameterTypeDef]],
    },
)

ListConnectionsResponseTypeDef = TypedDict(
    "ListConnectionsResponseTypeDef",
    {
        "Connections": List[ConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEventBusRequestRequestTypeDef = TypedDict(
    "CreateEventBusRequestRequestTypeDef",
    {
        "Name": str,
        "EventSourceName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutRuleRequestRequestTypeDef = TypedDict(
    "PutRuleRequestRequestTypeDef",
    {
        "Name": str,
        "ScheduleExpression": NotRequired[str],
        "EventPattern": NotRequired[str],
        "State": NotRequired[RuleStateType],
        "Description": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "EventBusName": NotRequired[str],
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "Tags": Sequence[TagTypeDef],
    },
)

DescribeReplayResponseTypeDef = TypedDict(
    "DescribeReplayResponseTypeDef",
    {
        "ReplayName": str,
        "ReplayArn": str,
        "Description": str,
        "State": ReplayStateType,
        "StateReason": str,
        "EventSourceArn": str,
        "Destination": ReplayDestinationTypeDef,
        "EventStartTime": datetime,
        "EventEndTime": datetime,
        "EventLastReplayedTime": datetime,
        "ReplayStartTime": datetime,
        "ReplayEndTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEventBusesResponseTypeDef = TypedDict(
    "ListEventBusesResponseTypeDef",
    {
        "EventBuses": List[EventBusTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEventSourcesResponseTypeDef = TypedDict(
    "ListEventSourcesResponseTypeDef",
    {
        "EventSources": List[EventSourceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FailoverConfigTypeDef = TypedDict(
    "FailoverConfigTypeDef",
    {
        "Primary": PrimaryTypeDef,
        "Secondary": SecondaryTypeDef,
    },
)

ListPartnerEventSourceAccountsResponseTypeDef = TypedDict(
    "ListPartnerEventSourceAccountsResponseTypeDef",
    {
        "PartnerEventSourceAccounts": List[PartnerEventSourceAccountTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPartnerEventSourcesResponseTypeDef = TypedDict(
    "ListPartnerEventSourcesResponseTypeDef",
    {
        "PartnerEventSources": List[PartnerEventSourceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListReplaysResponseTypeDef = TypedDict(
    "ListReplaysResponseTypeDef",
    {
        "Replays": List[ReplayTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRuleNamesByTargetRequestListRuleNamesByTargetPaginateTypeDef = TypedDict(
    "ListRuleNamesByTargetRequestListRuleNamesByTargetPaginateTypeDef",
    {
        "TargetArn": str,
        "EventBusName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListRulesRequestListRulesPaginateTypeDef = TypedDict(
    "ListRulesRequestListRulesPaginateTypeDef",
    {
        "NamePrefix": NotRequired[str],
        "EventBusName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTargetsByRuleRequestListTargetsByRulePaginateTypeDef = TypedDict(
    "ListTargetsByRuleRequestListTargetsByRulePaginateTypeDef",
    {
        "Rule": str,
        "EventBusName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListRulesResponseTypeDef = TypedDict(
    "ListRulesResponseTypeDef",
    {
        "Rules": List[RuleTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutEventsRequestEntryTypeDef = TypedDict(
    "PutEventsRequestEntryTypeDef",
    {
        "Time": NotRequired[TimestampTypeDef],
        "Source": NotRequired[str],
        "Resources": NotRequired[Sequence[str]],
        "DetailType": NotRequired[str],
        "Detail": NotRequired[str],
        "EventBusName": NotRequired[str],
        "TraceHeader": NotRequired[str],
    },
)

PutPartnerEventsRequestEntryTypeDef = TypedDict(
    "PutPartnerEventsRequestEntryTypeDef",
    {
        "Time": NotRequired[TimestampTypeDef],
        "Source": NotRequired[str],
        "Resources": NotRequired[Sequence[str]],
        "DetailType": NotRequired[str],
        "Detail": NotRequired[str],
    },
)

StartReplayRequestRequestTypeDef = TypedDict(
    "StartReplayRequestRequestTypeDef",
    {
        "ReplayName": str,
        "EventSourceArn": str,
        "EventStartTime": TimestampTypeDef,
        "EventEndTime": TimestampTypeDef,
        "Destination": ReplayDestinationTypeDef,
        "Description": NotRequired[str],
    },
)

PutEventsResponseTypeDef = TypedDict(
    "PutEventsResponseTypeDef",
    {
        "FailedEntryCount": int,
        "Entries": List[PutEventsResultEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutPartnerEventsResponseTypeDef = TypedDict(
    "PutPartnerEventsResponseTypeDef",
    {
        "FailedEntryCount": int,
        "Entries": List[PutPartnerEventsResultEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutTargetsResponseTypeDef = TypedDict(
    "PutTargetsResponseTypeDef",
    {
        "FailedEntryCount": int,
        "FailedEntries": List[PutTargetsResultEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RemoveTargetsResponseTypeDef = TypedDict(
    "RemoveTargetsResponseTypeDef",
    {
        "FailedEntryCount": int,
        "FailedEntries": List[RemoveTargetsResultEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RunCommandParametersTypeDef = TypedDict(
    "RunCommandParametersTypeDef",
    {
        "RunCommandTargets": List[RunCommandTargetTypeDef],
    },
)

SageMakerPipelineParametersTypeDef = TypedDict(
    "SageMakerPipelineParametersTypeDef",
    {
        "PipelineParameterList": NotRequired[List[SageMakerPipelineParameterTypeDef]],
    },
)

EcsParametersTypeDef = TypedDict(
    "EcsParametersTypeDef",
    {
        "TaskDefinitionArn": str,
        "TaskCount": NotRequired[int],
        "LaunchType": NotRequired[LaunchTypeType],
        "NetworkConfiguration": NotRequired[NetworkConfigurationTypeDef],
        "PlatformVersion": NotRequired[str],
        "Group": NotRequired[str],
        "CapacityProviderStrategy": NotRequired[List[CapacityProviderStrategyItemTypeDef]],
        "EnableECSManagedTags": NotRequired[bool],
        "EnableExecuteCommand": NotRequired[bool],
        "PlacementConstraints": NotRequired[List[PlacementConstraintTypeDef]],
        "PlacementStrategy": NotRequired[List[PlacementStrategyTypeDef]],
        "PropagateTags": NotRequired[Literal["TASK_DEFINITION"]],
        "ReferenceId": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

ConnectionOAuthResponseParametersTypeDef = TypedDict(
    "ConnectionOAuthResponseParametersTypeDef",
    {
        "ClientParameters": NotRequired[ConnectionOAuthClientResponseParametersTypeDef],
        "AuthorizationEndpoint": NotRequired[str],
        "HttpMethod": NotRequired[ConnectionOAuthHttpMethodType],
        "OAuthHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

CreateConnectionOAuthRequestParametersTypeDef = TypedDict(
    "CreateConnectionOAuthRequestParametersTypeDef",
    {
        "ClientParameters": CreateConnectionOAuthClientRequestParametersTypeDef,
        "AuthorizationEndpoint": str,
        "HttpMethod": ConnectionOAuthHttpMethodType,
        "OAuthHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

UpdateConnectionOAuthRequestParametersTypeDef = TypedDict(
    "UpdateConnectionOAuthRequestParametersTypeDef",
    {
        "ClientParameters": NotRequired[UpdateConnectionOAuthClientRequestParametersTypeDef],
        "AuthorizationEndpoint": NotRequired[str],
        "HttpMethod": NotRequired[ConnectionOAuthHttpMethodType],
        "OAuthHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

RoutingConfigTypeDef = TypedDict(
    "RoutingConfigTypeDef",
    {
        "FailoverConfig": FailoverConfigTypeDef,
    },
)

PutEventsRequestRequestTypeDef = TypedDict(
    "PutEventsRequestRequestTypeDef",
    {
        "Entries": Sequence[PutEventsRequestEntryTypeDef],
        "EndpointId": NotRequired[str],
    },
)

PutPartnerEventsRequestRequestTypeDef = TypedDict(
    "PutPartnerEventsRequestRequestTypeDef",
    {
        "Entries": Sequence[PutPartnerEventsRequestEntryTypeDef],
    },
)

TargetTypeDef = TypedDict(
    "TargetTypeDef",
    {
        "Id": str,
        "Arn": str,
        "RoleArn": NotRequired[str],
        "Input": NotRequired[str],
        "InputPath": NotRequired[str],
        "InputTransformer": NotRequired[InputTransformerTypeDef],
        "KinesisParameters": NotRequired[KinesisParametersTypeDef],
        "RunCommandParameters": NotRequired[RunCommandParametersTypeDef],
        "EcsParameters": NotRequired[EcsParametersTypeDef],
        "BatchParameters": NotRequired[BatchParametersTypeDef],
        "SqsParameters": NotRequired[SqsParametersTypeDef],
        "HttpParameters": NotRequired[HttpParametersTypeDef],
        "RedshiftDataParameters": NotRequired[RedshiftDataParametersTypeDef],
        "SageMakerPipelineParameters": NotRequired[SageMakerPipelineParametersTypeDef],
        "DeadLetterConfig": NotRequired[DeadLetterConfigTypeDef],
        "RetryPolicy": NotRequired[RetryPolicyTypeDef],
    },
)

ConnectionAuthResponseParametersTypeDef = TypedDict(
    "ConnectionAuthResponseParametersTypeDef",
    {
        "BasicAuthParameters": NotRequired[ConnectionBasicAuthResponseParametersTypeDef],
        "OAuthParameters": NotRequired[ConnectionOAuthResponseParametersTypeDef],
        "ApiKeyAuthParameters": NotRequired[ConnectionApiKeyAuthResponseParametersTypeDef],
        "InvocationHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

CreateConnectionAuthRequestParametersTypeDef = TypedDict(
    "CreateConnectionAuthRequestParametersTypeDef",
    {
        "BasicAuthParameters": NotRequired[CreateConnectionBasicAuthRequestParametersTypeDef],
        "OAuthParameters": NotRequired[CreateConnectionOAuthRequestParametersTypeDef],
        "ApiKeyAuthParameters": NotRequired[CreateConnectionApiKeyAuthRequestParametersTypeDef],
        "InvocationHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

UpdateConnectionAuthRequestParametersTypeDef = TypedDict(
    "UpdateConnectionAuthRequestParametersTypeDef",
    {
        "BasicAuthParameters": NotRequired[UpdateConnectionBasicAuthRequestParametersTypeDef],
        "OAuthParameters": NotRequired[UpdateConnectionOAuthRequestParametersTypeDef],
        "ApiKeyAuthParameters": NotRequired[UpdateConnectionApiKeyAuthRequestParametersTypeDef],
        "InvocationHttpParameters": NotRequired[ConnectionHttpParametersTypeDef],
    },
)

CreateEndpointRequestRequestTypeDef = TypedDict(
    "CreateEndpointRequestRequestTypeDef",
    {
        "Name": str,
        "RoutingConfig": RoutingConfigTypeDef,
        "EventBuses": Sequence[EndpointEventBusTypeDef],
        "Description": NotRequired[str],
        "ReplicationConfig": NotRequired[ReplicationConfigTypeDef],
        "RoleArn": NotRequired[str],
    },
)

CreateEndpointResponseTypeDef = TypedDict(
    "CreateEndpointResponseTypeDef",
    {
        "Name": str,
        "Arn": str,
        "RoutingConfig": RoutingConfigTypeDef,
        "ReplicationConfig": ReplicationConfigTypeDef,
        "EventBuses": List[EndpointEventBusTypeDef],
        "RoleArn": str,
        "State": EndpointStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEndpointResponseTypeDef = TypedDict(
    "DescribeEndpointResponseTypeDef",
    {
        "Name": str,
        "Description": str,
        "Arn": str,
        "RoutingConfig": RoutingConfigTypeDef,
        "ReplicationConfig": ReplicationConfigTypeDef,
        "EventBuses": List[EndpointEventBusTypeDef],
        "RoleArn": str,
        "EndpointId": str,
        "EndpointUrl": str,
        "State": EndpointStateType,
        "StateReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Arn": NotRequired[str],
        "RoutingConfig": NotRequired[RoutingConfigTypeDef],
        "ReplicationConfig": NotRequired[ReplicationConfigTypeDef],
        "EventBuses": NotRequired[List[EndpointEventBusTypeDef]],
        "RoleArn": NotRequired[str],
        "EndpointId": NotRequired[str],
        "EndpointUrl": NotRequired[str],
        "State": NotRequired[EndpointStateType],
        "StateReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

UpdateEndpointRequestRequestTypeDef = TypedDict(
    "UpdateEndpointRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "RoutingConfig": NotRequired[RoutingConfigTypeDef],
        "ReplicationConfig": NotRequired[ReplicationConfigTypeDef],
        "EventBuses": NotRequired[Sequence[EndpointEventBusTypeDef]],
        "RoleArn": NotRequired[str],
    },
)

UpdateEndpointResponseTypeDef = TypedDict(
    "UpdateEndpointResponseTypeDef",
    {
        "Name": str,
        "Arn": str,
        "RoutingConfig": RoutingConfigTypeDef,
        "ReplicationConfig": ReplicationConfigTypeDef,
        "EventBuses": List[EndpointEventBusTypeDef],
        "RoleArn": str,
        "EndpointId": str,
        "EndpointUrl": str,
        "State": EndpointStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTargetsByRuleResponseTypeDef = TypedDict(
    "ListTargetsByRuleResponseTypeDef",
    {
        "Targets": List[TargetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutTargetsRequestRequestTypeDef = TypedDict(
    "PutTargetsRequestRequestTypeDef",
    {
        "Rule": str,
        "Targets": Sequence[TargetTypeDef],
        "EventBusName": NotRequired[str],
    },
)

DescribeConnectionResponseTypeDef = TypedDict(
    "DescribeConnectionResponseTypeDef",
    {
        "ConnectionArn": str,
        "Name": str,
        "Description": str,
        "ConnectionState": ConnectionStateType,
        "StateReason": str,
        "AuthorizationType": ConnectionAuthorizationTypeType,
        "SecretArn": str,
        "AuthParameters": ConnectionAuthResponseParametersTypeDef,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastAuthorizedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateConnectionRequestRequestTypeDef = TypedDict(
    "CreateConnectionRequestRequestTypeDef",
    {
        "Name": str,
        "AuthorizationType": ConnectionAuthorizationTypeType,
        "AuthParameters": CreateConnectionAuthRequestParametersTypeDef,
        "Description": NotRequired[str],
    },
)

UpdateConnectionRequestRequestTypeDef = TypedDict(
    "UpdateConnectionRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "AuthorizationType": NotRequired[ConnectionAuthorizationTypeType],
        "AuthParameters": NotRequired[UpdateConnectionAuthRequestParametersTypeDef],
    },
)

ListEndpointsResponseTypeDef = TypedDict(
    "ListEndpointsResponseTypeDef",
    {
        "Endpoints": List[EndpointTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
