"""
Type annotations for cloud9 service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloud9/type_defs/)

Usage::

    ```python
    from mypy_boto3_cloud9.type_defs import TagTypeDef

    data: TagTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    ConnectionTypeType,
    EnvironmentLifecycleStatusType,
    EnvironmentStatusType,
    EnvironmentTypeType,
    ManagedCredentialsActionType,
    ManagedCredentialsStatusType,
    MemberPermissionsType,
    PermissionsType,
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
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "CreateEnvironmentMembershipRequestRequestTypeDef",
    "EnvironmentMemberTypeDef",
    "DeleteEnvironmentMembershipRequestRequestTypeDef",
    "DeleteEnvironmentRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeEnvironmentMembershipsRequestRequestTypeDef",
    "DescribeEnvironmentStatusRequestRequestTypeDef",
    "DescribeEnvironmentsRequestRequestTypeDef",
    "EnvironmentLifecycleTypeDef",
    "ListEnvironmentsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateEnvironmentMembershipRequestRequestTypeDef",
    "UpdateEnvironmentRequestRequestTypeDef",
    "CreateEnvironmentEC2RequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateEnvironmentEC2ResultTypeDef",
    "DescribeEnvironmentStatusResultTypeDef",
    "ListEnvironmentsResultTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "CreateEnvironmentMembershipResultTypeDef",
    "DescribeEnvironmentMembershipsResultTypeDef",
    "UpdateEnvironmentMembershipResultTypeDef",
    "DescribeEnvironmentMembershipsRequestDescribeEnvironmentMembershipsPaginateTypeDef",
    "ListEnvironmentsRequestListEnvironmentsPaginateTypeDef",
    "EnvironmentTypeDef",
    "DescribeEnvironmentsResultTypeDef",
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
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

CreateEnvironmentMembershipRequestRequestTypeDef = TypedDict(
    "CreateEnvironmentMembershipRequestRequestTypeDef",
    {
        "environmentId": str,
        "userArn": str,
        "permissions": MemberPermissionsType,
    },
)

EnvironmentMemberTypeDef = TypedDict(
    "EnvironmentMemberTypeDef",
    {
        "permissions": PermissionsType,
        "userId": str,
        "userArn": str,
        "environmentId": str,
        "lastAccess": NotRequired[datetime],
    },
)

DeleteEnvironmentMembershipRequestRequestTypeDef = TypedDict(
    "DeleteEnvironmentMembershipRequestRequestTypeDef",
    {
        "environmentId": str,
        "userArn": str,
    },
)

DeleteEnvironmentRequestRequestTypeDef = TypedDict(
    "DeleteEnvironmentRequestRequestTypeDef",
    {
        "environmentId": str,
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

DescribeEnvironmentMembershipsRequestRequestTypeDef = TypedDict(
    "DescribeEnvironmentMembershipsRequestRequestTypeDef",
    {
        "userArn": NotRequired[str],
        "environmentId": NotRequired[str],
        "permissions": NotRequired[Sequence[PermissionsType]],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)

DescribeEnvironmentStatusRequestRequestTypeDef = TypedDict(
    "DescribeEnvironmentStatusRequestRequestTypeDef",
    {
        "environmentId": str,
    },
)

DescribeEnvironmentsRequestRequestTypeDef = TypedDict(
    "DescribeEnvironmentsRequestRequestTypeDef",
    {
        "environmentIds": Sequence[str],
    },
)

EnvironmentLifecycleTypeDef = TypedDict(
    "EnvironmentLifecycleTypeDef",
    {
        "status": NotRequired[EnvironmentLifecycleStatusType],
        "reason": NotRequired[str],
        "failureResource": NotRequired[str],
    },
)

ListEnvironmentsRequestRequestTypeDef = TypedDict(
    "ListEnvironmentsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "TagKeys": Sequence[str],
    },
)

UpdateEnvironmentMembershipRequestRequestTypeDef = TypedDict(
    "UpdateEnvironmentMembershipRequestRequestTypeDef",
    {
        "environmentId": str,
        "userArn": str,
        "permissions": MemberPermissionsType,
    },
)

UpdateEnvironmentRequestRequestTypeDef = TypedDict(
    "UpdateEnvironmentRequestRequestTypeDef",
    {
        "environmentId": str,
        "name": NotRequired[str],
        "description": NotRequired[str],
        "managedCredentialsAction": NotRequired[ManagedCredentialsActionType],
    },
)

CreateEnvironmentEC2RequestRequestTypeDef = TypedDict(
    "CreateEnvironmentEC2RequestRequestTypeDef",
    {
        "name": str,
        "instanceType": str,
        "description": NotRequired[str],
        "clientRequestToken": NotRequired[str],
        "subnetId": NotRequired[str],
        "imageId": NotRequired[str],
        "automaticStopTimeMinutes": NotRequired[int],
        "ownerArn": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "connectionType": NotRequired[ConnectionTypeType],
        "dryRun": NotRequired[bool],
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "Tags": Sequence[TagTypeDef],
    },
)

CreateEnvironmentEC2ResultTypeDef = TypedDict(
    "CreateEnvironmentEC2ResultTypeDef",
    {
        "environmentId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEnvironmentStatusResultTypeDef = TypedDict(
    "DescribeEnvironmentStatusResultTypeDef",
    {
        "status": EnvironmentStatusType,
        "message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEnvironmentsResultTypeDef = TypedDict(
    "ListEnvironmentsResultTypeDef",
    {
        "nextToken": str,
        "environmentIds": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEnvironmentMembershipResultTypeDef = TypedDict(
    "CreateEnvironmentMembershipResultTypeDef",
    {
        "membership": EnvironmentMemberTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEnvironmentMembershipsResultTypeDef = TypedDict(
    "DescribeEnvironmentMembershipsResultTypeDef",
    {
        "memberships": List[EnvironmentMemberTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEnvironmentMembershipResultTypeDef = TypedDict(
    "UpdateEnvironmentMembershipResultTypeDef",
    {
        "membership": EnvironmentMemberTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEnvironmentMembershipsRequestDescribeEnvironmentMembershipsPaginateTypeDef = TypedDict(
    "DescribeEnvironmentMembershipsRequestDescribeEnvironmentMembershipsPaginateTypeDef",
    {
        "userArn": NotRequired[str],
        "environmentId": NotRequired[str],
        "permissions": NotRequired[Sequence[PermissionsType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEnvironmentsRequestListEnvironmentsPaginateTypeDef = TypedDict(
    "ListEnvironmentsRequestListEnvironmentsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

EnvironmentTypeDef = TypedDict(
    "EnvironmentTypeDef",
    {
        "type": EnvironmentTypeType,
        "arn": str,
        "ownerArn": str,
        "id": NotRequired[str],
        "name": NotRequired[str],
        "description": NotRequired[str],
        "connectionType": NotRequired[ConnectionTypeType],
        "lifecycle": NotRequired[EnvironmentLifecycleTypeDef],
        "managedCredentialsStatus": NotRequired[ManagedCredentialsStatusType],
    },
)

DescribeEnvironmentsResultTypeDef = TypedDict(
    "DescribeEnvironmentsResultTypeDef",
    {
        "environments": List[EnvironmentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
