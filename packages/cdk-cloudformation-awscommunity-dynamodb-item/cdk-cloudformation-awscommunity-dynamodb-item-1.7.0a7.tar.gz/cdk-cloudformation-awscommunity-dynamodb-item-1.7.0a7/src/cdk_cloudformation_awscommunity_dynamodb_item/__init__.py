'''
# awscommunity-dynamodb-item

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::DynamoDB::Item` v1.7.0.

## Description

This resource will manage the lifecycle of items in a DynamoDB table

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::DynamoDB::Item \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-DynamoDB-Item \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::DynamoDB::Item`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-dynamodb-item+v1.7.0).
* Issues related to `AwsCommunity::DynamoDB::Item` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions.git).

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


class CfnItem(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-dynamodb-item.CfnItem",
):
    '''A CloudFormation ``AwsCommunity::DynamoDB::Item``.

    :cloudformationResource: AwsCommunity::DynamoDB::Item
    :link: https://github.com/aws-cloudformation/community-registry-extensions.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        keys: typing.Sequence[typing.Union["Key", typing.Dict[builtins.str, typing.Any]]],
        table_name: builtins.str,
        item: typing.Any = None,
    ) -> None:
        '''Create a new ``AwsCommunity::DynamoDB::Item``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param keys: 
        :param table_name: The table to put the item into.
        :param item: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc3b03d1fe7da447962092f3cf91474e82cb7c50a0db6cf87a335b38f5b69ab9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnItemProps(keys=keys, table_name=table_name, item=item)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrCompositeKey")
    def attr_composite_key(self) -> builtins.str:
        '''Attribute ``AwsCommunity::DynamoDB::Item.CompositeKey``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCompositeKey"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnItemProps":
        '''Resource props.'''
        return typing.cast("CfnItemProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-dynamodb-item.CfnItemProps",
    jsii_struct_bases=[],
    name_mapping={"keys": "keys", "table_name": "tableName", "item": "item"},
)
class CfnItemProps:
    def __init__(
        self,
        *,
        keys: typing.Sequence[typing.Union["Key", typing.Dict[builtins.str, typing.Any]]],
        table_name: builtins.str,
        item: typing.Any = None,
    ) -> None:
        '''This resource will manage the lifecycle of items in a DynamoDB table.

        :param keys: 
        :param table_name: The table to put the item into.
        :param item: 

        :schema: CfnItemProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__188da368e00e9aaa4072b7bc630c9731aae09bfd5ecbc54f71bfa6f79c2754d8)
            check_type(argname="argument keys", value=keys, expected_type=type_hints["keys"])
            check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
            check_type(argname="argument item", value=item, expected_type=type_hints["item"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "keys": keys,
            "table_name": table_name,
        }
        if item is not None:
            self._values["item"] = item

    @builtins.property
    def keys(self) -> typing.List["Key"]:
        '''
        :schema: CfnItemProps#Keys
        '''
        result = self._values.get("keys")
        assert result is not None, "Required property 'keys' is missing"
        return typing.cast(typing.List["Key"], result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''The table to put the item into.

        :schema: CfnItemProps#TableName
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def item(self) -> typing.Any:
        '''
        :schema: CfnItemProps#Item
        '''
        result = self._values.get("item")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnItemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-dynamodb-item.Key",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_type": "attributeType",
        "attribute_value": "attributeValue",
    },
)
class Key:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_type: builtins.str,
        attribute_value: builtins.str,
    ) -> None:
        '''
        :param attribute_name: 
        :param attribute_type: 
        :param attribute_value: 

        :schema: Key
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__983bdca4e7aee7c73796409ede0e35e22fe29a8308892d167b5b3cd87216c5c1)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument attribute_type", value=attribute_type, expected_type=type_hints["attribute_type"])
            check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_name": attribute_name,
            "attribute_type": attribute_type,
            "attribute_value": attribute_value,
        }

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''
        :schema: Key#AttributeName
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_type(self) -> builtins.str:
        '''
        :schema: Key#AttributeType
        '''
        result = self._values.get("attribute_type")
        assert result is not None, "Required property 'attribute_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''
        :schema: Key#AttributeValue
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Key(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnItem",
    "CfnItemProps",
    "Key",
]

publication.publish()

def _typecheckingstub__fc3b03d1fe7da447962092f3cf91474e82cb7c50a0db6cf87a335b38f5b69ab9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    keys: typing.Sequence[typing.Union[Key, typing.Dict[builtins.str, typing.Any]]],
    table_name: builtins.str,
    item: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__188da368e00e9aaa4072b7bc630c9731aae09bfd5ecbc54f71bfa6f79c2754d8(
    *,
    keys: typing.Sequence[typing.Union[Key, typing.Dict[builtins.str, typing.Any]]],
    table_name: builtins.str,
    item: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983bdca4e7aee7c73796409ede0e35e22fe29a8308892d167b5b3cd87216c5c1(
    *,
    attribute_name: builtins.str,
    attribute_type: builtins.str,
    attribute_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
