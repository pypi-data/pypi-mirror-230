"""
Type annotations for appstream service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_appstream/type_defs/)

Usage::

    ```python
    from mypy_boto3_appstream.type_defs import AccessEndpointTypeDef

    data: AccessEndpointTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    ActionType,
    AppBlockBuilderAttributeType,
    AppBlockBuilderStateType,
    AppBlockStateType,
    ApplicationAttributeType,
    AppVisibilityType,
    AuthenticationTypeType,
    CertificateBasedAuthStatusType,
    FleetAttributeType,
    FleetErrorCodeType,
    FleetStateType,
    FleetTypeType,
    ImageBuilderStateChangeReasonCodeType,
    ImageBuilderStateType,
    ImageStateChangeReasonCodeType,
    ImageStateType,
    MessageActionType,
    PackagingTypeType,
    PermissionType,
    PlatformTypeType,
    PreferredProtocolType,
    SessionConnectionStateType,
    SessionStateType,
    StackAttributeType,
    StackErrorCodeType,
    StorageConnectorTypeType,
    StreamViewType,
    UsageReportExecutionErrorCodeType,
    UserStackAssociationErrorCodeType,
    VisibilityTypeType,
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
    "AccessEndpointTypeDef",
    "AppBlockBuilderAppBlockAssociationTypeDef",
    "AppBlockBuilderStateChangeReasonTypeDef",
    "ResourceErrorTypeDef",
    "VpcConfigTypeDef",
    "ErrorDetailsTypeDef",
    "S3LocationTypeDef",
    "ApplicationFleetAssociationTypeDef",
    "ApplicationSettingsResponseTypeDef",
    "ApplicationSettingsTypeDef",
    "AssociateAppBlockBuilderAppBlockRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AssociateApplicationFleetRequestRequestTypeDef",
    "AssociateApplicationToEntitlementRequestRequestTypeDef",
    "AssociateFleetRequestRequestTypeDef",
    "UserStackAssociationTypeDef",
    "CertificateBasedAuthPropertiesTypeDef",
    "ComputeCapacityStatusTypeDef",
    "ComputeCapacityTypeDef",
    "CopyImageRequestRequestTypeDef",
    "CreateAppBlockBuilderStreamingURLRequestRequestTypeDef",
    "ServiceAccountCredentialsTypeDef",
    "EntitlementAttributeTypeDef",
    "DomainJoinInfoTypeDef",
    "CreateImageBuilderStreamingURLRequestRequestTypeDef",
    "StorageConnectorTypeDef",
    "StreamingExperienceSettingsTypeDef",
    "UserSettingTypeDef",
    "CreateStreamingURLRequestRequestTypeDef",
    "CreateUpdatedImageRequestRequestTypeDef",
    "CreateUserRequestRequestTypeDef",
    "DeleteAppBlockBuilderRequestRequestTypeDef",
    "DeleteAppBlockRequestRequestTypeDef",
    "DeleteApplicationRequestRequestTypeDef",
    "DeleteDirectoryConfigRequestRequestTypeDef",
    "DeleteEntitlementRequestRequestTypeDef",
    "DeleteFleetRequestRequestTypeDef",
    "DeleteImageBuilderRequestRequestTypeDef",
    "DeleteImagePermissionsRequestRequestTypeDef",
    "DeleteImageRequestRequestTypeDef",
    "DeleteStackRequestRequestTypeDef",
    "DeleteUserRequestRequestTypeDef",
    "DescribeAppBlockBuilderAppBlockAssociationsRequestRequestTypeDef",
    "DescribeAppBlockBuildersRequestRequestTypeDef",
    "DescribeAppBlocksRequestRequestTypeDef",
    "DescribeApplicationFleetAssociationsRequestRequestTypeDef",
    "DescribeApplicationsRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeDirectoryConfigsRequestRequestTypeDef",
    "DescribeEntitlementsRequestRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeFleetsRequestRequestTypeDef",
    "DescribeImageBuildersRequestRequestTypeDef",
    "DescribeImagePermissionsRequestRequestTypeDef",
    "DescribeImagesRequestRequestTypeDef",
    "DescribeSessionsRequestRequestTypeDef",
    "DescribeStacksRequestRequestTypeDef",
    "DescribeUsageReportSubscriptionsRequestRequestTypeDef",
    "DescribeUserStackAssociationsRequestRequestTypeDef",
    "DescribeUsersRequestRequestTypeDef",
    "UserTypeDef",
    "DisableUserRequestRequestTypeDef",
    "DisassociateAppBlockBuilderAppBlockRequestRequestTypeDef",
    "DisassociateApplicationFleetRequestRequestTypeDef",
    "DisassociateApplicationFromEntitlementRequestRequestTypeDef",
    "DisassociateFleetRequestRequestTypeDef",
    "EnableUserRequestRequestTypeDef",
    "EntitledApplicationTypeDef",
    "ExpireSessionRequestRequestTypeDef",
    "FleetErrorTypeDef",
    "VpcConfigPaginatorTypeDef",
    "ImageBuilderStateChangeReasonTypeDef",
    "NetworkAccessConfigurationTypeDef",
    "ImagePermissionsTypeDef",
    "ImageStateChangeReasonTypeDef",
    "LastReportGenerationExecutionErrorTypeDef",
    "ListAssociatedFleetsRequestRequestTypeDef",
    "ListAssociatedStacksRequestRequestTypeDef",
    "ListEntitledApplicationsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "StackErrorTypeDef",
    "StorageConnectorPaginatorTypeDef",
    "StartAppBlockBuilderRequestRequestTypeDef",
    "StartFleetRequestRequestTypeDef",
    "StartImageBuilderRequestRequestTypeDef",
    "StopAppBlockBuilderRequestRequestTypeDef",
    "StopFleetRequestRequestTypeDef",
    "StopImageBuilderRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "AppBlockBuilderTypeDef",
    "CreateAppBlockBuilderRequestRequestTypeDef",
    "UpdateAppBlockBuilderRequestRequestTypeDef",
    "ApplicationTypeDef",
    "CreateApplicationRequestRequestTypeDef",
    "ScriptDetailsTypeDef",
    "UpdateApplicationRequestRequestTypeDef",
    "AssociateAppBlockBuilderAppBlockResultTypeDef",
    "AssociateApplicationFleetResultTypeDef",
    "CopyImageResponseTypeDef",
    "CreateAppBlockBuilderStreamingURLResultTypeDef",
    "CreateImageBuilderStreamingURLResultTypeDef",
    "CreateStreamingURLResultTypeDef",
    "CreateUsageReportSubscriptionResultTypeDef",
    "DescribeAppBlockBuilderAppBlockAssociationsResultTypeDef",
    "DescribeApplicationFleetAssociationsResultTypeDef",
    "ListAssociatedFleetsResultTypeDef",
    "ListAssociatedStacksResultTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "BatchAssociateUserStackRequestRequestTypeDef",
    "BatchDisassociateUserStackRequestRequestTypeDef",
    "DescribeUserStackAssociationsResultTypeDef",
    "UserStackAssociationErrorTypeDef",
    "CreateDirectoryConfigRequestRequestTypeDef",
    "DirectoryConfigTypeDef",
    "UpdateDirectoryConfigRequestRequestTypeDef",
    "CreateEntitlementRequestRequestTypeDef",
    "EntitlementTypeDef",
    "UpdateEntitlementRequestRequestTypeDef",
    "CreateFleetRequestRequestTypeDef",
    "CreateImageBuilderRequestRequestTypeDef",
    "UpdateFleetRequestRequestTypeDef",
    "CreateStackRequestRequestTypeDef",
    "UpdateStackRequestRequestTypeDef",
    "DescribeDirectoryConfigsRequestDescribeDirectoryConfigsPaginateTypeDef",
    "DescribeFleetsRequestDescribeFleetsPaginateTypeDef",
    "DescribeImageBuildersRequestDescribeImageBuildersPaginateTypeDef",
    "DescribeImagesRequestDescribeImagesPaginateTypeDef",
    "DescribeSessionsRequestDescribeSessionsPaginateTypeDef",
    "DescribeStacksRequestDescribeStacksPaginateTypeDef",
    "DescribeUserStackAssociationsRequestDescribeUserStackAssociationsPaginateTypeDef",
    "DescribeUsersRequestDescribeUsersPaginateTypeDef",
    "ListAssociatedFleetsRequestListAssociatedFleetsPaginateTypeDef",
    "ListAssociatedStacksRequestListAssociatedStacksPaginateTypeDef",
    "DescribeFleetsRequestFleetStartedWaitTypeDef",
    "DescribeFleetsRequestFleetStoppedWaitTypeDef",
    "DescribeUsersResultTypeDef",
    "ListEntitledApplicationsResultTypeDef",
    "FleetTypeDef",
    "FleetPaginatorTypeDef",
    "ImageBuilderPaginatorTypeDef",
    "ImageBuilderTypeDef",
    "SessionTypeDef",
    "SharedImagePermissionsTypeDef",
    "UpdateImagePermissionsRequestRequestTypeDef",
    "UsageReportSubscriptionTypeDef",
    "StackTypeDef",
    "StackPaginatorTypeDef",
    "CreateAppBlockBuilderResultTypeDef",
    "DescribeAppBlockBuildersResultTypeDef",
    "StartAppBlockBuilderResultTypeDef",
    "StopAppBlockBuilderResultTypeDef",
    "UpdateAppBlockBuilderResultTypeDef",
    "CreateApplicationResultTypeDef",
    "DescribeApplicationsResultTypeDef",
    "ImageTypeDef",
    "UpdateApplicationResultTypeDef",
    "AppBlockTypeDef",
    "CreateAppBlockRequestRequestTypeDef",
    "BatchAssociateUserStackResultTypeDef",
    "BatchDisassociateUserStackResultTypeDef",
    "CreateDirectoryConfigResultTypeDef",
    "DescribeDirectoryConfigsResultTypeDef",
    "UpdateDirectoryConfigResultTypeDef",
    "CreateEntitlementResultTypeDef",
    "DescribeEntitlementsResultTypeDef",
    "UpdateEntitlementResultTypeDef",
    "CreateFleetResultTypeDef",
    "DescribeFleetsResultTypeDef",
    "UpdateFleetResultTypeDef",
    "DescribeFleetsResultPaginatorTypeDef",
    "DescribeImageBuildersResultPaginatorTypeDef",
    "CreateImageBuilderResultTypeDef",
    "DeleteImageBuilderResultTypeDef",
    "DescribeImageBuildersResultTypeDef",
    "StartImageBuilderResultTypeDef",
    "StopImageBuilderResultTypeDef",
    "DescribeSessionsResultTypeDef",
    "DescribeImagePermissionsResultTypeDef",
    "DescribeUsageReportSubscriptionsResultTypeDef",
    "CreateStackResultTypeDef",
    "DescribeStacksResultTypeDef",
    "UpdateStackResultTypeDef",
    "DescribeStacksResultPaginatorTypeDef",
    "CreateUpdatedImageResultTypeDef",
    "DeleteImageResultTypeDef",
    "DescribeImagesResultTypeDef",
    "CreateAppBlockResultTypeDef",
    "DescribeAppBlocksResultTypeDef",
)

AccessEndpointTypeDef = TypedDict(
    "AccessEndpointTypeDef",
    {
        "EndpointType": Literal["STREAMING"],
        "VpceId": NotRequired[str],
    },
)

AppBlockBuilderAppBlockAssociationTypeDef = TypedDict(
    "AppBlockBuilderAppBlockAssociationTypeDef",
    {
        "AppBlockArn": str,
        "AppBlockBuilderName": str,
    },
)

AppBlockBuilderStateChangeReasonTypeDef = TypedDict(
    "AppBlockBuilderStateChangeReasonTypeDef",
    {
        "Code": NotRequired[Literal["INTERNAL_ERROR"]],
        "Message": NotRequired[str],
    },
)

ResourceErrorTypeDef = TypedDict(
    "ResourceErrorTypeDef",
    {
        "ErrorCode": NotRequired[FleetErrorCodeType],
        "ErrorMessage": NotRequired[str],
        "ErrorTimestamp": NotRequired[datetime],
    },
)

VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "SubnetIds": NotRequired[Sequence[str]],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)

ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "S3Bucket": str,
        "S3Key": NotRequired[str],
    },
)

ApplicationFleetAssociationTypeDef = TypedDict(
    "ApplicationFleetAssociationTypeDef",
    {
        "FleetName": str,
        "ApplicationArn": str,
    },
)

ApplicationSettingsResponseTypeDef = TypedDict(
    "ApplicationSettingsResponseTypeDef",
    {
        "Enabled": NotRequired[bool],
        "SettingsGroup": NotRequired[str],
        "S3BucketName": NotRequired[str],
    },
)

ApplicationSettingsTypeDef = TypedDict(
    "ApplicationSettingsTypeDef",
    {
        "Enabled": bool,
        "SettingsGroup": NotRequired[str],
    },
)

AssociateAppBlockBuilderAppBlockRequestRequestTypeDef = TypedDict(
    "AssociateAppBlockBuilderAppBlockRequestRequestTypeDef",
    {
        "AppBlockArn": str,
        "AppBlockBuilderName": str,
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

AssociateApplicationFleetRequestRequestTypeDef = TypedDict(
    "AssociateApplicationFleetRequestRequestTypeDef",
    {
        "FleetName": str,
        "ApplicationArn": str,
    },
)

AssociateApplicationToEntitlementRequestRequestTypeDef = TypedDict(
    "AssociateApplicationToEntitlementRequestRequestTypeDef",
    {
        "StackName": str,
        "EntitlementName": str,
        "ApplicationIdentifier": str,
    },
)

AssociateFleetRequestRequestTypeDef = TypedDict(
    "AssociateFleetRequestRequestTypeDef",
    {
        "FleetName": str,
        "StackName": str,
    },
)

UserStackAssociationTypeDef = TypedDict(
    "UserStackAssociationTypeDef",
    {
        "StackName": str,
        "UserName": str,
        "AuthenticationType": AuthenticationTypeType,
        "SendEmailNotification": NotRequired[bool],
    },
)

CertificateBasedAuthPropertiesTypeDef = TypedDict(
    "CertificateBasedAuthPropertiesTypeDef",
    {
        "Status": NotRequired[CertificateBasedAuthStatusType],
        "CertificateAuthorityArn": NotRequired[str],
    },
)

ComputeCapacityStatusTypeDef = TypedDict(
    "ComputeCapacityStatusTypeDef",
    {
        "Desired": int,
        "Running": NotRequired[int],
        "InUse": NotRequired[int],
        "Available": NotRequired[int],
    },
)

ComputeCapacityTypeDef = TypedDict(
    "ComputeCapacityTypeDef",
    {
        "DesiredInstances": int,
    },
)

CopyImageRequestRequestTypeDef = TypedDict(
    "CopyImageRequestRequestTypeDef",
    {
        "SourceImageName": str,
        "DestinationImageName": str,
        "DestinationRegion": str,
        "DestinationImageDescription": NotRequired[str],
    },
)

CreateAppBlockBuilderStreamingURLRequestRequestTypeDef = TypedDict(
    "CreateAppBlockBuilderStreamingURLRequestRequestTypeDef",
    {
        "AppBlockBuilderName": str,
        "Validity": NotRequired[int],
    },
)

ServiceAccountCredentialsTypeDef = TypedDict(
    "ServiceAccountCredentialsTypeDef",
    {
        "AccountName": str,
        "AccountPassword": str,
    },
)

EntitlementAttributeTypeDef = TypedDict(
    "EntitlementAttributeTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)

DomainJoinInfoTypeDef = TypedDict(
    "DomainJoinInfoTypeDef",
    {
        "DirectoryName": NotRequired[str],
        "OrganizationalUnitDistinguishedName": NotRequired[str],
    },
)

CreateImageBuilderStreamingURLRequestRequestTypeDef = TypedDict(
    "CreateImageBuilderStreamingURLRequestRequestTypeDef",
    {
        "Name": str,
        "Validity": NotRequired[int],
    },
)

StorageConnectorTypeDef = TypedDict(
    "StorageConnectorTypeDef",
    {
        "ConnectorType": StorageConnectorTypeType,
        "ResourceIdentifier": NotRequired[str],
        "Domains": NotRequired[Sequence[str]],
    },
)

StreamingExperienceSettingsTypeDef = TypedDict(
    "StreamingExperienceSettingsTypeDef",
    {
        "PreferredProtocol": NotRequired[PreferredProtocolType],
    },
)

UserSettingTypeDef = TypedDict(
    "UserSettingTypeDef",
    {
        "Action": ActionType,
        "Permission": PermissionType,
    },
)

CreateStreamingURLRequestRequestTypeDef = TypedDict(
    "CreateStreamingURLRequestRequestTypeDef",
    {
        "StackName": str,
        "FleetName": str,
        "UserId": str,
        "ApplicationId": NotRequired[str],
        "Validity": NotRequired[int],
        "SessionContext": NotRequired[str],
    },
)

CreateUpdatedImageRequestRequestTypeDef = TypedDict(
    "CreateUpdatedImageRequestRequestTypeDef",
    {
        "existingImageName": str,
        "newImageName": str,
        "newImageDescription": NotRequired[str],
        "newImageDisplayName": NotRequired[str],
        "newImageTags": NotRequired[Mapping[str, str]],
        "dryRun": NotRequired[bool],
    },
)

CreateUserRequestRequestTypeDef = TypedDict(
    "CreateUserRequestRequestTypeDef",
    {
        "UserName": str,
        "AuthenticationType": AuthenticationTypeType,
        "MessageAction": NotRequired[MessageActionType],
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
    },
)

DeleteAppBlockBuilderRequestRequestTypeDef = TypedDict(
    "DeleteAppBlockBuilderRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteAppBlockRequestRequestTypeDef = TypedDict(
    "DeleteAppBlockRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteApplicationRequestRequestTypeDef = TypedDict(
    "DeleteApplicationRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteDirectoryConfigRequestRequestTypeDef = TypedDict(
    "DeleteDirectoryConfigRequestRequestTypeDef",
    {
        "DirectoryName": str,
    },
)

DeleteEntitlementRequestRequestTypeDef = TypedDict(
    "DeleteEntitlementRequestRequestTypeDef",
    {
        "Name": str,
        "StackName": str,
    },
)

DeleteFleetRequestRequestTypeDef = TypedDict(
    "DeleteFleetRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteImageBuilderRequestRequestTypeDef = TypedDict(
    "DeleteImageBuilderRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteImagePermissionsRequestRequestTypeDef = TypedDict(
    "DeleteImagePermissionsRequestRequestTypeDef",
    {
        "Name": str,
        "SharedAccountId": str,
    },
)

DeleteImageRequestRequestTypeDef = TypedDict(
    "DeleteImageRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteStackRequestRequestTypeDef = TypedDict(
    "DeleteStackRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteUserRequestRequestTypeDef = TypedDict(
    "DeleteUserRequestRequestTypeDef",
    {
        "UserName": str,
        "AuthenticationType": AuthenticationTypeType,
    },
)

DescribeAppBlockBuilderAppBlockAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeAppBlockBuilderAppBlockAssociationsRequestRequestTypeDef",
    {
        "AppBlockArn": NotRequired[str],
        "AppBlockBuilderName": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeAppBlockBuildersRequestRequestTypeDef = TypedDict(
    "DescribeAppBlockBuildersRequestRequestTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

DescribeAppBlocksRequestRequestTypeDef = TypedDict(
    "DescribeAppBlocksRequestRequestTypeDef",
    {
        "Arns": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

DescribeApplicationFleetAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeApplicationFleetAssociationsRequestRequestTypeDef",
    {
        "FleetName": NotRequired[str],
        "ApplicationArn": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeApplicationsRequestRequestTypeDef = TypedDict(
    "DescribeApplicationsRequestRequestTypeDef",
    {
        "Arns": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
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

DescribeDirectoryConfigsRequestRequestTypeDef = TypedDict(
    "DescribeDirectoryConfigsRequestRequestTypeDef",
    {
        "DirectoryNames": NotRequired[Sequence[str]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeEntitlementsRequestRequestTypeDef = TypedDict(
    "DescribeEntitlementsRequestRequestTypeDef",
    {
        "StackName": str,
        "Name": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)

DescribeFleetsRequestRequestTypeDef = TypedDict(
    "DescribeFleetsRequestRequestTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
    },
)

DescribeImageBuildersRequestRequestTypeDef = TypedDict(
    "DescribeImageBuildersRequestRequestTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeImagePermissionsRequestRequestTypeDef = TypedDict(
    "DescribeImagePermissionsRequestRequestTypeDef",
    {
        "Name": str,
        "MaxResults": NotRequired[int],
        "SharedAwsAccountIds": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
    },
)

DescribeImagesRequestRequestTypeDef = TypedDict(
    "DescribeImagesRequestRequestTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "Arns": NotRequired[Sequence[str]],
        "Type": NotRequired[VisibilityTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

DescribeSessionsRequestRequestTypeDef = TypedDict(
    "DescribeSessionsRequestRequestTypeDef",
    {
        "StackName": str,
        "FleetName": str,
        "UserId": NotRequired[str],
        "NextToken": NotRequired[str],
        "Limit": NotRequired[int],
        "AuthenticationType": NotRequired[AuthenticationTypeType],
    },
)

DescribeStacksRequestRequestTypeDef = TypedDict(
    "DescribeStacksRequestRequestTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
    },
)

DescribeUsageReportSubscriptionsRequestRequestTypeDef = TypedDict(
    "DescribeUsageReportSubscriptionsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeUserStackAssociationsRequestRequestTypeDef = TypedDict(
    "DescribeUserStackAssociationsRequestRequestTypeDef",
    {
        "StackName": NotRequired[str],
        "UserName": NotRequired[str],
        "AuthenticationType": NotRequired[AuthenticationTypeType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DescribeUsersRequestRequestTypeDef = TypedDict(
    "DescribeUsersRequestRequestTypeDef",
    {
        "AuthenticationType": AuthenticationTypeType,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

UserTypeDef = TypedDict(
    "UserTypeDef",
    {
        "AuthenticationType": AuthenticationTypeType,
        "Arn": NotRequired[str],
        "UserName": NotRequired[str],
        "Enabled": NotRequired[bool],
        "Status": NotRequired[str],
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
    },
)

DisableUserRequestRequestTypeDef = TypedDict(
    "DisableUserRequestRequestTypeDef",
    {
        "UserName": str,
        "AuthenticationType": AuthenticationTypeType,
    },
)

DisassociateAppBlockBuilderAppBlockRequestRequestTypeDef = TypedDict(
    "DisassociateAppBlockBuilderAppBlockRequestRequestTypeDef",
    {
        "AppBlockArn": str,
        "AppBlockBuilderName": str,
    },
)

DisassociateApplicationFleetRequestRequestTypeDef = TypedDict(
    "DisassociateApplicationFleetRequestRequestTypeDef",
    {
        "FleetName": str,
        "ApplicationArn": str,
    },
)

DisassociateApplicationFromEntitlementRequestRequestTypeDef = TypedDict(
    "DisassociateApplicationFromEntitlementRequestRequestTypeDef",
    {
        "StackName": str,
        "EntitlementName": str,
        "ApplicationIdentifier": str,
    },
)

DisassociateFleetRequestRequestTypeDef = TypedDict(
    "DisassociateFleetRequestRequestTypeDef",
    {
        "FleetName": str,
        "StackName": str,
    },
)

EnableUserRequestRequestTypeDef = TypedDict(
    "EnableUserRequestRequestTypeDef",
    {
        "UserName": str,
        "AuthenticationType": AuthenticationTypeType,
    },
)

EntitledApplicationTypeDef = TypedDict(
    "EntitledApplicationTypeDef",
    {
        "ApplicationIdentifier": str,
    },
)

ExpireSessionRequestRequestTypeDef = TypedDict(
    "ExpireSessionRequestRequestTypeDef",
    {
        "SessionId": str,
    },
)

FleetErrorTypeDef = TypedDict(
    "FleetErrorTypeDef",
    {
        "ErrorCode": NotRequired[FleetErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

VpcConfigPaginatorTypeDef = TypedDict(
    "VpcConfigPaginatorTypeDef",
    {
        "SubnetIds": NotRequired[List[str]],
        "SecurityGroupIds": NotRequired[List[str]],
    },
)

ImageBuilderStateChangeReasonTypeDef = TypedDict(
    "ImageBuilderStateChangeReasonTypeDef",
    {
        "Code": NotRequired[ImageBuilderStateChangeReasonCodeType],
        "Message": NotRequired[str],
    },
)

NetworkAccessConfigurationTypeDef = TypedDict(
    "NetworkAccessConfigurationTypeDef",
    {
        "EniPrivateIpAddress": NotRequired[str],
        "EniId": NotRequired[str],
    },
)

ImagePermissionsTypeDef = TypedDict(
    "ImagePermissionsTypeDef",
    {
        "allowFleet": NotRequired[bool],
        "allowImageBuilder": NotRequired[bool],
    },
)

ImageStateChangeReasonTypeDef = TypedDict(
    "ImageStateChangeReasonTypeDef",
    {
        "Code": NotRequired[ImageStateChangeReasonCodeType],
        "Message": NotRequired[str],
    },
)

LastReportGenerationExecutionErrorTypeDef = TypedDict(
    "LastReportGenerationExecutionErrorTypeDef",
    {
        "ErrorCode": NotRequired[UsageReportExecutionErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

ListAssociatedFleetsRequestRequestTypeDef = TypedDict(
    "ListAssociatedFleetsRequestRequestTypeDef",
    {
        "StackName": str,
        "NextToken": NotRequired[str],
    },
)

ListAssociatedStacksRequestRequestTypeDef = TypedDict(
    "ListAssociatedStacksRequestRequestTypeDef",
    {
        "FleetName": str,
        "NextToken": NotRequired[str],
    },
)

ListEntitledApplicationsRequestRequestTypeDef = TypedDict(
    "ListEntitledApplicationsRequestRequestTypeDef",
    {
        "StackName": str,
        "EntitlementName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

StackErrorTypeDef = TypedDict(
    "StackErrorTypeDef",
    {
        "ErrorCode": NotRequired[StackErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

StorageConnectorPaginatorTypeDef = TypedDict(
    "StorageConnectorPaginatorTypeDef",
    {
        "ConnectorType": StorageConnectorTypeType,
        "ResourceIdentifier": NotRequired[str],
        "Domains": NotRequired[List[str]],
    },
)

StartAppBlockBuilderRequestRequestTypeDef = TypedDict(
    "StartAppBlockBuilderRequestRequestTypeDef",
    {
        "Name": str,
    },
)

StartFleetRequestRequestTypeDef = TypedDict(
    "StartFleetRequestRequestTypeDef",
    {
        "Name": str,
    },
)

StartImageBuilderRequestRequestTypeDef = TypedDict(
    "StartImageBuilderRequestRequestTypeDef",
    {
        "Name": str,
        "AppstreamAgentVersion": NotRequired[str],
    },
)

StopAppBlockBuilderRequestRequestTypeDef = TypedDict(
    "StopAppBlockBuilderRequestRequestTypeDef",
    {
        "Name": str,
    },
)

StopFleetRequestRequestTypeDef = TypedDict(
    "StopFleetRequestRequestTypeDef",
    {
        "Name": str,
    },
)

StopImageBuilderRequestRequestTypeDef = TypedDict(
    "StopImageBuilderRequestRequestTypeDef",
    {
        "Name": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

AppBlockBuilderTypeDef = TypedDict(
    "AppBlockBuilderTypeDef",
    {
        "Arn": str,
        "Name": str,
        "Platform": Literal["WINDOWS_SERVER_2019"],
        "InstanceType": str,
        "VpcConfig": VpcConfigTypeDef,
        "State": AppBlockBuilderStateType,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "IamRoleArn": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "AppBlockBuilderErrors": NotRequired[List[ResourceErrorTypeDef]],
        "StateChangeReason": NotRequired[AppBlockBuilderStateChangeReasonTypeDef],
        "AccessEndpoints": NotRequired[List[AccessEndpointTypeDef]],
    },
)

CreateAppBlockBuilderRequestRequestTypeDef = TypedDict(
    "CreateAppBlockBuilderRequestRequestTypeDef",
    {
        "Name": str,
        "Platform": Literal["WINDOWS_SERVER_2019"],
        "InstanceType": str,
        "VpcConfig": VpcConfigTypeDef,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "IamRoleArn": NotRequired[str],
        "AccessEndpoints": NotRequired[Sequence[AccessEndpointTypeDef]],
    },
)

UpdateAppBlockBuilderRequestRequestTypeDef = TypedDict(
    "UpdateAppBlockBuilderRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Platform": NotRequired[PlatformTypeType],
        "InstanceType": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "IamRoleArn": NotRequired[str],
        "AccessEndpoints": NotRequired[Sequence[AccessEndpointTypeDef]],
        "AttributesToDelete": NotRequired[Sequence[AppBlockBuilderAttributeType]],
    },
)

ApplicationTypeDef = TypedDict(
    "ApplicationTypeDef",
    {
        "Name": NotRequired[str],
        "DisplayName": NotRequired[str],
        "IconURL": NotRequired[str],
        "LaunchPath": NotRequired[str],
        "LaunchParameters": NotRequired[str],
        "Enabled": NotRequired[bool],
        "Metadata": NotRequired[Dict[str, str]],
        "WorkingDirectory": NotRequired[str],
        "Description": NotRequired[str],
        "Arn": NotRequired[str],
        "AppBlockArn": NotRequired[str],
        "IconS3Location": NotRequired[S3LocationTypeDef],
        "Platforms": NotRequired[List[PlatformTypeType]],
        "InstanceFamilies": NotRequired[List[str]],
        "CreatedTime": NotRequired[datetime],
    },
)

CreateApplicationRequestRequestTypeDef = TypedDict(
    "CreateApplicationRequestRequestTypeDef",
    {
        "Name": str,
        "IconS3Location": S3LocationTypeDef,
        "LaunchPath": str,
        "Platforms": Sequence[PlatformTypeType],
        "InstanceFamilies": Sequence[str],
        "AppBlockArn": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "WorkingDirectory": NotRequired[str],
        "LaunchParameters": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)

ScriptDetailsTypeDef = TypedDict(
    "ScriptDetailsTypeDef",
    {
        "ScriptS3Location": S3LocationTypeDef,
        "ExecutablePath": str,
        "TimeoutInSeconds": int,
        "ExecutableParameters": NotRequired[str],
    },
)

UpdateApplicationRequestRequestTypeDef = TypedDict(
    "UpdateApplicationRequestRequestTypeDef",
    {
        "Name": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "IconS3Location": NotRequired[S3LocationTypeDef],
        "LaunchPath": NotRequired[str],
        "WorkingDirectory": NotRequired[str],
        "LaunchParameters": NotRequired[str],
        "AppBlockArn": NotRequired[str],
        "AttributesToDelete": NotRequired[Sequence[ApplicationAttributeType]],
    },
)

AssociateAppBlockBuilderAppBlockResultTypeDef = TypedDict(
    "AssociateAppBlockBuilderAppBlockResultTypeDef",
    {
        "AppBlockBuilderAppBlockAssociation": AppBlockBuilderAppBlockAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateApplicationFleetResultTypeDef = TypedDict(
    "AssociateApplicationFleetResultTypeDef",
    {
        "ApplicationFleetAssociation": ApplicationFleetAssociationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CopyImageResponseTypeDef = TypedDict(
    "CopyImageResponseTypeDef",
    {
        "DestinationImageName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAppBlockBuilderStreamingURLResultTypeDef = TypedDict(
    "CreateAppBlockBuilderStreamingURLResultTypeDef",
    {
        "StreamingURL": str,
        "Expires": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateImageBuilderStreamingURLResultTypeDef = TypedDict(
    "CreateImageBuilderStreamingURLResultTypeDef",
    {
        "StreamingURL": str,
        "Expires": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStreamingURLResultTypeDef = TypedDict(
    "CreateStreamingURLResultTypeDef",
    {
        "StreamingURL": str,
        "Expires": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUsageReportSubscriptionResultTypeDef = TypedDict(
    "CreateUsageReportSubscriptionResultTypeDef",
    {
        "S3BucketName": str,
        "Schedule": Literal["DAILY"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAppBlockBuilderAppBlockAssociationsResultTypeDef = TypedDict(
    "DescribeAppBlockBuilderAppBlockAssociationsResultTypeDef",
    {
        "AppBlockBuilderAppBlockAssociations": List[AppBlockBuilderAppBlockAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeApplicationFleetAssociationsResultTypeDef = TypedDict(
    "DescribeApplicationFleetAssociationsResultTypeDef",
    {
        "ApplicationFleetAssociations": List[ApplicationFleetAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAssociatedFleetsResultTypeDef = TypedDict(
    "ListAssociatedFleetsResultTypeDef",
    {
        "Names": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAssociatedStacksResultTypeDef = TypedDict(
    "ListAssociatedStacksResultTypeDef",
    {
        "Names": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchAssociateUserStackRequestRequestTypeDef = TypedDict(
    "BatchAssociateUserStackRequestRequestTypeDef",
    {
        "UserStackAssociations": Sequence[UserStackAssociationTypeDef],
    },
)

BatchDisassociateUserStackRequestRequestTypeDef = TypedDict(
    "BatchDisassociateUserStackRequestRequestTypeDef",
    {
        "UserStackAssociations": Sequence[UserStackAssociationTypeDef],
    },
)

DescribeUserStackAssociationsResultTypeDef = TypedDict(
    "DescribeUserStackAssociationsResultTypeDef",
    {
        "UserStackAssociations": List[UserStackAssociationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UserStackAssociationErrorTypeDef = TypedDict(
    "UserStackAssociationErrorTypeDef",
    {
        "UserStackAssociation": NotRequired[UserStackAssociationTypeDef],
        "ErrorCode": NotRequired[UserStackAssociationErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)

CreateDirectoryConfigRequestRequestTypeDef = TypedDict(
    "CreateDirectoryConfigRequestRequestTypeDef",
    {
        "DirectoryName": str,
        "OrganizationalUnitDistinguishedNames": Sequence[str],
        "ServiceAccountCredentials": NotRequired[ServiceAccountCredentialsTypeDef],
        "CertificateBasedAuthProperties": NotRequired[CertificateBasedAuthPropertiesTypeDef],
    },
)

DirectoryConfigTypeDef = TypedDict(
    "DirectoryConfigTypeDef",
    {
        "DirectoryName": str,
        "OrganizationalUnitDistinguishedNames": NotRequired[List[str]],
        "ServiceAccountCredentials": NotRequired[ServiceAccountCredentialsTypeDef],
        "CreatedTime": NotRequired[datetime],
        "CertificateBasedAuthProperties": NotRequired[CertificateBasedAuthPropertiesTypeDef],
    },
)

UpdateDirectoryConfigRequestRequestTypeDef = TypedDict(
    "UpdateDirectoryConfigRequestRequestTypeDef",
    {
        "DirectoryName": str,
        "OrganizationalUnitDistinguishedNames": NotRequired[Sequence[str]],
        "ServiceAccountCredentials": NotRequired[ServiceAccountCredentialsTypeDef],
        "CertificateBasedAuthProperties": NotRequired[CertificateBasedAuthPropertiesTypeDef],
    },
)

CreateEntitlementRequestRequestTypeDef = TypedDict(
    "CreateEntitlementRequestRequestTypeDef",
    {
        "Name": str,
        "StackName": str,
        "AppVisibility": AppVisibilityType,
        "Attributes": Sequence[EntitlementAttributeTypeDef],
        "Description": NotRequired[str],
    },
)

EntitlementTypeDef = TypedDict(
    "EntitlementTypeDef",
    {
        "Name": str,
        "StackName": str,
        "AppVisibility": AppVisibilityType,
        "Attributes": List[EntitlementAttributeTypeDef],
        "Description": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

UpdateEntitlementRequestRequestTypeDef = TypedDict(
    "UpdateEntitlementRequestRequestTypeDef",
    {
        "Name": str,
        "StackName": str,
        "Description": NotRequired[str],
        "AppVisibility": NotRequired[AppVisibilityType],
        "Attributes": NotRequired[Sequence[EntitlementAttributeTypeDef]],
    },
)

CreateFleetRequestRequestTypeDef = TypedDict(
    "CreateFleetRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceType": str,
        "ImageName": NotRequired[str],
        "ImageArn": NotRequired[str],
        "FleetType": NotRequired[FleetTypeType],
        "ComputeCapacity": NotRequired[ComputeCapacityTypeDef],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "MaxUserDurationInSeconds": NotRequired[int],
        "DisconnectTimeoutInSeconds": NotRequired[int],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "Tags": NotRequired[Mapping[str, str]],
        "IdleDisconnectTimeoutInSeconds": NotRequired[int],
        "IamRoleArn": NotRequired[str],
        "StreamView": NotRequired[StreamViewType],
        "Platform": NotRequired[PlatformTypeType],
        "MaxConcurrentSessions": NotRequired[int],
        "UsbDeviceFilterStrings": NotRequired[Sequence[str]],
        "SessionScriptS3Location": NotRequired[S3LocationTypeDef],
    },
)

CreateImageBuilderRequestRequestTypeDef = TypedDict(
    "CreateImageBuilderRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceType": str,
        "ImageName": NotRequired[str],
        "ImageArn": NotRequired[str],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "IamRoleArn": NotRequired[str],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "AppstreamAgentVersion": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "AccessEndpoints": NotRequired[Sequence[AccessEndpointTypeDef]],
    },
)

UpdateFleetRequestRequestTypeDef = TypedDict(
    "UpdateFleetRequestRequestTypeDef",
    {
        "ImageName": NotRequired[str],
        "ImageArn": NotRequired[str],
        "Name": NotRequired[str],
        "InstanceType": NotRequired[str],
        "ComputeCapacity": NotRequired[ComputeCapacityTypeDef],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "MaxUserDurationInSeconds": NotRequired[int],
        "DisconnectTimeoutInSeconds": NotRequired[int],
        "DeleteVpcConfig": NotRequired[bool],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "IdleDisconnectTimeoutInSeconds": NotRequired[int],
        "AttributesToDelete": NotRequired[Sequence[FleetAttributeType]],
        "IamRoleArn": NotRequired[str],
        "StreamView": NotRequired[StreamViewType],
        "Platform": NotRequired[PlatformTypeType],
        "MaxConcurrentSessions": NotRequired[int],
        "UsbDeviceFilterStrings": NotRequired[Sequence[str]],
        "SessionScriptS3Location": NotRequired[S3LocationTypeDef],
    },
)

CreateStackRequestRequestTypeDef = TypedDict(
    "CreateStackRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "StorageConnectors": NotRequired[Sequence[StorageConnectorTypeDef]],
        "RedirectURL": NotRequired[str],
        "FeedbackURL": NotRequired[str],
        "UserSettings": NotRequired[Sequence[UserSettingTypeDef]],
        "ApplicationSettings": NotRequired[ApplicationSettingsTypeDef],
        "Tags": NotRequired[Mapping[str, str]],
        "AccessEndpoints": NotRequired[Sequence[AccessEndpointTypeDef]],
        "EmbedHostDomains": NotRequired[Sequence[str]],
        "StreamingExperienceSettings": NotRequired[StreamingExperienceSettingsTypeDef],
    },
)

UpdateStackRequestRequestTypeDef = TypedDict(
    "UpdateStackRequestRequestTypeDef",
    {
        "Name": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "StorageConnectors": NotRequired[Sequence[StorageConnectorTypeDef]],
        "DeleteStorageConnectors": NotRequired[bool],
        "RedirectURL": NotRequired[str],
        "FeedbackURL": NotRequired[str],
        "AttributesToDelete": NotRequired[Sequence[StackAttributeType]],
        "UserSettings": NotRequired[Sequence[UserSettingTypeDef]],
        "ApplicationSettings": NotRequired[ApplicationSettingsTypeDef],
        "AccessEndpoints": NotRequired[Sequence[AccessEndpointTypeDef]],
        "EmbedHostDomains": NotRequired[Sequence[str]],
        "StreamingExperienceSettings": NotRequired[StreamingExperienceSettingsTypeDef],
    },
)

DescribeDirectoryConfigsRequestDescribeDirectoryConfigsPaginateTypeDef = TypedDict(
    "DescribeDirectoryConfigsRequestDescribeDirectoryConfigsPaginateTypeDef",
    {
        "DirectoryNames": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeFleetsRequestDescribeFleetsPaginateTypeDef = TypedDict(
    "DescribeFleetsRequestDescribeFleetsPaginateTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeImageBuildersRequestDescribeImageBuildersPaginateTypeDef = TypedDict(
    "DescribeImageBuildersRequestDescribeImageBuildersPaginateTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeImagesRequestDescribeImagesPaginateTypeDef = TypedDict(
    "DescribeImagesRequestDescribeImagesPaginateTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "Arns": NotRequired[Sequence[str]],
        "Type": NotRequired[VisibilityTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeSessionsRequestDescribeSessionsPaginateTypeDef = TypedDict(
    "DescribeSessionsRequestDescribeSessionsPaginateTypeDef",
    {
        "StackName": str,
        "FleetName": str,
        "UserId": NotRequired[str],
        "AuthenticationType": NotRequired[AuthenticationTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeStacksRequestDescribeStacksPaginateTypeDef = TypedDict(
    "DescribeStacksRequestDescribeStacksPaginateTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeUserStackAssociationsRequestDescribeUserStackAssociationsPaginateTypeDef = TypedDict(
    "DescribeUserStackAssociationsRequestDescribeUserStackAssociationsPaginateTypeDef",
    {
        "StackName": NotRequired[str],
        "UserName": NotRequired[str],
        "AuthenticationType": NotRequired[AuthenticationTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeUsersRequestDescribeUsersPaginateTypeDef = TypedDict(
    "DescribeUsersRequestDescribeUsersPaginateTypeDef",
    {
        "AuthenticationType": AuthenticationTypeType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAssociatedFleetsRequestListAssociatedFleetsPaginateTypeDef = TypedDict(
    "ListAssociatedFleetsRequestListAssociatedFleetsPaginateTypeDef",
    {
        "StackName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAssociatedStacksRequestListAssociatedStacksPaginateTypeDef = TypedDict(
    "ListAssociatedStacksRequestListAssociatedStacksPaginateTypeDef",
    {
        "FleetName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

DescribeFleetsRequestFleetStartedWaitTypeDef = TypedDict(
    "DescribeFleetsRequestFleetStartedWaitTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeFleetsRequestFleetStoppedWaitTypeDef = TypedDict(
    "DescribeFleetsRequestFleetStoppedWaitTypeDef",
    {
        "Names": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeUsersResultTypeDef = TypedDict(
    "DescribeUsersResultTypeDef",
    {
        "Users": List[UserTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEntitledApplicationsResultTypeDef = TypedDict(
    "ListEntitledApplicationsResultTypeDef",
    {
        "EntitledApplications": List[EntitledApplicationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FleetTypeDef = TypedDict(
    "FleetTypeDef",
    {
        "Arn": str,
        "Name": str,
        "InstanceType": str,
        "ComputeCapacityStatus": ComputeCapacityStatusTypeDef,
        "State": FleetStateType,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "ImageName": NotRequired[str],
        "ImageArn": NotRequired[str],
        "FleetType": NotRequired[FleetTypeType],
        "MaxUserDurationInSeconds": NotRequired[int],
        "DisconnectTimeoutInSeconds": NotRequired[int],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "CreatedTime": NotRequired[datetime],
        "FleetErrors": NotRequired[List[FleetErrorTypeDef]],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "IdleDisconnectTimeoutInSeconds": NotRequired[int],
        "IamRoleArn": NotRequired[str],
        "StreamView": NotRequired[StreamViewType],
        "Platform": NotRequired[PlatformTypeType],
        "MaxConcurrentSessions": NotRequired[int],
        "UsbDeviceFilterStrings": NotRequired[List[str]],
        "SessionScriptS3Location": NotRequired[S3LocationTypeDef],
    },
)

FleetPaginatorTypeDef = TypedDict(
    "FleetPaginatorTypeDef",
    {
        "Arn": str,
        "Name": str,
        "InstanceType": str,
        "ComputeCapacityStatus": ComputeCapacityStatusTypeDef,
        "State": FleetStateType,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "ImageName": NotRequired[str],
        "ImageArn": NotRequired[str],
        "FleetType": NotRequired[FleetTypeType],
        "MaxUserDurationInSeconds": NotRequired[int],
        "DisconnectTimeoutInSeconds": NotRequired[int],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
        "CreatedTime": NotRequired[datetime],
        "FleetErrors": NotRequired[List[FleetErrorTypeDef]],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "IdleDisconnectTimeoutInSeconds": NotRequired[int],
        "IamRoleArn": NotRequired[str],
        "StreamView": NotRequired[StreamViewType],
        "Platform": NotRequired[PlatformTypeType],
        "MaxConcurrentSessions": NotRequired[int],
        "UsbDeviceFilterStrings": NotRequired[List[str]],
        "SessionScriptS3Location": NotRequired[S3LocationTypeDef],
    },
)

ImageBuilderPaginatorTypeDef = TypedDict(
    "ImageBuilderPaginatorTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "ImageArn": NotRequired[str],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
        "InstanceType": NotRequired[str],
        "Platform": NotRequired[PlatformTypeType],
        "IamRoleArn": NotRequired[str],
        "State": NotRequired[ImageBuilderStateType],
        "StateChangeReason": NotRequired[ImageBuilderStateChangeReasonTypeDef],
        "CreatedTime": NotRequired[datetime],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "NetworkAccessConfiguration": NotRequired[NetworkAccessConfigurationTypeDef],
        "ImageBuilderErrors": NotRequired[List[ResourceErrorTypeDef]],
        "AppstreamAgentVersion": NotRequired[str],
        "AccessEndpoints": NotRequired[List[AccessEndpointTypeDef]],
    },
)

ImageBuilderTypeDef = TypedDict(
    "ImageBuilderTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "ImageArn": NotRequired[str],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "InstanceType": NotRequired[str],
        "Platform": NotRequired[PlatformTypeType],
        "IamRoleArn": NotRequired[str],
        "State": NotRequired[ImageBuilderStateType],
        "StateChangeReason": NotRequired[ImageBuilderStateChangeReasonTypeDef],
        "CreatedTime": NotRequired[datetime],
        "EnableDefaultInternetAccess": NotRequired[bool],
        "DomainJoinInfo": NotRequired[DomainJoinInfoTypeDef],
        "NetworkAccessConfiguration": NotRequired[NetworkAccessConfigurationTypeDef],
        "ImageBuilderErrors": NotRequired[List[ResourceErrorTypeDef]],
        "AppstreamAgentVersion": NotRequired[str],
        "AccessEndpoints": NotRequired[List[AccessEndpointTypeDef]],
    },
)

SessionTypeDef = TypedDict(
    "SessionTypeDef",
    {
        "Id": str,
        "UserId": str,
        "StackName": str,
        "FleetName": str,
        "State": SessionStateType,
        "ConnectionState": NotRequired[SessionConnectionStateType],
        "StartTime": NotRequired[datetime],
        "MaxExpirationTime": NotRequired[datetime],
        "AuthenticationType": NotRequired[AuthenticationTypeType],
        "NetworkAccessConfiguration": NotRequired[NetworkAccessConfigurationTypeDef],
    },
)

SharedImagePermissionsTypeDef = TypedDict(
    "SharedImagePermissionsTypeDef",
    {
        "sharedAccountId": str,
        "imagePermissions": ImagePermissionsTypeDef,
    },
)

UpdateImagePermissionsRequestRequestTypeDef = TypedDict(
    "UpdateImagePermissionsRequestRequestTypeDef",
    {
        "Name": str,
        "SharedAccountId": str,
        "ImagePermissions": ImagePermissionsTypeDef,
    },
)

UsageReportSubscriptionTypeDef = TypedDict(
    "UsageReportSubscriptionTypeDef",
    {
        "S3BucketName": NotRequired[str],
        "Schedule": NotRequired[Literal["DAILY"]],
        "LastGeneratedReportDate": NotRequired[datetime],
        "SubscriptionErrors": NotRequired[List[LastReportGenerationExecutionErrorTypeDef]],
    },
)

StackTypeDef = TypedDict(
    "StackTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "StorageConnectors": NotRequired[List[StorageConnectorTypeDef]],
        "RedirectURL": NotRequired[str],
        "FeedbackURL": NotRequired[str],
        "StackErrors": NotRequired[List[StackErrorTypeDef]],
        "UserSettings": NotRequired[List[UserSettingTypeDef]],
        "ApplicationSettings": NotRequired[ApplicationSettingsResponseTypeDef],
        "AccessEndpoints": NotRequired[List[AccessEndpointTypeDef]],
        "EmbedHostDomains": NotRequired[List[str]],
        "StreamingExperienceSettings": NotRequired[StreamingExperienceSettingsTypeDef],
    },
)

StackPaginatorTypeDef = TypedDict(
    "StackPaginatorTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "StorageConnectors": NotRequired[List[StorageConnectorPaginatorTypeDef]],
        "RedirectURL": NotRequired[str],
        "FeedbackURL": NotRequired[str],
        "StackErrors": NotRequired[List[StackErrorTypeDef]],
        "UserSettings": NotRequired[List[UserSettingTypeDef]],
        "ApplicationSettings": NotRequired[ApplicationSettingsResponseTypeDef],
        "AccessEndpoints": NotRequired[List[AccessEndpointTypeDef]],
        "EmbedHostDomains": NotRequired[List[str]],
        "StreamingExperienceSettings": NotRequired[StreamingExperienceSettingsTypeDef],
    },
)

CreateAppBlockBuilderResultTypeDef = TypedDict(
    "CreateAppBlockBuilderResultTypeDef",
    {
        "AppBlockBuilder": AppBlockBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAppBlockBuildersResultTypeDef = TypedDict(
    "DescribeAppBlockBuildersResultTypeDef",
    {
        "AppBlockBuilders": List[AppBlockBuilderTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartAppBlockBuilderResultTypeDef = TypedDict(
    "StartAppBlockBuilderResultTypeDef",
    {
        "AppBlockBuilder": AppBlockBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopAppBlockBuilderResultTypeDef = TypedDict(
    "StopAppBlockBuilderResultTypeDef",
    {
        "AppBlockBuilder": AppBlockBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAppBlockBuilderResultTypeDef = TypedDict(
    "UpdateAppBlockBuilderResultTypeDef",
    {
        "AppBlockBuilder": AppBlockBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateApplicationResultTypeDef = TypedDict(
    "CreateApplicationResultTypeDef",
    {
        "Application": ApplicationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeApplicationsResultTypeDef = TypedDict(
    "DescribeApplicationsResultTypeDef",
    {
        "Applications": List[ApplicationTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImageTypeDef = TypedDict(
    "ImageTypeDef",
    {
        "Name": str,
        "Arn": NotRequired[str],
        "BaseImageArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "State": NotRequired[ImageStateType],
        "Visibility": NotRequired[VisibilityTypeType],
        "ImageBuilderSupported": NotRequired[bool],
        "ImageBuilderName": NotRequired[str],
        "Platform": NotRequired[PlatformTypeType],
        "Description": NotRequired[str],
        "StateChangeReason": NotRequired[ImageStateChangeReasonTypeDef],
        "Applications": NotRequired[List[ApplicationTypeDef]],
        "CreatedTime": NotRequired[datetime],
        "PublicBaseImageReleasedDate": NotRequired[datetime],
        "AppstreamAgentVersion": NotRequired[str],
        "ImagePermissions": NotRequired[ImagePermissionsTypeDef],
        "ImageErrors": NotRequired[List[ResourceErrorTypeDef]],
    },
)

UpdateApplicationResultTypeDef = TypedDict(
    "UpdateApplicationResultTypeDef",
    {
        "Application": ApplicationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AppBlockTypeDef = TypedDict(
    "AppBlockTypeDef",
    {
        "Name": str,
        "Arn": str,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "SourceS3Location": NotRequired[S3LocationTypeDef],
        "SetupScriptDetails": NotRequired[ScriptDetailsTypeDef],
        "CreatedTime": NotRequired[datetime],
        "PostSetupScriptDetails": NotRequired[ScriptDetailsTypeDef],
        "PackagingType": NotRequired[PackagingTypeType],
        "State": NotRequired[AppBlockStateType],
        "AppBlockErrors": NotRequired[List[ErrorDetailsTypeDef]],
    },
)

CreateAppBlockRequestRequestTypeDef = TypedDict(
    "CreateAppBlockRequestRequestTypeDef",
    {
        "Name": str,
        "SourceS3Location": S3LocationTypeDef,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "SetupScriptDetails": NotRequired[ScriptDetailsTypeDef],
        "Tags": NotRequired[Mapping[str, str]],
        "PostSetupScriptDetails": NotRequired[ScriptDetailsTypeDef],
        "PackagingType": NotRequired[PackagingTypeType],
    },
)

BatchAssociateUserStackResultTypeDef = TypedDict(
    "BatchAssociateUserStackResultTypeDef",
    {
        "errors": List[UserStackAssociationErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchDisassociateUserStackResultTypeDef = TypedDict(
    "BatchDisassociateUserStackResultTypeDef",
    {
        "errors": List[UserStackAssociationErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDirectoryConfigResultTypeDef = TypedDict(
    "CreateDirectoryConfigResultTypeDef",
    {
        "DirectoryConfig": DirectoryConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDirectoryConfigsResultTypeDef = TypedDict(
    "DescribeDirectoryConfigsResultTypeDef",
    {
        "DirectoryConfigs": List[DirectoryConfigTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDirectoryConfigResultTypeDef = TypedDict(
    "UpdateDirectoryConfigResultTypeDef",
    {
        "DirectoryConfig": DirectoryConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEntitlementResultTypeDef = TypedDict(
    "CreateEntitlementResultTypeDef",
    {
        "Entitlement": EntitlementTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEntitlementsResultTypeDef = TypedDict(
    "DescribeEntitlementsResultTypeDef",
    {
        "Entitlements": List[EntitlementTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEntitlementResultTypeDef = TypedDict(
    "UpdateEntitlementResultTypeDef",
    {
        "Entitlement": EntitlementTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFleetResultTypeDef = TypedDict(
    "CreateFleetResultTypeDef",
    {
        "Fleet": FleetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFleetsResultTypeDef = TypedDict(
    "DescribeFleetsResultTypeDef",
    {
        "Fleets": List[FleetTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateFleetResultTypeDef = TypedDict(
    "UpdateFleetResultTypeDef",
    {
        "Fleet": FleetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFleetsResultPaginatorTypeDef = TypedDict(
    "DescribeFleetsResultPaginatorTypeDef",
    {
        "Fleets": List[FleetPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImageBuildersResultPaginatorTypeDef = TypedDict(
    "DescribeImageBuildersResultPaginatorTypeDef",
    {
        "ImageBuilders": List[ImageBuilderPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateImageBuilderResultTypeDef = TypedDict(
    "CreateImageBuilderResultTypeDef",
    {
        "ImageBuilder": ImageBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteImageBuilderResultTypeDef = TypedDict(
    "DeleteImageBuilderResultTypeDef",
    {
        "ImageBuilder": ImageBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImageBuildersResultTypeDef = TypedDict(
    "DescribeImageBuildersResultTypeDef",
    {
        "ImageBuilders": List[ImageBuilderTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartImageBuilderResultTypeDef = TypedDict(
    "StartImageBuilderResultTypeDef",
    {
        "ImageBuilder": ImageBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopImageBuilderResultTypeDef = TypedDict(
    "StopImageBuilderResultTypeDef",
    {
        "ImageBuilder": ImageBuilderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSessionsResultTypeDef = TypedDict(
    "DescribeSessionsResultTypeDef",
    {
        "Sessions": List[SessionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImagePermissionsResultTypeDef = TypedDict(
    "DescribeImagePermissionsResultTypeDef",
    {
        "Name": str,
        "SharedImagePermissionsList": List[SharedImagePermissionsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeUsageReportSubscriptionsResultTypeDef = TypedDict(
    "DescribeUsageReportSubscriptionsResultTypeDef",
    {
        "UsageReportSubscriptions": List[UsageReportSubscriptionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStackResultTypeDef = TypedDict(
    "CreateStackResultTypeDef",
    {
        "Stack": StackTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStacksResultTypeDef = TypedDict(
    "DescribeStacksResultTypeDef",
    {
        "Stacks": List[StackTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateStackResultTypeDef = TypedDict(
    "UpdateStackResultTypeDef",
    {
        "Stack": StackTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStacksResultPaginatorTypeDef = TypedDict(
    "DescribeStacksResultPaginatorTypeDef",
    {
        "Stacks": List[StackPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUpdatedImageResultTypeDef = TypedDict(
    "CreateUpdatedImageResultTypeDef",
    {
        "image": ImageTypeDef,
        "canUpdateImage": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteImageResultTypeDef = TypedDict(
    "DeleteImageResultTypeDef",
    {
        "Image": ImageTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImagesResultTypeDef = TypedDict(
    "DescribeImagesResultTypeDef",
    {
        "Images": List[ImageTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAppBlockResultTypeDef = TypedDict(
    "CreateAppBlockResultTypeDef",
    {
        "AppBlock": AppBlockTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAppBlocksResultTypeDef = TypedDict(
    "DescribeAppBlocksResultTypeDef",
    {
        "AppBlocks": List[AppBlockTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
