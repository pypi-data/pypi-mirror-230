"""
Type annotations for ivs-realtime service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivs_realtime/type_defs/)

Usage::

    ```python
    from mypy_boto3_ivs_realtime.type_defs import CreateParticipantTokenRequestRequestTypeDef

    data: CreateParticipantTokenRequestRequestTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    EventErrorCodeType,
    EventNameType,
    ParticipantStateType,
    ParticipantTokenCapabilityType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "CreateParticipantTokenRequestRequestTypeDef",
    "ParticipantTokenTypeDef",
    "ResponseMetadataTypeDef",
    "ParticipantTokenConfigurationTypeDef",
    "StageTypeDef",
    "DeleteStageRequestRequestTypeDef",
    "DisconnectParticipantRequestRequestTypeDef",
    "EventTypeDef",
    "GetParticipantRequestRequestTypeDef",
    "ParticipantTypeDef",
    "GetStageRequestRequestTypeDef",
    "GetStageSessionRequestRequestTypeDef",
    "StageSessionTypeDef",
    "ListParticipantEventsRequestRequestTypeDef",
    "ListParticipantsRequestRequestTypeDef",
    "ParticipantSummaryTypeDef",
    "ListStageSessionsRequestRequestTypeDef",
    "StageSessionSummaryTypeDef",
    "ListStagesRequestRequestTypeDef",
    "StageSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateStageRequestRequestTypeDef",
    "CreateParticipantTokenResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "CreateStageRequestRequestTypeDef",
    "CreateStageResponseTypeDef",
    "GetStageResponseTypeDef",
    "UpdateStageResponseTypeDef",
    "ListParticipantEventsResponseTypeDef",
    "GetParticipantResponseTypeDef",
    "GetStageSessionResponseTypeDef",
    "ListParticipantsResponseTypeDef",
    "ListStageSessionsResponseTypeDef",
    "ListStagesResponseTypeDef",
)

CreateParticipantTokenRequestRequestTypeDef = TypedDict(
    "CreateParticipantTokenRequestRequestTypeDef",
    {
        "stageArn": str,
        "attributes": NotRequired[Mapping[str, str]],
        "capabilities": NotRequired[Sequence[ParticipantTokenCapabilityType]],
        "duration": NotRequired[int],
        "userId": NotRequired[str],
    },
)

ParticipantTokenTypeDef = TypedDict(
    "ParticipantTokenTypeDef",
    {
        "attributes": NotRequired[Dict[str, str]],
        "capabilities": NotRequired[List[ParticipantTokenCapabilityType]],
        "duration": NotRequired[int],
        "expirationTime": NotRequired[datetime],
        "participantId": NotRequired[str],
        "token": NotRequired[str],
        "userId": NotRequired[str],
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

ParticipantTokenConfigurationTypeDef = TypedDict(
    "ParticipantTokenConfigurationTypeDef",
    {
        "attributes": NotRequired[Mapping[str, str]],
        "capabilities": NotRequired[Sequence[ParticipantTokenCapabilityType]],
        "duration": NotRequired[int],
        "userId": NotRequired[str],
    },
)

StageTypeDef = TypedDict(
    "StageTypeDef",
    {
        "arn": str,
        "activeSessionId": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)

DeleteStageRequestRequestTypeDef = TypedDict(
    "DeleteStageRequestRequestTypeDef",
    {
        "arn": str,
    },
)

DisconnectParticipantRequestRequestTypeDef = TypedDict(
    "DisconnectParticipantRequestRequestTypeDef",
    {
        "participantId": str,
        "stageArn": str,
        "reason": NotRequired[str],
    },
)

EventTypeDef = TypedDict(
    "EventTypeDef",
    {
        "errorCode": NotRequired[EventErrorCodeType],
        "eventTime": NotRequired[datetime],
        "name": NotRequired[EventNameType],
        "participantId": NotRequired[str],
        "remoteParticipantId": NotRequired[str],
    },
)

GetParticipantRequestRequestTypeDef = TypedDict(
    "GetParticipantRequestRequestTypeDef",
    {
        "participantId": str,
        "sessionId": str,
        "stageArn": str,
    },
)

ParticipantTypeDef = TypedDict(
    "ParticipantTypeDef",
    {
        "attributes": NotRequired[Dict[str, str]],
        "firstJoinTime": NotRequired[datetime],
        "participantId": NotRequired[str],
        "published": NotRequired[bool],
        "state": NotRequired[ParticipantStateType],
        "userId": NotRequired[str],
    },
)

GetStageRequestRequestTypeDef = TypedDict(
    "GetStageRequestRequestTypeDef",
    {
        "arn": str,
    },
)

GetStageSessionRequestRequestTypeDef = TypedDict(
    "GetStageSessionRequestRequestTypeDef",
    {
        "sessionId": str,
        "stageArn": str,
    },
)

StageSessionTypeDef = TypedDict(
    "StageSessionTypeDef",
    {
        "endTime": NotRequired[datetime],
        "sessionId": NotRequired[str],
        "startTime": NotRequired[datetime],
    },
)

ListParticipantEventsRequestRequestTypeDef = TypedDict(
    "ListParticipantEventsRequestRequestTypeDef",
    {
        "participantId": str,
        "sessionId": str,
        "stageArn": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

ListParticipantsRequestRequestTypeDef = TypedDict(
    "ListParticipantsRequestRequestTypeDef",
    {
        "sessionId": str,
        "stageArn": str,
        "filterByPublished": NotRequired[bool],
        "filterByState": NotRequired[ParticipantStateType],
        "filterByUserId": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

ParticipantSummaryTypeDef = TypedDict(
    "ParticipantSummaryTypeDef",
    {
        "firstJoinTime": NotRequired[datetime],
        "participantId": NotRequired[str],
        "published": NotRequired[bool],
        "state": NotRequired[ParticipantStateType],
        "userId": NotRequired[str],
    },
)

ListStageSessionsRequestRequestTypeDef = TypedDict(
    "ListStageSessionsRequestRequestTypeDef",
    {
        "stageArn": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

StageSessionSummaryTypeDef = TypedDict(
    "StageSessionSummaryTypeDef",
    {
        "endTime": NotRequired[datetime],
        "sessionId": NotRequired[str],
        "startTime": NotRequired[datetime],
    },
)

ListStagesRequestRequestTypeDef = TypedDict(
    "ListStagesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

StageSummaryTypeDef = TypedDict(
    "StageSummaryTypeDef",
    {
        "arn": str,
        "activeSessionId": NotRequired[str],
        "name": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

UpdateStageRequestRequestTypeDef = TypedDict(
    "UpdateStageRequestRequestTypeDef",
    {
        "arn": str,
        "name": NotRequired[str],
    },
)

CreateParticipantTokenResponseTypeDef = TypedDict(
    "CreateParticipantTokenResponseTypeDef",
    {
        "participantToken": ParticipantTokenTypeDef,
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

CreateStageRequestRequestTypeDef = TypedDict(
    "CreateStageRequestRequestTypeDef",
    {
        "name": NotRequired[str],
        "participantTokenConfigurations": NotRequired[
            Sequence[ParticipantTokenConfigurationTypeDef]
        ],
        "tags": NotRequired[Mapping[str, str]],
    },
)

CreateStageResponseTypeDef = TypedDict(
    "CreateStageResponseTypeDef",
    {
        "participantTokens": List[ParticipantTokenTypeDef],
        "stage": StageTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetStageResponseTypeDef = TypedDict(
    "GetStageResponseTypeDef",
    {
        "stage": StageTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateStageResponseTypeDef = TypedDict(
    "UpdateStageResponseTypeDef",
    {
        "stage": StageTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListParticipantEventsResponseTypeDef = TypedDict(
    "ListParticipantEventsResponseTypeDef",
    {
        "events": List[EventTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetParticipantResponseTypeDef = TypedDict(
    "GetParticipantResponseTypeDef",
    {
        "participant": ParticipantTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetStageSessionResponseTypeDef = TypedDict(
    "GetStageSessionResponseTypeDef",
    {
        "stageSession": StageSessionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListParticipantsResponseTypeDef = TypedDict(
    "ListParticipantsResponseTypeDef",
    {
        "nextToken": str,
        "participants": List[ParticipantSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStageSessionsResponseTypeDef = TypedDict(
    "ListStageSessionsResponseTypeDef",
    {
        "nextToken": str,
        "stageSessions": List[StageSessionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStagesResponseTypeDef = TypedDict(
    "ListStagesResponseTypeDef",
    {
        "nextToken": str,
        "stages": List[StageSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
