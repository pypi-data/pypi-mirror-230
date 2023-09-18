'''
# awscommunity-applicationautoscaling-scheduledaction

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::ApplicationAutoscaling::ScheduledAction` v1.6.0.

## Description

Application Autoscaling Scheduled Action.

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::ApplicationAutoscaling::ScheduledAction \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-ApplicationAutoscaling-ScheduledAction \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::ApplicationAutoscaling::ScheduledAction`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-applicationautoscaling-scheduledaction+v1.6.0).
* Issues related to `AwsCommunity::ApplicationAutoscaling::ScheduledAction` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions).

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


class CfnScheduledAction(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-applicationautoscaling-scheduledaction.CfnScheduledAction",
):
    '''A CloudFormation ``AwsCommunity::ApplicationAutoscaling::ScheduledAction``.

    :cloudformationResource: AwsCommunity::ApplicationAutoscaling::ScheduledAction
    :link: https://github.com/aws-cloudformation/community-registry-extensions
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        resource_id: builtins.str,
        scalable_dimension: builtins.str,
        scalable_target_action: typing.Union["CfnScheduledActionPropsScalableTargetAction", typing.Dict[builtins.str, typing.Any]],
        schedule: builtins.str,
        scheduled_action_name: builtins.str,
        service_namespace: builtins.str,
        end_time: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::ApplicationAutoscaling::ScheduledAction``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resource_id: 
        :param scalable_dimension: 
        :param scalable_target_action: 
        :param schedule: 
        :param scheduled_action_name: 
        :param service_namespace: 
        :param end_time: 
        :param start_time: 
        :param timezone: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e8c65d6aaa20489b846d1b329bd3ba98e9733f7f26d698b7f2f31516fe8a1e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnScheduledActionProps(
            resource_id=resource_id,
            scalable_dimension=scalable_dimension,
            scalable_target_action=scalable_target_action,
            schedule=schedule,
            scheduled_action_name=scheduled_action_name,
            service_namespace=service_namespace,
            end_time=end_time,
            start_time=start_time,
            timezone=timezone,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrScheduledActionARN")
    def attr_scheduled_action_arn(self) -> builtins.str:
        '''Attribute ``AwsCommunity::ApplicationAutoscaling::ScheduledAction.ScheduledActionARN``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrScheduledActionARN"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnScheduledActionProps":
        '''Resource props.'''
        return typing.cast("CfnScheduledActionProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-applicationautoscaling-scheduledaction.CfnScheduledActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource_id": "resourceId",
        "scalable_dimension": "scalableDimension",
        "scalable_target_action": "scalableTargetAction",
        "schedule": "schedule",
        "scheduled_action_name": "scheduledActionName",
        "service_namespace": "serviceNamespace",
        "end_time": "endTime",
        "start_time": "startTime",
        "timezone": "timezone",
    },
)
class CfnScheduledActionProps:
    def __init__(
        self,
        *,
        resource_id: builtins.str,
        scalable_dimension: builtins.str,
        scalable_target_action: typing.Union["CfnScheduledActionPropsScalableTargetAction", typing.Dict[builtins.str, typing.Any]],
        schedule: builtins.str,
        scheduled_action_name: builtins.str,
        service_namespace: builtins.str,
        end_time: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Application Autoscaling Scheduled Action.

        :param resource_id: 
        :param scalable_dimension: 
        :param scalable_target_action: 
        :param schedule: 
        :param scheduled_action_name: 
        :param service_namespace: 
        :param end_time: 
        :param start_time: 
        :param timezone: 

        :schema: CfnScheduledActionProps
        '''
        if isinstance(scalable_target_action, dict):
            scalable_target_action = CfnScheduledActionPropsScalableTargetAction(**scalable_target_action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1d99d03d526ffbbce22836d8adb5c0c9700302c8bd91ccf2fdc93a1b7d2d3a)
            check_type(argname="argument resource_id", value=resource_id, expected_type=type_hints["resource_id"])
            check_type(argname="argument scalable_dimension", value=scalable_dimension, expected_type=type_hints["scalable_dimension"])
            check_type(argname="argument scalable_target_action", value=scalable_target_action, expected_type=type_hints["scalable_target_action"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument scheduled_action_name", value=scheduled_action_name, expected_type=type_hints["scheduled_action_name"])
            check_type(argname="argument service_namespace", value=service_namespace, expected_type=type_hints["service_namespace"])
            check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource_id": resource_id,
            "scalable_dimension": scalable_dimension,
            "scalable_target_action": scalable_target_action,
            "schedule": schedule,
            "scheduled_action_name": scheduled_action_name,
            "service_namespace": service_namespace,
        }
        if end_time is not None:
            self._values["end_time"] = end_time
        if start_time is not None:
            self._values["start_time"] = start_time
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''
        :schema: CfnScheduledActionProps#ResourceId
        '''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scalable_dimension(self) -> builtins.str:
        '''
        :schema: CfnScheduledActionProps#ScalableDimension
        '''
        result = self._values.get("scalable_dimension")
        assert result is not None, "Required property 'scalable_dimension' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scalable_target_action(self) -> "CfnScheduledActionPropsScalableTargetAction":
        '''
        :schema: CfnScheduledActionProps#ScalableTargetAction
        '''
        result = self._values.get("scalable_target_action")
        assert result is not None, "Required property 'scalable_target_action' is missing"
        return typing.cast("CfnScheduledActionPropsScalableTargetAction", result)

    @builtins.property
    def schedule(self) -> builtins.str:
        '''
        :schema: CfnScheduledActionProps#Schedule
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheduled_action_name(self) -> builtins.str:
        '''
        :schema: CfnScheduledActionProps#ScheduledActionName
        '''
        result = self._values.get("scheduled_action_name")
        assert result is not None, "Required property 'scheduled_action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_namespace(self) -> builtins.str:
        '''
        :schema: CfnScheduledActionProps#ServiceNamespace
        '''
        result = self._values.get("service_namespace")
        assert result is not None, "Required property 'service_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def end_time(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnScheduledActionProps#EndTime
        '''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnScheduledActionProps#StartTime
        '''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnScheduledActionProps#Timezone
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnScheduledActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-applicationautoscaling-scheduledaction.CfnScheduledActionPropsScalableTargetAction",
    jsii_struct_bases=[],
    name_mapping={"max_capacity": "maxCapacity", "min_capacity": "minCapacity"},
)
class CfnScheduledActionPropsScalableTargetAction:
    def __init__(
        self,
        *,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_capacity: 
        :param min_capacity: 

        :schema: CfnScheduledActionPropsScalableTargetAction
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d907a2c0218923256a1a9f7282c2cec1d8cf7d75080bf06605d0f521949cb8ce)
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :schema: CfnScheduledActionPropsScalableTargetAction#MaxCapacity
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :schema: CfnScheduledActionPropsScalableTargetAction#MinCapacity
        '''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnScheduledActionPropsScalableTargetAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnScheduledAction",
    "CfnScheduledActionProps",
    "CfnScheduledActionPropsScalableTargetAction",
]

publication.publish()

def _typecheckingstub__b8e8c65d6aaa20489b846d1b329bd3ba98e9733f7f26d698b7f2f31516fe8a1e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    resource_id: builtins.str,
    scalable_dimension: builtins.str,
    scalable_target_action: typing.Union[CfnScheduledActionPropsScalableTargetAction, typing.Dict[builtins.str, typing.Any]],
    schedule: builtins.str,
    scheduled_action_name: builtins.str,
    service_namespace: builtins.str,
    end_time: typing.Optional[builtins.str] = None,
    start_time: typing.Optional[builtins.str] = None,
    timezone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1d99d03d526ffbbce22836d8adb5c0c9700302c8bd91ccf2fdc93a1b7d2d3a(
    *,
    resource_id: builtins.str,
    scalable_dimension: builtins.str,
    scalable_target_action: typing.Union[CfnScheduledActionPropsScalableTargetAction, typing.Dict[builtins.str, typing.Any]],
    schedule: builtins.str,
    scheduled_action_name: builtins.str,
    service_namespace: builtins.str,
    end_time: typing.Optional[builtins.str] = None,
    start_time: typing.Optional[builtins.str] = None,
    timezone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d907a2c0218923256a1a9f7282c2cec1d8cf7d75080bf06605d0f521949cb8ce(
    *,
    max_capacity: typing.Optional[jsii.Number] = None,
    min_capacity: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
