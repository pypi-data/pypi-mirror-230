"""
Type annotations for drs service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_drs/type_defs/)

Usage::

    ```python
    from mypy_boto3_drs.type_defs import AccountTypeDef

    data: AccountTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    DataReplicationErrorStringType,
    DataReplicationInitiationStepNameType,
    DataReplicationInitiationStepStatusType,
    DataReplicationStateType,
    EC2InstanceStateType,
    ExtensionStatusType,
    FailbackLaunchTypeType,
    FailbackReplicationErrorType,
    FailbackStateType,
    InitiatedByType,
    JobLogEventType,
    JobStatusType,
    JobTypeType,
    LastLaunchResultType,
    LastLaunchTypeType,
    LaunchActionCategoryType,
    LaunchActionParameterTypeType,
    LaunchActionRunStatusType,
    LaunchActionTypeType,
    LaunchDispositionType,
    LaunchStatusType,
    OriginEnvironmentType,
    PITPolicyRuleUnitsType,
    RecoveryInstanceDataReplicationInitiationStepNameType,
    RecoveryInstanceDataReplicationInitiationStepStatusType,
    RecoveryInstanceDataReplicationStateType,
    RecoveryResultType,
    RecoverySnapshotsOrderType,
    ReplicationConfigurationDataPlaneRoutingType,
    ReplicationConfigurationDefaultLargeStagingDiskTypeType,
    ReplicationConfigurationEbsEncryptionType,
    ReplicationConfigurationReplicatedDiskStagingDiskTypeType,
    ReplicationDirectionType,
    ReplicationStatusType,
    TargetInstanceTypeRightSizingMethodType,
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
    "AccountTypeDef",
    "AssociateSourceNetworkStackRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "CPUTypeDef",
    "ConversionPropertiesTypeDef",
    "CreateExtendedSourceServerRequestRequestTypeDef",
    "LicensingTypeDef",
    "PITPolicyRuleTypeDef",
    "CreateSourceNetworkRequestRequestTypeDef",
    "DataReplicationErrorTypeDef",
    "DataReplicationInfoReplicatedDiskTypeDef",
    "DataReplicationInitiationStepTypeDef",
    "DeleteJobRequestRequestTypeDef",
    "DeleteLaunchActionRequestRequestTypeDef",
    "DeleteLaunchConfigurationTemplateRequestRequestTypeDef",
    "DeleteRecoveryInstanceRequestRequestTypeDef",
    "DeleteReplicationConfigurationTemplateRequestRequestTypeDef",
    "DeleteSourceNetworkRequestRequestTypeDef",
    "DeleteSourceServerRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeJobLogItemsRequestRequestTypeDef",
    "DescribeJobsRequestFiltersTypeDef",
    "DescribeLaunchConfigurationTemplatesRequestRequestTypeDef",
    "DescribeRecoveryInstancesRequestFiltersTypeDef",
    "DescribeRecoverySnapshotsRequestFiltersTypeDef",
    "RecoverySnapshotTypeDef",
    "DescribeReplicationConfigurationTemplatesRequestRequestTypeDef",
    "DescribeSourceNetworksRequestFiltersTypeDef",
    "DescribeSourceServersRequestFiltersTypeDef",
    "DisconnectRecoveryInstanceRequestRequestTypeDef",
    "DisconnectSourceServerRequestRequestTypeDef",
    "DiskTypeDef",
    "SourceNetworkDataTypeDef",
    "ExportSourceNetworkCfnTemplateRequestRequestTypeDef",
    "GetFailbackReplicationConfigurationRequestRequestTypeDef",
    "GetLaunchConfigurationRequestRequestTypeDef",
    "GetReplicationConfigurationRequestRequestTypeDef",
    "IdentificationHintsTypeDef",
    "LaunchActionParameterTypeDef",
    "LaunchActionsRequestFiltersTypeDef",
    "LifeCycleLastLaunchInitiatedTypeDef",
    "ListExtensibleSourceServersRequestRequestTypeDef",
    "StagingSourceServerTypeDef",
    "ListStagingAccountsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "NetworkInterfaceTypeDef",
    "OSTypeDef",
    "ParticipatingResourceIDTypeDef",
    "RecoveryInstanceDataReplicationErrorTypeDef",
    "RecoveryInstanceDataReplicationInfoReplicatedDiskTypeDef",
    "RecoveryInstanceDataReplicationInitiationStepTypeDef",
    "RecoveryInstanceDiskTypeDef",
    "RecoveryInstanceFailbackTypeDef",
    "RecoveryLifeCycleTypeDef",
    "ReplicationConfigurationReplicatedDiskTypeDef",
    "RetryDataReplicationRequestRequestTypeDef",
    "ReverseReplicationRequestRequestTypeDef",
    "SourceCloudPropertiesTypeDef",
    "StagingAreaTypeDef",
    "StartFailbackLaunchRequestRequestTypeDef",
    "StartRecoveryRequestSourceServerTypeDef",
    "StartReplicationRequestRequestTypeDef",
    "StartSourceNetworkRecoveryRequestNetworkEntryTypeDef",
    "StartSourceNetworkReplicationRequestRequestTypeDef",
    "StopFailbackRequestRequestTypeDef",
    "StopReplicationRequestRequestTypeDef",
    "StopSourceNetworkReplicationRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TerminateRecoveryInstancesRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateFailbackReplicationConfigurationRequestRequestTypeDef",
    "CreateSourceNetworkResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ExportSourceNetworkCfnTemplateResponseTypeDef",
    "GetFailbackReplicationConfigurationResponseTypeDef",
    "ListStagingAccountsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ReverseReplicationResponseTypeDef",
    "CreateLaunchConfigurationTemplateRequestRequestTypeDef",
    "LaunchConfigurationTemplateTypeDef",
    "LaunchConfigurationTypeDef",
    "UpdateLaunchConfigurationRequestRequestTypeDef",
    "UpdateLaunchConfigurationTemplateRequestRequestTypeDef",
    "CreateReplicationConfigurationTemplateRequestRequestTypeDef",
    "ReplicationConfigurationTemplateResponseTypeDef",
    "ReplicationConfigurationTemplateTypeDef",
    "UpdateReplicationConfigurationTemplateRequestRequestTypeDef",
    "DataReplicationInitiationTypeDef",
    "DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef",
    "DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef",
    "DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef",
    "ListExtensibleSourceServersRequestListExtensibleSourceServersPaginateTypeDef",
    "ListStagingAccountsRequestListStagingAccountsPaginateTypeDef",
    "DescribeJobsRequestDescribeJobsPaginateTypeDef",
    "DescribeJobsRequestRequestTypeDef",
    "DescribeRecoveryInstancesRequestDescribeRecoveryInstancesPaginateTypeDef",
    "DescribeRecoveryInstancesRequestRequestTypeDef",
    "DescribeRecoverySnapshotsRequestDescribeRecoverySnapshotsPaginateTypeDef",
    "DescribeRecoverySnapshotsRequestRequestTypeDef",
    "DescribeRecoverySnapshotsResponseTypeDef",
    "DescribeSourceNetworksRequestDescribeSourceNetworksPaginateTypeDef",
    "DescribeSourceNetworksRequestRequestTypeDef",
    "DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef",
    "DescribeSourceServersRequestRequestTypeDef",
    "EventResourceDataTypeDef",
    "LaunchActionTypeDef",
    "PutLaunchActionRequestRequestTypeDef",
    "PutLaunchActionResponseTypeDef",
    "ListLaunchActionsRequestListLaunchActionsPaginateTypeDef",
    "ListLaunchActionsRequestRequestTypeDef",
    "LifeCycleLastLaunchTypeDef",
    "ListExtensibleSourceServersResponseTypeDef",
    "SourcePropertiesTypeDef",
    "ParticipatingResourceTypeDef",
    "RecoveryInstanceDataReplicationInitiationTypeDef",
    "RecoveryInstancePropertiesTypeDef",
    "SourceNetworkTypeDef",
    "ReplicationConfigurationTypeDef",
    "UpdateReplicationConfigurationRequestRequestTypeDef",
    "StartRecoveryRequestRequestTypeDef",
    "StartSourceNetworkRecoveryRequestRequestTypeDef",
    "CreateLaunchConfigurationTemplateResponseTypeDef",
    "DescribeLaunchConfigurationTemplatesResponseTypeDef",
    "UpdateLaunchConfigurationTemplateResponseTypeDef",
    "DescribeReplicationConfigurationTemplatesResponseTypeDef",
    "DataReplicationInfoTypeDef",
    "JobLogEventDataTypeDef",
    "LaunchActionRunTypeDef",
    "ListLaunchActionsResponseTypeDef",
    "LifeCycleTypeDef",
    "RecoveryInstanceDataReplicationInfoTypeDef",
    "DescribeSourceNetworksResponseTypeDef",
    "StartSourceNetworkReplicationResponseTypeDef",
    "StopSourceNetworkReplicationResponseTypeDef",
    "JobLogTypeDef",
    "LaunchActionsStatusTypeDef",
    "SourceServerResponseTypeDef",
    "SourceServerTypeDef",
    "RecoveryInstanceTypeDef",
    "DescribeJobLogItemsResponseTypeDef",
    "ParticipatingServerTypeDef",
    "CreateExtendedSourceServerResponseTypeDef",
    "DescribeSourceServersResponseTypeDef",
    "StartReplicationResponseTypeDef",
    "StopReplicationResponseTypeDef",
    "DescribeRecoveryInstancesResponseTypeDef",
    "JobTypeDef",
    "AssociateSourceNetworkStackResponseTypeDef",
    "DescribeJobsResponseTypeDef",
    "StartFailbackLaunchResponseTypeDef",
    "StartRecoveryResponseTypeDef",
    "StartSourceNetworkRecoveryResponseTypeDef",
    "TerminateRecoveryInstancesResponseTypeDef",
)

AccountTypeDef = TypedDict(
    "AccountTypeDef",
    {
        "accountID": NotRequired[str],
    },
)

AssociateSourceNetworkStackRequestRequestTypeDef = TypedDict(
    "AssociateSourceNetworkStackRequestRequestTypeDef",
    {
        "cfnStackName": str,
        "sourceNetworkID": str,
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

CPUTypeDef = TypedDict(
    "CPUTypeDef",
    {
        "cores": NotRequired[int],
        "modelName": NotRequired[str],
    },
)

ConversionPropertiesTypeDef = TypedDict(
    "ConversionPropertiesTypeDef",
    {
        "dataTimestamp": NotRequired[str],
        "forceUefi": NotRequired[bool],
        "rootVolumeName": NotRequired[str],
        "volumeToConversionMap": NotRequired[Dict[str, Dict[str, str]]],
        "volumeToVolumeSize": NotRequired[Dict[str, int]],
    },
)

CreateExtendedSourceServerRequestRequestTypeDef = TypedDict(
    "CreateExtendedSourceServerRequestRequestTypeDef",
    {
        "sourceServerArn": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)

LicensingTypeDef = TypedDict(
    "LicensingTypeDef",
    {
        "osByol": NotRequired[bool],
    },
)

PITPolicyRuleTypeDef = TypedDict(
    "PITPolicyRuleTypeDef",
    {
        "interval": int,
        "retentionDuration": int,
        "units": PITPolicyRuleUnitsType,
        "enabled": NotRequired[bool],
        "ruleID": NotRequired[int],
    },
)

CreateSourceNetworkRequestRequestTypeDef = TypedDict(
    "CreateSourceNetworkRequestRequestTypeDef",
    {
        "originAccountID": str,
        "originRegion": str,
        "vpcID": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)

DataReplicationErrorTypeDef = TypedDict(
    "DataReplicationErrorTypeDef",
    {
        "error": NotRequired[DataReplicationErrorStringType],
        "rawError": NotRequired[str],
    },
)

DataReplicationInfoReplicatedDiskTypeDef = TypedDict(
    "DataReplicationInfoReplicatedDiskTypeDef",
    {
        "backloggedStorageBytes": NotRequired[int],
        "deviceName": NotRequired[str],
        "replicatedStorageBytes": NotRequired[int],
        "rescannedStorageBytes": NotRequired[int],
        "totalStorageBytes": NotRequired[int],
    },
)

DataReplicationInitiationStepTypeDef = TypedDict(
    "DataReplicationInitiationStepTypeDef",
    {
        "name": NotRequired[DataReplicationInitiationStepNameType],
        "status": NotRequired[DataReplicationInitiationStepStatusType],
    },
)

DeleteJobRequestRequestTypeDef = TypedDict(
    "DeleteJobRequestRequestTypeDef",
    {
        "jobID": str,
    },
)

DeleteLaunchActionRequestRequestTypeDef = TypedDict(
    "DeleteLaunchActionRequestRequestTypeDef",
    {
        "actionId": str,
        "resourceId": str,
    },
)

DeleteLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "DeleteLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "launchConfigurationTemplateID": str,
    },
)

DeleteRecoveryInstanceRequestRequestTypeDef = TypedDict(
    "DeleteRecoveryInstanceRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
    },
)

DeleteReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "DeleteReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "replicationConfigurationTemplateID": str,
    },
)

DeleteSourceNetworkRequestRequestTypeDef = TypedDict(
    "DeleteSourceNetworkRequestRequestTypeDef",
    {
        "sourceNetworkID": str,
    },
)

DeleteSourceServerRequestRequestTypeDef = TypedDict(
    "DeleteSourceServerRequestRequestTypeDef",
    {
        "sourceServerID": str,
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

DescribeJobLogItemsRequestRequestTypeDef = TypedDict(
    "DescribeJobLogItemsRequestRequestTypeDef",
    {
        "jobID": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

DescribeJobsRequestFiltersTypeDef = TypedDict(
    "DescribeJobsRequestFiltersTypeDef",
    {
        "fromDate": NotRequired[str],
        "jobIDs": NotRequired[Sequence[str]],
        "toDate": NotRequired[str],
    },
)

DescribeLaunchConfigurationTemplatesRequestRequestTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesRequestRequestTypeDef",
    {
        "launchConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

DescribeRecoveryInstancesRequestFiltersTypeDef = TypedDict(
    "DescribeRecoveryInstancesRequestFiltersTypeDef",
    {
        "recoveryInstanceIDs": NotRequired[Sequence[str]],
        "sourceServerIDs": NotRequired[Sequence[str]],
    },
)

DescribeRecoverySnapshotsRequestFiltersTypeDef = TypedDict(
    "DescribeRecoverySnapshotsRequestFiltersTypeDef",
    {
        "fromDateTime": NotRequired[str],
        "toDateTime": NotRequired[str],
    },
)

RecoverySnapshotTypeDef = TypedDict(
    "RecoverySnapshotTypeDef",
    {
        "expectedTimestamp": str,
        "snapshotID": str,
        "sourceServerID": str,
        "ebsSnapshots": NotRequired[List[str]],
        "timestamp": NotRequired[str],
    },
)

DescribeReplicationConfigurationTemplatesRequestRequestTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "replicationConfigurationTemplateIDs": NotRequired[Sequence[str]],
    },
)

DescribeSourceNetworksRequestFiltersTypeDef = TypedDict(
    "DescribeSourceNetworksRequestFiltersTypeDef",
    {
        "originAccountID": NotRequired[str],
        "originRegion": NotRequired[str],
        "sourceNetworkIDs": NotRequired[Sequence[str]],
    },
)

DescribeSourceServersRequestFiltersTypeDef = TypedDict(
    "DescribeSourceServersRequestFiltersTypeDef",
    {
        "hardwareId": NotRequired[str],
        "sourceServerIDs": NotRequired[Sequence[str]],
        "stagingAccountIDs": NotRequired[Sequence[str]],
    },
)

DisconnectRecoveryInstanceRequestRequestTypeDef = TypedDict(
    "DisconnectRecoveryInstanceRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
    },
)

DisconnectSourceServerRequestRequestTypeDef = TypedDict(
    "DisconnectSourceServerRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

DiskTypeDef = TypedDict(
    "DiskTypeDef",
    {
        "bytes": NotRequired[int],
        "deviceName": NotRequired[str],
    },
)

SourceNetworkDataTypeDef = TypedDict(
    "SourceNetworkDataTypeDef",
    {
        "sourceNetworkID": NotRequired[str],
        "sourceVpc": NotRequired[str],
        "stackName": NotRequired[str],
        "targetVpc": NotRequired[str],
    },
)

ExportSourceNetworkCfnTemplateRequestRequestTypeDef = TypedDict(
    "ExportSourceNetworkCfnTemplateRequestRequestTypeDef",
    {
        "sourceNetworkID": str,
    },
)

GetFailbackReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "GetFailbackReplicationConfigurationRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
    },
)

GetLaunchConfigurationRequestRequestTypeDef = TypedDict(
    "GetLaunchConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

GetReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "GetReplicationConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

IdentificationHintsTypeDef = TypedDict(
    "IdentificationHintsTypeDef",
    {
        "awsInstanceID": NotRequired[str],
        "fqdn": NotRequired[str],
        "hostname": NotRequired[str],
        "vmWareUuid": NotRequired[str],
    },
)

LaunchActionParameterTypeDef = TypedDict(
    "LaunchActionParameterTypeDef",
    {
        "type": NotRequired[LaunchActionParameterTypeType],
        "value": NotRequired[str],
    },
)

LaunchActionsRequestFiltersTypeDef = TypedDict(
    "LaunchActionsRequestFiltersTypeDef",
    {
        "actionIds": NotRequired[Sequence[str]],
    },
)

LifeCycleLastLaunchInitiatedTypeDef = TypedDict(
    "LifeCycleLastLaunchInitiatedTypeDef",
    {
        "apiCallDateTime": NotRequired[str],
        "jobID": NotRequired[str],
        "type": NotRequired[LastLaunchTypeType],
    },
)

ListExtensibleSourceServersRequestRequestTypeDef = TypedDict(
    "ListExtensibleSourceServersRequestRequestTypeDef",
    {
        "stagingAccountID": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

StagingSourceServerTypeDef = TypedDict(
    "StagingSourceServerTypeDef",
    {
        "arn": NotRequired[str],
        "hostname": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)

ListStagingAccountsRequestRequestTypeDef = TypedDict(
    "ListStagingAccountsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "ips": NotRequired[List[str]],
        "isPrimary": NotRequired[bool],
        "macAddress": NotRequired[str],
    },
)

OSTypeDef = TypedDict(
    "OSTypeDef",
    {
        "fullString": NotRequired[str],
    },
)

ParticipatingResourceIDTypeDef = TypedDict(
    "ParticipatingResourceIDTypeDef",
    {
        "sourceNetworkID": NotRequired[str],
    },
)

RecoveryInstanceDataReplicationErrorTypeDef = TypedDict(
    "RecoveryInstanceDataReplicationErrorTypeDef",
    {
        "error": NotRequired[FailbackReplicationErrorType],
        "rawError": NotRequired[str],
    },
)

RecoveryInstanceDataReplicationInfoReplicatedDiskTypeDef = TypedDict(
    "RecoveryInstanceDataReplicationInfoReplicatedDiskTypeDef",
    {
        "backloggedStorageBytes": NotRequired[int],
        "deviceName": NotRequired[str],
        "replicatedStorageBytes": NotRequired[int],
        "rescannedStorageBytes": NotRequired[int],
        "totalStorageBytes": NotRequired[int],
    },
)

RecoveryInstanceDataReplicationInitiationStepTypeDef = TypedDict(
    "RecoveryInstanceDataReplicationInitiationStepTypeDef",
    {
        "name": NotRequired[RecoveryInstanceDataReplicationInitiationStepNameType],
        "status": NotRequired[RecoveryInstanceDataReplicationInitiationStepStatusType],
    },
)

RecoveryInstanceDiskTypeDef = TypedDict(
    "RecoveryInstanceDiskTypeDef",
    {
        "bytes": NotRequired[int],
        "ebsVolumeID": NotRequired[str],
        "internalDeviceName": NotRequired[str],
    },
)

RecoveryInstanceFailbackTypeDef = TypedDict(
    "RecoveryInstanceFailbackTypeDef",
    {
        "agentLastSeenByServiceDateTime": NotRequired[str],
        "elapsedReplicationDuration": NotRequired[str],
        "failbackClientID": NotRequired[str],
        "failbackClientLastSeenByServiceDateTime": NotRequired[str],
        "failbackInitiationTime": NotRequired[str],
        "failbackJobID": NotRequired[str],
        "failbackLaunchType": NotRequired[FailbackLaunchTypeType],
        "failbackToOriginalServer": NotRequired[bool],
        "firstByteDateTime": NotRequired[str],
        "state": NotRequired[FailbackStateType],
    },
)

RecoveryLifeCycleTypeDef = TypedDict(
    "RecoveryLifeCycleTypeDef",
    {
        "apiCallDateTime": NotRequired[datetime],
        "jobID": NotRequired[str],
        "lastRecoveryResult": NotRequired[RecoveryResultType],
    },
)

ReplicationConfigurationReplicatedDiskTypeDef = TypedDict(
    "ReplicationConfigurationReplicatedDiskTypeDef",
    {
        "deviceName": NotRequired[str],
        "iops": NotRequired[int],
        "isBootDisk": NotRequired[bool],
        "optimizedStagingDiskType": NotRequired[
            ReplicationConfigurationReplicatedDiskStagingDiskTypeType
        ],
        "stagingDiskType": NotRequired[ReplicationConfigurationReplicatedDiskStagingDiskTypeType],
        "throughput": NotRequired[int],
    },
)

RetryDataReplicationRequestRequestTypeDef = TypedDict(
    "RetryDataReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

ReverseReplicationRequestRequestTypeDef = TypedDict(
    "ReverseReplicationRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
    },
)

SourceCloudPropertiesTypeDef = TypedDict(
    "SourceCloudPropertiesTypeDef",
    {
        "originAccountID": NotRequired[str],
        "originAvailabilityZone": NotRequired[str],
        "originRegion": NotRequired[str],
    },
)

StagingAreaTypeDef = TypedDict(
    "StagingAreaTypeDef",
    {
        "errorMessage": NotRequired[str],
        "stagingAccountID": NotRequired[str],
        "stagingSourceServerArn": NotRequired[str],
        "status": NotRequired[ExtensionStatusType],
    },
)

StartFailbackLaunchRequestRequestTypeDef = TypedDict(
    "StartFailbackLaunchRequestRequestTypeDef",
    {
        "recoveryInstanceIDs": Sequence[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)

StartRecoveryRequestSourceServerTypeDef = TypedDict(
    "StartRecoveryRequestSourceServerTypeDef",
    {
        "sourceServerID": str,
        "recoverySnapshotID": NotRequired[str],
    },
)

StartReplicationRequestRequestTypeDef = TypedDict(
    "StartReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

StartSourceNetworkRecoveryRequestNetworkEntryTypeDef = TypedDict(
    "StartSourceNetworkRecoveryRequestNetworkEntryTypeDef",
    {
        "sourceNetworkID": str,
        "cfnStackName": NotRequired[str],
    },
)

StartSourceNetworkReplicationRequestRequestTypeDef = TypedDict(
    "StartSourceNetworkReplicationRequestRequestTypeDef",
    {
        "sourceNetworkID": str,
    },
)

StopFailbackRequestRequestTypeDef = TypedDict(
    "StopFailbackRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
    },
)

StopReplicationRequestRequestTypeDef = TypedDict(
    "StopReplicationRequestRequestTypeDef",
    {
        "sourceServerID": str,
    },
)

StopSourceNetworkReplicationRequestRequestTypeDef = TypedDict(
    "StopSourceNetworkReplicationRequestRequestTypeDef",
    {
        "sourceNetworkID": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

TerminateRecoveryInstancesRequestRequestTypeDef = TypedDict(
    "TerminateRecoveryInstancesRequestRequestTypeDef",
    {
        "recoveryInstanceIDs": Sequence[str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

UpdateFailbackReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateFailbackReplicationConfigurationRequestRequestTypeDef",
    {
        "recoveryInstanceID": str,
        "bandwidthThrottling": NotRequired[int],
        "name": NotRequired[str],
        "usePrivateIP": NotRequired[bool],
    },
)

CreateSourceNetworkResponseTypeDef = TypedDict(
    "CreateSourceNetworkResponseTypeDef",
    {
        "sourceNetworkID": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportSourceNetworkCfnTemplateResponseTypeDef = TypedDict(
    "ExportSourceNetworkCfnTemplateResponseTypeDef",
    {
        "s3DestinationUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetFailbackReplicationConfigurationResponseTypeDef = TypedDict(
    "GetFailbackReplicationConfigurationResponseTypeDef",
    {
        "bandwidthThrottling": int,
        "name": str,
        "recoveryInstanceID": str,
        "usePrivateIP": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStagingAccountsResponseTypeDef = TypedDict(
    "ListStagingAccountsResponseTypeDef",
    {
        "accounts": List[AccountTypeDef],
        "nextToken": str,
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

ReverseReplicationResponseTypeDef = TypedDict(
    "ReverseReplicationResponseTypeDef",
    {
        "reversedDirectionSourceServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "CreateLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "exportBucketArn": NotRequired[str],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "postLaunchEnabled": NotRequired[bool],
        "tags": NotRequired[Mapping[str, str]],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)

LaunchConfigurationTemplateTypeDef = TypedDict(
    "LaunchConfigurationTemplateTypeDef",
    {
        "arn": NotRequired[str],
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "exportBucketArn": NotRequired[str],
        "launchConfigurationTemplateID": NotRequired[str],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "postLaunchEnabled": NotRequired[bool],
        "tags": NotRequired[Dict[str, str]],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)

LaunchConfigurationTypeDef = TypedDict(
    "LaunchConfigurationTypeDef",
    {
        "copyPrivateIp": bool,
        "copyTags": bool,
        "ec2LaunchTemplateID": str,
        "launchDisposition": LaunchDispositionType,
        "licensing": LicensingTypeDef,
        "name": str,
        "postLaunchEnabled": bool,
        "sourceServerID": str,
        "targetInstanceTypeRightSizingMethod": TargetInstanceTypeRightSizingMethodType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateLaunchConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateLaunchConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "name": NotRequired[str],
        "postLaunchEnabled": NotRequired[bool],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)

UpdateLaunchConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "UpdateLaunchConfigurationTemplateRequestRequestTypeDef",
    {
        "launchConfigurationTemplateID": str,
        "copyPrivateIp": NotRequired[bool],
        "copyTags": NotRequired[bool],
        "exportBucketArn": NotRequired[str],
        "launchDisposition": NotRequired[LaunchDispositionType],
        "licensing": NotRequired[LicensingTypeDef],
        "postLaunchEnabled": NotRequired[bool],
        "targetInstanceTypeRightSizingMethod": NotRequired[TargetInstanceTypeRightSizingMethodType],
    },
)

CreateReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "CreateReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "associateDefaultSecurityGroup": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "pitPolicy": Sequence[PITPolicyRuleTypeDef],
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": Sequence[str],
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Mapping[str, str],
        "useDedicatedReplicationServer": bool,
        "autoReplicateNewDisks": NotRequired[bool],
        "ebsEncryptionKeyArn": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)

ReplicationConfigurationTemplateResponseTypeDef = TypedDict(
    "ReplicationConfigurationTemplateResponseTypeDef",
    {
        "arn": str,
        "associateDefaultSecurityGroup": bool,
        "autoReplicateNewDisks": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "ebsEncryptionKeyArn": str,
        "pitPolicy": List[PITPolicyRuleTypeDef],
        "replicationConfigurationTemplateID": str,
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": List[str],
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Dict[str, str],
        "tags": Dict[str, str],
        "useDedicatedReplicationServer": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ReplicationConfigurationTemplateTypeDef = TypedDict(
    "ReplicationConfigurationTemplateTypeDef",
    {
        "replicationConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associateDefaultSecurityGroup": NotRequired[bool],
        "autoReplicateNewDisks": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "pitPolicy": NotRequired[List[PITPolicyRuleTypeDef]],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[List[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Dict[str, str]],
        "tags": NotRequired[Dict[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
    },
)

UpdateReplicationConfigurationTemplateRequestRequestTypeDef = TypedDict(
    "UpdateReplicationConfigurationTemplateRequestRequestTypeDef",
    {
        "replicationConfigurationTemplateID": str,
        "arn": NotRequired[str],
        "associateDefaultSecurityGroup": NotRequired[bool],
        "autoReplicateNewDisks": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "pitPolicy": NotRequired[Sequence[PITPolicyRuleTypeDef]],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[Sequence[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Mapping[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
    },
)

DataReplicationInitiationTypeDef = TypedDict(
    "DataReplicationInitiationTypeDef",
    {
        "nextAttemptDateTime": NotRequired[str],
        "startDateTime": NotRequired[str],
        "steps": NotRequired[List[DataReplicationInitiationStepTypeDef]],
    },
)

DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef = TypedDict(
    "DescribeJobLogItemsRequestDescribeJobLogItemsPaginateTypeDef",
    {
        "jobID": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesRequestDescribeLaunchConfigurationTemplatesPaginateTypeDef",
    {
        "launchConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesRequestDescribeReplicationConfigurationTemplatesPaginateTypeDef",
    {
        "replicationConfigurationTemplateIDs": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListExtensibleSourceServersRequestListExtensibleSourceServersPaginateTypeDef = TypedDict(
    "ListExtensibleSourceServersRequestListExtensibleSourceServersPaginateTypeDef",
    {
        "stagingAccountID": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListStagingAccountsRequestListStagingAccountsPaginateTypeDef = TypedDict(
    "ListStagingAccountsRequestListStagingAccountsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeJobsRequestDescribeJobsPaginateTypeDef = TypedDict(
    "DescribeJobsRequestDescribeJobsPaginateTypeDef",
    {
        "filters": NotRequired[DescribeJobsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeJobsRequestRequestTypeDef = TypedDict(
    "DescribeJobsRequestRequestTypeDef",
    {
        "filters": NotRequired[DescribeJobsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

DescribeRecoveryInstancesRequestDescribeRecoveryInstancesPaginateTypeDef = TypedDict(
    "DescribeRecoveryInstancesRequestDescribeRecoveryInstancesPaginateTypeDef",
    {
        "filters": NotRequired[DescribeRecoveryInstancesRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeRecoveryInstancesRequestRequestTypeDef = TypedDict(
    "DescribeRecoveryInstancesRequestRequestTypeDef",
    {
        "filters": NotRequired[DescribeRecoveryInstancesRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

DescribeRecoverySnapshotsRequestDescribeRecoverySnapshotsPaginateTypeDef = TypedDict(
    "DescribeRecoverySnapshotsRequestDescribeRecoverySnapshotsPaginateTypeDef",
    {
        "sourceServerID": str,
        "filters": NotRequired[DescribeRecoverySnapshotsRequestFiltersTypeDef],
        "order": NotRequired[RecoverySnapshotsOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeRecoverySnapshotsRequestRequestTypeDef = TypedDict(
    "DescribeRecoverySnapshotsRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "filters": NotRequired[DescribeRecoverySnapshotsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "order": NotRequired[RecoverySnapshotsOrderType],
    },
)

DescribeRecoverySnapshotsResponseTypeDef = TypedDict(
    "DescribeRecoverySnapshotsResponseTypeDef",
    {
        "items": List[RecoverySnapshotTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSourceNetworksRequestDescribeSourceNetworksPaginateTypeDef = TypedDict(
    "DescribeSourceNetworksRequestDescribeSourceNetworksPaginateTypeDef",
    {
        "filters": NotRequired[DescribeSourceNetworksRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeSourceNetworksRequestRequestTypeDef = TypedDict(
    "DescribeSourceNetworksRequestRequestTypeDef",
    {
        "filters": NotRequired[DescribeSourceNetworksRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef = TypedDict(
    "DescribeSourceServersRequestDescribeSourceServersPaginateTypeDef",
    {
        "filters": NotRequired[DescribeSourceServersRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeSourceServersRequestRequestTypeDef = TypedDict(
    "DescribeSourceServersRequestRequestTypeDef",
    {
        "filters": NotRequired[DescribeSourceServersRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

EventResourceDataTypeDef = TypedDict(
    "EventResourceDataTypeDef",
    {
        "sourceNetworkData": NotRequired[SourceNetworkDataTypeDef],
    },
)

LaunchActionTypeDef = TypedDict(
    "LaunchActionTypeDef",
    {
        "actionCode": NotRequired[str],
        "actionId": NotRequired[str],
        "actionVersion": NotRequired[str],
        "active": NotRequired[bool],
        "category": NotRequired[LaunchActionCategoryType],
        "description": NotRequired[str],
        "name": NotRequired[str],
        "optional": NotRequired[bool],
        "order": NotRequired[int],
        "parameters": NotRequired[Dict[str, LaunchActionParameterTypeDef]],
        "type": NotRequired[LaunchActionTypeType],
    },
)

PutLaunchActionRequestRequestTypeDef = TypedDict(
    "PutLaunchActionRequestRequestTypeDef",
    {
        "actionCode": str,
        "actionId": str,
        "actionVersion": str,
        "active": bool,
        "category": LaunchActionCategoryType,
        "name": str,
        "optional": bool,
        "order": int,
        "resourceId": str,
        "description": NotRequired[str],
        "parameters": NotRequired[Mapping[str, LaunchActionParameterTypeDef]],
    },
)

PutLaunchActionResponseTypeDef = TypedDict(
    "PutLaunchActionResponseTypeDef",
    {
        "actionCode": str,
        "actionId": str,
        "actionVersion": str,
        "active": bool,
        "category": LaunchActionCategoryType,
        "description": str,
        "name": str,
        "optional": bool,
        "order": int,
        "parameters": Dict[str, LaunchActionParameterTypeDef],
        "resourceId": str,
        "type": LaunchActionTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListLaunchActionsRequestListLaunchActionsPaginateTypeDef = TypedDict(
    "ListLaunchActionsRequestListLaunchActionsPaginateTypeDef",
    {
        "resourceId": str,
        "filters": NotRequired[LaunchActionsRequestFiltersTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLaunchActionsRequestRequestTypeDef = TypedDict(
    "ListLaunchActionsRequestRequestTypeDef",
    {
        "resourceId": str,
        "filters": NotRequired[LaunchActionsRequestFiltersTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

LifeCycleLastLaunchTypeDef = TypedDict(
    "LifeCycleLastLaunchTypeDef",
    {
        "initiated": NotRequired[LifeCycleLastLaunchInitiatedTypeDef],
        "status": NotRequired[LaunchStatusType],
    },
)

ListExtensibleSourceServersResponseTypeDef = TypedDict(
    "ListExtensibleSourceServersResponseTypeDef",
    {
        "items": List[StagingSourceServerTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SourcePropertiesTypeDef = TypedDict(
    "SourcePropertiesTypeDef",
    {
        "cpus": NotRequired[List[CPUTypeDef]],
        "disks": NotRequired[List[DiskTypeDef]],
        "identificationHints": NotRequired[IdentificationHintsTypeDef],
        "lastUpdatedDateTime": NotRequired[str],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
        "os": NotRequired[OSTypeDef],
        "ramBytes": NotRequired[int],
        "recommendedInstanceType": NotRequired[str],
        "supportsNitroInstances": NotRequired[bool],
    },
)

ParticipatingResourceTypeDef = TypedDict(
    "ParticipatingResourceTypeDef",
    {
        "launchStatus": NotRequired[LaunchStatusType],
        "participatingResourceID": NotRequired[ParticipatingResourceIDTypeDef],
    },
)

RecoveryInstanceDataReplicationInitiationTypeDef = TypedDict(
    "RecoveryInstanceDataReplicationInitiationTypeDef",
    {
        "startDateTime": NotRequired[str],
        "steps": NotRequired[List[RecoveryInstanceDataReplicationInitiationStepTypeDef]],
    },
)

RecoveryInstancePropertiesTypeDef = TypedDict(
    "RecoveryInstancePropertiesTypeDef",
    {
        "cpus": NotRequired[List[CPUTypeDef]],
        "disks": NotRequired[List[RecoveryInstanceDiskTypeDef]],
        "identificationHints": NotRequired[IdentificationHintsTypeDef],
        "lastUpdatedDateTime": NotRequired[str],
        "networkInterfaces": NotRequired[List[NetworkInterfaceTypeDef]],
        "os": NotRequired[OSTypeDef],
        "ramBytes": NotRequired[int],
    },
)

SourceNetworkTypeDef = TypedDict(
    "SourceNetworkTypeDef",
    {
        "arn": NotRequired[str],
        "cfnStackName": NotRequired[str],
        "lastRecovery": NotRequired[RecoveryLifeCycleTypeDef],
        "launchedVpcID": NotRequired[str],
        "replicationStatus": NotRequired[ReplicationStatusType],
        "replicationStatusDetails": NotRequired[str],
        "sourceAccountID": NotRequired[str],
        "sourceNetworkID": NotRequired[str],
        "sourceRegion": NotRequired[str],
        "sourceVpcID": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)

ReplicationConfigurationTypeDef = TypedDict(
    "ReplicationConfigurationTypeDef",
    {
        "associateDefaultSecurityGroup": bool,
        "autoReplicateNewDisks": bool,
        "bandwidthThrottling": int,
        "createPublicIP": bool,
        "dataPlaneRouting": ReplicationConfigurationDataPlaneRoutingType,
        "defaultLargeStagingDiskType": ReplicationConfigurationDefaultLargeStagingDiskTypeType,
        "ebsEncryption": ReplicationConfigurationEbsEncryptionType,
        "ebsEncryptionKeyArn": str,
        "name": str,
        "pitPolicy": List[PITPolicyRuleTypeDef],
        "replicatedDisks": List[ReplicationConfigurationReplicatedDiskTypeDef],
        "replicationServerInstanceType": str,
        "replicationServersSecurityGroupsIDs": List[str],
        "sourceServerID": str,
        "stagingAreaSubnetId": str,
        "stagingAreaTags": Dict[str, str],
        "useDedicatedReplicationServer": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateReplicationConfigurationRequestRequestTypeDef",
    {
        "sourceServerID": str,
        "associateDefaultSecurityGroup": NotRequired[bool],
        "autoReplicateNewDisks": NotRequired[bool],
        "bandwidthThrottling": NotRequired[int],
        "createPublicIP": NotRequired[bool],
        "dataPlaneRouting": NotRequired[ReplicationConfigurationDataPlaneRoutingType],
        "defaultLargeStagingDiskType": NotRequired[
            ReplicationConfigurationDefaultLargeStagingDiskTypeType
        ],
        "ebsEncryption": NotRequired[ReplicationConfigurationEbsEncryptionType],
        "ebsEncryptionKeyArn": NotRequired[str],
        "name": NotRequired[str],
        "pitPolicy": NotRequired[Sequence[PITPolicyRuleTypeDef]],
        "replicatedDisks": NotRequired[Sequence[ReplicationConfigurationReplicatedDiskTypeDef]],
        "replicationServerInstanceType": NotRequired[str],
        "replicationServersSecurityGroupsIDs": NotRequired[Sequence[str]],
        "stagingAreaSubnetId": NotRequired[str],
        "stagingAreaTags": NotRequired[Mapping[str, str]],
        "useDedicatedReplicationServer": NotRequired[bool],
    },
)

StartRecoveryRequestRequestTypeDef = TypedDict(
    "StartRecoveryRequestRequestTypeDef",
    {
        "sourceServers": Sequence[StartRecoveryRequestSourceServerTypeDef],
        "isDrill": NotRequired[bool],
        "tags": NotRequired[Mapping[str, str]],
    },
)

StartSourceNetworkRecoveryRequestRequestTypeDef = TypedDict(
    "StartSourceNetworkRecoveryRequestRequestTypeDef",
    {
        "sourceNetworks": Sequence[StartSourceNetworkRecoveryRequestNetworkEntryTypeDef],
        "deployAsNew": NotRequired[bool],
        "tags": NotRequired[Mapping[str, str]],
    },
)

CreateLaunchConfigurationTemplateResponseTypeDef = TypedDict(
    "CreateLaunchConfigurationTemplateResponseTypeDef",
    {
        "launchConfigurationTemplate": LaunchConfigurationTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLaunchConfigurationTemplatesResponseTypeDef = TypedDict(
    "DescribeLaunchConfigurationTemplatesResponseTypeDef",
    {
        "items": List[LaunchConfigurationTemplateTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateLaunchConfigurationTemplateResponseTypeDef = TypedDict(
    "UpdateLaunchConfigurationTemplateResponseTypeDef",
    {
        "launchConfigurationTemplate": LaunchConfigurationTemplateTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeReplicationConfigurationTemplatesResponseTypeDef = TypedDict(
    "DescribeReplicationConfigurationTemplatesResponseTypeDef",
    {
        "items": List[ReplicationConfigurationTemplateTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DataReplicationInfoTypeDef = TypedDict(
    "DataReplicationInfoTypeDef",
    {
        "dataReplicationError": NotRequired[DataReplicationErrorTypeDef],
        "dataReplicationInitiation": NotRequired[DataReplicationInitiationTypeDef],
        "dataReplicationState": NotRequired[DataReplicationStateType],
        "etaDateTime": NotRequired[str],
        "lagDuration": NotRequired[str],
        "replicatedDisks": NotRequired[List[DataReplicationInfoReplicatedDiskTypeDef]],
        "stagingAvailabilityZone": NotRequired[str],
    },
)

JobLogEventDataTypeDef = TypedDict(
    "JobLogEventDataTypeDef",
    {
        "conversionProperties": NotRequired[ConversionPropertiesTypeDef],
        "conversionServerID": NotRequired[str],
        "eventResourceData": NotRequired[EventResourceDataTypeDef],
        "rawError": NotRequired[str],
        "sourceServerID": NotRequired[str],
        "targetInstanceID": NotRequired[str],
    },
)

LaunchActionRunTypeDef = TypedDict(
    "LaunchActionRunTypeDef",
    {
        "action": NotRequired[LaunchActionTypeDef],
        "failureReason": NotRequired[str],
        "runId": NotRequired[str],
        "status": NotRequired[LaunchActionRunStatusType],
    },
)

ListLaunchActionsResponseTypeDef = TypedDict(
    "ListLaunchActionsResponseTypeDef",
    {
        "items": List[LaunchActionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LifeCycleTypeDef = TypedDict(
    "LifeCycleTypeDef",
    {
        "addedToServiceDateTime": NotRequired[str],
        "elapsedReplicationDuration": NotRequired[str],
        "firstByteDateTime": NotRequired[str],
        "lastLaunch": NotRequired[LifeCycleLastLaunchTypeDef],
        "lastSeenByServiceDateTime": NotRequired[str],
    },
)

RecoveryInstanceDataReplicationInfoTypeDef = TypedDict(
    "RecoveryInstanceDataReplicationInfoTypeDef",
    {
        "dataReplicationError": NotRequired[RecoveryInstanceDataReplicationErrorTypeDef],
        "dataReplicationInitiation": NotRequired[RecoveryInstanceDataReplicationInitiationTypeDef],
        "dataReplicationState": NotRequired[RecoveryInstanceDataReplicationStateType],
        "etaDateTime": NotRequired[str],
        "lagDuration": NotRequired[str],
        "replicatedDisks": NotRequired[
            List[RecoveryInstanceDataReplicationInfoReplicatedDiskTypeDef]
        ],
        "stagingAvailabilityZone": NotRequired[str],
    },
)

DescribeSourceNetworksResponseTypeDef = TypedDict(
    "DescribeSourceNetworksResponseTypeDef",
    {
        "items": List[SourceNetworkTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSourceNetworkReplicationResponseTypeDef = TypedDict(
    "StartSourceNetworkReplicationResponseTypeDef",
    {
        "sourceNetwork": SourceNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopSourceNetworkReplicationResponseTypeDef = TypedDict(
    "StopSourceNetworkReplicationResponseTypeDef",
    {
        "sourceNetwork": SourceNetworkTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

JobLogTypeDef = TypedDict(
    "JobLogTypeDef",
    {
        "event": NotRequired[JobLogEventType],
        "eventData": NotRequired[JobLogEventDataTypeDef],
        "logDateTime": NotRequired[str],
    },
)

LaunchActionsStatusTypeDef = TypedDict(
    "LaunchActionsStatusTypeDef",
    {
        "runs": NotRequired[List[LaunchActionRunTypeDef]],
        "ssmAgentDiscoveryDatetime": NotRequired[str],
    },
)

SourceServerResponseTypeDef = TypedDict(
    "SourceServerResponseTypeDef",
    {
        "arn": str,
        "dataReplicationInfo": DataReplicationInfoTypeDef,
        "lastLaunchResult": LastLaunchResultType,
        "lifeCycle": LifeCycleTypeDef,
        "recoveryInstanceId": str,
        "replicationDirection": ReplicationDirectionType,
        "reversedDirectionSourceServerArn": str,
        "sourceCloudProperties": SourceCloudPropertiesTypeDef,
        "sourceNetworkID": str,
        "sourceProperties": SourcePropertiesTypeDef,
        "sourceServerID": str,
        "stagingArea": StagingAreaTypeDef,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SourceServerTypeDef = TypedDict(
    "SourceServerTypeDef",
    {
        "arn": NotRequired[str],
        "dataReplicationInfo": NotRequired[DataReplicationInfoTypeDef],
        "lastLaunchResult": NotRequired[LastLaunchResultType],
        "lifeCycle": NotRequired[LifeCycleTypeDef],
        "recoveryInstanceId": NotRequired[str],
        "replicationDirection": NotRequired[ReplicationDirectionType],
        "reversedDirectionSourceServerArn": NotRequired[str],
        "sourceCloudProperties": NotRequired[SourceCloudPropertiesTypeDef],
        "sourceNetworkID": NotRequired[str],
        "sourceProperties": NotRequired[SourcePropertiesTypeDef],
        "sourceServerID": NotRequired[str],
        "stagingArea": NotRequired[StagingAreaTypeDef],
        "tags": NotRequired[Dict[str, str]],
    },
)

RecoveryInstanceTypeDef = TypedDict(
    "RecoveryInstanceTypeDef",
    {
        "arn": NotRequired[str],
        "dataReplicationInfo": NotRequired[RecoveryInstanceDataReplicationInfoTypeDef],
        "ec2InstanceID": NotRequired[str],
        "ec2InstanceState": NotRequired[EC2InstanceStateType],
        "failback": NotRequired[RecoveryInstanceFailbackTypeDef],
        "isDrill": NotRequired[bool],
        "jobID": NotRequired[str],
        "originAvailabilityZone": NotRequired[str],
        "originEnvironment": NotRequired[OriginEnvironmentType],
        "pointInTimeSnapshotDateTime": NotRequired[str],
        "recoveryInstanceID": NotRequired[str],
        "recoveryInstanceProperties": NotRequired[RecoveryInstancePropertiesTypeDef],
        "sourceServerID": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)

DescribeJobLogItemsResponseTypeDef = TypedDict(
    "DescribeJobLogItemsResponseTypeDef",
    {
        "items": List[JobLogTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ParticipatingServerTypeDef = TypedDict(
    "ParticipatingServerTypeDef",
    {
        "launchActionsStatus": NotRequired[LaunchActionsStatusTypeDef],
        "launchStatus": NotRequired[LaunchStatusType],
        "recoveryInstanceID": NotRequired[str],
        "sourceServerID": NotRequired[str],
    },
)

CreateExtendedSourceServerResponseTypeDef = TypedDict(
    "CreateExtendedSourceServerResponseTypeDef",
    {
        "sourceServer": SourceServerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSourceServersResponseTypeDef = TypedDict(
    "DescribeSourceServersResponseTypeDef",
    {
        "items": List[SourceServerTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartReplicationResponseTypeDef = TypedDict(
    "StartReplicationResponseTypeDef",
    {
        "sourceServer": SourceServerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopReplicationResponseTypeDef = TypedDict(
    "StopReplicationResponseTypeDef",
    {
        "sourceServer": SourceServerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRecoveryInstancesResponseTypeDef = TypedDict(
    "DescribeRecoveryInstancesResponseTypeDef",
    {
        "items": List[RecoveryInstanceTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "jobID": str,
        "arn": NotRequired[str],
        "creationDateTime": NotRequired[str],
        "endDateTime": NotRequired[str],
        "initiatedBy": NotRequired[InitiatedByType],
        "participatingResources": NotRequired[List[ParticipatingResourceTypeDef]],
        "participatingServers": NotRequired[List[ParticipatingServerTypeDef]],
        "status": NotRequired[JobStatusType],
        "tags": NotRequired[Dict[str, str]],
        "type": NotRequired[JobTypeType],
    },
)

AssociateSourceNetworkStackResponseTypeDef = TypedDict(
    "AssociateSourceNetworkStackResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeJobsResponseTypeDef = TypedDict(
    "DescribeJobsResponseTypeDef",
    {
        "items": List[JobTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartFailbackLaunchResponseTypeDef = TypedDict(
    "StartFailbackLaunchResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartRecoveryResponseTypeDef = TypedDict(
    "StartRecoveryResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSourceNetworkRecoveryResponseTypeDef = TypedDict(
    "StartSourceNetworkRecoveryResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TerminateRecoveryInstancesResponseTypeDef = TypedDict(
    "TerminateRecoveryInstancesResponseTypeDef",
    {
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
