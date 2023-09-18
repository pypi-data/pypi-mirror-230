'''
# awscommunity-resource-lookup

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::Resource::Lookup` v1.5.0.

## Description

This resource uses AWS Cloud Control API to perform a lookup of a resource of a given type (such as, `AWS::EC2::VPC`) in your AWS account and current region, based on a query you specify.  If only one match is found, this resource returns the primary ID of the resource (in the `AWS::EC2::VPC` example, the VPC ID) and the resource properties, that you can then reference in your template with the `Fn::GetAtt` intrinsic function.  Specify resource type search targets that are supported by Cloud Control API.

## References

* [Documentation](https://github.com/aws-cloudformation/community-registry-extensions/blob/main/resources/Resource_Lookup/README.md)
* [Source](https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/Resource_Lookup)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::Resource::Lookup \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-Resource-Lookup \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::Resource::Lookup`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-resource-lookup+v1.5.0).
* Issues related to `AwsCommunity::Resource::Lookup` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions/blob/main/resources/Resource_Lookup/README.md).

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


class CfnLookup(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-resource-lookup.CfnLookup",
):
    '''A CloudFormation ``AwsCommunity::Resource::Lookup``.

    :cloudformationResource: AwsCommunity::Resource::Lookup
    :link: https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/Resource_Lookup
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        jmes_path_query: builtins.str,
        resource_lookup_role_arn: builtins.str,
        type_name: builtins.str,
        lookup_serial_number: typing.Optional[builtins.str] = None,
        resource_model: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AwsCommunity::Resource::Lookup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param jmes_path_query: A query, in JMESPath (https://jmespath.org/) format, to perform the resource lookup; for example: ``Tags[?Key == 'Owner' && Value == 'test-only']``. When you specify a new value on resource updates (for example, when you update the stack that describes this resource), a new lookup will be performed.
        :param resource_lookup_role_arn: The Amazon Resource Name (ARN) of the IAM role you wish to use for performing resource lookup operations in your AWS account on your behalf; for example: ``arn:aws:iam::111122223333:role/my-example-role``. The role whose ARN you specify for this property is passed to AWS Cloud Control API's ``ListResources`` and ``GetResource`` actions when this resource type calls them on your behalf against resource type targets (such as, ``AWS::EC2::VPC``). As for the role, for example, you could create an IAM role whose ``Service`` ``Principal`` is ``cloudformation.amazonaws.com`` in the trust policy, and whose policy is e.g., a ``ReadOnlyAccess`` AWS managed policy, or another managed policy you choose, or your own policy, depending on which permissions you require.
        :param type_name: The resource type name you wish to use for the lookup operation.
        :param lookup_serial_number: Optional, numeric integer value (such as ``1``, ``2``), that you can specify to induce a new search on e.g., stack updates without modifying the value for ``JmesPathQuery``. Specify a value that is different from the previous one to induce the update; note that either adding this property to the resource if not present before an update, or removing it if previously added to the resource, will yield the same effect of changing the property value and will induce an update.
        :param resource_model: The model of the resource you're using: this additional information is required if you're using a resource type shown in the ``Resources that require additional information`` page (https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-operations-list.html#resource-operations-list-containers). Specify the required properties using the JSON format; for example, to specify ``LoadBalancerArn`` and its ARN value for ``AWS::ElasticLoadBalancingV2::Listener`` (that you specify in the ``TypeName`` property): ``{"LoadBalancerArn": "REPLACE_WITH_YOUR_LOAD_BALANCER_ARN"}``.
        :param tags: Optional key-value pairs object (such as, ``Env: Dev``, ``Name: Test``) to associate to the AWS Systems Manager Parameter Store parameter resource, that the implementation of this resource type creates in your account to persist the lookup result.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be669f514a474a9358c1506e3639a7b8bde9665fe687ccd003d65168782083a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnLookupProps(
            jmes_path_query=jmes_path_query,
            resource_lookup_role_arn=resource_lookup_role_arn,
            type_name=type_name,
            lookup_serial_number=lookup_serial_number,
            resource_model=resource_model,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrResourceIdentifier")
    def attr_resource_identifier(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Resource::Lookup.ResourceIdentifier``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/Resource_Lookup
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResourceIdentifier"))

    @builtins.property
    @jsii.member(jsii_name="attrResourceLookupId")
    def attr_resource_lookup_id(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Resource::Lookup.ResourceLookupId``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/Resource_Lookup
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResourceLookupId"))

    @builtins.property
    @jsii.member(jsii_name="attrResourceProperties")
    def attr_resource_properties(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Resource::Lookup.ResourceProperties``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/Resource_Lookup
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrResourceProperties"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnLookupProps":
        '''Resource props.'''
        return typing.cast("CfnLookupProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-resource-lookup.CfnLookupProps",
    jsii_struct_bases=[],
    name_mapping={
        "jmes_path_query": "jmesPathQuery",
        "resource_lookup_role_arn": "resourceLookupRoleArn",
        "type_name": "typeName",
        "lookup_serial_number": "lookupSerialNumber",
        "resource_model": "resourceModel",
        "tags": "tags",
    },
)
class CfnLookupProps:
    def __init__(
        self,
        *,
        jmes_path_query: builtins.str,
        resource_lookup_role_arn: builtins.str,
        type_name: builtins.str,
        lookup_serial_number: typing.Optional[builtins.str] = None,
        resource_model: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''This resource uses AWS Cloud Control API to perform a lookup of a resource of a given type (such as, ``AWS::EC2::VPC``) in your AWS account and current region, based on a query you specify.

        If only one match is found, this resource returns the primary ID of the resource (in the ``AWS::EC2::VPC`` example, the VPC ID) and the resource properties, that you can then reference in your template with the ``Fn::GetAtt`` intrinsic function.  Specify resource type search targets that are supported by Cloud Control API.

        :param jmes_path_query: A query, in JMESPath (https://jmespath.org/) format, to perform the resource lookup; for example: ``Tags[?Key == 'Owner' && Value == 'test-only']``. When you specify a new value on resource updates (for example, when you update the stack that describes this resource), a new lookup will be performed.
        :param resource_lookup_role_arn: The Amazon Resource Name (ARN) of the IAM role you wish to use for performing resource lookup operations in your AWS account on your behalf; for example: ``arn:aws:iam::111122223333:role/my-example-role``. The role whose ARN you specify for this property is passed to AWS Cloud Control API's ``ListResources`` and ``GetResource`` actions when this resource type calls them on your behalf against resource type targets (such as, ``AWS::EC2::VPC``). As for the role, for example, you could create an IAM role whose ``Service`` ``Principal`` is ``cloudformation.amazonaws.com`` in the trust policy, and whose policy is e.g., a ``ReadOnlyAccess`` AWS managed policy, or another managed policy you choose, or your own policy, depending on which permissions you require.
        :param type_name: The resource type name you wish to use for the lookup operation.
        :param lookup_serial_number: Optional, numeric integer value (such as ``1``, ``2``), that you can specify to induce a new search on e.g., stack updates without modifying the value for ``JmesPathQuery``. Specify a value that is different from the previous one to induce the update; note that either adding this property to the resource if not present before an update, or removing it if previously added to the resource, will yield the same effect of changing the property value and will induce an update.
        :param resource_model: The model of the resource you're using: this additional information is required if you're using a resource type shown in the ``Resources that require additional information`` page (https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-operations-list.html#resource-operations-list-containers). Specify the required properties using the JSON format; for example, to specify ``LoadBalancerArn`` and its ARN value for ``AWS::ElasticLoadBalancingV2::Listener`` (that you specify in the ``TypeName`` property): ``{"LoadBalancerArn": "REPLACE_WITH_YOUR_LOAD_BALANCER_ARN"}``.
        :param tags: Optional key-value pairs object (such as, ``Env: Dev``, ``Name: Test``) to associate to the AWS Systems Manager Parameter Store parameter resource, that the implementation of this resource type creates in your account to persist the lookup result.

        :schema: CfnLookupProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a90370851cc08f62ab8c81629194178ecab8c5cbb3667f775a4b9c90657dca)
            check_type(argname="argument jmes_path_query", value=jmes_path_query, expected_type=type_hints["jmes_path_query"])
            check_type(argname="argument resource_lookup_role_arn", value=resource_lookup_role_arn, expected_type=type_hints["resource_lookup_role_arn"])
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument lookup_serial_number", value=lookup_serial_number, expected_type=type_hints["lookup_serial_number"])
            check_type(argname="argument resource_model", value=resource_model, expected_type=type_hints["resource_model"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "jmes_path_query": jmes_path_query,
            "resource_lookup_role_arn": resource_lookup_role_arn,
            "type_name": type_name,
        }
        if lookup_serial_number is not None:
            self._values["lookup_serial_number"] = lookup_serial_number
        if resource_model is not None:
            self._values["resource_model"] = resource_model
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def jmes_path_query(self) -> builtins.str:
        '''A query, in JMESPath (https://jmespath.org/) format, to perform the resource lookup; for example: ``Tags[?Key == 'Owner' && Value == 'test-only']``.  When you specify a new value on resource updates (for example, when you update the stack that describes this resource), a new lookup will be performed.

        :schema: CfnLookupProps#JmesPathQuery
        '''
        result = self._values.get("jmes_path_query")
        assert result is not None, "Required property 'jmes_path_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_lookup_role_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the IAM role you wish to use for performing resource lookup operations in your AWS account on your behalf;

        for example: ``arn:aws:iam::111122223333:role/my-example-role``.  The role whose ARN you specify for this property is passed to AWS Cloud Control API's ``ListResources`` and ``GetResource`` actions when this resource type calls them on your behalf against resource type targets (such as, ``AWS::EC2::VPC``).  As for the role, for example, you could create an IAM role whose ``Service`` ``Principal`` is ``cloudformation.amazonaws.com`` in the trust policy, and whose policy is e.g., a ``ReadOnlyAccess`` AWS managed policy, or another managed policy you choose, or your own policy, depending on which permissions you require.

        :schema: CfnLookupProps#ResourceLookupRoleArn
        '''
        result = self._values.get("resource_lookup_role_arn")
        assert result is not None, "Required property 'resource_lookup_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''The resource type name you wish to use for the lookup operation.

        :schema: CfnLookupProps#TypeName
        '''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_serial_number(self) -> typing.Optional[builtins.str]:
        '''Optional, numeric integer value (such as ``1``, ``2``), that you can specify to induce a new search on e.g., stack updates without modifying the value for ``JmesPathQuery``.  Specify a value that is different from the previous one to induce the update; note that either adding this property to the resource if not present before an update, or removing it if previously added to the resource, will yield the same effect of changing the property value and will induce an update.

        :schema: CfnLookupProps#LookupSerialNumber
        '''
        result = self._values.get("lookup_serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_model(self) -> typing.Optional[builtins.str]:
        '''The model of the resource you're using: this additional information is required if you're using a resource type shown in the ``Resources that require additional information`` page (https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/resource-operations-list.html#resource-operations-list-containers).  Specify the required properties using the JSON format; for example, to specify ``LoadBalancerArn`` and its ARN value for ``AWS::ElasticLoadBalancingV2::Listener`` (that you specify in the ``TypeName`` property): ``{"LoadBalancerArn": "REPLACE_WITH_YOUR_LOAD_BALANCER_ARN"}``.

        :schema: CfnLookupProps#ResourceModel
        '''
        result = self._values.get("resource_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''Optional key-value pairs object (such as, ``Env: Dev``, ``Name: Test``) to associate to the AWS Systems Manager Parameter Store parameter resource, that the implementation of this resource type creates in your account to persist the lookup result.

        :schema: CfnLookupProps#Tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnLookupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnLookup",
    "CfnLookupProps",
]

publication.publish()

def _typecheckingstub__5be669f514a474a9358c1506e3639a7b8bde9665fe687ccd003d65168782083a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    jmes_path_query: builtins.str,
    resource_lookup_role_arn: builtins.str,
    type_name: builtins.str,
    lookup_serial_number: typing.Optional[builtins.str] = None,
    resource_model: typing.Optional[builtins.str] = None,
    tags: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a90370851cc08f62ab8c81629194178ecab8c5cbb3667f775a4b9c90657dca(
    *,
    jmes_path_query: builtins.str,
    resource_lookup_role_arn: builtins.str,
    type_name: builtins.str,
    lookup_serial_number: typing.Optional[builtins.str] = None,
    resource_model: typing.Optional[builtins.str] = None,
    tags: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass
