'''
# awscommunity-time-offset

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::Time::Offset` v1.6.0.

## Description

Creates a time based resource with an offset from the provided time or now.

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::Time::Offset \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-Time-Offset \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::Time::Offset`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-time-offset+v1.6.0).
* Issues related to `AwsCommunity::Time::Offset` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions.git).

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


class CfnOffset(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-time-offset.CfnOffset",
):
    '''A CloudFormation ``AwsCommunity::Time::Offset``.

    :cloudformationResource: AwsCommunity::Time::Offset
    :link: https://github.com/aws-cloudformation/community-registry-extensions.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        offset_days: typing.Optional[jsii.Number] = None,
        offset_hours: typing.Optional[jsii.Number] = None,
        offset_minutes: typing.Optional[jsii.Number] = None,
        offset_months: typing.Optional[jsii.Number] = None,
        offset_seconds: typing.Optional[jsii.Number] = None,
        offset_years: typing.Optional[jsii.Number] = None,
        time: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::Time::Offset``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param offset_days: Number of days to offset the base timestamp.
        :param offset_hours: Number of hours to offset the base timestamp.
        :param offset_minutes: Number of minutes to offset the base timestamp.
        :param offset_months: Number of months to offset the base timestamp.
        :param offset_seconds: Number of seconds to offset the base timestamp.
        :param offset_years: Number of years to offset the base timestamp.
        :param time: Optional parameter to represent the time or default is now.
        :param triggers: A value to represent when an update to the time should occur.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__740d09f349a1af4757358905717b41eb7228e1058e40bfc34706592cf6edae21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnOffsetProps(
            offset_days=offset_days,
            offset_hours=offset_hours,
            offset_minutes=offset_minutes,
            offset_months=offset_months,
            offset_seconds=offset_seconds,
            offset_years=offset_years,
            time=time,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrDay")
    def attr_day(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Day``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDay"))

    @builtins.property
    @jsii.member(jsii_name="attrHour")
    def attr_hour(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Hour``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrHour"))

    @builtins.property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Id``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property
    @jsii.member(jsii_name="attrMinute")
    def attr_minute(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Minute``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMinute"))

    @builtins.property
    @jsii.member(jsii_name="attrMonth")
    def attr_month(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Month``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMonth"))

    @builtins.property
    @jsii.member(jsii_name="attrSecond")
    def attr_second(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Second``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrSecond"))

    @builtins.property
    @jsii.member(jsii_name="attrUnix")
    def attr_unix(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Unix``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUnix"))

    @builtins.property
    @jsii.member(jsii_name="attrUtc")
    def attr_utc(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Utc``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUtc"))

    @builtins.property
    @jsii.member(jsii_name="attrYear")
    def attr_year(self) -> builtins.str:
        '''Attribute ``AwsCommunity::Time::Offset.Year``.

        :link: https://github.com/aws-cloudformation/community-registry-extensions.git
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrYear"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnOffsetProps":
        '''Resource props.'''
        return typing.cast("CfnOffsetProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-time-offset.CfnOffsetProps",
    jsii_struct_bases=[],
    name_mapping={
        "offset_days": "offsetDays",
        "offset_hours": "offsetHours",
        "offset_minutes": "offsetMinutes",
        "offset_months": "offsetMonths",
        "offset_seconds": "offsetSeconds",
        "offset_years": "offsetYears",
        "time": "time",
        "triggers": "triggers",
    },
)
class CfnOffsetProps:
    def __init__(
        self,
        *,
        offset_days: typing.Optional[jsii.Number] = None,
        offset_hours: typing.Optional[jsii.Number] = None,
        offset_minutes: typing.Optional[jsii.Number] = None,
        offset_months: typing.Optional[jsii.Number] = None,
        offset_seconds: typing.Optional[jsii.Number] = None,
        offset_years: typing.Optional[jsii.Number] = None,
        time: typing.Optional[builtins.str] = None,
        triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Creates a time based resource with an offset from the provided time or now.

        :param offset_days: Number of days to offset the base timestamp.
        :param offset_hours: Number of hours to offset the base timestamp.
        :param offset_minutes: Number of minutes to offset the base timestamp.
        :param offset_months: Number of months to offset the base timestamp.
        :param offset_seconds: Number of seconds to offset the base timestamp.
        :param offset_years: Number of years to offset the base timestamp.
        :param time: Optional parameter to represent the time or default is now.
        :param triggers: A value to represent when an update to the time should occur.

        :schema: CfnOffsetProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb7aab966f8bb80a25cd08e05693f4cc137072de5f6620fce58da6a86ca25ffb)
            check_type(argname="argument offset_days", value=offset_days, expected_type=type_hints["offset_days"])
            check_type(argname="argument offset_hours", value=offset_hours, expected_type=type_hints["offset_hours"])
            check_type(argname="argument offset_minutes", value=offset_minutes, expected_type=type_hints["offset_minutes"])
            check_type(argname="argument offset_months", value=offset_months, expected_type=type_hints["offset_months"])
            check_type(argname="argument offset_seconds", value=offset_seconds, expected_type=type_hints["offset_seconds"])
            check_type(argname="argument offset_years", value=offset_years, expected_type=type_hints["offset_years"])
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if offset_days is not None:
            self._values["offset_days"] = offset_days
        if offset_hours is not None:
            self._values["offset_hours"] = offset_hours
        if offset_minutes is not None:
            self._values["offset_minutes"] = offset_minutes
        if offset_months is not None:
            self._values["offset_months"] = offset_months
        if offset_seconds is not None:
            self._values["offset_seconds"] = offset_seconds
        if offset_years is not None:
            self._values["offset_years"] = offset_years
        if time is not None:
            self._values["time"] = time
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def offset_days(self) -> typing.Optional[jsii.Number]:
        '''Number of days to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetDays
        '''
        result = self._values.get("offset_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_hours(self) -> typing.Optional[jsii.Number]:
        '''Number of hours to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetHours
        '''
        result = self._values.get("offset_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_minutes(self) -> typing.Optional[jsii.Number]:
        '''Number of minutes to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetMinutes
        '''
        result = self._values.get("offset_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_months(self) -> typing.Optional[jsii.Number]:
        '''Number of months to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetMonths
        '''
        result = self._values.get("offset_months")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_seconds(self) -> typing.Optional[jsii.Number]:
        '''Number of seconds to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetSeconds
        '''
        result = self._values.get("offset_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offset_years(self) -> typing.Optional[jsii.Number]:
        '''Number of years to offset the base timestamp.

        :schema: CfnOffsetProps#OffsetYears
        '''
        result = self._values.get("offset_years")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time(self) -> typing.Optional[builtins.str]:
        '''Optional parameter to represent the time or default is now.

        :schema: CfnOffsetProps#Time
        '''
        result = self._values.get("time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A value to represent when an update to the time should occur.

        :schema: CfnOffsetProps#Triggers
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnOffsetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnOffset",
    "CfnOffsetProps",
]

publication.publish()

def _typecheckingstub__740d09f349a1af4757358905717b41eb7228e1058e40bfc34706592cf6edae21(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    offset_days: typing.Optional[jsii.Number] = None,
    offset_hours: typing.Optional[jsii.Number] = None,
    offset_minutes: typing.Optional[jsii.Number] = None,
    offset_months: typing.Optional[jsii.Number] = None,
    offset_seconds: typing.Optional[jsii.Number] = None,
    offset_years: typing.Optional[jsii.Number] = None,
    time: typing.Optional[builtins.str] = None,
    triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb7aab966f8bb80a25cd08e05693f4cc137072de5f6620fce58da6a86ca25ffb(
    *,
    offset_days: typing.Optional[jsii.Number] = None,
    offset_hours: typing.Optional[jsii.Number] = None,
    offset_minutes: typing.Optional[jsii.Number] = None,
    offset_months: typing.Optional[jsii.Number] = None,
    offset_seconds: typing.Optional[jsii.Number] = None,
    offset_years: typing.Optional[jsii.Number] = None,
    time: typing.Optional[builtins.str] = None,
    triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
