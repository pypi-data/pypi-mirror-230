'''
# `google_identity_platform_config`

Refer to the Terraform Registory for docs: [`google_identity_platform_config`](https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class IdentityPlatformConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config google_identity_platform_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        authorized_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        autodelete_anonymous_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        blocking_functions: typing.Optional[typing.Union["IdentityPlatformConfigBlockingFunctions", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        quota: typing.Optional[typing.Union["IdentityPlatformConfigQuota", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["IdentityPlatformConfigTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config google_identity_platform_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authorized_domains: List of domains authorized for OAuth redirects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#authorized_domains IdentityPlatformConfig#authorized_domains}
        :param autodelete_anonymous_users: Whether anonymous users will be auto-deleted after a period of 30 days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#autodelete_anonymous_users IdentityPlatformConfig#autodelete_anonymous_users}
        :param blocking_functions: blocking_functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#blocking_functions IdentityPlatformConfig#blocking_functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id IdentityPlatformConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#project IdentityPlatformConfig#project}.
        :param quota: quota block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#timeouts IdentityPlatformConfig#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b7f2b7c995d2e86a749a49b40eff4be838e002c489fa2b5d03a6f21b4b0f3d2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = IdentityPlatformConfigConfig(
            authorized_domains=authorized_domains,
            autodelete_anonymous_users=autodelete_anonymous_users,
            blocking_functions=blocking_functions,
            id=id,
            project=project,
            quota=quota,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putBlockingFunctions")
    def put_blocking_functions(
        self,
        *,
        triggers: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["IdentityPlatformConfigBlockingFunctionsTriggers", typing.Dict[builtins.str, typing.Any]]]],
        forward_inbound_credentials: typing.Optional[typing.Union["IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param triggers: triggers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#triggers IdentityPlatformConfig#triggers}
        :param forward_inbound_credentials: forward_inbound_credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#forward_inbound_credentials IdentityPlatformConfig#forward_inbound_credentials}
        '''
        value = IdentityPlatformConfigBlockingFunctions(
            triggers=triggers, forward_inbound_credentials=forward_inbound_credentials
        )

        return typing.cast(None, jsii.invoke(self, "putBlockingFunctions", [value]))

    @jsii.member(jsii_name="putQuota")
    def put_quota(
        self,
        *,
        sign_up_quota_config: typing.Optional[typing.Union["IdentityPlatformConfigQuotaSignUpQuotaConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sign_up_quota_config: sign_up_quota_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#sign_up_quota_config IdentityPlatformConfig#sign_up_quota_config}
        '''
        value = IdentityPlatformConfigQuota(sign_up_quota_config=sign_up_quota_config)

        return typing.cast(None, jsii.invoke(self, "putQuota", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#create IdentityPlatformConfig#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#delete IdentityPlatformConfig#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#update IdentityPlatformConfig#update}.
        '''
        value = IdentityPlatformConfigTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAuthorizedDomains")
    def reset_authorized_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizedDomains", []))

    @jsii.member(jsii_name="resetAutodeleteAnonymousUsers")
    def reset_autodelete_anonymous_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodeleteAnonymousUsers", []))

    @jsii.member(jsii_name="resetBlockingFunctions")
    def reset_blocking_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockingFunctions", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetQuota")
    def reset_quota(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuota", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="blockingFunctions")
    def blocking_functions(
        self,
    ) -> "IdentityPlatformConfigBlockingFunctionsOutputReference":
        return typing.cast("IdentityPlatformConfigBlockingFunctionsOutputReference", jsii.get(self, "blockingFunctions"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="quota")
    def quota(self) -> "IdentityPlatformConfigQuotaOutputReference":
        return typing.cast("IdentityPlatformConfigQuotaOutputReference", jsii.get(self, "quota"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "IdentityPlatformConfigTimeoutsOutputReference":
        return typing.cast("IdentityPlatformConfigTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="authorizedDomainsInput")
    def authorized_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authorizedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="autodeleteAnonymousUsersInput")
    def autodelete_anonymous_users_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autodeleteAnonymousUsersInput"))

    @builtins.property
    @jsii.member(jsii_name="blockingFunctionsInput")
    def blocking_functions_input(
        self,
    ) -> typing.Optional["IdentityPlatformConfigBlockingFunctions"]:
        return typing.cast(typing.Optional["IdentityPlatformConfigBlockingFunctions"], jsii.get(self, "blockingFunctionsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="quotaInput")
    def quota_input(self) -> typing.Optional["IdentityPlatformConfigQuota"]:
        return typing.cast(typing.Optional["IdentityPlatformConfigQuota"], jsii.get(self, "quotaInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "IdentityPlatformConfigTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "IdentityPlatformConfigTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizedDomains")
    def authorized_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authorizedDomains"))

    @authorized_domains.setter
    def authorized_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0bcfcfa2aa6771c72db35b61d07f1f2bcdf55a135ca1d5984ff7dc91881a847)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizedDomains", value)

    @builtins.property
    @jsii.member(jsii_name="autodeleteAnonymousUsers")
    def autodelete_anonymous_users(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autodeleteAnonymousUsers"))

    @autodelete_anonymous_users.setter
    def autodelete_anonymous_users(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e1fe055b084c476abfe2731a785123530145316a42c88a08616f83ef8c037d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodeleteAnonymousUsers", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c60e8e56702b4a670d0c1815c986277ce85e98e5ba4a2ac2b75ad3371f61dc82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b600b9041b4160ef06fb37cb6f9658c98d2d1f99efddaa2e2792398e5316a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctions",
    jsii_struct_bases=[],
    name_mapping={
        "triggers": "triggers",
        "forward_inbound_credentials": "forwardInboundCredentials",
    },
)
class IdentityPlatformConfigBlockingFunctions:
    def __init__(
        self,
        *,
        triggers: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["IdentityPlatformConfigBlockingFunctionsTriggers", typing.Dict[builtins.str, typing.Any]]]],
        forward_inbound_credentials: typing.Optional[typing.Union["IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param triggers: triggers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#triggers IdentityPlatformConfig#triggers}
        :param forward_inbound_credentials: forward_inbound_credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#forward_inbound_credentials IdentityPlatformConfig#forward_inbound_credentials}
        '''
        if isinstance(forward_inbound_credentials, dict):
            forward_inbound_credentials = IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials(**forward_inbound_credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a0a74f2bcd2cef65ec44ecdeaddd5d3d50329738bb8692d23cde163e46514be)
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
            check_type(argname="argument forward_inbound_credentials", value=forward_inbound_credentials, expected_type=type_hints["forward_inbound_credentials"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "triggers": triggers,
        }
        if forward_inbound_credentials is not None:
            self._values["forward_inbound_credentials"] = forward_inbound_credentials

    @builtins.property
    def triggers(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["IdentityPlatformConfigBlockingFunctionsTriggers"]]:
        '''triggers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#triggers IdentityPlatformConfig#triggers}
        '''
        result = self._values.get("triggers")
        assert result is not None, "Required property 'triggers' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["IdentityPlatformConfigBlockingFunctionsTriggers"]], result)

    @builtins.property
    def forward_inbound_credentials(
        self,
    ) -> typing.Optional["IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials"]:
        '''forward_inbound_credentials block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#forward_inbound_credentials IdentityPlatformConfig#forward_inbound_credentials}
        '''
        result = self._values.get("forward_inbound_credentials")
        return typing.cast(typing.Optional["IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigBlockingFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "id_token": "idToken",
        "refresh_token": "refreshToken",
    },
)
class IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials:
    def __init__(
        self,
        *,
        access_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        refresh_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param access_token: Whether to pass the user's OAuth identity provider's access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#access_token IdentityPlatformConfig#access_token}
        :param id_token: Whether to pass the user's OIDC identity provider's ID token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id_token IdentityPlatformConfig#id_token}
        :param refresh_token: Whether to pass the user's OAuth identity provider's refresh token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#refresh_token IdentityPlatformConfig#refresh_token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9299d36033b7cab22b1eb5b1ea868b34e0a61dd18a7387b411068dc99a06daee)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument id_token", value=id_token, expected_type=type_hints["id_token"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if id_token is not None:
            self._values["id_token"] = id_token
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def access_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to pass the user's OAuth identity provider's access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#access_token IdentityPlatformConfig#access_token}
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to pass the user's OIDC identity provider's ID token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id_token IdentityPlatformConfig#id_token}
        '''
        result = self._values.get("id_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def refresh_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to pass the user's OAuth identity provider's refresh token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#refresh_token IdentityPlatformConfig#refresh_token}
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IdentityPlatformConfigBlockingFunctionsForwardInboundCredentialsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsForwardInboundCredentialsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb120ef282e4ef4761e46fa26ed3b34fa4a0dea209047f8e6f394cf7f5c1af9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAccessToken")
    def reset_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessToken", []))

    @jsii.member(jsii_name="resetIdToken")
    def reset_id_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdToken", []))

    @jsii.member(jsii_name="resetRefreshToken")
    def reset_refresh_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshToken", []))

    @builtins.property
    @jsii.member(jsii_name="accessTokenInput")
    def access_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "accessTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="idTokenInput")
    def id_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "idTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="refreshTokenInput")
    def refresh_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "refreshTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4d45a34dcce05007140f4104db688559a7b673d7e9fe267485abbeab0e0138d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessToken", value)

    @builtins.property
    @jsii.member(jsii_name="idToken")
    def id_token(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "idToken"))

    @id_token.setter
    def id_token(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ea1ef788e52f56ba082f54d9301f32a1e2c536b82621d134edcfb2779a611ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idToken", value)

    @builtins.property
    @jsii.member(jsii_name="refreshToken")
    def refresh_token(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "refreshToken"))

    @refresh_token.setter
    def refresh_token(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d8dd87fd0f9a14e3dfef6328ab902944c202bda55eda996c2f147db186f3fa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "refreshToken", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials]:
        return typing.cast(typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__801a34f3130b73de4952dd443abd60f0263bc19c31aca8aef4994cb875cdccd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class IdentityPlatformConfigBlockingFunctionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea82a39a24000471d15325cd2e8712a89128c55197d350e97a8c2304cdcc2dd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putForwardInboundCredentials")
    def put_forward_inbound_credentials(
        self,
        *,
        access_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        refresh_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param access_token: Whether to pass the user's OAuth identity provider's access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#access_token IdentityPlatformConfig#access_token}
        :param id_token: Whether to pass the user's OIDC identity provider's ID token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id_token IdentityPlatformConfig#id_token}
        :param refresh_token: Whether to pass the user's OAuth identity provider's refresh token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#refresh_token IdentityPlatformConfig#refresh_token}
        '''
        value = IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials(
            access_token=access_token, id_token=id_token, refresh_token=refresh_token
        )

        return typing.cast(None, jsii.invoke(self, "putForwardInboundCredentials", [value]))

    @jsii.member(jsii_name="putTriggers")
    def put_triggers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["IdentityPlatformConfigBlockingFunctionsTriggers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d9380d84963a6160ff4f6de220325ac47687c165ac2d5e0076d6ca820a38030)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTriggers", [value]))

    @jsii.member(jsii_name="resetForwardInboundCredentials")
    def reset_forward_inbound_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForwardInboundCredentials", []))

    @builtins.property
    @jsii.member(jsii_name="forwardInboundCredentials")
    def forward_inbound_credentials(
        self,
    ) -> IdentityPlatformConfigBlockingFunctionsForwardInboundCredentialsOutputReference:
        return typing.cast(IdentityPlatformConfigBlockingFunctionsForwardInboundCredentialsOutputReference, jsii.get(self, "forwardInboundCredentials"))

    @builtins.property
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> "IdentityPlatformConfigBlockingFunctionsTriggersList":
        return typing.cast("IdentityPlatformConfigBlockingFunctionsTriggersList", jsii.get(self, "triggers"))

    @builtins.property
    @jsii.member(jsii_name="forwardInboundCredentialsInput")
    def forward_inbound_credentials_input(
        self,
    ) -> typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials]:
        return typing.cast(typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials], jsii.get(self, "forwardInboundCredentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["IdentityPlatformConfigBlockingFunctionsTriggers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["IdentityPlatformConfigBlockingFunctionsTriggers"]]], jsii.get(self, "triggersInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IdentityPlatformConfigBlockingFunctions]:
        return typing.cast(typing.Optional[IdentityPlatformConfigBlockingFunctions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IdentityPlatformConfigBlockingFunctions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d31a0ff7331f03093b5e70d40d6e2f746b70f98b898e17c281037a142d74d5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsTriggers",
    jsii_struct_bases=[],
    name_mapping={"event_type": "eventType", "function_uri": "functionUri"},
)
class IdentityPlatformConfigBlockingFunctionsTriggers:
    def __init__(self, *, event_type: builtins.str, function_uri: builtins.str) -> None:
        '''
        :param event_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#event_type IdentityPlatformConfig#event_type}.
        :param function_uri: HTTP URI trigger for the Cloud Function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#function_uri IdentityPlatformConfig#function_uri}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dda06e59673111e6ff97766bcbbb60c44530c9bdbe44883df471b01642686fe)
            check_type(argname="argument event_type", value=event_type, expected_type=type_hints["event_type"])
            check_type(argname="argument function_uri", value=function_uri, expected_type=type_hints["function_uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_type": event_type,
            "function_uri": function_uri,
        }

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#event_type IdentityPlatformConfig#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_uri(self) -> builtins.str:
        '''HTTP URI trigger for the Cloud Function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#function_uri IdentityPlatformConfig#function_uri}
        '''
        result = self._values.get("function_uri")
        assert result is not None, "Required property 'function_uri' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigBlockingFunctionsTriggers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IdentityPlatformConfigBlockingFunctionsTriggersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsTriggersList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b370ff145206ba3f43e5479c3ef886d93f3ed0c3d992cea5606538fc6e3ad16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "IdentityPlatformConfigBlockingFunctionsTriggersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06075886b5824d0e6be33539477807d564814122d3e7de25ce71e5727c81e9b1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("IdentityPlatformConfigBlockingFunctionsTriggersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03a6a35e0fccb80adc749f73c60302364ac5ba5f0cbc535fce422d0c72825a00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afdb0fc2e816dab687175b61e8c397055ad106f7239bf547d95659c32e2bd1a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acd7a8789a157b7780a179fb5abf86c208a43a5793c6cf63e1ae3d9235697f5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[IdentityPlatformConfigBlockingFunctionsTriggers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[IdentityPlatformConfigBlockingFunctionsTriggers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[IdentityPlatformConfigBlockingFunctionsTriggers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47b410bef3af3be6cbe495c603f778bd3d8caa8f12b075ab681c531ead286c16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class IdentityPlatformConfigBlockingFunctionsTriggersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigBlockingFunctionsTriggersOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e101d9fcecc8a59be8ab9cbfbe0d8b078cc9cd4b34d8de4aa4a2bbf85d02a90e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="eventTypeInput")
    def event_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="functionUriInput")
    def function_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionUriInput"))

    @builtins.property
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventType"))

    @event_type.setter
    def event_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ff3b68957025c5a90190abd87d1e3f1450b579e442d8aef236959bfba0c884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventType", value)

    @builtins.property
    @jsii.member(jsii_name="functionUri")
    def function_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionUri"))

    @function_uri.setter
    def function_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8fa1cac36c3e1e25219739be8ec3d13492532cc8a119c8470abc657c5ad2484)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionUri", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigBlockingFunctionsTriggers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigBlockingFunctionsTriggers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigBlockingFunctionsTriggers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b765c08c8b4fd0a5ca9e01e3b24caca80cab021de1c4242508437f1280a3e8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "authorized_domains": "authorizedDomains",
        "autodelete_anonymous_users": "autodeleteAnonymousUsers",
        "blocking_functions": "blockingFunctions",
        "id": "id",
        "project": "project",
        "quota": "quota",
        "timeouts": "timeouts",
    },
)
class IdentityPlatformConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        authorized_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        autodelete_anonymous_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        blocking_functions: typing.Optional[typing.Union[IdentityPlatformConfigBlockingFunctions, typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        quota: typing.Optional[typing.Union["IdentityPlatformConfigQuota", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["IdentityPlatformConfigTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param authorized_domains: List of domains authorized for OAuth redirects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#authorized_domains IdentityPlatformConfig#authorized_domains}
        :param autodelete_anonymous_users: Whether anonymous users will be auto-deleted after a period of 30 days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#autodelete_anonymous_users IdentityPlatformConfig#autodelete_anonymous_users}
        :param blocking_functions: blocking_functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#blocking_functions IdentityPlatformConfig#blocking_functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id IdentityPlatformConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#project IdentityPlatformConfig#project}.
        :param quota: quota block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#timeouts IdentityPlatformConfig#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(blocking_functions, dict):
            blocking_functions = IdentityPlatformConfigBlockingFunctions(**blocking_functions)
        if isinstance(quota, dict):
            quota = IdentityPlatformConfigQuota(**quota)
        if isinstance(timeouts, dict):
            timeouts = IdentityPlatformConfigTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c65289ba252bfde714602bec691f328768fa5b77566d85c699f713af705d9d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument authorized_domains", value=authorized_domains, expected_type=type_hints["authorized_domains"])
            check_type(argname="argument autodelete_anonymous_users", value=autodelete_anonymous_users, expected_type=type_hints["autodelete_anonymous_users"])
            check_type(argname="argument blocking_functions", value=blocking_functions, expected_type=type_hints["blocking_functions"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument quota", value=quota, expected_type=type_hints["quota"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if authorized_domains is not None:
            self._values["authorized_domains"] = authorized_domains
        if autodelete_anonymous_users is not None:
            self._values["autodelete_anonymous_users"] = autodelete_anonymous_users
        if blocking_functions is not None:
            self._values["blocking_functions"] = blocking_functions
        if id is not None:
            self._values["id"] = id
        if project is not None:
            self._values["project"] = project
        if quota is not None:
            self._values["quota"] = quota
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def authorized_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains authorized for OAuth redirects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#authorized_domains IdentityPlatformConfig#authorized_domains}
        '''
        result = self._values.get("authorized_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def autodelete_anonymous_users(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether anonymous users will be auto-deleted after a period of 30 days.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#autodelete_anonymous_users IdentityPlatformConfig#autodelete_anonymous_users}
        '''
        result = self._values.get("autodelete_anonymous_users")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def blocking_functions(
        self,
    ) -> typing.Optional[IdentityPlatformConfigBlockingFunctions]:
        '''blocking_functions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#blocking_functions IdentityPlatformConfig#blocking_functions}
        '''
        result = self._values.get("blocking_functions")
        return typing.cast(typing.Optional[IdentityPlatformConfigBlockingFunctions], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#id IdentityPlatformConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#project IdentityPlatformConfig#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quota(self) -> typing.Optional["IdentityPlatformConfigQuota"]:
        '''quota block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        '''
        result = self._values.get("quota")
        return typing.cast(typing.Optional["IdentityPlatformConfigQuota"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["IdentityPlatformConfigTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#timeouts IdentityPlatformConfig#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["IdentityPlatformConfigTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigQuota",
    jsii_struct_bases=[],
    name_mapping={"sign_up_quota_config": "signUpQuotaConfig"},
)
class IdentityPlatformConfigQuota:
    def __init__(
        self,
        *,
        sign_up_quota_config: typing.Optional[typing.Union["IdentityPlatformConfigQuotaSignUpQuotaConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sign_up_quota_config: sign_up_quota_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#sign_up_quota_config IdentityPlatformConfig#sign_up_quota_config}
        '''
        if isinstance(sign_up_quota_config, dict):
            sign_up_quota_config = IdentityPlatformConfigQuotaSignUpQuotaConfig(**sign_up_quota_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14681c9040323dc00c921c27e398e58b2aaa995e317b557292476ca2e1a2fbcd)
            check_type(argname="argument sign_up_quota_config", value=sign_up_quota_config, expected_type=type_hints["sign_up_quota_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sign_up_quota_config is not None:
            self._values["sign_up_quota_config"] = sign_up_quota_config

    @builtins.property
    def sign_up_quota_config(
        self,
    ) -> typing.Optional["IdentityPlatformConfigQuotaSignUpQuotaConfig"]:
        '''sign_up_quota_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#sign_up_quota_config IdentityPlatformConfig#sign_up_quota_config}
        '''
        result = self._values.get("sign_up_quota_config")
        return typing.cast(typing.Optional["IdentityPlatformConfigQuotaSignUpQuotaConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigQuota(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IdentityPlatformConfigQuotaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigQuotaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c988653d5f5aef939a53453c7695ae0ecebd01ac01772c2440fb453d0a026c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSignUpQuotaConfig")
    def put_sign_up_quota_config(
        self,
        *,
        quota: typing.Optional[jsii.Number] = None,
        quota_duration: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quota: A sign up APIs quota that customers can override temporarily. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        :param quota_duration: How long this quota will be active for. It is measurred in seconds, e.g., Example: "9.615s". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota_duration IdentityPlatformConfig#quota_duration}
        :param start_time: When this quota will take affect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#start_time IdentityPlatformConfig#start_time}
        '''
        value = IdentityPlatformConfigQuotaSignUpQuotaConfig(
            quota=quota, quota_duration=quota_duration, start_time=start_time
        )

        return typing.cast(None, jsii.invoke(self, "putSignUpQuotaConfig", [value]))

    @jsii.member(jsii_name="resetSignUpQuotaConfig")
    def reset_sign_up_quota_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignUpQuotaConfig", []))

    @builtins.property
    @jsii.member(jsii_name="signUpQuotaConfig")
    def sign_up_quota_config(
        self,
    ) -> "IdentityPlatformConfigQuotaSignUpQuotaConfigOutputReference":
        return typing.cast("IdentityPlatformConfigQuotaSignUpQuotaConfigOutputReference", jsii.get(self, "signUpQuotaConfig"))

    @builtins.property
    @jsii.member(jsii_name="signUpQuotaConfigInput")
    def sign_up_quota_config_input(
        self,
    ) -> typing.Optional["IdentityPlatformConfigQuotaSignUpQuotaConfig"]:
        return typing.cast(typing.Optional["IdentityPlatformConfigQuotaSignUpQuotaConfig"], jsii.get(self, "signUpQuotaConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IdentityPlatformConfigQuota]:
        return typing.cast(typing.Optional[IdentityPlatformConfigQuota], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IdentityPlatformConfigQuota],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fb70ddbe257226b371147fb8f04608702ac4f59c616551f02a10e3398a9ddc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigQuotaSignUpQuotaConfig",
    jsii_struct_bases=[],
    name_mapping={
        "quota": "quota",
        "quota_duration": "quotaDuration",
        "start_time": "startTime",
    },
)
class IdentityPlatformConfigQuotaSignUpQuotaConfig:
    def __init__(
        self,
        *,
        quota: typing.Optional[jsii.Number] = None,
        quota_duration: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quota: A sign up APIs quota that customers can override temporarily. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        :param quota_duration: How long this quota will be active for. It is measurred in seconds, e.g., Example: "9.615s". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota_duration IdentityPlatformConfig#quota_duration}
        :param start_time: When this quota will take affect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#start_time IdentityPlatformConfig#start_time}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba7991cae0a5aa0ceb55da5669d10701a19bdfc8e435ac6506aab264b9fd2f4c)
            check_type(argname="argument quota", value=quota, expected_type=type_hints["quota"])
            check_type(argname="argument quota_duration", value=quota_duration, expected_type=type_hints["quota_duration"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if quota is not None:
            self._values["quota"] = quota
        if quota_duration is not None:
            self._values["quota_duration"] = quota_duration
        if start_time is not None:
            self._values["start_time"] = start_time

    @builtins.property
    def quota(self) -> typing.Optional[jsii.Number]:
        '''A sign up APIs quota that customers can override temporarily.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota IdentityPlatformConfig#quota}
        '''
        result = self._values.get("quota")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def quota_duration(self) -> typing.Optional[builtins.str]:
        '''How long this quota will be active for. It is measurred in seconds, e.g., Example: "9.615s".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#quota_duration IdentityPlatformConfig#quota_duration}
        '''
        result = self._values.get("quota_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''When this quota will take affect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#start_time IdentityPlatformConfig#start_time}
        '''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigQuotaSignUpQuotaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IdentityPlatformConfigQuotaSignUpQuotaConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigQuotaSignUpQuotaConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e51e80ff7f10bdba200f8a7da9ce262c57eb405bf29d687e3075d660a640f4fb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetQuota")
    def reset_quota(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuota", []))

    @jsii.member(jsii_name="resetQuotaDuration")
    def reset_quota_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuotaDuration", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

    @builtins.property
    @jsii.member(jsii_name="quotaDurationInput")
    def quota_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quotaDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="quotaInput")
    def quota_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "quotaInput"))

    @builtins.property
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="quota")
    def quota(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "quota"))

    @quota.setter
    def quota(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34e6cbe2b96f6912e5a27b37f213c584109c5a99c28a58bb3f91e0737f79b745)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quota", value)

    @builtins.property
    @jsii.member(jsii_name="quotaDuration")
    def quota_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quotaDuration"))

    @quota_duration.setter
    def quota_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1766f85b9e539c669390882c339496610fede4cb09f23d8a33a5184d0df265b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quotaDuration", value)

    @builtins.property
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb19c7d0bce2acf4cd2c685bd4532e6beb829b07ae17bf50f8afd8cf73ff992c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTime", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IdentityPlatformConfigQuotaSignUpQuotaConfig]:
        return typing.cast(typing.Optional[IdentityPlatformConfigQuotaSignUpQuotaConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IdentityPlatformConfigQuotaSignUpQuotaConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a67e2d97663441da7b655ca0f3bbfa15e9593e022c06eb47e853209ff557dcf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class IdentityPlatformConfigTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#create IdentityPlatformConfig#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#delete IdentityPlatformConfig#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#update IdentityPlatformConfig#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__431fd73a336c906448f3317b1f0925cf9eb10815f27e7f3ffe0e1ad0d68d2966)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#create IdentityPlatformConfig#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#delete IdentityPlatformConfig#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/identity_platform_config#update IdentityPlatformConfig#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPlatformConfigTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IdentityPlatformConfigTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.identityPlatformConfig.IdentityPlatformConfigTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5159cf07335950dc909abf4879cdb07e06eee6ad11f0ee55da5964e4f351512)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57f369ea5ee8bbe9e65b2ea7b3159eca07cfa415dceef228f5c41744b1587182)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41e579d366802818e01769b75243b1771aacb6afb31ebad8b318f305f9df84a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70265ce095db4c5ee0df97c553f3b89e5e818e1afee8554f025714d6305b9883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a05b354f0621dc4fba54d6e1b2c9ad97065087105cd81fbbbbf2c3b4952bae5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "IdentityPlatformConfig",
    "IdentityPlatformConfigBlockingFunctions",
    "IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials",
    "IdentityPlatformConfigBlockingFunctionsForwardInboundCredentialsOutputReference",
    "IdentityPlatformConfigBlockingFunctionsOutputReference",
    "IdentityPlatformConfigBlockingFunctionsTriggers",
    "IdentityPlatformConfigBlockingFunctionsTriggersList",
    "IdentityPlatformConfigBlockingFunctionsTriggersOutputReference",
    "IdentityPlatformConfigConfig",
    "IdentityPlatformConfigQuota",
    "IdentityPlatformConfigQuotaOutputReference",
    "IdentityPlatformConfigQuotaSignUpQuotaConfig",
    "IdentityPlatformConfigQuotaSignUpQuotaConfigOutputReference",
    "IdentityPlatformConfigTimeouts",
    "IdentityPlatformConfigTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__0b7f2b7c995d2e86a749a49b40eff4be838e002c489fa2b5d03a6f21b4b0f3d2(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    authorized_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    autodelete_anonymous_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    blocking_functions: typing.Optional[typing.Union[IdentityPlatformConfigBlockingFunctions, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    quota: typing.Optional[typing.Union[IdentityPlatformConfigQuota, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[IdentityPlatformConfigTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0bcfcfa2aa6771c72db35b61d07f1f2bcdf55a135ca1d5984ff7dc91881a847(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e1fe055b084c476abfe2731a785123530145316a42c88a08616f83ef8c037d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c60e8e56702b4a670d0c1815c986277ce85e98e5ba4a2ac2b75ad3371f61dc82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b600b9041b4160ef06fb37cb6f9658c98d2d1f99efddaa2e2792398e5316a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a0a74f2bcd2cef65ec44ecdeaddd5d3d50329738bb8692d23cde163e46514be(
    *,
    triggers: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[IdentityPlatformConfigBlockingFunctionsTriggers, typing.Dict[builtins.str, typing.Any]]]],
    forward_inbound_credentials: typing.Optional[typing.Union[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9299d36033b7cab22b1eb5b1ea868b34e0a61dd18a7387b411068dc99a06daee(
    *,
    access_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    refresh_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb120ef282e4ef4761e46fa26ed3b34fa4a0dea209047f8e6f394cf7f5c1af9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d45a34dcce05007140f4104db688559a7b673d7e9fe267485abbeab0e0138d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ea1ef788e52f56ba082f54d9301f32a1e2c536b82621d134edcfb2779a611ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8dd87fd0f9a14e3dfef6328ab902944c202bda55eda996c2f147db186f3fa2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801a34f3130b73de4952dd443abd60f0263bc19c31aca8aef4994cb875cdccd0(
    value: typing.Optional[IdentityPlatformConfigBlockingFunctionsForwardInboundCredentials],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea82a39a24000471d15325cd2e8712a89128c55197d350e97a8c2304cdcc2dd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d9380d84963a6160ff4f6de220325ac47687c165ac2d5e0076d6ca820a38030(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[IdentityPlatformConfigBlockingFunctionsTriggers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d31a0ff7331f03093b5e70d40d6e2f746b70f98b898e17c281037a142d74d5c(
    value: typing.Optional[IdentityPlatformConfigBlockingFunctions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dda06e59673111e6ff97766bcbbb60c44530c9bdbe44883df471b01642686fe(
    *,
    event_type: builtins.str,
    function_uri: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b370ff145206ba3f43e5479c3ef886d93f3ed0c3d992cea5606538fc6e3ad16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06075886b5824d0e6be33539477807d564814122d3e7de25ce71e5727c81e9b1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03a6a35e0fccb80adc749f73c60302364ac5ba5f0cbc535fce422d0c72825a00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afdb0fc2e816dab687175b61e8c397055ad106f7239bf547d95659c32e2bd1a8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acd7a8789a157b7780a179fb5abf86c208a43a5793c6cf63e1ae3d9235697f5c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b410bef3af3be6cbe495c603f778bd3d8caa8f12b075ab681c531ead286c16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[IdentityPlatformConfigBlockingFunctionsTriggers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e101d9fcecc8a59be8ab9cbfbe0d8b078cc9cd4b34d8de4aa4a2bbf85d02a90e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ff3b68957025c5a90190abd87d1e3f1450b579e442d8aef236959bfba0c884(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8fa1cac36c3e1e25219739be8ec3d13492532cc8a119c8470abc657c5ad2484(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b765c08c8b4fd0a5ca9e01e3b24caca80cab021de1c4242508437f1280a3e8c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigBlockingFunctionsTriggers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c65289ba252bfde714602bec691f328768fa5b77566d85c699f713af705d9d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    authorized_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    autodelete_anonymous_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    blocking_functions: typing.Optional[typing.Union[IdentityPlatformConfigBlockingFunctions, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    quota: typing.Optional[typing.Union[IdentityPlatformConfigQuota, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[IdentityPlatformConfigTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14681c9040323dc00c921c27e398e58b2aaa995e317b557292476ca2e1a2fbcd(
    *,
    sign_up_quota_config: typing.Optional[typing.Union[IdentityPlatformConfigQuotaSignUpQuotaConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c988653d5f5aef939a53453c7695ae0ecebd01ac01772c2440fb453d0a026c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fb70ddbe257226b371147fb8f04608702ac4f59c616551f02a10e3398a9ddc5(
    value: typing.Optional[IdentityPlatformConfigQuota],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7991cae0a5aa0ceb55da5669d10701a19bdfc8e435ac6506aab264b9fd2f4c(
    *,
    quota: typing.Optional[jsii.Number] = None,
    quota_duration: typing.Optional[builtins.str] = None,
    start_time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e51e80ff7f10bdba200f8a7da9ce262c57eb405bf29d687e3075d660a640f4fb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34e6cbe2b96f6912e5a27b37f213c584109c5a99c28a58bb3f91e0737f79b745(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1766f85b9e539c669390882c339496610fede4cb09f23d8a33a5184d0df265b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb19c7d0bce2acf4cd2c685bd4532e6beb829b07ae17bf50f8afd8cf73ff992c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a67e2d97663441da7b655ca0f3bbfa15e9593e022c06eb47e853209ff557dcf1(
    value: typing.Optional[IdentityPlatformConfigQuotaSignUpQuotaConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__431fd73a336c906448f3317b1f0925cf9eb10815f27e7f3ffe0e1ad0d68d2966(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5159cf07335950dc909abf4879cdb07e06eee6ad11f0ee55da5964e4f351512(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57f369ea5ee8bbe9e65b2ea7b3159eca07cfa415dceef228f5c41744b1587182(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e579d366802818e01769b75243b1771aacb6afb31ebad8b318f305f9df84a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70265ce095db4c5ee0df97c553f3b89e5e818e1afee8554f025714d6305b9883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a05b354f0621dc4fba54d6e1b2c9ad97065087105cd81fbbbbf2c3b4952bae5b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, IdentityPlatformConfigTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
