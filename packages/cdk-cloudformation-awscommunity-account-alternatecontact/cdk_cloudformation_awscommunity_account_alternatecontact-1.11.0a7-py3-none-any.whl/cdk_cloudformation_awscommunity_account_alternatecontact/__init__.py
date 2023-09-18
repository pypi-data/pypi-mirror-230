'''
# awscommunity-account-alternatecontact

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::Account::AlternateContact` v1.11.0.

## Description

An alternate contact attached to an Amazon Web Services account.

## References

* [Source](https://github.com/aws-cloudformation/community-registry-extensions.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::Account::AlternateContact \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-Account-AlternateContact \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::Account::AlternateContact`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-account-alternatecontact+v1.11.0).
* Issues related to `AwsCommunity::Account::AlternateContact` should be reported to the [publisher](https://github.com/aws-cloudformation/community-registry-extensions.git).

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


class CfnAlternateContact(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-account-alternatecontact.CfnAlternateContact",
):
    '''A CloudFormation ``AwsCommunity::Account::AlternateContact``.

    :cloudformationResource: AwsCommunity::Account::AlternateContact
    :link: https://github.com/aws-cloudformation/community-registry-extensions.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        alternate_contact_type: "CfnAlternateContactPropsAlternateContactType",
        email_address: builtins.str,
        name: builtins.str,
        phone_number: builtins.str,
        title: builtins.str,
    ) -> None:
        '''Create a new ``AwsCommunity::Account::AlternateContact``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param account_id: The account ID of the AWS account that you want to add an alternate contact to.
        :param alternate_contact_type: The type of alternate contact you want to create.
        :param email_address: The email address for the alternate contact.
        :param name: The name for the alternate contact.
        :param phone_number: The phone number for the alternate contact.
        :param title: The title for the alternate contact.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b462972a4eb175865d2058a85c569cebb75e38c852f63df539eeedc2370588e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAlternateContactProps(
            account_id=account_id,
            alternate_contact_type=alternate_contact_type,
            email_address=email_address,
            name=name,
            phone_number=phone_number,
            title=title,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnAlternateContactProps":
        '''Resource props.'''
        return typing.cast("CfnAlternateContactProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-account-alternatecontact.CfnAlternateContactProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "alternate_contact_type": "alternateContactType",
        "email_address": "emailAddress",
        "name": "name",
        "phone_number": "phoneNumber",
        "title": "title",
    },
)
class CfnAlternateContactProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        alternate_contact_type: "CfnAlternateContactPropsAlternateContactType",
        email_address: builtins.str,
        name: builtins.str,
        phone_number: builtins.str,
        title: builtins.str,
    ) -> None:
        '''An alternate contact attached to an Amazon Web Services account.

        :param account_id: The account ID of the AWS account that you want to add an alternate contact to.
        :param alternate_contact_type: The type of alternate contact you want to create.
        :param email_address: The email address for the alternate contact.
        :param name: The name for the alternate contact.
        :param phone_number: The phone number for the alternate contact.
        :param title: The title for the alternate contact.

        :schema: CfnAlternateContactProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4caf54befdccfbf9b3a9ff4706ae23330cfedc638560e2b39685c2a39a9e457)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument alternate_contact_type", value=alternate_contact_type, expected_type=type_hints["alternate_contact_type"])
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "alternate_contact_type": alternate_contact_type,
            "email_address": email_address,
            "name": name,
            "phone_number": phone_number,
            "title": title,
        }

    @builtins.property
    def account_id(self) -> builtins.str:
        '''The account ID of the AWS account that you want to add an alternate contact to.

        :schema: CfnAlternateContactProps#AccountId
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alternate_contact_type(self) -> "CfnAlternateContactPropsAlternateContactType":
        '''The type of alternate contact you want to create.

        :schema: CfnAlternateContactProps#AlternateContactType
        '''
        result = self._values.get("alternate_contact_type")
        assert result is not None, "Required property 'alternate_contact_type' is missing"
        return typing.cast("CfnAlternateContactPropsAlternateContactType", result)

    @builtins.property
    def email_address(self) -> builtins.str:
        '''The email address for the alternate contact.

        :schema: CfnAlternateContactProps#EmailAddress
        '''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the alternate contact.

        :schema: CfnAlternateContactProps#Name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def phone_number(self) -> builtins.str:
        '''The phone number for the alternate contact.

        :schema: CfnAlternateContactProps#PhoneNumber
        '''
        result = self._values.get("phone_number")
        assert result is not None, "Required property 'phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''The title for the alternate contact.

        :schema: CfnAlternateContactProps#Title
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAlternateContactProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdk-cloudformation/awscommunity-account-alternatecontact.CfnAlternateContactPropsAlternateContactType"
)
class CfnAlternateContactPropsAlternateContactType(enum.Enum):
    '''The type of alternate contact you want to create.

    :schema: CfnAlternateContactPropsAlternateContactType
    '''

    BILLING = "BILLING"
    '''BILLING.'''
    OPERATIONS = "OPERATIONS"
    '''OPERATIONS.'''
    SECURITY = "SECURITY"
    '''SECURITY.'''


__all__ = [
    "CfnAlternateContact",
    "CfnAlternateContactProps",
    "CfnAlternateContactPropsAlternateContactType",
]

publication.publish()

def _typecheckingstub__4b462972a4eb175865d2058a85c569cebb75e38c852f63df539eeedc2370588e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    alternate_contact_type: CfnAlternateContactPropsAlternateContactType,
    email_address: builtins.str,
    name: builtins.str,
    phone_number: builtins.str,
    title: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4caf54befdccfbf9b3a9ff4706ae23330cfedc638560e2b39685c2a39a9e457(
    *,
    account_id: builtins.str,
    alternate_contact_type: CfnAlternateContactPropsAlternateContactType,
    email_address: builtins.str,
    name: builtins.str,
    phone_number: builtins.str,
    title: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
