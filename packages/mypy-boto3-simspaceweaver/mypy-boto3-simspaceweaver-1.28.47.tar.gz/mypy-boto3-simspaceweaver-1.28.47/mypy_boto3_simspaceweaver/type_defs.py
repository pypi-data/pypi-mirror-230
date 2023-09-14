"""
Type annotations for simspaceweaver service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/type_defs/)

Usage::

    ```python
    from mypy_boto3_simspaceweaver.type_defs import CloudWatchLogsLogGroupTypeDef

    data: CloudWatchLogsLogGroupTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    ClockStatusType,
    ClockTargetStatusType,
    LifecycleManagementStrategyType,
    SimulationAppStatusType,
    SimulationAppTargetStatusType,
    SimulationStatusType,
    SimulationTargetStatusType,
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
    "CloudWatchLogsLogGroupTypeDef",
    "S3DestinationTypeDef",
    "DeleteAppInputRequestTypeDef",
    "DeleteSimulationInputRequestTypeDef",
    "DescribeAppInputRequestTypeDef",
    "LaunchOverridesTypeDef",
    "ResponseMetadataTypeDef",
    "DescribeSimulationInputRequestTypeDef",
    "S3LocationTypeDef",
    "DomainTypeDef",
    "ListAppsInputRequestTypeDef",
    "SimulationAppMetadataTypeDef",
    "ListSimulationsInputRequestTypeDef",
    "SimulationMetadataTypeDef",
    "ListTagsForResourceInputRequestTypeDef",
    "SimulationClockTypeDef",
    "SimulationAppPortMappingTypeDef",
    "StartClockInputRequestTypeDef",
    "StopAppInputRequestTypeDef",
    "StopClockInputRequestTypeDef",
    "StopSimulationInputRequestTypeDef",
    "TagResourceInputRequestTypeDef",
    "UntagResourceInputRequestTypeDef",
    "LogDestinationTypeDef",
    "CreateSnapshotInputRequestTypeDef",
    "StartAppInputRequestTypeDef",
    "ListTagsForResourceOutputTypeDef",
    "StartAppOutputTypeDef",
    "StartSimulationOutputTypeDef",
    "StartSimulationInputRequestTypeDef",
    "ListAppsOutputTypeDef",
    "ListSimulationsOutputTypeDef",
    "LiveSimulationStateTypeDef",
    "SimulationAppEndpointInfoTypeDef",
    "LoggingConfigurationTypeDef",
    "DescribeAppOutputTypeDef",
    "DescribeSimulationOutputTypeDef",
)

CloudWatchLogsLogGroupTypeDef = TypedDict(
    "CloudWatchLogsLogGroupTypeDef",
    {
        "LogGroupArn": NotRequired[str],
    },
)

S3DestinationTypeDef = TypedDict(
    "S3DestinationTypeDef",
    {
        "BucketName": str,
        "ObjectKeyPrefix": NotRequired[str],
    },
)

DeleteAppInputRequestTypeDef = TypedDict(
    "DeleteAppInputRequestTypeDef",
    {
        "App": str,
        "Domain": str,
        "Simulation": str,
    },
)

DeleteSimulationInputRequestTypeDef = TypedDict(
    "DeleteSimulationInputRequestTypeDef",
    {
        "Simulation": str,
    },
)

DescribeAppInputRequestTypeDef = TypedDict(
    "DescribeAppInputRequestTypeDef",
    {
        "App": str,
        "Domain": str,
        "Simulation": str,
    },
)

LaunchOverridesTypeDef = TypedDict(
    "LaunchOverridesTypeDef",
    {
        "LaunchCommands": NotRequired[List[str]],
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

DescribeSimulationInputRequestTypeDef = TypedDict(
    "DescribeSimulationInputRequestTypeDef",
    {
        "Simulation": str,
    },
)

S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "BucketName": str,
        "ObjectKey": str,
    },
)

DomainTypeDef = TypedDict(
    "DomainTypeDef",
    {
        "Lifecycle": NotRequired[LifecycleManagementStrategyType],
        "Name": NotRequired[str],
    },
)

ListAppsInputRequestTypeDef = TypedDict(
    "ListAppsInputRequestTypeDef",
    {
        "Simulation": str,
        "Domain": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

SimulationAppMetadataTypeDef = TypedDict(
    "SimulationAppMetadataTypeDef",
    {
        "Domain": NotRequired[str],
        "Name": NotRequired[str],
        "Simulation": NotRequired[str],
        "Status": NotRequired[SimulationAppStatusType],
        "TargetStatus": NotRequired[SimulationAppTargetStatusType],
    },
)

ListSimulationsInputRequestTypeDef = TypedDict(
    "ListSimulationsInputRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

SimulationMetadataTypeDef = TypedDict(
    "SimulationMetadataTypeDef",
    {
        "Arn": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "Name": NotRequired[str],
        "Status": NotRequired[SimulationStatusType],
        "TargetStatus": NotRequired[SimulationTargetStatusType],
    },
)

ListTagsForResourceInputRequestTypeDef = TypedDict(
    "ListTagsForResourceInputRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

SimulationClockTypeDef = TypedDict(
    "SimulationClockTypeDef",
    {
        "Status": NotRequired[ClockStatusType],
        "TargetStatus": NotRequired[ClockTargetStatusType],
    },
)

SimulationAppPortMappingTypeDef = TypedDict(
    "SimulationAppPortMappingTypeDef",
    {
        "Actual": NotRequired[int],
        "Declared": NotRequired[int],
    },
)

StartClockInputRequestTypeDef = TypedDict(
    "StartClockInputRequestTypeDef",
    {
        "Simulation": str,
    },
)

StopAppInputRequestTypeDef = TypedDict(
    "StopAppInputRequestTypeDef",
    {
        "App": str,
        "Domain": str,
        "Simulation": str,
    },
)

StopClockInputRequestTypeDef = TypedDict(
    "StopClockInputRequestTypeDef",
    {
        "Simulation": str,
    },
)

StopSimulationInputRequestTypeDef = TypedDict(
    "StopSimulationInputRequestTypeDef",
    {
        "Simulation": str,
    },
)

TagResourceInputRequestTypeDef = TypedDict(
    "TagResourceInputRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Mapping[str, str],
    },
)

UntagResourceInputRequestTypeDef = TypedDict(
    "UntagResourceInputRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

LogDestinationTypeDef = TypedDict(
    "LogDestinationTypeDef",
    {
        "CloudWatchLogsLogGroup": NotRequired[CloudWatchLogsLogGroupTypeDef],
    },
)

CreateSnapshotInputRequestTypeDef = TypedDict(
    "CreateSnapshotInputRequestTypeDef",
    {
        "Destination": S3DestinationTypeDef,
        "Simulation": str,
    },
)

StartAppInputRequestTypeDef = TypedDict(
    "StartAppInputRequestTypeDef",
    {
        "Domain": str,
        "Name": str,
        "Simulation": str,
        "ClientToken": NotRequired[str],
        "Description": NotRequired[str],
        "LaunchOverrides": NotRequired[LaunchOverridesTypeDef],
    },
)

ListTagsForResourceOutputTypeDef = TypedDict(
    "ListTagsForResourceOutputTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartAppOutputTypeDef = TypedDict(
    "StartAppOutputTypeDef",
    {
        "Domain": str,
        "Name": str,
        "Simulation": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSimulationOutputTypeDef = TypedDict(
    "StartSimulationOutputTypeDef",
    {
        "Arn": str,
        "CreationTime": datetime,
        "ExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartSimulationInputRequestTypeDef = TypedDict(
    "StartSimulationInputRequestTypeDef",
    {
        "Name": str,
        "RoleArn": str,
        "ClientToken": NotRequired[str],
        "Description": NotRequired[str],
        "MaximumDuration": NotRequired[str],
        "SchemaS3Location": NotRequired[S3LocationTypeDef],
        "SnapshotS3Location": NotRequired[S3LocationTypeDef],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

ListAppsOutputTypeDef = TypedDict(
    "ListAppsOutputTypeDef",
    {
        "Apps": List[SimulationAppMetadataTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSimulationsOutputTypeDef = TypedDict(
    "ListSimulationsOutputTypeDef",
    {
        "NextToken": str,
        "Simulations": List[SimulationMetadataTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LiveSimulationStateTypeDef = TypedDict(
    "LiveSimulationStateTypeDef",
    {
        "Clocks": NotRequired[List[SimulationClockTypeDef]],
        "Domains": NotRequired[List[DomainTypeDef]],
    },
)

SimulationAppEndpointInfoTypeDef = TypedDict(
    "SimulationAppEndpointInfoTypeDef",
    {
        "Address": NotRequired[str],
        "IngressPortMappings": NotRequired[List[SimulationAppPortMappingTypeDef]],
    },
)

LoggingConfigurationTypeDef = TypedDict(
    "LoggingConfigurationTypeDef",
    {
        "Destinations": NotRequired[List[LogDestinationTypeDef]],
    },
)

DescribeAppOutputTypeDef = TypedDict(
    "DescribeAppOutputTypeDef",
    {
        "Description": str,
        "Domain": str,
        "EndpointInfo": SimulationAppEndpointInfoTypeDef,
        "LaunchOverrides": LaunchOverridesTypeDef,
        "Name": str,
        "Simulation": str,
        "Status": SimulationAppStatusType,
        "TargetStatus": SimulationAppTargetStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSimulationOutputTypeDef = TypedDict(
    "DescribeSimulationOutputTypeDef",
    {
        "Arn": str,
        "CreationTime": datetime,
        "Description": str,
        "ExecutionId": str,
        "LiveSimulationState": LiveSimulationStateTypeDef,
        "LoggingConfiguration": LoggingConfigurationTypeDef,
        "MaximumDuration": str,
        "Name": str,
        "RoleArn": str,
        "SchemaError": str,
        "SchemaS3Location": S3LocationTypeDef,
        "SnapshotS3Location": S3LocationTypeDef,
        "StartError": str,
        "Status": SimulationStatusType,
        "TargetStatus": SimulationTargetStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
