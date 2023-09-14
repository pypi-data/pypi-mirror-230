'''
# poc-azure-blobstorage

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `POC::Azure::BlobStorage` v1.1.0.

## Description

An example resource that creates an Azure Storage account along with a Blob container.

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name POC::Azure::BlobStorage \
  --publisher-id fbafc40f22913f42efb711903e40c701642af7ee \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/fbafc40f22913f42efb711903e40c701642af7ee/POC-Azure-BlobStorage \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `POC::Azure::BlobStorage`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fpoc-azure-blobstorage+v1.1.0).
* Issues related to `POC::Azure::BlobStorage` should be reported to the [publisher](undefined).

## License

Distributed under the Apache-2.0 License.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8


class CfnBlobStorage(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/poc-azure-blobstorage.CfnBlobStorage",
):
    '''A CloudFormation ``POC::Azure::BlobStorage``.

    :cloudformationResource: POC::Azure::BlobStorage
    :link: http://unknown-url
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        azure_client_id: builtins.str,
        azure_client_secret: builtins.str,
        azure_subscription_id: builtins.str,
        azure_tenant_id: builtins.str,
    ) -> None:
        '''Create a new ``POC::Azure::BlobStorage``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param azure_client_id: App ID CloudFormation will use to access Azure.
        :param azure_client_secret: Client credentials CloudFormation will use to authenticate to Azure and access services.
        :param azure_subscription_id: Subscription ID of the Azure Account.
        :param azure_tenant_id: Directory ID CloudFormation will use to access Azure.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7da23994f5f376c90a1df7b30cf6e1bebb26e3a46d57bc7a879c2d5ca3521621)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnBlobStorageProps(
            azure_client_id=azure_client_id,
            azure_client_secret=azure_client_secret,
            azure_subscription_id=azure_subscription_id,
            azure_tenant_id=azure_tenant_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrAzureBlobContainerUrl")
    def attr_azure_blob_container_url(self) -> builtins.str:
        '''Attribute ``POC::Azure::BlobStorage.AzureBlobContainerUrl``.

        :link: http://unknown-url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAzureBlobContainerUrl"))

    @builtins.property
    @jsii.member(jsii_name="attrAzureBlobStorageAccountName")
    def attr_azure_blob_storage_account_name(self) -> builtins.str:
        '''Attribute ``POC::Azure::BlobStorage.AzureBlobStorageAccountName``.

        :link: http://unknown-url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAzureBlobStorageAccountName"))

    @builtins.property
    @jsii.member(jsii_name="attrAzureResourceGroup")
    def attr_azure_resource_group(self) -> builtins.str:
        '''Attribute ``POC::Azure::BlobStorage.AzureResourceGroup``.

        :link: http://unknown-url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAzureResourceGroup"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnBlobStorageProps":
        '''Resource props.'''
        return typing.cast("CfnBlobStorageProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/poc-azure-blobstorage.CfnBlobStorageProps",
    jsii_struct_bases=[],
    name_mapping={
        "azure_client_id": "azureClientId",
        "azure_client_secret": "azureClientSecret",
        "azure_subscription_id": "azureSubscriptionId",
        "azure_tenant_id": "azureTenantId",
    },
)
class CfnBlobStorageProps:
    def __init__(
        self,
        *,
        azure_client_id: builtins.str,
        azure_client_secret: builtins.str,
        azure_subscription_id: builtins.str,
        azure_tenant_id: builtins.str,
    ) -> None:
        '''An example resource that creates an Azure Storage account along with a Blob container.

        :param azure_client_id: App ID CloudFormation will use to access Azure.
        :param azure_client_secret: Client credentials CloudFormation will use to authenticate to Azure and access services.
        :param azure_subscription_id: Subscription ID of the Azure Account.
        :param azure_tenant_id: Directory ID CloudFormation will use to access Azure.

        :schema: CfnBlobStorageProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbb8995e62aad39d6797a8751682597908d24d2b518a55b4f643c51a196aedb6)
            check_type(argname="argument azure_client_id", value=azure_client_id, expected_type=type_hints["azure_client_id"])
            check_type(argname="argument azure_client_secret", value=azure_client_secret, expected_type=type_hints["azure_client_secret"])
            check_type(argname="argument azure_subscription_id", value=azure_subscription_id, expected_type=type_hints["azure_subscription_id"])
            check_type(argname="argument azure_tenant_id", value=azure_tenant_id, expected_type=type_hints["azure_tenant_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "azure_client_id": azure_client_id,
            "azure_client_secret": azure_client_secret,
            "azure_subscription_id": azure_subscription_id,
            "azure_tenant_id": azure_tenant_id,
        }

    @builtins.property
    def azure_client_id(self) -> builtins.str:
        '''App ID CloudFormation will use to access Azure.

        :schema: CfnBlobStorageProps#AzureClientId
        '''
        result = self._values.get("azure_client_id")
        assert result is not None, "Required property 'azure_client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def azure_client_secret(self) -> builtins.str:
        '''Client credentials CloudFormation will use to authenticate to Azure and access services.

        :schema: CfnBlobStorageProps#AzureClientSecret
        '''
        result = self._values.get("azure_client_secret")
        assert result is not None, "Required property 'azure_client_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def azure_subscription_id(self) -> builtins.str:
        '''Subscription ID of the Azure Account.

        :schema: CfnBlobStorageProps#AzureSubscriptionId
        '''
        result = self._values.get("azure_subscription_id")
        assert result is not None, "Required property 'azure_subscription_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def azure_tenant_id(self) -> builtins.str:
        '''Directory ID CloudFormation will use to access Azure.

        :schema: CfnBlobStorageProps#AzureTenantId
        '''
        result = self._values.get("azure_tenant_id")
        assert result is not None, "Required property 'azure_tenant_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBlobStorageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnBlobStorage",
    "CfnBlobStorageProps",
]

publication.publish()

def _typecheckingstub__7da23994f5f376c90a1df7b30cf6e1bebb26e3a46d57bc7a879c2d5ca3521621(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    azure_client_id: builtins.str,
    azure_client_secret: builtins.str,
    azure_subscription_id: builtins.str,
    azure_tenant_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbb8995e62aad39d6797a8751682597908d24d2b518a55b4f643c51a196aedb6(
    *,
    azure_client_id: builtins.str,
    azure_client_secret: builtins.str,
    azure_subscription_id: builtins.str,
    azure_tenant_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
