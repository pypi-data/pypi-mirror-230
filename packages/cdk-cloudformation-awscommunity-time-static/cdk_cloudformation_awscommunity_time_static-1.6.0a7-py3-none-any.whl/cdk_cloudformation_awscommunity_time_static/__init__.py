'''
# awscommunity-time-static

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::Time::Static` v1.6.0.

## Description

Creates a static time stamp.

## References

* [Source](https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::Time::Static \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-Time-Static \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::Time::Static`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-time-static+v1.6.0).
* Issues related to `AwsCommunity::Time::Static` should be reported to the [publisher](https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git).

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


class CfnStatic(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-time-static.CfnStatic",
):
    '''A CloudFormation ``AwsCommunity::Time::Static``.

    :cloudformationResource: AwsCommunity::Time::Static
    :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::Time::Static``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param time: Optional parameter to represent the time or default is now.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca02b500ebe924e37a7d228fa16032c0be39ce424af948e1624b418482d710f5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnStaticProps(time=time)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrDay")
    def attr_day(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Day``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDay"))

    @builtins.property
    @jsii.member(jsii_name="attrHour")
    def attr_hour(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Hour``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrHour"))

    @builtins.property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Id``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="attrMinute")
    def attr_minute(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Minute``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMinute"))

    @builtins.property
    @jsii.member(jsii_name="attrMonth")
    def attr_month(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Month``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMonth"))

    @builtins.property
    @jsii.member(jsii_name="attrSecond")
    def attr_second(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Second``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrSecond"))

    @builtins.property
    @jsii.member(jsii_name="attrUnix")
    def attr_unix(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Unix``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUnix"))

    @builtins.property
    @jsii.member(jsii_name="attrUtc")
    def attr_utc(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Utc``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUtc"))

    @builtins.property
    @jsii.member(jsii_name="attrYear")
    def attr_year(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Static.Year``.

        :link: https://github.com/aws-cloudformation/awscommunity-registry-extensions/resources/Time_Static.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrYear"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnStaticProps":
        '''Resource props.'''
        return typing.cast("CfnStaticProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-time-static.CfnStaticProps",
    jsii_struct_bases=[],
    name_mapping={"time": "time"},
)
class CfnStaticProps:
    def __init__(self, *, time: typing.Optional[builtins.str] = None) -> None:
        '''Creates a static time stamp.

        :param time: Optional parameter to represent the time or default is now.

        :schema: CfnStaticProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37161a422d58fb8525b83e52dc81207942be4b6e5aaaf9944c95b724481b9cb1)
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if time is not None:
            self._values["time"] = time

    @builtins.property
    def time(self) -> typing.Optional[builtins.str]:
        '''Optional parameter to represent the time or default is now.

        :schema: CfnStaticProps#Time
        '''
        result = self._values.get("time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnStaticProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnStatic",
    "CfnStaticProps",
]

publication.publish()

def _typecheckingstub__ca02b500ebe924e37a7d228fa16032c0be39ce424af948e1624b418482d710f5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37161a422d58fb8525b83e52dc81207942be4b6e5aaaf9944c95b724481b9cb1(
    *,
    time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
