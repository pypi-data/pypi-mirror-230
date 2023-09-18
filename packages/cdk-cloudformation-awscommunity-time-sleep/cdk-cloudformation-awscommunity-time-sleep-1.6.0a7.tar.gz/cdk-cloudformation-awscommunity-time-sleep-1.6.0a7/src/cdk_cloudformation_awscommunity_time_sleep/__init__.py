'''
# awscommunity-time-sleep

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::Time::Sleep` v1.6.0.

## Description

Sleep a provided number of seconds between create, update, or delete operations.

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::Time::Sleep \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-Time-Sleep \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::Time::Sleep`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-time-sleep+v1.6.0).
* Issues related to `AwsCommunity::Time::Sleep` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions.git).

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


class CfnSleep(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-time-sleep.CfnSleep",
):
    '''A CloudFormation ``AwsCommunity::Time::Sleep``.

    :cloudformationResource: AwsCommunity::Time::Sleep
    :link: https://github.com/aws-cloudformation/community-registry-extensions.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        seconds: jsii.Number,
        sleep_on_create: typing.Optional[builtins.bool] = None,
        sleep_on_delete: typing.Optional[builtins.bool] = None,
        sleep_on_update: typing.Optional[builtins.bool] = None,
        triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::Time::Sleep``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param seconds: The number of seconds to sleep for.
        :param sleep_on_create: If we should sleep on a create.
        :param sleep_on_delete: If we should sleep on a delete.
        :param sleep_on_update: If we should sleep on an update.
        :param triggers: A value to represent when a sleep should occur. Any time this is updated this resource will sleep.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28d821b4b3a13d3f44a768d736b9a2a5ca16c4ed418e422057fcb3add134340)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnSleepProps(
            seconds=seconds,
            sleep_on_create=sleep_on_create,
            sleep_on_delete=sleep_on_delete,
            sleep_on_update=sleep_on_update,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Sleep.Id``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnSleepProps":
        '''Resource props.'''
        return typing.cast("CfnSleepProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-time-sleep.CfnSleepProps",
    jsii_struct_bases=[],
    name_mapping={
        "seconds": "seconds",
        "sleep_on_create": "sleepOnCreate",
        "sleep_on_delete": "sleepOnDelete",
        "sleep_on_update": "sleepOnUpdate",
        "triggers": "triggers",
    },
)
class CfnSleepProps:
    def __init__(
        self,
        *,
        seconds: jsii.Number,
        sleep_on_create: typing.Optional[builtins.bool] = None,
        sleep_on_delete: typing.Optional[builtins.bool] = None,
        sleep_on_update: typing.Optional[builtins.bool] = None,
        triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Sleep a provided number of seconds between create, update, or delete operations.

        :param seconds: The number of seconds to sleep for.
        :param sleep_on_create: If we should sleep on a create.
        :param sleep_on_delete: If we should sleep on a delete.
        :param sleep_on_update: If we should sleep on an update.
        :param triggers: A value to represent when a sleep should occur. Any time this is updated this resource will sleep.

        :schema: CfnSleepProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4431ab26801c41108382b076db32367885fcb70a428030ee53d17aeae9f2ad4)
            check_type(argname="argument seconds", value=seconds, expected_type=type_hints["seconds"])
            check_type(argname="argument sleep_on_create", value=sleep_on_create, expected_type=type_hints["sleep_on_create"])
            check_type(argname="argument sleep_on_delete", value=sleep_on_delete, expected_type=type_hints["sleep_on_delete"])
            check_type(argname="argument sleep_on_update", value=sleep_on_update, expected_type=type_hints["sleep_on_update"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "seconds": seconds,
        }
        if sleep_on_create is not None:
            self._values["sleep_on_create"] = sleep_on_create
        if sleep_on_delete is not None:
            self._values["sleep_on_delete"] = sleep_on_delete
        if sleep_on_update is not None:
            self._values["sleep_on_update"] = sleep_on_update
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def seconds(self) -> jsii.Number:
        '''The number of seconds to sleep for.

        :schema: CfnSleepProps#Seconds
        '''
        result = self._values.get("seconds")
        assert result is not None, "Required property 'seconds' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def sleep_on_create(self) -> typing.Optional[builtins.bool]:
        '''If we should sleep on a create.

        :schema: CfnSleepProps#SleepOnCreate
        '''
        result = self._values.get("sleep_on_create")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sleep_on_delete(self) -> typing.Optional[builtins.bool]:
        '''If we should sleep on a delete.

        :schema: CfnSleepProps#SleepOnDelete
        '''
        result = self._values.get("sleep_on_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sleep_on_update(self) -> typing.Optional[builtins.bool]:
        '''If we should sleep on an update.

        :schema: CfnSleepProps#SleepOnUpdate
        '''
        result = self._values.get("sleep_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A value to represent when a sleep should occur.

        Any time this is updated this resource will sleep.

        :schema: CfnSleepProps#Triggers
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSleepProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnSleep",
    "CfnSleepProps",
]

publication.publish()

def _typecheckingstub__d28d821b4b3a13d3f44a768d736b9a2a5ca16c4ed418e422057fcb3add134340(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    seconds: jsii.Number,
    sleep_on_create: typing.Optional[builtins.bool] = None,
    sleep_on_delete: typing.Optional[builtins.bool] = None,
    sleep_on_update: typing.Optional[builtins.bool] = None,
    triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4431ab26801c41108382b076db32367885fcb70a428030ee53d17aeae9f2ad4(
    *,
    seconds: jsii.Number,
    sleep_on_create: typing.Optional[builtins.bool] = None,
    sleep_on_delete: typing.Optional[builtins.bool] = None,
    sleep_on_update: typing.Optional[builtins.bool] = None,
    triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
