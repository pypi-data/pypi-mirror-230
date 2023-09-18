'''
# awscommunity-s3-deletebucketcontents

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::S3::DeleteBucketContents` v1.17.0.

## Description

An experimental extension that deletes all contents of the referenced bucket when the stack is deleted. Use with caution!

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::S3::DeleteBucketContents \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-S3-DeleteBucketContents \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::S3::DeleteBucketContents`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-s3-deletebucketcontents+v1.17.0).
* Issues related to `AwsCommunity::S3::DeleteBucketContents` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions.git).

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


class CfnDeleteBucketContents(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-s3-deletebucketcontents.CfnDeleteBucketContents",
):
    '''A CloudFormation ``AwsCommunity::S3::DeleteBucketContents``.

    :cloudformationResource: AwsCommunity::S3::DeleteBucketContents
    :link: https://github.com/aws-cloudformation/community-registry-extensions.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
    ) -> None:
        '''Create a new ``AwsCommunity::S3::DeleteBucketContents``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param bucket_name: The name of the bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56aaf6553f8b39971fb7b45b74b947a40a7b50411b70bccd9614204539ed1956)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnDeleteBucketContentsProps(bucket_name=bucket_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnDeleteBucketContentsProps":
        '''Resource props.'''
        return typing.cast("CfnDeleteBucketContentsProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-deletebucketcontents.CfnDeleteBucketContentsProps",
    jsii_struct_bases=[],
    name_mapping={"bucket_name": "bucketName"},
)
class CfnDeleteBucketContentsProps:
    def __init__(self, *, bucket_name: builtins.str) -> None:
        '''An experimental extension that deletes all contents of the referenced bucket when the stack is deleted.

        Use with caution!

        :param bucket_name: The name of the bucket.

        :schema: CfnDeleteBucketContentsProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b73cefc36f9fbaf3c7bb588579cf1a06bb00627052a7abdf1565da9222a41bfd)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_name": bucket_name,
        }

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''The name of the bucket.

        :schema: CfnDeleteBucketContentsProps#BucketName
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeleteBucketContentsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnDeleteBucketContents",
    "CfnDeleteBucketContentsProps",
]

publication.publish()

def _typecheckingstub__56aaf6553f8b39971fb7b45b74b947a40a7b50411b70bccd9614204539ed1956(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b73cefc36f9fbaf3c7bb588579cf1a06bb00627052a7abdf1565da9222a41bfd(
    *,
    bucket_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
