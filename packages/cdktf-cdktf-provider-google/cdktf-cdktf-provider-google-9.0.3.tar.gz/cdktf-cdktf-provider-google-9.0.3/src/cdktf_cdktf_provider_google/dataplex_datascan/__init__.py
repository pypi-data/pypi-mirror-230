'''
# `google_dataplex_datascan`

Refer to the Terraform Registory for docs: [`google_dataplex_datascan`](https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan).
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


class DataplexDatascan(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascan",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan google_dataplex_datascan}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        data: typing.Union["DataplexDatascanData", typing.Dict[builtins.str, typing.Any]],
        data_scan_id: builtins.str,
        execution_spec: typing.Union["DataplexDatascanExecutionSpec", typing.Dict[builtins.str, typing.Any]],
        location: builtins.str,
        data_profile_spec: typing.Optional[typing.Union["DataplexDatascanDataProfileSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        data_quality_spec: typing.Optional[typing.Union["DataplexDatascanDataQualitySpec", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["DataplexDatascanTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan google_dataplex_datascan} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: data block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data DataplexDatascan#data}
        :param data_scan_id: DataScan identifier. Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_scan_id DataplexDatascan#data_scan_id}
        :param execution_spec: execution_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#execution_spec DataplexDatascan#execution_spec}
        :param location: The location where the data scan should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#location DataplexDatascan#location}
        :param data_profile_spec: data_profile_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_profile_spec DataplexDatascan#data_profile_spec}
        :param data_quality_spec: data_quality_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_quality_spec DataplexDatascan#data_quality_spec}
        :param description: Description of the scan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#description DataplexDatascan#description}
        :param display_name: User friendly display name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#display_name DataplexDatascan#display_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#id DataplexDatascan#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User-defined labels for the scan. A list of key->value pairs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#labels DataplexDatascan#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#project DataplexDatascan#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#timeouts DataplexDatascan#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7d978d3a14103b3ef12c1f35fc9a0641f3a0e983ba57bcdb6a7dd8fa7392d37)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataplexDatascanConfig(
            data=data,
            data_scan_id=data_scan_id,
            execution_spec=execution_spec,
            location=location,
            data_profile_spec=data_profile_spec,
            data_quality_spec=data_quality_spec,
            description=description,
            display_name=display_name,
            id=id,
            labels=labels,
            project=project,
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

    @jsii.member(jsii_name="putData")
    def put_data(
        self,
        *,
        entity: typing.Optional[builtins.str] = None,
        resource: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity: The Dataplex entity that represents the data source(e.g. BigQuery table) for Datascan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#entity DataplexDatascan#entity}
        :param resource: The service-qualified full resource name of the cloud resource for a DataScan job to scan against. The field could be: (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#resource DataplexDatascan#resource}
        '''
        value = DataplexDatascanData(entity=entity, resource=resource)

        return typing.cast(None, jsii.invoke(self, "putData", [value]))

    @jsii.member(jsii_name="putDataProfileSpec")
    def put_data_profile_spec(
        self,
        *,
        exclude_fields: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecExcludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        include_fields: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecIncludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        post_scan_actions: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_fields: exclude_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#exclude_fields DataplexDatascan#exclude_fields}
        :param include_fields: include_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#include_fields DataplexDatascan#include_fields}
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        value = DataplexDatascanDataProfileSpec(
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            post_scan_actions=post_scan_actions,
            row_filter=row_filter,
            sampling_percent=sampling_percent,
        )

        return typing.cast(None, jsii.invoke(self, "putDataProfileSpec", [value]))

    @jsii.member(jsii_name="putDataQualitySpec")
    def put_data_quality_spec(
        self,
        *,
        post_scan_actions: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#rules DataplexDatascan#rules}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        value = DataplexDatascanDataQualitySpec(
            post_scan_actions=post_scan_actions,
            row_filter=row_filter,
            rules=rules,
            sampling_percent=sampling_percent,
        )

        return typing.cast(None, jsii.invoke(self, "putDataQualitySpec", [value]))

    @jsii.member(jsii_name="putExecutionSpec")
    def put_execution_spec(
        self,
        *,
        trigger: typing.Union["DataplexDatascanExecutionSpecTrigger", typing.Dict[builtins.str, typing.Any]],
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#trigger DataplexDatascan#trigger}
        :param field: The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time. If not specified, a data scan will run for all data in the table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field DataplexDatascan#field}
        '''
        value = DataplexDatascanExecutionSpec(trigger=trigger, field=field)

        return typing.cast(None, jsii.invoke(self, "putExecutionSpec", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#create DataplexDatascan#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#delete DataplexDatascan#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#update DataplexDatascan#update}.
        '''
        value = DataplexDatascanTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDataProfileSpec")
    def reset_data_profile_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataProfileSpec", []))

    @jsii.member(jsii_name="resetDataQualitySpec")
    def reset_data_quality_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataQualitySpec", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

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
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> "DataplexDatascanDataOutputReference":
        return typing.cast("DataplexDatascanDataOutputReference", jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileResult")
    def data_profile_result(self) -> "DataplexDatascanDataProfileResultList":
        return typing.cast("DataplexDatascanDataProfileResultList", jsii.get(self, "dataProfileResult"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileSpec")
    def data_profile_spec(self) -> "DataplexDatascanDataProfileSpecOutputReference":
        return typing.cast("DataplexDatascanDataProfileSpecOutputReference", jsii.get(self, "dataProfileSpec"))

    @builtins.property
    @jsii.member(jsii_name="dataQualityResult")
    def data_quality_result(self) -> "DataplexDatascanDataQualityResultList":
        return typing.cast("DataplexDatascanDataQualityResultList", jsii.get(self, "dataQualityResult"))

    @builtins.property
    @jsii.member(jsii_name="dataQualitySpec")
    def data_quality_spec(self) -> "DataplexDatascanDataQualitySpecOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecOutputReference", jsii.get(self, "dataQualitySpec"))

    @builtins.property
    @jsii.member(jsii_name="executionSpec")
    def execution_spec(self) -> "DataplexDatascanExecutionSpecOutputReference":
        return typing.cast("DataplexDatascanExecutionSpecOutputReference", jsii.get(self, "executionSpec"))

    @builtins.property
    @jsii.member(jsii_name="executionStatus")
    def execution_status(self) -> "DataplexDatascanExecutionStatusList":
        return typing.cast("DataplexDatascanExecutionStatusList", jsii.get(self, "executionStatus"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DataplexDatascanTimeoutsOutputReference":
        return typing.cast("DataplexDatascanTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional["DataplexDatascanData"]:
        return typing.cast(typing.Optional["DataplexDatascanData"], jsii.get(self, "dataInput"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileSpecInput")
    def data_profile_spec_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpec"]:
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpec"], jsii.get(self, "dataProfileSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="dataQualitySpecInput")
    def data_quality_spec_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpec"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpec"], jsii.get(self, "dataQualitySpecInput"))

    @builtins.property
    @jsii.member(jsii_name="dataScanIdInput")
    def data_scan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataScanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="executionSpecInput")
    def execution_spec_input(self) -> typing.Optional["DataplexDatascanExecutionSpec"]:
        return typing.cast(typing.Optional["DataplexDatascanExecutionSpec"], jsii.get(self, "executionSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataplexDatascanTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataplexDatascanTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataScanId")
    def data_scan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataScanId"))

    @data_scan_id.setter
    def data_scan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e599fb759e13751ed4e9d77184f41e10d6c3e05dc3490fedfd53a40515ed90d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataScanId", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9177039bf399af0070309fe327788cbf0f4a3ba85ca45b30ca264e3821ebe69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7acddc10756adbd43ebd70f29476a8202acf88a6d91e235c4ceb847ca2e99d1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01402634ddabb6c346b4cb2c18c6624021a009b09431401735ca8c1d779f9d6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f3d64f33812a62d780f892003e5f8802daa4860abf27562a4a358eb53e212c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8453c5d69cbc241fd463cde478b1c8b4320b9f09468b4be2f475d7f47adcc2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c6e3f10a1999fb9aa8f39e401feeeb6b48be2e9b7d28ede14ab07b3a7571f19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "data": "data",
        "data_scan_id": "dataScanId",
        "execution_spec": "executionSpec",
        "location": "location",
        "data_profile_spec": "dataProfileSpec",
        "data_quality_spec": "dataQualitySpec",
        "description": "description",
        "display_name": "displayName",
        "id": "id",
        "labels": "labels",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class DataplexDatascanConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        data: typing.Union["DataplexDatascanData", typing.Dict[builtins.str, typing.Any]],
        data_scan_id: builtins.str,
        execution_spec: typing.Union["DataplexDatascanExecutionSpec", typing.Dict[builtins.str, typing.Any]],
        location: builtins.str,
        data_profile_spec: typing.Optional[typing.Union["DataplexDatascanDataProfileSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        data_quality_spec: typing.Optional[typing.Union["DataplexDatascanDataQualitySpec", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["DataplexDatascanTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param data: data block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data DataplexDatascan#data}
        :param data_scan_id: DataScan identifier. Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_scan_id DataplexDatascan#data_scan_id}
        :param execution_spec: execution_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#execution_spec DataplexDatascan#execution_spec}
        :param location: The location where the data scan should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#location DataplexDatascan#location}
        :param data_profile_spec: data_profile_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_profile_spec DataplexDatascan#data_profile_spec}
        :param data_quality_spec: data_quality_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_quality_spec DataplexDatascan#data_quality_spec}
        :param description: Description of the scan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#description DataplexDatascan#description}
        :param display_name: User friendly display name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#display_name DataplexDatascan#display_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#id DataplexDatascan#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User-defined labels for the scan. A list of key->value pairs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#labels DataplexDatascan#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#project DataplexDatascan#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#timeouts DataplexDatascan#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(data, dict):
            data = DataplexDatascanData(**data)
        if isinstance(execution_spec, dict):
            execution_spec = DataplexDatascanExecutionSpec(**execution_spec)
        if isinstance(data_profile_spec, dict):
            data_profile_spec = DataplexDatascanDataProfileSpec(**data_profile_spec)
        if isinstance(data_quality_spec, dict):
            data_quality_spec = DataplexDatascanDataQualitySpec(**data_quality_spec)
        if isinstance(timeouts, dict):
            timeouts = DataplexDatascanTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59b584f3c2ab4707c1e0552da13804a76b02aef972499ba94c6adac30ad061a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument data_scan_id", value=data_scan_id, expected_type=type_hints["data_scan_id"])
            check_type(argname="argument execution_spec", value=execution_spec, expected_type=type_hints["execution_spec"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument data_profile_spec", value=data_profile_spec, expected_type=type_hints["data_profile_spec"])
            check_type(argname="argument data_quality_spec", value=data_quality_spec, expected_type=type_hints["data_quality_spec"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data": data,
            "data_scan_id": data_scan_id,
            "execution_spec": execution_spec,
            "location": location,
        }
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
        if data_profile_spec is not None:
            self._values["data_profile_spec"] = data_profile_spec
        if data_quality_spec is not None:
            self._values["data_quality_spec"] = data_quality_spec
        if description is not None:
            self._values["description"] = description
        if display_name is not None:
            self._values["display_name"] = display_name
        if id is not None:
            self._values["id"] = id
        if labels is not None:
            self._values["labels"] = labels
        if project is not None:
            self._values["project"] = project
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
    def data(self) -> "DataplexDatascanData":
        '''data block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data DataplexDatascan#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast("DataplexDatascanData", result)

    @builtins.property
    def data_scan_id(self) -> builtins.str:
        '''DataScan identifier.

        Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_scan_id DataplexDatascan#data_scan_id}
        '''
        result = self._values.get("data_scan_id")
        assert result is not None, "Required property 'data_scan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_spec(self) -> "DataplexDatascanExecutionSpec":
        '''execution_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#execution_spec DataplexDatascan#execution_spec}
        '''
        result = self._values.get("execution_spec")
        assert result is not None, "Required property 'execution_spec' is missing"
        return typing.cast("DataplexDatascanExecutionSpec", result)

    @builtins.property
    def location(self) -> builtins.str:
        '''The location where the data scan should reside.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#location DataplexDatascan#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_profile_spec(self) -> typing.Optional["DataplexDatascanDataProfileSpec"]:
        '''data_profile_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_profile_spec DataplexDatascan#data_profile_spec}
        '''
        result = self._values.get("data_profile_spec")
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpec"], result)

    @builtins.property
    def data_quality_spec(self) -> typing.Optional["DataplexDatascanDataQualitySpec"]:
        '''data_quality_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#data_quality_spec DataplexDatascan#data_quality_spec}
        '''
        result = self._values.get("data_quality_spec")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpec"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the scan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#description DataplexDatascan#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''User friendly display name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#display_name DataplexDatascan#display_name}
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#id DataplexDatascan#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User-defined labels for the scan. A list of key->value pairs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#labels DataplexDatascan#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#project DataplexDatascan#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DataplexDatascanTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#timeouts DataplexDatascan#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DataplexDatascanTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanData",
    jsii_struct_bases=[],
    name_mapping={"entity": "entity", "resource": "resource"},
)
class DataplexDatascanData:
    def __init__(
        self,
        *,
        entity: typing.Optional[builtins.str] = None,
        resource: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity: The Dataplex entity that represents the data source(e.g. BigQuery table) for Datascan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#entity DataplexDatascan#entity}
        :param resource: The service-qualified full resource name of the cloud resource for a DataScan job to scan against. The field could be: (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#resource DataplexDatascan#resource}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__887b51eb9dc74c5797b8b0d833c1f65c3c1c65e4e91004ea510fa663bde76d5d)
            check_type(argname="argument entity", value=entity, expected_type=type_hints["entity"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if entity is not None:
            self._values["entity"] = entity
        if resource is not None:
            self._values["resource"] = resource

    @builtins.property
    def entity(self) -> typing.Optional[builtins.str]:
        '''The Dataplex entity that represents the data source(e.g. BigQuery table) for Datascan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#entity DataplexDatascan#entity}
        '''
        result = self._values.get("entity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource(self) -> typing.Optional[builtins.str]:
        '''The service-qualified full resource name of the cloud resource for a DataScan job to scan against.

        The field could be:
        (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#resource DataplexDatascan#resource}
        '''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d07a3087d95dce1b616a931956230cfd53d601f3db40f9da601a820db8924c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEntity")
    def reset_entity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntity", []))

    @jsii.member(jsii_name="resetResource")
    def reset_resource(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResource", []))

    @builtins.property
    @jsii.member(jsii_name="entityInput")
    def entity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceInput")
    def resource_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceInput"))

    @builtins.property
    @jsii.member(jsii_name="entity")
    def entity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entity"))

    @entity.setter
    def entity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe8b1ee53c0d22ea8df64f3ec598e967dc156a10fed885a0f729cf7f651bdf06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entity", value)

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d02c9fc495878cbebd90c932cc5aeefd43e50d9834c4799b71ac8a184cf05d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanData]:
        return typing.cast(typing.Optional[DataplexDatascanData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataplexDatascanData]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ecfe3da18a82a79c7d4e90e51f374b6340929ff8062d6c77258151ec9f7f51a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26e3b467f2021fee7dc89df85d9ebd3d2cc78b2b9a16e9faaf5c0051676da26f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11b66833ff2b741c4b38df472871d50f6858c4c6b79255c71984e64322084788)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd6b514f7e3038389e0aee09831826d21dae1bb1db6cd33f5f26b1bb396c6ea5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__294fc7cbddb7d0a25b27aea945ac93d09e4e7a2bdb3a046c61ee39848b3bb896)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2f65afb01bd5b7e7ddbe4d37302570c794df2863c8f28bb612e0e7b99b6cf10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab66f1aef82de267bcd627a387b959c2eeb79fc0a4b86f3d12de27b52982516d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> "DataplexDatascanDataProfileResultProfileList":
        return typing.cast("DataplexDatascanDataProfileResultProfileList", jsii.get(self, "profile"))

    @builtins.property
    @jsii.member(jsii_name="rowCount")
    def row_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rowCount"))

    @builtins.property
    @jsii.member(jsii_name="scannedData")
    def scanned_data(self) -> "DataplexDatascanDataProfileResultScannedDataList":
        return typing.cast("DataplexDatascanDataProfileResultScannedDataList", jsii.get(self, "scannedData"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanDataProfileResult]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3ab023f9059ca1892bb3b658f598c8e7b9d5ddfe138dc05d5463ecb0266a548)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFields",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFields:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultProfileFieldsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dcc4f366f45ccc6fe4f290f954a95463f92dbd07bd32738b49eb84d640508c73)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03fc2178c7d0c30bb7bfd393de7c0e369248abc051259aa59b0a3c4c87f74516)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16143a38095dcf738a64171689439bf083a0c8f859a3351bd539ac7b3633ef6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab00cdf8ed11fdd127e6d632601b0fd9a07530645a95f0753fbcdf51fbd9b315)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc203b49df205d28079ed27f941ce94fe453faa8ce6badb0414d75ae594c2b30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ac0332ba8735d3523ca65364903869fa85f8f7c58c96b28fb253363b55750fd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> "DataplexDatascanDataProfileResultProfileFieldsProfileList":
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileList", jsii.get(self, "profile"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFields]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85deac29e3b65d23fbb71c0d128cb0c3d25b6b6976d9414a18f382fe61e9ccf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFieldsProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFieldsProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8451bc250e4b108a20df2761cb59ecf4ef44ea3d0c8c441cd478f647e79b8d8d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff2a6762171eff0c19dfd025fc5c0db2e6e5ed484a1bde170dfa9f0d2a2025be)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a36520d7bada342b889fa3b068cf207b8b65ed8b4f82bbdfa67d6617f411eade)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0315497d98badbfdb477efddbcac334a796b5188df782e47cd026331a107c133)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05dc95c6faf2f069bea254710bf7a7bb35788786add0bc7fa073d83034b25f25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d06ff2a037d28853297eaba92971eae32fc90fa0bcbde1a2b95a1825b1e50bf3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="average")
    def average(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "average"))

    @builtins.property
    @jsii.member(jsii_name="max")
    def max(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "max"))

    @builtins.property
    @jsii.member(jsii_name="min")
    def min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "min"))

    @builtins.property
    @jsii.member(jsii_name="quartiles")
    def quartiles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartiles"))

    @builtins.property
    @jsii.member(jsii_name="standardDeviation")
    def standard_deviation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "standardDeviation"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b186f05c66247c291e761ad2b3f4a4db13f4b1b6fc084f29ec91fbf856dd257d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9af998b752df2b55f42530bdb3e02f8f810589f8f5e5d80bf88b288e9790b20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__909dcd897e286a866786e636f8cb00d17a1ae6e8bbfb0d9ae86073b18e399c6a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6b6a412a727483b5b86e5d260290157c49c97cd078de7841d9cf5e5f38e2ba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60528c619946ec926cf1eba80b8d209cb6013d57b8d6b858a307ee3c62524da3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2b714e846c51b1bd6e0320e70a83c75deb2e770749bd61ac91cd570b05a6aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3381b2cb69697ea9fd8e31203126bcffa81142ac55f8a6ffcebe90ae7721def1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="average")
    def average(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "average"))

    @builtins.property
    @jsii.member(jsii_name="max")
    def max(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "max"))

    @builtins.property
    @jsii.member(jsii_name="min")
    def min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "min"))

    @builtins.property
    @jsii.member(jsii_name="quartiles")
    def quartiles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartiles"))

    @builtins.property
    @jsii.member(jsii_name="standardDeviation")
    def standard_deviation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "standardDeviation"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a4790a25281b7e5f0f05b86eb6d2caec78f3c7b22bf4f297fded4844ea24c60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26cc362fc01d8faaea1b1e831696ead7a9ad938e1f2c115f410e73036068560d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a98aec9ef8a20222be8978702faf9ff2e560ebc615e27c19e1ec3e7adf926d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__319eadda73579ff24698cec9f3ea800dc9a5b05f11d3c9ffb670a9af410e9d47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc2a98c4321c3a023fdd77a79232f982b524938ddcd8a76bff66fa0e24d8f5d5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__07690f3cf1dc64b46656654f995a1f24ab297968ff6ffd88166f21f68dc773be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdabff3fd1ca871d6fdd97cc8e569d6ac4236850a5553441c87d0952031428d7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="distinctRatio")
    def distinct_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "distinctRatio"))

    @builtins.property
    @jsii.member(jsii_name="doubleProfile")
    def double_profile(
        self,
    ) -> DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList:
        return typing.cast(DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList, jsii.get(self, "doubleProfile"))

    @builtins.property
    @jsii.member(jsii_name="integerProfile")
    def integer_profile(
        self,
    ) -> DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList:
        return typing.cast(DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList, jsii.get(self, "integerProfile"))

    @builtins.property
    @jsii.member(jsii_name="nullRatio")
    def null_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nullRatio"))

    @builtins.property
    @jsii.member(jsii_name="stringProfile")
    def string_profile(
        self,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList":
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList", jsii.get(self, "stringProfile"))

    @builtins.property
    @jsii.member(jsii_name="topNValues")
    def top_n_values(
        self,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList":
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList", jsii.get(self, "topNValues"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfile]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db62f7bc153eb7339abcf49174ed471cf547ed733c84e9b25f56a0a28ad216f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e451a3060baa7114248de3eb0dd4bf8adebb2db2bddfe6c82323d425841ed39e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d760806f0b263138ba974c3eaae8a0e81fba84e9839cf2f7b01c8acbb559a91)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2049d9d2d08f5deb3700cf0b1eefe0a41f67524cf9bb169d270cbcbe5289a320)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90d9172a88e215dcf989750a688a9d7c8fd6bbebc14c51174adb6112669ce24d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e09ddf63d755ef729e9a6b66b2e95cce1fc4619d35bf712fa5c27762afd190f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9004ffe8f8e5214d437786516a133324638c109b7477b0aa261f9e3fcdab8a06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="averageLength")
    def average_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "averageLength"))

    @builtins.property
    @jsii.member(jsii_name="maxLength")
    def max_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxLength"))

    @builtins.property
    @jsii.member(jsii_name="minLength")
    def min_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minLength"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__804a47584025c53ef32ecd48430766480de042a0c5db2fc147b90cfe6d7a8d88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0d076b5e20d79b2c7cc962315cfe1f7ae800ab623f775749929004657f181a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e3ad39bc38afcf3c066e80edcbd01d8e6a96e108a91c7822b5b5405ebf8b96f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4439870f4f3e7c5c78ac35c7b22e37ba6a67d9bace9c1c27db01dbe52ca70138)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c2e71285afb6ee7e30f40d08f9b1020cc2a849616224370f889e11cc3a4015f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e3487abbd458f47242f52a1fa40a9f6f0957623377f472bdaafbdeca3753c26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a934767e18436ae480737fd6a0e9ff125e7a44653e7342348abf56054219788)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="count")
    def count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "count"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54815abd1472b134d809a5539f930e64285a627e7f475fb50f689c7d47e5ad16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataProfileResultProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae22c78457c9f71bea6bef180e69389fe5465adc29eaf035c92cc1f10ab99f01)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a6d481c057dec1a88f5ca98d157c2002688c7020e255a31d9f4fa282ed5ec24)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e16970047a048fbad424620742740d97a4b032cb3c7cf0416840ef15862a9f46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da392bd693c1ff368d4c2c401fbc681f23b941d74663c5122bf99640704afe62)
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
            type_hints = typing.get_type_hints(_typecheckingstub__09aa6bd668f2187b36f45402be4531433f67406f4d7914ad6ea4b5cbf726a83c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__73ee4e16381ea029a83469f1f69c20bbed658d369833568afc7dd09e2b7b2b99)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fields")
    def fields(self) -> DataplexDatascanDataProfileResultProfileFieldsList:
        return typing.cast(DataplexDatascanDataProfileResultProfileFieldsList, jsii.get(self, "fields"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultProfile]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c015d769d468ac0a2d9002bb945ad8cc9c43f218cba2a116f8dc92e0524be0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedData",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultScannedData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultScannedData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedDataIncrementalField",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataProfileResultScannedDataIncrementalField:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileResultScannedDataIncrementalField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileResultScannedDataIncrementalFieldList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedDataIncrementalFieldList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__943b7ee7d2d635b4f91de7057d50b0218efeba8f47b80e356b92e788a93e64d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__941b8302c431e4b7f8467e1ac422009ee700621bcb862abd0887cecec01c0f89)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3039a012dd1f9d30f88ef39a706a1b666f49cc865435efa16b6d70a51bae0cae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5029a4185d9e5499a5bdb167a7d5ec59bf760ab26e21145e0022faeb0371412a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd21901eb268e122ae4877d6787006765603bca31e8da2c91254fa88a7a5c803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c150c86abe5dff6871da611509e2517b7b3ea0b89a0b3c8695e74a0b81931ebb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="end")
    def end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "end"))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultScannedDataIncrementalField]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultScannedDataIncrementalField], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultScannedDataIncrementalField],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fdab52235dceef7b9d099e69ee2119cbd8ec0e0250a9c69bf02205038ec0569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataProfileResultScannedDataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedDataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__13766f2e8ad40df9f06a8579749639af102623e65accc2ad6752a04b98dd1878)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataProfileResultScannedDataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e154cbde9e01cdbf2008feb5761f9f5ac0475c025db197fbc4d435cefb9aff)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataProfileResultScannedDataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c0965cb262695dba1ed8e8502d7fbfbf0044bb6a2a17d9a48a8bc00754b54e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a887dcd44f19b3521a52d8a7086c20076b133912c3dab668a1edb2310603d9bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2122d4bf4c057a5860e10ec10903be645f9d002f2d938735c2f346190626dc63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataProfileResultScannedDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileResultScannedDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49da29bfc89ccad3a11e9127a1ec5cdda5183425e9b2a400c4c716cf259cdeb4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="incrementalField")
    def incremental_field(
        self,
    ) -> DataplexDatascanDataProfileResultScannedDataIncrementalFieldList:
        return typing.cast(DataplexDatascanDataProfileResultScannedDataIncrementalFieldList, jsii.get(self, "incrementalField"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileResultScannedData]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileResultScannedData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileResultScannedData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453eb12bfec1c69a72452f33873946a8034ce29d226fe5c2e1fa7e134cee41b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpec",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_fields": "excludeFields",
        "include_fields": "includeFields",
        "post_scan_actions": "postScanActions",
        "row_filter": "rowFilter",
        "sampling_percent": "samplingPercent",
    },
)
class DataplexDatascanDataProfileSpec:
    def __init__(
        self,
        *,
        exclude_fields: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecExcludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        include_fields: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecIncludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        post_scan_actions: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_fields: exclude_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#exclude_fields DataplexDatascan#exclude_fields}
        :param include_fields: include_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#include_fields DataplexDatascan#include_fields}
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        if isinstance(exclude_fields, dict):
            exclude_fields = DataplexDatascanDataProfileSpecExcludeFields(**exclude_fields)
        if isinstance(include_fields, dict):
            include_fields = DataplexDatascanDataProfileSpecIncludeFields(**include_fields)
        if isinstance(post_scan_actions, dict):
            post_scan_actions = DataplexDatascanDataProfileSpecPostScanActions(**post_scan_actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97359cc1586f9deb4de9c7e12f4682dac9e7dd4d4fca628be49da0ff075b12f8)
            check_type(argname="argument exclude_fields", value=exclude_fields, expected_type=type_hints["exclude_fields"])
            check_type(argname="argument include_fields", value=include_fields, expected_type=type_hints["include_fields"])
            check_type(argname="argument post_scan_actions", value=post_scan_actions, expected_type=type_hints["post_scan_actions"])
            check_type(argname="argument row_filter", value=row_filter, expected_type=type_hints["row_filter"])
            check_type(argname="argument sampling_percent", value=sampling_percent, expected_type=type_hints["sampling_percent"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_fields is not None:
            self._values["exclude_fields"] = exclude_fields
        if include_fields is not None:
            self._values["include_fields"] = include_fields
        if post_scan_actions is not None:
            self._values["post_scan_actions"] = post_scan_actions
        if row_filter is not None:
            self._values["row_filter"] = row_filter
        if sampling_percent is not None:
            self._values["sampling_percent"] = sampling_percent

    @builtins.property
    def exclude_fields(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpecExcludeFields"]:
        '''exclude_fields block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#exclude_fields DataplexDatascan#exclude_fields}
        '''
        result = self._values.get("exclude_fields")
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpecExcludeFields"], result)

    @builtins.property
    def include_fields(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpecIncludeFields"]:
        '''include_fields block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#include_fields DataplexDatascan#include_fields}
        '''
        result = self._values.get("include_fields")
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpecIncludeFields"], result)

    @builtins.property
    def post_scan_actions(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpecPostScanActions"]:
        '''post_scan_actions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        '''
        result = self._values.get("post_scan_actions")
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpecPostScanActions"], result)

    @builtins.property
    def row_filter(self) -> typing.Optional[builtins.str]:
        '''A filter applied to all rows in a single DataScan job.

        The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        '''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sampling_percent(self) -> typing.Optional[jsii.Number]:
        '''The percentage of the records to be selected from the dataset for DataScan.

        Value can range between 0.0 and 100.0 with up to 3 significant decimal digits.
        Sampling is not applied if 'sampling_percent' is not specified, 0 or 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        result = self._values.get("sampling_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecExcludeFields",
    jsii_struct_bases=[],
    name_mapping={"field_names": "fieldNames"},
)
class DataplexDatascanDataProfileSpecExcludeFields:
    def __init__(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__317b91e781a70d6fad6013a374886068dda8ff121929bec9c8d0657b1c3d5c9d)
            check_type(argname="argument field_names", value=field_names, expected_type=type_hints["field_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if field_names is not None:
            self._values["field_names"] = field_names

    @builtins.property
    def field_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Expected input is a list of fully qualified names of fields as in the schema.

        Only top-level field names for nested fields are supported.
        For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        result = self._values.get("field_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileSpecExcludeFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileSpecExcludeFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecExcludeFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dab82f93c5b430d1788ef410438ff3eab940d106ffbb978fe7152cc4d80febe4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFieldNames")
    def reset_field_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldNames", []))

    @builtins.property
    @jsii.member(jsii_name="fieldNamesInput")
    def field_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "fieldNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldNames")
    def field_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fieldNames"))

    @field_names.setter
    def field_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bdcac021b9965491bda49fa6b9d1406131d6d600cb12123b8c19c44c5395a09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldNames", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecExcludeFields]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecExcludeFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileSpecExcludeFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__514fe3bbc8323bba64096b62898c41318dc3be0ce5781178f037e79d6403a6cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecIncludeFields",
    jsii_struct_bases=[],
    name_mapping={"field_names": "fieldNames"},
)
class DataplexDatascanDataProfileSpecIncludeFields:
    def __init__(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12cc9d674cdfa8f3c1724cafe1f5a3fb480acc9c68cd6b5ddd424cfed9fa399f)
            check_type(argname="argument field_names", value=field_names, expected_type=type_hints["field_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if field_names is not None:
            self._values["field_names"] = field_names

    @builtins.property
    def field_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Expected input is a list of fully qualified names of fields as in the schema.

        Only top-level field names for nested fields are supported.
        For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        result = self._values.get("field_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileSpecIncludeFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileSpecIncludeFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecIncludeFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__31d1fb585271177c44c468dd93dcad4ad5389daaec077cbe2bbb1992aaa20e28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFieldNames")
    def reset_field_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldNames", []))

    @builtins.property
    @jsii.member(jsii_name="fieldNamesInput")
    def field_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "fieldNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldNames")
    def field_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fieldNames"))

    @field_names.setter
    def field_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90af2e7104018dd67faba658bf81aa1f23ddf543605d7aae58e7263e7ce1311a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldNames", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecIncludeFields]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecIncludeFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileSpecIncludeFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c4137798a894c7cadf23b6e98b2ce6982be340029ba4d8aac394476d64d9cc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataProfileSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__249c1b17060819390364350da4fc04f801484cad1eea5c334ddd06a25e947453)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putExcludeFields")
    def put_exclude_fields(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        value = DataplexDatascanDataProfileSpecExcludeFields(field_names=field_names)

        return typing.cast(None, jsii.invoke(self, "putExcludeFields", [value]))

    @jsii.member(jsii_name="putIncludeFields")
    def put_include_fields(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field_names DataplexDatascan#field_names}
        '''
        value = DataplexDatascanDataProfileSpecIncludeFields(field_names=field_names)

        return typing.cast(None, jsii.invoke(self, "putIncludeFields", [value]))

    @jsii.member(jsii_name="putPostScanActions")
    def put_post_scan_actions(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        value = DataplexDatascanDataProfileSpecPostScanActions(
            bigquery_export=bigquery_export
        )

        return typing.cast(None, jsii.invoke(self, "putPostScanActions", [value]))

    @jsii.member(jsii_name="resetExcludeFields")
    def reset_exclude_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeFields", []))

    @jsii.member(jsii_name="resetIncludeFields")
    def reset_include_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeFields", []))

    @jsii.member(jsii_name="resetPostScanActions")
    def reset_post_scan_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostScanActions", []))

    @jsii.member(jsii_name="resetRowFilter")
    def reset_row_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRowFilter", []))

    @jsii.member(jsii_name="resetSamplingPercent")
    def reset_sampling_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamplingPercent", []))

    @builtins.property
    @jsii.member(jsii_name="excludeFields")
    def exclude_fields(
        self,
    ) -> DataplexDatascanDataProfileSpecExcludeFieldsOutputReference:
        return typing.cast(DataplexDatascanDataProfileSpecExcludeFieldsOutputReference, jsii.get(self, "excludeFields"))

    @builtins.property
    @jsii.member(jsii_name="includeFields")
    def include_fields(
        self,
    ) -> DataplexDatascanDataProfileSpecIncludeFieldsOutputReference:
        return typing.cast(DataplexDatascanDataProfileSpecIncludeFieldsOutputReference, jsii.get(self, "includeFields"))

    @builtins.property
    @jsii.member(jsii_name="postScanActions")
    def post_scan_actions(
        self,
    ) -> "DataplexDatascanDataProfileSpecPostScanActionsOutputReference":
        return typing.cast("DataplexDatascanDataProfileSpecPostScanActionsOutputReference", jsii.get(self, "postScanActions"))

    @builtins.property
    @jsii.member(jsii_name="excludeFieldsInput")
    def exclude_fields_input(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecExcludeFields]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecExcludeFields], jsii.get(self, "excludeFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeFieldsInput")
    def include_fields_input(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecIncludeFields]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecIncludeFields], jsii.get(self, "includeFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="postScanActionsInput")
    def post_scan_actions_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpecPostScanActions"]:
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpecPostScanActions"], jsii.get(self, "postScanActionsInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilterInput")
    def row_filter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="samplingPercentInput")
    def sampling_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "samplingPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rowFilter"))

    @row_filter.setter
    def row_filter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7258d6e996ed8fc69dfd98fa4ea5915f2f62b8f0221713857a361f4c50a1f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rowFilter", value)

    @builtins.property
    @jsii.member(jsii_name="samplingPercent")
    def sampling_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingPercent"))

    @sampling_percent.setter
    def sampling_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3d642e4e66f780a58eed116cc3f089bd8e13713e1e836c1f427d6ea4b8edd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingPercent", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanDataProfileSpec]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ebfe7dbf82ace6f2dc587fc4a14e5eef3cdbe8a0d7af1cf282b0ec0e78fdba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecPostScanActions",
    jsii_struct_bases=[],
    name_mapping={"bigquery_export": "bigqueryExport"},
)
class DataplexDatascanDataProfileSpecPostScanActions:
    def __init__(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        if isinstance(bigquery_export, dict):
            bigquery_export = DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(**bigquery_export)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca2420faf9c7d516a166319fa522692d6f12166431d6e6c3d20dc893e930b081)
            check_type(argname="argument bigquery_export", value=bigquery_export, expected_type=type_hints["bigquery_export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bigquery_export is not None:
            self._values["bigquery_export"] = bigquery_export

    @builtins.property
    def bigquery_export(
        self,
    ) -> typing.Optional["DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport"]:
        '''bigquery_export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        result = self._values.get("bigquery_export")
        return typing.cast(typing.Optional["DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileSpecPostScanActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport",
    jsii_struct_bases=[],
    name_mapping={"results_table": "resultsTable"},
)
class DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport:
    def __init__(self, *, results_table: typing.Optional[builtins.str] = None) -> None:
        '''
        :param results_table: The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0ff25a7f34bc05f1c2964df3baba773c1bd7f5fd73c27abde8ff1d63ca483a1)
            check_type(argname="argument results_table", value=results_table, expected_type=type_hints["results_table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if results_table is not None:
            self._values["results_table"] = results_table

    @builtins.property
    def results_table(self) -> typing.Optional[builtins.str]:
        '''The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        result = self._values.get("results_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91f2d719ea688fb37587f352bdc503c8570b92b2b73b01633d9c4fb5bd1238ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetResultsTable")
    def reset_results_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResultsTable", []))

    @builtins.property
    @jsii.member(jsii_name="resultsTableInput")
    def results_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resultsTableInput"))

    @builtins.property
    @jsii.member(jsii_name="resultsTable")
    def results_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resultsTable"))

    @results_table.setter
    def results_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0523fdb60e6c58d72823452f982496b52d9bd851de801ee582959968a2ccb189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resultsTable", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1376163de2a44cd1f2ea700e708602a69aabb542d6697dd07af9f3842980d19f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataProfileSpecPostScanActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataProfileSpecPostScanActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd7e37c13b20d42c56e72f6294c14dd314bb931cf25dd59bfa022a8a963d77ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBigqueryExport")
    def put_bigquery_export(
        self,
        *,
        results_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param results_table: The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        value = DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(
            results_table=results_table
        )

        return typing.cast(None, jsii.invoke(self, "putBigqueryExport", [value]))

    @jsii.member(jsii_name="resetBigqueryExport")
    def reset_bigquery_export(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBigqueryExport", []))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExport")
    def bigquery_export(
        self,
    ) -> DataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference:
        return typing.cast(DataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference, jsii.get(self, "bigqueryExport"))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExportInput")
    def bigquery_export_input(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport], jsii.get(self, "bigqueryExportInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataProfileSpecPostScanActions]:
        return typing.cast(typing.Optional[DataplexDatascanDataProfileSpecPostScanActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataProfileSpecPostScanActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d8b9c26ad5ee444d69a6d0d5affdaa135f0cd75916453d317c13c29d7e23a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultDimensions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultDimensions:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3648bcd762471381f5e70730afd27c0a926c836f5ff09691fe58f75fcf646da)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60a57beb6473505dbe3733831ded5a43f2626704c3b048de03946b799d6b217)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b39855c020ed5694a2ab5df8235c0395374f565ec6590f56e80979c05f3b7ee)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00d2726d9b6a8f95d7a30035674e496b98424a0507a35aa38dad70b111782461)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bba5d100b401a54f18cec614cde46090335216a28cb7d0d621220f323caf0ab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cabaf5a38d9a7cc909bb84d5f5cf89a8b646912f5404856dbaeea0e0b3cc946b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="passed")
    def passed(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "passed"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultDimensions]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultDimensions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultDimensions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234058f62278a0913f884c4a472cdbcd57cc59111129772d3dba1d9b13fcf264)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataQualityResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3565fe2fb2c5dcae7399bbe70244ea77c9efc31ec47e9aad8405c28112c30ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a09a4a054942e93cac2a53397faad9459ec5f9f8ffdf0de9d44bf84cc03aa1a0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8820ac958e1ab897e78cf3276d98b060603f593ac5fb0b35f3a1f4089ed1ac8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__952b3c7c61b1da7b002fb6c0ff13f144721fc9dd8dc661cdf5a12b60e4f3dce4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82cd69ee1e3db666b70a48bbeb621c4b5d349d8b3a4fb684b470998b2be701e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f590ff226f1de3af11df5056d3e7b4af46d88bd69c9b33a12d6621b309c27c58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> DataplexDatascanDataQualityResultDimensionsList:
        return typing.cast(DataplexDatascanDataQualityResultDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="passed")
    def passed(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "passed"))

    @builtins.property
    @jsii.member(jsii_name="rowCount")
    def row_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rowCount"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "DataplexDatascanDataQualityResultRulesList":
        return typing.cast("DataplexDatascanDataQualityResultRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="scannedData")
    def scanned_data(self) -> "DataplexDatascanDataQualityResultScannedDataList":
        return typing.cast("DataplexDatascanDataQualityResultScannedDataList", jsii.get(self, "scannedData"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanDataQualityResult]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd68929bbcbb0b3c0e4d5d81ebbfe513d341620c7e8aadb28c7928ead5b6749)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32987e5d61a6d3c161ca05aab09712f68342d177db76853cf14a9b3b06e4f252)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec1a89757d530e15349a3ccb04ac4028bb48c51fe08e57c4aa46deb1aa457a56)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__975de62a685a91966d5ee68b4c1e9ac823500e516bc6ab517ffe9b751c3a2eea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a63a3d1a5ffc165daac856a7b7456e588c91eb94f80ca30e2dca943349bd1a33)
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
            type_hints = typing.get_type_hints(_typecheckingstub__145fa5f88338e38557cd2b13a5614d24fdd02a1481d650b2bae588aa45803cee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca9558c55f6ecda8d41e0df9f7677bece453992c86913b42d3f65350ea42eb2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="evaluatedCount")
    def evaluated_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evaluatedCount"))

    @builtins.property
    @jsii.member(jsii_name="failingRowsQuery")
    def failing_rows_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failingRowsQuery"))

    @builtins.property
    @jsii.member(jsii_name="nullCount")
    def null_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nullCount"))

    @builtins.property
    @jsii.member(jsii_name="passed")
    def passed(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "passed"))

    @builtins.property
    @jsii.member(jsii_name="passedCount")
    def passed_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passedCount"))

    @builtins.property
    @jsii.member(jsii_name="passRatio")
    def pass_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passRatio"))

    @builtins.property
    @jsii.member(jsii_name="rule")
    def rule(self) -> "DataplexDatascanDataQualityResultRulesRuleList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleList", jsii.get(self, "rule"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanDataQualityResultRules]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7ed51a7d035ba32511413c1104a2e352af487de594749ce135ce394489dccaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRule",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRule:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8a455bbbc9aab7c18b509f54eeade8df96769cfe47f96b9f494dbae7ec496d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d108b4c34535cc38c204083f2364edd400f6b1eccf6c67a5ba00e49f7158a0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06bd86bda327e30d4e9da8b8a0f21e366f18c67cba52b6e7de2b4e72b7e097c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__197923fb8b46e010f8f607213663a776dbf7ceba36e430938dcaf71e84b1ec08)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c825fdb39bc375f188ac878b30899bc3c1299c5d7057d7408af855c402228d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleNonNullExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleNonNullExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleNonNullExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleNonNullExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleNonNullExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0a3cdfbd501453b0970d47e4929c905903932c09215dfb88b448389aa85662b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1813fd171630b4a91eba7d11a2ee80383d7a1b7e20865eb2e6cf9ab1ab40fa19)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c298dc11c5e2ac9c5988fdab1a3f4561ae36a7ea34f956aa650f63432da14759)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00115d3558bd350d768dc166d2dd3fe31a2eadc8eaaf2f1dfbf58b482971fbda)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df677cdb19263e177199697bb9e8cc761f7d5f07980728f21d0a14cc4fddab1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a5c9758c576ec6b6e95d4f304552eb58f51de5f24879bee25f6a99419a2303e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleNonNullExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleNonNullExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleNonNullExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d275db3494d1427adce59217816e8947628162217909da68aa68a618fc489f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataQualityResultRulesRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a546eaf3912ff49dc10fb8f5eb8618a734508ee607365468a60ab1ed925afdd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="column")
    def column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "column"))

    @builtins.property
    @jsii.member(jsii_name="dimension")
    def dimension(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dimension"))

    @builtins.property
    @jsii.member(jsii_name="ignoreNull")
    def ignore_null(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ignoreNull"))

    @builtins.property
    @jsii.member(jsii_name="nonNullExpectation")
    def non_null_expectation(
        self,
    ) -> DataplexDatascanDataQualityResultRulesRuleNonNullExpectationList:
        return typing.cast(DataplexDatascanDataQualityResultRulesRuleNonNullExpectationList, jsii.get(self, "nonNullExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectation")
    def range_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRangeExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRangeExpectationList", jsii.get(self, "rangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectation")
    def regex_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRegexExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRegexExpectationList", jsii.get(self, "regexExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectation")
    def row_condition_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList", jsii.get(self, "rowConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="setExpectation")
    def set_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleSetExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleSetExpectationList", jsii.get(self, "setExpectation"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectation")
    def statistic_range_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList", jsii.get(self, "statisticRangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectation")
    def table_condition_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList", jsii.get(self, "tableConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectation")
    def uniqueness_expectation(
        self,
    ) -> "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList":
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList", jsii.get(self, "uniquenessExpectation"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRule]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c30f90156f88d28965d3dcf00ffb37c7482eecdaa279d5db6f8b69554aa0bd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleRangeExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleRangeExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRangeExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__240f6596fd209f7ba298a98e7550395516d3d72ad7c658758e258559f9fee85e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd850b0f343ea7ba8ae3f9c151ed98ecb7710dd40554370f0183f963fd1819e2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e598b864387f4e786da8ada19e0024d01ba1a14c13a6f527a452fc0035df966)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8cee20d005c58fae9a1ce198d085b92306b9fac237a2fb2a98d55b77c10b6b5e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00d8d252f367bf74eee1b29925e773fd128bc5868adf1abef243d0e9695e2c7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3ff7cb2ce44359378bf982b4b4c8b651f454b262ceeab63348ad4dedec6cfe0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabled")
    def strict_max_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "strictMaxEnabled"))

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabled")
    def strict_min_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "strictMinEnabled"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleRangeExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__655d29cef738da6197f0d81d3377276467746d29533e6cbb4a846bdb8d823eb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRegexExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleRegexExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleRegexExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleRegexExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRegexExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41982a269b038131c62ce5917319059652b30c798cef4ddd2d782fecc7509b41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f7ad04cff632b5c6e0bb343a6bacf1473423fb1fabd2811a7e33fe9f7fa3ae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97fb11268868b7e1c45fe1bc0e268c31fbb529f76cd9b7cb78871b416ab6c76d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc25dd5bbb9c15c89c3f059fe87339952dd0317162b73e191063aceecc6af358)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db788582109e7572431ac78d4042da7c834830fdec49f475db2fe1d5e78c53ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0076a18d5d45af397eb85a13c6fdf34f76191a4e8e70f060ecd67081629cca7a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleRegexExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleRegexExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRegexExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fba36a282b784024139165bad9014418c538622d6425f91de4c2d3ecfab9f600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1237b709b5c917e9f24ef57985c270922c02649a81b68f88ffef54ed08eafc1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d95325c29eff370c108e390b2be4ccb2ccfd1f869260fb9807a06cc23fd85f0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c352b6a079a8fbcbf6a3a6479ef6ecf668693587281e3b80f0738f24325807a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__76d34e27bbfde9f3ab05a010676fb850f7467c77e10aa32670f1bb0b307b573b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9feb01ff8a4c50663ebe7563baab28785fc2924e0cef974f52a021b4bd4eb259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf8b54dc01e1e083b8d92fcea63ac0dcb7731cbb90a98703e742a5bee9fa2185)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="sqlExpression")
    def sql_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlExpression"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19aea8cadc2535952b016f4441f0dc7cdeba4778e44f2799ba02e90eec903c21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleSetExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleSetExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleSetExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleSetExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleSetExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9824ca4923cfc4d83293da96f4c516bba8465e2c4678d50555a658be4ecf610)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9acbd71d542c349dbe98fd5367e14e773e9bdb23eb23afdd71c2a2b2c1f559f2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0618e969b8bfc83e0ac10288e52deaaa887635ddb55f16ac7135d5c4d9b907e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da253ba56f80c07b44d8cf75d4cb60121879f9cffcd72611c768afe4a8b6784a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a66b9ffdc99af020e043a08be04a1541b660c7be1cebee6faeeb22f4388c349e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b70e26fd8b7210ca4fcac97a99c256b27a2584392085d92ed1d0757960718b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleSetExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleSetExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleSetExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc3a8fc7c9867b98c991b032b7a6bdf88a023ebbab47ebd044286a57cc2d0773)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d0335de06e47b1defd41015b351ebcaf8f6e5963a955e5d903640211dd32eb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60a0a50ba008a98bd50f888939afd47323fc199e13f1f5b810b189371a603ae0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__325876c2483fe766764cc4ce1f879ff5e113d0bea53f4268518ee0df79f7b064)
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
            type_hints = typing.get_type_hints(_typecheckingstub__89350774af7188cece13628b265ad75de4b72e17b3395091fee5266c1253278f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2eb9d97605cfe3b34225960a6707c8e937c8b460add99a9c359c24e7b8ce674f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1887d44fd8c07fdd7418b0c208d1ccd15be0ee0408e096f9efe2da853a3562bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabled")
    def strict_max_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "strictMaxEnabled"))

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabled")
    def strict_min_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "strictMinEnabled"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13da13b4c3892019cd5f48c4685cfc58c41256e2d60555a9903b17752bf9819)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20de8463467128c676b5d44aa2f6bf348fd638684c9e7db2bbc0b8be812483a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6faba148cbe9fcbe6692e4f822158ad6dce3db7cb0f09b422b8f10c1e1cec8a0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5f05364dd99105fa923e5d6e5733c79ab320a8cff766a6307616338d1f74b3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d964d6d27fa903e6e32ac306b97cbf7019f989c87c48b647fd819f5909408064)
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
            type_hints = typing.get_type_hints(_typecheckingstub__406eee650309c3700f4c953abd4c8a33262bbd2774a4554af8f875a542fb867e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea8d8c49d9cd32ea9ef8b919878211085d363523ca70fe7b844bef760fae4e3f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="sqlExpression")
    def sql_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlExpression"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e47ab065c1ec6ea8d24b670e278e5c4112aa8150cc2ca0b0619aa513dd5c6584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0a3b301bd2eb54ebb3f9651ff1d48a9236bb74b8ab936e6611bc945e9a8acc7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1497e44c0ab368bdd04e2e9b64cb5865e35f083ea63d3f515948061ff0a3f1f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e47cbcc488e2669da45222a341d8c6446e6484f72b47a003ccbe6b47fdae5267)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa89997a9afacd7344ca26b56461b80348f7fcb71baae0f205bc3cf79d14a84c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2715f92e57f236bda10f81a08ab8d85c183692fe0b600cc6faebfa0b957a5a19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62d74bd1c849491f1a71f3f235b72d8594b6fa0ab9d253bde406f0cf7bdc7a02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26ee377389501e9baf5023ac7aad712f718bf166b4bda62c3cc32714490e4e71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedData",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultScannedData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultScannedData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedDataIncrementalField",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualityResultScannedDataIncrementalField:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualityResultScannedDataIncrementalField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualityResultScannedDataIncrementalFieldList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedDataIncrementalFieldList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f04e7422613d021a194e0bab8e5a508cb1b7e7029d0f63b67fbf3437ea9d220f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5a54543a79e75ee3cf77e3afb18fd06943fac88d62493222d5d2a4974b616d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48ce6a953f962aa641e8bf6be480924444a73ae9c2ec14c7defa6b5246e4b203)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18cb720eafe0e4804895481cdf0cc48556afc1639b490407c17eece084b34a2f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8310b6201b81a1192ebd58ee63bc4c4b1fa741d59a0075fbca2216c00e8274f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__033733554bd4a4392adc538fec8aaa932bddf61370576f4aa6a342e05e3a48fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="end")
    def end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "end"))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultScannedDataIncrementalField]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultScannedDataIncrementalField], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultScannedDataIncrementalField],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68fd44bd93701a142f6aa1696709f0fccc70e7e6658a5316ff3e7b68ac88006)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataQualityResultScannedDataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedDataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ae65118a1f0de7cd0fa2e449a003e889ea3a17a35650fd8c2b373be8618b076)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualityResultScannedDataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e8418de531ce55580b734d4989b3ba4069530a4c25aada55acdbe3944b7176)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualityResultScannedDataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__288f0cc97b1630a9db667bace84e84a48e5580e28e599f523b8305de8be605f7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dea8ce19c3e0847f7bd9fcbf9a3615357f8dcab4eb24094b7969ff04c6ae4bdd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce9f35d1da4851e4a36982d3a300172ae61300bc4d350865ef08808af63f7b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanDataQualityResultScannedDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualityResultScannedDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c47a9caa7a824f18710b78481f502f3ceb822ad9614f5ed4e78bfd64f456cba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="incrementalField")
    def incremental_field(
        self,
    ) -> DataplexDatascanDataQualityResultScannedDataIncrementalFieldList:
        return typing.cast(DataplexDatascanDataQualityResultScannedDataIncrementalFieldList, jsii.get(self, "incrementalField"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualityResultScannedData]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualityResultScannedData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualityResultScannedData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31929e026c6161221554d1b707170d6893081a113a42eab54c81049964d2c069)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpec",
    jsii_struct_bases=[],
    name_mapping={
        "post_scan_actions": "postScanActions",
        "row_filter": "rowFilter",
        "rules": "rules",
        "sampling_percent": "samplingPercent",
    },
)
class DataplexDatascanDataQualitySpec:
    def __init__(
        self,
        *,
        post_scan_actions: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#rules DataplexDatascan#rules}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        if isinstance(post_scan_actions, dict):
            post_scan_actions = DataplexDatascanDataQualitySpecPostScanActions(**post_scan_actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85c98a56040ac5f9e591bba4e1a4fa0a58d92446f6282e22ad7ef9e5ead6bb80)
            check_type(argname="argument post_scan_actions", value=post_scan_actions, expected_type=type_hints["post_scan_actions"])
            check_type(argname="argument row_filter", value=row_filter, expected_type=type_hints["row_filter"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
            check_type(argname="argument sampling_percent", value=sampling_percent, expected_type=type_hints["sampling_percent"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if post_scan_actions is not None:
            self._values["post_scan_actions"] = post_scan_actions
        if row_filter is not None:
            self._values["row_filter"] = row_filter
        if rules is not None:
            self._values["rules"] = rules
        if sampling_percent is not None:
            self._values["sampling_percent"] = sampling_percent

    @builtins.property
    def post_scan_actions(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecPostScanActions"]:
        '''post_scan_actions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#post_scan_actions DataplexDatascan#post_scan_actions}
        '''
        result = self._values.get("post_scan_actions")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecPostScanActions"], result)

    @builtins.property
    def row_filter(self) -> typing.Optional[builtins.str]:
        '''A filter applied to all rows in a single DataScan job.

        The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_filter DataplexDatascan#row_filter}
        '''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataplexDatascanDataQualitySpecRules"]]]:
        '''rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#rules DataplexDatascan#rules}
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataplexDatascanDataQualitySpecRules"]]], result)

    @builtins.property
    def sampling_percent(self) -> typing.Optional[jsii.Number]:
        '''The percentage of the records to be selected from the dataset for DataScan.

        Value can range between 0.0 and 100.0 with up to 3 significant decimal digits.
        Sampling is not applied if 'sampling_percent' is not specified, 0 or 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sampling_percent DataplexDatascan#sampling_percent}
        '''
        result = self._values.get("sampling_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71887d414bfebf19c33160aca3d7a99a4057fb053019e41bade2100377d75079)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPostScanActions")
    def put_post_scan_actions(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        value = DataplexDatascanDataQualitySpecPostScanActions(
            bigquery_export=bigquery_export
        )

        return typing.cast(None, jsii.invoke(self, "putPostScanActions", [value]))

    @jsii.member(jsii_name="putRules")
    def put_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97e4645c0fdd4af9c8d94abd52201f612cfbfa74e577e76ff4fbf50d84f02469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRules", [value]))

    @jsii.member(jsii_name="resetPostScanActions")
    def reset_post_scan_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostScanActions", []))

    @jsii.member(jsii_name="resetRowFilter")
    def reset_row_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRowFilter", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

    @jsii.member(jsii_name="resetSamplingPercent")
    def reset_sampling_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamplingPercent", []))

    @builtins.property
    @jsii.member(jsii_name="postScanActions")
    def post_scan_actions(
        self,
    ) -> "DataplexDatascanDataQualitySpecPostScanActionsOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecPostScanActionsOutputReference", jsii.get(self, "postScanActions"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "DataplexDatascanDataQualitySpecRulesList":
        return typing.cast("DataplexDatascanDataQualitySpecRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="postScanActionsInput")
    def post_scan_actions_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecPostScanActions"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecPostScanActions"], jsii.get(self, "postScanActionsInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilterInput")
    def row_filter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataplexDatascanDataQualitySpecRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataplexDatascanDataQualitySpecRules"]]], jsii.get(self, "rulesInput"))

    @builtins.property
    @jsii.member(jsii_name="samplingPercentInput")
    def sampling_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "samplingPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rowFilter"))

    @row_filter.setter
    def row_filter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e684f7a223bd3b8697103319d545d5f73bca5ac008fad80de4cc4771349e5a07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rowFilter", value)

    @builtins.property
    @jsii.member(jsii_name="samplingPercent")
    def sampling_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingPercent"))

    @sampling_percent.setter
    def sampling_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99d588c57dd79bf1e283d4a386394ec6a940747baec8dcf253f1b84e309d0f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingPercent", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanDataQualitySpec]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97c50c625b58b82848acec8bc31b41279f7450881cce359286c40783633e1958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecPostScanActions",
    jsii_struct_bases=[],
    name_mapping={"bigquery_export": "bigqueryExport"},
)
class DataplexDatascanDataQualitySpecPostScanActions:
    def __init__(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        if isinstance(bigquery_export, dict):
            bigquery_export = DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(**bigquery_export)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88d4c425f3b0ef2a8bf372e542b1b79e03c2b5dd24990a7772494847d9bb38ad)
            check_type(argname="argument bigquery_export", value=bigquery_export, expected_type=type_hints["bigquery_export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bigquery_export is not None:
            self._values["bigquery_export"] = bigquery_export

    @builtins.property
    def bigquery_export(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport"]:
        '''bigquery_export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#bigquery_export DataplexDatascan#bigquery_export}
        '''
        result = self._values.get("bigquery_export")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecPostScanActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport",
    jsii_struct_bases=[],
    name_mapping={"results_table": "resultsTable"},
)
class DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport:
    def __init__(self, *, results_table: typing.Optional[builtins.str] = None) -> None:
        '''
        :param results_table: The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1e32e88c2d9c7cd520d7abd11db51ab1b32ff1f7b952820017f0d4daff9d350)
            check_type(argname="argument results_table", value=results_table, expected_type=type_hints["results_table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if results_table is not None:
            self._values["results_table"] = results_table

    @builtins.property
    def results_table(self) -> typing.Optional[builtins.str]:
        '''The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        result = self._values.get("results_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41229a1a441415a484969f33dada1770a0fb2d61e0725348faa5589b289e36d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetResultsTable")
    def reset_results_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResultsTable", []))

    @builtins.property
    @jsii.member(jsii_name="resultsTableInput")
    def results_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resultsTableInput"))

    @builtins.property
    @jsii.member(jsii_name="resultsTable")
    def results_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resultsTable"))

    @results_table.setter
    def results_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e7ae2abb3d11a2028b835c1fd6c58b13d7fcf533f62a55063d175fe4722b97d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resultsTable", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f739184964e852d91eadef2fc4f35a73e0469d3c5f34f023cf0479e34316711)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataQualitySpecPostScanActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecPostScanActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40ec4d4f2bc1503a9faf7d8be3e8d256c28eef9a3c72260b1f154ace0564aa77)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBigqueryExport")
    def put_bigquery_export(
        self,
        *,
        results_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param results_table: The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#results_table DataplexDatascan#results_table}
        '''
        value = DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(
            results_table=results_table
        )

        return typing.cast(None, jsii.invoke(self, "putBigqueryExport", [value]))

    @jsii.member(jsii_name="resetBigqueryExport")
    def reset_bigquery_export(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBigqueryExport", []))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExport")
    def bigquery_export(
        self,
    ) -> DataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference:
        return typing.cast(DataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference, jsii.get(self, "bigqueryExport"))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExportInput")
    def bigquery_export_input(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport], jsii.get(self, "bigqueryExportInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecPostScanActions]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecPostScanActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecPostScanActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdb7c645be6acadab8d8cfd96c2cc485f3a057bf8c6fcae2bee9feb29607ccce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRules",
    jsii_struct_bases=[],
    name_mapping={
        "dimension": "dimension",
        "column": "column",
        "description": "description",
        "ignore_null": "ignoreNull",
        "name": "name",
        "non_null_expectation": "nonNullExpectation",
        "range_expectation": "rangeExpectation",
        "regex_expectation": "regexExpectation",
        "row_condition_expectation": "rowConditionExpectation",
        "set_expectation": "setExpectation",
        "statistic_range_expectation": "statisticRangeExpectation",
        "table_condition_expectation": "tableConditionExpectation",
        "threshold": "threshold",
        "uniqueness_expectation": "uniquenessExpectation",
    },
)
class DataplexDatascanDataQualitySpecRules:
    def __init__(
        self,
        *,
        dimension: builtins.str,
        column: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        ignore_null: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        non_null_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesNonNullExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        range_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesRangeExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        regex_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesRegexExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        row_condition_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesRowConditionExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        set_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesSetExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        statistic_range_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        table_condition_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesTableConditionExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[jsii.Number] = None,
        uniqueness_expectation: typing.Optional[typing.Union["DataplexDatascanDataQualitySpecRulesUniquenessExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dimension: The dimension a rule belongs to. Results are also aggregated at the dimension level. Supported dimensions are ["COMPLETENESS", "ACCURACY", "CONSISTENCY", "VALIDITY", "UNIQUENESS", "INTEGRITY"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#dimension DataplexDatascan#dimension}
        :param column: The unnested column which this rule is evaluated against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#column DataplexDatascan#column}
        :param description: Description of the rule. The maximum length is 1,024 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#description DataplexDatascan#description}
        :param ignore_null: Rows with null values will automatically fail a rule, unless ignoreNull is true. In that case, such null rows are trivially considered passing. Only applicable to ColumnMap rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#ignore_null DataplexDatascan#ignore_null}
        :param name: A mutable name for the rule. The name must contain only letters (a-z, A-Z), numbers (0-9), or hyphens (-). The maximum length is 63 characters. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#name DataplexDatascan#name}
        :param non_null_expectation: non_null_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#non_null_expectation DataplexDatascan#non_null_expectation}
        :param range_expectation: range_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#range_expectation DataplexDatascan#range_expectation}
        :param regex_expectation: regex_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#regex_expectation DataplexDatascan#regex_expectation}
        :param row_condition_expectation: row_condition_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_condition_expectation DataplexDatascan#row_condition_expectation}
        :param set_expectation: set_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#set_expectation DataplexDatascan#set_expectation}
        :param statistic_range_expectation: statistic_range_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#statistic_range_expectation DataplexDatascan#statistic_range_expectation}
        :param table_condition_expectation: table_condition_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#table_condition_expectation DataplexDatascan#table_condition_expectation}
        :param threshold: The minimum ratio of passing_rows / total_rows required to pass this rule, with a range of [0.0, 1.0]. 0 indicates default value (i.e. 1.0). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#threshold DataplexDatascan#threshold}
        :param uniqueness_expectation: uniqueness_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#uniqueness_expectation DataplexDatascan#uniqueness_expectation}
        '''
        if isinstance(non_null_expectation, dict):
            non_null_expectation = DataplexDatascanDataQualitySpecRulesNonNullExpectation(**non_null_expectation)
        if isinstance(range_expectation, dict):
            range_expectation = DataplexDatascanDataQualitySpecRulesRangeExpectation(**range_expectation)
        if isinstance(regex_expectation, dict):
            regex_expectation = DataplexDatascanDataQualitySpecRulesRegexExpectation(**regex_expectation)
        if isinstance(row_condition_expectation, dict):
            row_condition_expectation = DataplexDatascanDataQualitySpecRulesRowConditionExpectation(**row_condition_expectation)
        if isinstance(set_expectation, dict):
            set_expectation = DataplexDatascanDataQualitySpecRulesSetExpectation(**set_expectation)
        if isinstance(statistic_range_expectation, dict):
            statistic_range_expectation = DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(**statistic_range_expectation)
        if isinstance(table_condition_expectation, dict):
            table_condition_expectation = DataplexDatascanDataQualitySpecRulesTableConditionExpectation(**table_condition_expectation)
        if isinstance(uniqueness_expectation, dict):
            uniqueness_expectation = DataplexDatascanDataQualitySpecRulesUniquenessExpectation(**uniqueness_expectation)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f31a3525e6b316fa85e52d9d95f27722bbbbeb6ecb5187454efa713bd2be01eb)
            check_type(argname="argument dimension", value=dimension, expected_type=type_hints["dimension"])
            check_type(argname="argument column", value=column, expected_type=type_hints["column"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument ignore_null", value=ignore_null, expected_type=type_hints["ignore_null"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument non_null_expectation", value=non_null_expectation, expected_type=type_hints["non_null_expectation"])
            check_type(argname="argument range_expectation", value=range_expectation, expected_type=type_hints["range_expectation"])
            check_type(argname="argument regex_expectation", value=regex_expectation, expected_type=type_hints["regex_expectation"])
            check_type(argname="argument row_condition_expectation", value=row_condition_expectation, expected_type=type_hints["row_condition_expectation"])
            check_type(argname="argument set_expectation", value=set_expectation, expected_type=type_hints["set_expectation"])
            check_type(argname="argument statistic_range_expectation", value=statistic_range_expectation, expected_type=type_hints["statistic_range_expectation"])
            check_type(argname="argument table_condition_expectation", value=table_condition_expectation, expected_type=type_hints["table_condition_expectation"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument uniqueness_expectation", value=uniqueness_expectation, expected_type=type_hints["uniqueness_expectation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dimension": dimension,
        }
        if column is not None:
            self._values["column"] = column
        if description is not None:
            self._values["description"] = description
        if ignore_null is not None:
            self._values["ignore_null"] = ignore_null
        if name is not None:
            self._values["name"] = name
        if non_null_expectation is not None:
            self._values["non_null_expectation"] = non_null_expectation
        if range_expectation is not None:
            self._values["range_expectation"] = range_expectation
        if regex_expectation is not None:
            self._values["regex_expectation"] = regex_expectation
        if row_condition_expectation is not None:
            self._values["row_condition_expectation"] = row_condition_expectation
        if set_expectation is not None:
            self._values["set_expectation"] = set_expectation
        if statistic_range_expectation is not None:
            self._values["statistic_range_expectation"] = statistic_range_expectation
        if table_condition_expectation is not None:
            self._values["table_condition_expectation"] = table_condition_expectation
        if threshold is not None:
            self._values["threshold"] = threshold
        if uniqueness_expectation is not None:
            self._values["uniqueness_expectation"] = uniqueness_expectation

    @builtins.property
    def dimension(self) -> builtins.str:
        '''The dimension a rule belongs to.

        Results are also aggregated at the dimension level. Supported dimensions are ["COMPLETENESS", "ACCURACY", "CONSISTENCY", "VALIDITY", "UNIQUENESS", "INTEGRITY"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#dimension DataplexDatascan#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def column(self) -> typing.Optional[builtins.str]:
        '''The unnested column which this rule is evaluated against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#column DataplexDatascan#column}
        '''
        result = self._values.get("column")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the rule. The maximum length is 1,024 characters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#description DataplexDatascan#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_null(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Rows with null values will automatically fail a rule, unless ignoreNull is true.

        In that case, such null rows are trivially considered passing. Only applicable to ColumnMap rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#ignore_null DataplexDatascan#ignore_null}
        '''
        result = self._values.get("ignore_null")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A mutable name for the rule.

        The name must contain only letters (a-z, A-Z), numbers (0-9), or hyphens (-).
        The maximum length is 63 characters.
        Must start with a letter.
        Must end with a number or a letter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#name DataplexDatascan#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def non_null_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesNonNullExpectation"]:
        '''non_null_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#non_null_expectation DataplexDatascan#non_null_expectation}
        '''
        result = self._values.get("non_null_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesNonNullExpectation"], result)

    @builtins.property
    def range_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRangeExpectation"]:
        '''range_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#range_expectation DataplexDatascan#range_expectation}
        '''
        result = self._values.get("range_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRangeExpectation"], result)

    @builtins.property
    def regex_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRegexExpectation"]:
        '''regex_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#regex_expectation DataplexDatascan#regex_expectation}
        '''
        result = self._values.get("regex_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRegexExpectation"], result)

    @builtins.property
    def row_condition_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRowConditionExpectation"]:
        '''row_condition_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#row_condition_expectation DataplexDatascan#row_condition_expectation}
        '''
        result = self._values.get("row_condition_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRowConditionExpectation"], result)

    @builtins.property
    def set_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesSetExpectation"]:
        '''set_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#set_expectation DataplexDatascan#set_expectation}
        '''
        result = self._values.get("set_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesSetExpectation"], result)

    @builtins.property
    def statistic_range_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"]:
        '''statistic_range_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#statistic_range_expectation DataplexDatascan#statistic_range_expectation}
        '''
        result = self._values.get("statistic_range_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"], result)

    @builtins.property
    def table_condition_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesTableConditionExpectation"]:
        '''table_condition_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#table_condition_expectation DataplexDatascan#table_condition_expectation}
        '''
        result = self._values.get("table_condition_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesTableConditionExpectation"], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''The minimum ratio of passing_rows / total_rows required to pass this rule, with a range of [0.0, 1.0]. 0 indicates default value (i.e. 1.0).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#threshold DataplexDatascan#threshold}
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uniqueness_expectation(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesUniquenessExpectation"]:
        '''uniqueness_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#uniqueness_expectation DataplexDatascan#uniqueness_expectation}
        '''
        result = self._values.get("uniqueness_expectation")
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesUniquenessExpectation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6f6a501cf2ff5783ab6573f714638d827de167ccba2b5a70a7696032f776bf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanDataQualitySpecRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1fcc45b0ed7e1e1cf1e37f592761f449a845a73c3ca5e397749e06fe0aa555a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanDataQualitySpecRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff8668d815b6c8ee4e1a2eaa2532af3505c6ff1a1857d15702c367a61a0b0b62)
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
            type_hints = typing.get_type_hints(_typecheckingstub__361e868f5fc2b28e7c42881dd07181155e351e9bf12e51f0e215207c6bbcfea2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f68d0f72f90e3e57736ddaa92ef1236e4788eb56b811ff69ff2eb95a5290559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataplexDatascanDataQualitySpecRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataplexDatascanDataQualitySpecRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataplexDatascanDataQualitySpecRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c64df4d8637ff6193481df214baf857507ab29651b730b860fd8631e35a1dca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesNonNullExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualitySpecRulesNonNullExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesNonNullExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3dfbe05de944fd068a47b5529354f9f73b3a6347629dd8c6b8e169870c5505f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8849d3bf809a221ce924ebb2c0f1c6a505fa0923bbfe7c73c078b94d769a3148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanDataQualitySpecRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__760ebc6a3289ef3333f8fbe92ff7f03a37bae78f9b3d33d7b73cc72482919682)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNonNullExpectation")
    def put_non_null_expectation(self) -> None:
        value = DataplexDatascanDataQualitySpecRulesNonNullExpectation()

        return typing.cast(None, jsii.invoke(self, "putNonNullExpectation", [value]))

    @jsii.member(jsii_name="putRangeExpectation")
    def put_range_expectation(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
        strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param max_value: The maximum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        :param min_value: The minimum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        :param strict_max_enabled: Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        value = DataplexDatascanDataQualitySpecRulesRangeExpectation(
            max_value=max_value,
            min_value=min_value,
            strict_max_enabled=strict_max_enabled,
            strict_min_enabled=strict_min_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putRangeExpectation", [value]))

    @jsii.member(jsii_name="putRegexExpectation")
    def put_regex_expectation(self, *, regex: builtins.str) -> None:
        '''
        :param regex: A regular expression the column value is expected to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#regex DataplexDatascan#regex}
        '''
        value = DataplexDatascanDataQualitySpecRulesRegexExpectation(regex=regex)

        return typing.cast(None, jsii.invoke(self, "putRegexExpectation", [value]))

    @jsii.member(jsii_name="putRowConditionExpectation")
    def put_row_condition_expectation(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        value = DataplexDatascanDataQualitySpecRulesRowConditionExpectation(
            sql_expression=sql_expression
        )

        return typing.cast(None, jsii.invoke(self, "putRowConditionExpectation", [value]))

    @jsii.member(jsii_name="putSetExpectation")
    def put_set_expectation(self, *, values: typing.Sequence[builtins.str]) -> None:
        '''
        :param values: Expected values for the column value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#values DataplexDatascan#values}
        '''
        value = DataplexDatascanDataQualitySpecRulesSetExpectation(values=values)

        return typing.cast(None, jsii.invoke(self, "putSetExpectation", [value]))

    @jsii.member(jsii_name="putStatisticRangeExpectation")
    def put_statistic_range_expectation(
        self,
        *,
        statistic: builtins.str,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
        strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param statistic: column statistics. Possible values: ["STATISTIC_UNDEFINED", "MEAN", "MIN", "MAX"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#statistic DataplexDatascan#statistic}
        :param max_value: The maximum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        :param min_value: The minimum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        :param strict_max_enabled: Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        value = DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(
            statistic=statistic,
            max_value=max_value,
            min_value=min_value,
            strict_max_enabled=strict_max_enabled,
            strict_min_enabled=strict_min_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putStatisticRangeExpectation", [value]))

    @jsii.member(jsii_name="putTableConditionExpectation")
    def put_table_condition_expectation(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        value = DataplexDatascanDataQualitySpecRulesTableConditionExpectation(
            sql_expression=sql_expression
        )

        return typing.cast(None, jsii.invoke(self, "putTableConditionExpectation", [value]))

    @jsii.member(jsii_name="putUniquenessExpectation")
    def put_uniqueness_expectation(self) -> None:
        value = DataplexDatascanDataQualitySpecRulesUniquenessExpectation()

        return typing.cast(None, jsii.invoke(self, "putUniquenessExpectation", [value]))

    @jsii.member(jsii_name="resetColumn")
    def reset_column(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColumn", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetIgnoreNull")
    def reset_ignore_null(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreNull", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNonNullExpectation")
    def reset_non_null_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNonNullExpectation", []))

    @jsii.member(jsii_name="resetRangeExpectation")
    def reset_range_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeExpectation", []))

    @jsii.member(jsii_name="resetRegexExpectation")
    def reset_regex_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegexExpectation", []))

    @jsii.member(jsii_name="resetRowConditionExpectation")
    def reset_row_condition_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRowConditionExpectation", []))

    @jsii.member(jsii_name="resetSetExpectation")
    def reset_set_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetExpectation", []))

    @jsii.member(jsii_name="resetStatisticRangeExpectation")
    def reset_statistic_range_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatisticRangeExpectation", []))

    @jsii.member(jsii_name="resetTableConditionExpectation")
    def reset_table_condition_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConditionExpectation", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @jsii.member(jsii_name="resetUniquenessExpectation")
    def reset_uniqueness_expectation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUniquenessExpectation", []))

    @builtins.property
    @jsii.member(jsii_name="nonNullExpectation")
    def non_null_expectation(
        self,
    ) -> DataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference:
        return typing.cast(DataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference, jsii.get(self, "nonNullExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectation")
    def range_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference", jsii.get(self, "rangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectation")
    def regex_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference", jsii.get(self, "regexExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectation")
    def row_condition_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference", jsii.get(self, "rowConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="setExpectation")
    def set_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesSetExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesSetExpectationOutputReference", jsii.get(self, "setExpectation"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectation")
    def statistic_range_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference", jsii.get(self, "statisticRangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectation")
    def table_condition_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference", jsii.get(self, "tableConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectation")
    def uniqueness_expectation(
        self,
    ) -> "DataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference":
        return typing.cast("DataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference", jsii.get(self, "uniquenessExpectation"))

    @builtins.property
    @jsii.member(jsii_name="columnInput")
    def column_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "columnInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dimensionInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreNullInput")
    def ignore_null_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ignoreNullInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nonNullExpectationInput")
    def non_null_expectation_input(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation], jsii.get(self, "nonNullExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectationInput")
    def range_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRangeExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRangeExpectation"], jsii.get(self, "rangeExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectationInput")
    def regex_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRegexExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRegexExpectation"], jsii.get(self, "regexExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectationInput")
    def row_condition_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesRowConditionExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesRowConditionExpectation"], jsii.get(self, "rowConditionExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="setExpectationInput")
    def set_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesSetExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesSetExpectation"], jsii.get(self, "setExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectationInput")
    def statistic_range_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"], jsii.get(self, "statisticRangeExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectationInput")
    def table_condition_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesTableConditionExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesTableConditionExpectation"], jsii.get(self, "tableConditionExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectationInput")
    def uniqueness_expectation_input(
        self,
    ) -> typing.Optional["DataplexDatascanDataQualitySpecRulesUniquenessExpectation"]:
        return typing.cast(typing.Optional["DataplexDatascanDataQualitySpecRulesUniquenessExpectation"], jsii.get(self, "uniquenessExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="column")
    def column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "column"))

    @column.setter
    def column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52047181638f5644a574c14b17beb5bcbd317c865a247170353629e24253f4db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "column", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb23ab7d88a75e61957d4e61cb08f4a0b45265454a5c7ea30046bf8ae768712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="dimension")
    def dimension(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dimension"))

    @dimension.setter
    def dimension(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa3219e0e4a1b50219d834a5a5c8c86b7f2e3bf5d1b7729947b7f2f43cc78cbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimension", value)

    @builtins.property
    @jsii.member(jsii_name="ignoreNull")
    def ignore_null(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ignoreNull"))

    @ignore_null.setter
    def ignore_null(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc0451e96f8f545004f44b04e92b7597de8201970d6739ba14f933614cc2034f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreNull", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08cfc1422780d9cbd9366c99bc1217235ed3e6d081f7d2d9f1017a784dd8856a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6a5aa8d2de5e9e8af1810fecb00dff022dd56eb7064e652447ac2c9bc15697a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanDataQualitySpecRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanDataQualitySpecRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanDataQualitySpecRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25ec6ab48b9f4324e4e1d654a33d91db63d358c80c0187abe2e74cc03952493d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={
        "max_value": "maxValue",
        "min_value": "minValue",
        "strict_max_enabled": "strictMaxEnabled",
        "strict_min_enabled": "strictMinEnabled",
    },
)
class DataplexDatascanDataQualitySpecRulesRangeExpectation:
    def __init__(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
        strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param max_value: The maximum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        :param min_value: The minimum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        :param strict_max_enabled: Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f6bc64dcf4f7f09f45fe73068b2c630074f63d470317245ba2a680d12c56c1d)
            check_type(argname="argument max_value", value=max_value, expected_type=type_hints["max_value"])
            check_type(argname="argument min_value", value=min_value, expected_type=type_hints["min_value"])
            check_type(argname="argument strict_max_enabled", value=strict_max_enabled, expected_type=type_hints["strict_max_enabled"])
            check_type(argname="argument strict_min_enabled", value=strict_min_enabled, expected_type=type_hints["strict_min_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_value is not None:
            self._values["max_value"] = max_value
        if min_value is not None:
            self._values["min_value"] = min_value
        if strict_max_enabled is not None:
            self._values["strict_max_enabled"] = strict_max_enabled
        if strict_min_enabled is not None:
            self._values["strict_min_enabled"] = strict_min_enabled

    @builtins.property
    def max_value(self) -> typing.Optional[builtins.str]:
        '''The maximum column value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        '''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''The minimum column value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        '''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def strict_max_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed.

        Only relevant if a maxValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        '''
        result = self._values.get("strict_max_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def strict_min_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed.

        Only relevant if a minValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        result = self._values.get("strict_min_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__759703238b5b0d1a3835089c0c71204d63a6a31f39c97f57b9ced2d8536fcec5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxValue")
    def reset_max_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxValue", []))

    @jsii.member(jsii_name="resetMinValue")
    def reset_min_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinValue", []))

    @jsii.member(jsii_name="resetStrictMaxEnabled")
    def reset_strict_max_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrictMaxEnabled", []))

    @jsii.member(jsii_name="resetStrictMinEnabled")
    def reset_strict_min_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrictMinEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="maxValueInput")
    def max_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxValueInput"))

    @builtins.property
    @jsii.member(jsii_name="minValueInput")
    def min_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minValueInput"))

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabledInput")
    def strict_max_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "strictMaxEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabledInput")
    def strict_min_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "strictMinEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @max_value.setter
    def max_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d3a9026c0215202dca02914dbdaa9cf1d2792ce6001755eb136f5a85b737005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxValue", value)

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12abae15248ea3615e37306659e5bf80f36d56a94fb5f11a4e5f9865a2e4fbe8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minValue", value)

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabled")
    def strict_max_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "strictMaxEnabled"))

    @strict_max_enabled.setter
    def strict_max_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a607fdaebb39b605219715663624e6bb2c3d5633dfd296aa771d67393d120d26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMaxEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabled")
    def strict_min_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "strictMinEnabled"))

    @strict_min_enabled.setter
    def strict_min_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e94da435a3316245418a11abcd0fbaa1ee9ae6201fcb4e8e3876ecacb7bcd8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMinEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesRangeExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b8c6819f966ceef61ffa34b5a8788e0b0d240d62390c25fb4062afd194442e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRegexExpectation",
    jsii_struct_bases=[],
    name_mapping={"regex": "regex"},
)
class DataplexDatascanDataQualitySpecRulesRegexExpectation:
    def __init__(self, *, regex: builtins.str) -> None:
        '''
        :param regex: A regular expression the column value is expected to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#regex DataplexDatascan#regex}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d572b0255331e03ccc7577a2e8133353b531f411231808b1ded5ae16b165b4)
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regex": regex,
        }

    @builtins.property
    def regex(self) -> builtins.str:
        '''A regular expression the column value is expected to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#regex DataplexDatascan#regex}
        '''
        result = self._values.get("regex")
        assert result is not None, "Required property 'regex' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesRegexExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__313b8a8891714003d03503677cfc9b8524bd53fb35f1155a99087a85f8efc796)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="regexInput")
    def regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexInput"))

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cea7c94bcdcae17875c5316055b54fa0200d0acf73f6a57c123789689f8d3b15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesRegexExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesRegexExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesRegexExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__475a09c26a9b7d34550a970d0233670a5fa5e0e0a026dc50558962b1e466798c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRowConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={"sql_expression": "sqlExpression"},
)
class DataplexDatascanDataQualitySpecRulesRowConditionExpectation:
    def __init__(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94ad4aba19ee0e8a72b9600566e5aaab50eea58d6fee6f1451b2210ceb858889)
            check_type(argname="argument sql_expression", value=sql_expression, expected_type=type_hints["sql_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sql_expression": sql_expression,
        }

    @builtins.property
    def sql_expression(self) -> builtins.str:
        '''The SQL expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        result = self._values.get("sql_expression")
        assert result is not None, "Required property 'sql_expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesRowConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3585d17a97171b4d2226f21863be39b6882b7880be852b3f36abced064cf6885)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="sqlExpressionInput")
    def sql_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlExpression")
    def sql_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlExpression"))

    @sql_expression.setter
    def sql_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a45d7af9028a72e0eff6f708fd474122a85a1bdf0b78cfe2b3594c326683ac34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlExpression", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesRowConditionExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesRowConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesRowConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__425e669bfd65f764df50ea8c0778b1c2b453198f2008d3836d8a38bdcde536cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesSetExpectation",
    jsii_struct_bases=[],
    name_mapping={"values": "values"},
)
class DataplexDatascanDataQualitySpecRulesSetExpectation:
    def __init__(self, *, values: typing.Sequence[builtins.str]) -> None:
        '''
        :param values: Expected values for the column value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#values DataplexDatascan#values}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c87bedf5b64085ec94bb7706f878c3c3db008d4c783a265f2009ba8315299b5)
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "values": values,
        }

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Expected values for the column value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#values DataplexDatascan#values}
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesSetExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesSetExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesSetExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6c453804a5e391cf62b798b805cb0df27c2e26acbcc062035dfd93abe6627de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8a2f911fa1c82f4b1c82be1cfd5e1d6013c3e1f95a73ba511aa8cf3756dc060)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesSetExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesSetExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesSetExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2d8295163aa80ea21d497e6a6bfd05b2c03c9fa074f40dbbc0de90a8cdc1c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={
        "statistic": "statistic",
        "max_value": "maxValue",
        "min_value": "minValue",
        "strict_max_enabled": "strictMaxEnabled",
        "strict_min_enabled": "strictMinEnabled",
    },
)
class DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation:
    def __init__(
        self,
        *,
        statistic: builtins.str,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
        strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param statistic: column statistics. Possible values: ["STATISTIC_UNDEFINED", "MEAN", "MIN", "MAX"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#statistic DataplexDatascan#statistic}
        :param max_value: The maximum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        :param min_value: The minimum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        :param strict_max_enabled: Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b0a5aa73adb2ee9583a2361bd732522f3b3dc6d97169e30893463bb70d70b15)
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument max_value", value=max_value, expected_type=type_hints["max_value"])
            check_type(argname="argument min_value", value=min_value, expected_type=type_hints["min_value"])
            check_type(argname="argument strict_max_enabled", value=strict_max_enabled, expected_type=type_hints["strict_max_enabled"])
            check_type(argname="argument strict_min_enabled", value=strict_min_enabled, expected_type=type_hints["strict_min_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "statistic": statistic,
        }
        if max_value is not None:
            self._values["max_value"] = max_value
        if min_value is not None:
            self._values["min_value"] = min_value
        if strict_max_enabled is not None:
            self._values["strict_max_enabled"] = strict_max_enabled
        if strict_min_enabled is not None:
            self._values["strict_min_enabled"] = strict_min_enabled

    @builtins.property
    def statistic(self) -> builtins.str:
        '''column statistics. Possible values: ["STATISTIC_UNDEFINED", "MEAN", "MIN", "MAX"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#statistic DataplexDatascan#statistic}
        '''
        result = self._values.get("statistic")
        assert result is not None, "Required property 'statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_value(self) -> typing.Optional[builtins.str]:
        '''The maximum column statistic value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#max_value DataplexDatascan#max_value}
        '''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''The minimum column statistic value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#min_value DataplexDatascan#min_value}
        '''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def strict_max_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed.

        Only relevant if a maxValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_max_enabled DataplexDatascan#strict_max_enabled}
        '''
        result = self._values.get("strict_max_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def strict_min_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed.

        Only relevant if a minValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#strict_min_enabled DataplexDatascan#strict_min_enabled}
        '''
        result = self._values.get("strict_min_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__975d32301b3563a6ee53e9ea35860ae76ed71a942de71dfa2f6539a64db59acf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxValue")
    def reset_max_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxValue", []))

    @jsii.member(jsii_name="resetMinValue")
    def reset_min_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinValue", []))

    @jsii.member(jsii_name="resetStrictMaxEnabled")
    def reset_strict_max_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrictMaxEnabled", []))

    @jsii.member(jsii_name="resetStrictMinEnabled")
    def reset_strict_min_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrictMinEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="maxValueInput")
    def max_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxValueInput"))

    @builtins.property
    @jsii.member(jsii_name="minValueInput")
    def min_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minValueInput"))

    @builtins.property
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabledInput")
    def strict_max_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "strictMaxEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabledInput")
    def strict_min_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "strictMinEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @max_value.setter
    def max_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf1b9df4f4acbe6c8c40f4e9a180a2ab96e1f5fcec945af5072b185516903aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxValue", value)

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd93fc38c3669a133ebb7fe4b55bc4c608e5c09ea6d4a01fab510b4abe81a5d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minValue", value)

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55ba00dbd43a80b645f71245295ea4290c2b02aaee0c8cee01a0f43db50082b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value)

    @builtins.property
    @jsii.member(jsii_name="strictMaxEnabled")
    def strict_max_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "strictMaxEnabled"))

    @strict_max_enabled.setter
    def strict_max_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d8d81305355619bc8c44b1303a525b01949934c01a2dc69651734abefe3832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMaxEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="strictMinEnabled")
    def strict_min_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "strictMinEnabled"))

    @strict_min_enabled.setter
    def strict_min_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__797c434697eb4e4d61ac5116af34212ab463c6c087edf28e28e77db13e64ef3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMinEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__929fa9c246994fdaef6c453521d03b51cef32b3868bf3fbfdafe7e012a19ac75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesTableConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={"sql_expression": "sqlExpression"},
)
class DataplexDatascanDataQualitySpecRulesTableConditionExpectation:
    def __init__(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46ef359ae5fae4724bfb144183e476594f79a5dae9d5269f2e5521757e32582a)
            check_type(argname="argument sql_expression", value=sql_expression, expected_type=type_hints["sql_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sql_expression": sql_expression,
        }

    @builtins.property
    def sql_expression(self) -> builtins.str:
        '''The SQL expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#sql_expression DataplexDatascan#sql_expression}
        '''
        result = self._values.get("sql_expression")
        assert result is not None, "Required property 'sql_expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesTableConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__08943a8e396992a3a68166c3b89eec5abd11c659b0b2c0f9a27306d8e06d7045)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="sqlExpressionInput")
    def sql_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlExpression")
    def sql_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlExpression"))

    @sql_expression.setter
    def sql_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebfd3f38bb494bd76daa96d507b86916e2a785b837cbe1a229f9429e91a57c4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlExpression", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesTableConditionExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesTableConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesTableConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e31bc4a5a6ae2fb8b6909bf2677b8a9dbbe5dfc9d72e326032091ffba8c647)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesUniquenessExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanDataQualitySpecRulesUniquenessExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanDataQualitySpecRulesUniquenessExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1806639908e2ddc758362aa1e6b7f35a6ad9f71c0d825ddc17056bd3ed079e19)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanDataQualitySpecRulesUniquenessExpectation]:
        return typing.cast(typing.Optional[DataplexDatascanDataQualitySpecRulesUniquenessExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanDataQualitySpecRulesUniquenessExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ff4cf9f9fe5e2387d40e51e7f1aac3f3b985dc5b2583111a77deeb60b231af4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpec",
    jsii_struct_bases=[],
    name_mapping={"trigger": "trigger", "field": "field"},
)
class DataplexDatascanExecutionSpec:
    def __init__(
        self,
        *,
        trigger: typing.Union["DataplexDatascanExecutionSpecTrigger", typing.Dict[builtins.str, typing.Any]],
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#trigger DataplexDatascan#trigger}
        :param field: The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time. If not specified, a data scan will run for all data in the table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field DataplexDatascan#field}
        '''
        if isinstance(trigger, dict):
            trigger = DataplexDatascanExecutionSpecTrigger(**trigger)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec8cc75270233134533a2ebea3761c0c9afbb2d5df361fc03ffa6e43a7424dbd)
            check_type(argname="argument trigger", value=trigger, expected_type=type_hints["trigger"])
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "trigger": trigger,
        }
        if field is not None:
            self._values["field"] = field

    @builtins.property
    def trigger(self) -> "DataplexDatascanExecutionSpecTrigger":
        '''trigger block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#trigger DataplexDatascan#trigger}
        '''
        result = self._values.get("trigger")
        assert result is not None, "Required property 'trigger' is missing"
        return typing.cast("DataplexDatascanExecutionSpecTrigger", result)

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time.

        If not specified, a data scan will run for all data in the table.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#field DataplexDatascan#field}
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanExecutionSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanExecutionSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b46009e0440d7a7f337ba02f1c1aeda149ef4674d2c0c6cba5eb415cd9b33213)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTrigger")
    def put_trigger(
        self,
        *,
        on_demand: typing.Optional[typing.Union["DataplexDatascanExecutionSpecTriggerOnDemand", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["DataplexDatascanExecutionSpecTriggerSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_demand: on_demand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#on_demand DataplexDatascan#on_demand}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#schedule DataplexDatascan#schedule}
        '''
        value = DataplexDatascanExecutionSpecTrigger(
            on_demand=on_demand, schedule=schedule
        )

        return typing.cast(None, jsii.invoke(self, "putTrigger", [value]))

    @jsii.member(jsii_name="resetField")
    def reset_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetField", []))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> "DataplexDatascanExecutionSpecTriggerOutputReference":
        return typing.cast("DataplexDatascanExecutionSpecTriggerOutputReference", jsii.get(self, "trigger"))

    @builtins.property
    @jsii.member(jsii_name="fieldInput")
    def field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerInput")
    def trigger_input(self) -> typing.Optional["DataplexDatascanExecutionSpecTrigger"]:
        return typing.cast(typing.Optional["DataplexDatascanExecutionSpecTrigger"], jsii.get(self, "triggerInput"))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @field.setter
    def field(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e92371b04ff583d035d6fb435a3214c481e4f7b1ae8902310ca5ba4db9bb033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "field", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanExecutionSpec]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanExecutionSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f40fcbea972db179740b8bbc2b444e7b2522f997b90d8da3644ae0cd870bab1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTrigger",
    jsii_struct_bases=[],
    name_mapping={"on_demand": "onDemand", "schedule": "schedule"},
)
class DataplexDatascanExecutionSpecTrigger:
    def __init__(
        self,
        *,
        on_demand: typing.Optional[typing.Union["DataplexDatascanExecutionSpecTriggerOnDemand", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["DataplexDatascanExecutionSpecTriggerSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_demand: on_demand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#on_demand DataplexDatascan#on_demand}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#schedule DataplexDatascan#schedule}
        '''
        if isinstance(on_demand, dict):
            on_demand = DataplexDatascanExecutionSpecTriggerOnDemand(**on_demand)
        if isinstance(schedule, dict):
            schedule = DataplexDatascanExecutionSpecTriggerSchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c326eb32426671157f23411fe7d5d60e206383138a9d0609e6b56135a5c8f47)
            check_type(argname="argument on_demand", value=on_demand, expected_type=type_hints["on_demand"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if on_demand is not None:
            self._values["on_demand"] = on_demand
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def on_demand(
        self,
    ) -> typing.Optional["DataplexDatascanExecutionSpecTriggerOnDemand"]:
        '''on_demand block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#on_demand DataplexDatascan#on_demand}
        '''
        result = self._values.get("on_demand")
        return typing.cast(typing.Optional["DataplexDatascanExecutionSpecTriggerOnDemand"], result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Optional["DataplexDatascanExecutionSpecTriggerSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#schedule DataplexDatascan#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["DataplexDatascanExecutionSpecTriggerSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanExecutionSpecTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTriggerOnDemand",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanExecutionSpecTriggerOnDemand:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanExecutionSpecTriggerOnDemand(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanExecutionSpecTriggerOnDemandOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTriggerOnDemandOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e79b2992d91166f552b247e99d167026617ab696a992286451173260fe7d8474)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ac2dd2832e47bbd25099eab7c46c2998bc0dc3b1ee32223be731361b5edf70f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataplexDatascanExecutionSpecTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af631a52da0b6f9c9527a1b4b147459b15214714a82a7fe79c65d4471218fc3b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOnDemand")
    def put_on_demand(self) -> None:
        value = DataplexDatascanExecutionSpecTriggerOnDemand()

        return typing.cast(None, jsii.invoke(self, "putOnDemand", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(self, *, cron: builtins.str) -> None:
        '''
        :param cron: Cron schedule for running scans periodically. This field is required for Schedule scans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#cron DataplexDatascan#cron}
        '''
        value = DataplexDatascanExecutionSpecTriggerSchedule(cron=cron)

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetOnDemand")
    def reset_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemand", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="onDemand")
    def on_demand(self) -> DataplexDatascanExecutionSpecTriggerOnDemandOutputReference:
        return typing.cast(DataplexDatascanExecutionSpecTriggerOnDemandOutputReference, jsii.get(self, "onDemand"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DataplexDatascanExecutionSpecTriggerScheduleOutputReference":
        return typing.cast("DataplexDatascanExecutionSpecTriggerScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="onDemandInput")
    def on_demand_input(
        self,
    ) -> typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand], jsii.get(self, "onDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional["DataplexDatascanExecutionSpecTriggerSchedule"]:
        return typing.cast(typing.Optional["DataplexDatascanExecutionSpecTriggerSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanExecutionSpecTrigger]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionSpecTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanExecutionSpecTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf68f8ce2d89be025bfa54077b2ff8e615d4e89bb13858f171ab866b8344e0bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTriggerSchedule",
    jsii_struct_bases=[],
    name_mapping={"cron": "cron"},
)
class DataplexDatascanExecutionSpecTriggerSchedule:
    def __init__(self, *, cron: builtins.str) -> None:
        '''
        :param cron: Cron schedule for running scans periodically. This field is required for Schedule scans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#cron DataplexDatascan#cron}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d67af15409251f4fe8b14154bb5d82fdb50d31d9078d511db381dcf238b8fa15)
            check_type(argname="argument cron", value=cron, expected_type=type_hints["cron"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron": cron,
        }

    @builtins.property
    def cron(self) -> builtins.str:
        '''Cron schedule for running scans periodically. This field is required for Schedule scans.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#cron DataplexDatascan#cron}
        '''
        result = self._values.get("cron")
        assert result is not None, "Required property 'cron' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanExecutionSpecTriggerSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanExecutionSpecTriggerScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionSpecTriggerScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76342835417c2ba3b6449ce682bbebb8a2bf2f1e3c01282eb313f49e2063f2b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="cronInput")
    def cron_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronInput"))

    @builtins.property
    @jsii.member(jsii_name="cron")
    def cron(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cron"))

    @cron.setter
    def cron(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0560f70824c04198cb1c6efe514a1edcc969529b4c7285ac0b6408ad207e74ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cron", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataplexDatascanExecutionSpecTriggerSchedule]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionSpecTriggerSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanExecutionSpecTriggerSchedule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db5a250d239b798f9e07fc500c4cff6fdc847eb63081f3fed168948a965eb84d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataplexDatascanExecutionStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanExecutionStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanExecutionStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__18f4fbf3a2ab3da0c905c4e58173fc4aced91b7399146dfe3b5367bbea675f0c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataplexDatascanExecutionStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b85987651862b400eaca66b701c273e12846f41884c31ab1a05b6f8c18b676cb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataplexDatascanExecutionStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf2820c64604b40cc3bede32da2b19364b4e5c3ba5617ad55fb7926fc5c3f67)
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
            type_hints = typing.get_type_hints(_typecheckingstub__61ffac7a646f442a9ab8409e62881bd3b8ea38b79aeb4db8cd3003391e9b37cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ec82fea6381ea48ecc94c1532c1f83b291ec95209592f4f3bcbcf7d128cfca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class DataplexDatascanExecutionStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanExecutionStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__908b95b79615cb54c32444bd58ba85e978ba45d0b741ea925d37c6a1dec91b6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="latestJobEndTime")
    def latest_job_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latestJobEndTime"))

    @builtins.property
    @jsii.member(jsii_name="latestJobStartTime")
    def latest_job_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latestJobStartTime"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataplexDatascanExecutionStatus]:
        return typing.cast(typing.Optional[DataplexDatascanExecutionStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataplexDatascanExecutionStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f44f24f13e6510f286786aee0fb68c01f6252572210f6ee6e372508451dc349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DataplexDatascanTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#create DataplexDatascan#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#delete DataplexDatascan#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#update DataplexDatascan#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9e767d17707360c1f5acec92641a1b9725c17bdddb5bfad21942bfaa7be421)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#create DataplexDatascan#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#delete DataplexDatascan#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/4.82.0/docs/resources/dataplex_datascan#update DataplexDatascan#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataplexDatascanTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataplexDatascanTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.dataplexDatascan.DataplexDatascanTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__27eac39fe10f76a66c07edab1599b9046c39a7d5462689d4ec4f346fa3a2785f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05e92ea2645f7fa6de5fe8cd3bd752a775b1a082f40ef49810a63b50b2bad12a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e692111a9603c4e81b1372ce4c8f4cd634021ee01e658a668b2dd253e5390d10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810f491654b4a796e2f9b5140e9ea1fe070ade83544bd5eea65c50a34babf380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeace9f1ee313460a947488670405a304c37c3925c7e0d8985b31cd695c84412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataplexDatascan",
    "DataplexDatascanConfig",
    "DataplexDatascanData",
    "DataplexDatascanDataOutputReference",
    "DataplexDatascanDataProfileResult",
    "DataplexDatascanDataProfileResultList",
    "DataplexDatascanDataProfileResultOutputReference",
    "DataplexDatascanDataProfileResultProfile",
    "DataplexDatascanDataProfileResultProfileFields",
    "DataplexDatascanDataProfileResultProfileFieldsList",
    "DataplexDatascanDataProfileResultProfileFieldsOutputReference",
    "DataplexDatascanDataProfileResultProfileFieldsProfile",
    "DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile",
    "DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList",
    "DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference",
    "DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile",
    "DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList",
    "DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference",
    "DataplexDatascanDataProfileResultProfileFieldsProfileList",
    "DataplexDatascanDataProfileResultProfileFieldsProfileOutputReference",
    "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile",
    "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList",
    "DataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference",
    "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues",
    "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList",
    "DataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference",
    "DataplexDatascanDataProfileResultProfileList",
    "DataplexDatascanDataProfileResultProfileOutputReference",
    "DataplexDatascanDataProfileResultScannedData",
    "DataplexDatascanDataProfileResultScannedDataIncrementalField",
    "DataplexDatascanDataProfileResultScannedDataIncrementalFieldList",
    "DataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference",
    "DataplexDatascanDataProfileResultScannedDataList",
    "DataplexDatascanDataProfileResultScannedDataOutputReference",
    "DataplexDatascanDataProfileSpec",
    "DataplexDatascanDataProfileSpecExcludeFields",
    "DataplexDatascanDataProfileSpecExcludeFieldsOutputReference",
    "DataplexDatascanDataProfileSpecIncludeFields",
    "DataplexDatascanDataProfileSpecIncludeFieldsOutputReference",
    "DataplexDatascanDataProfileSpecOutputReference",
    "DataplexDatascanDataProfileSpecPostScanActions",
    "DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport",
    "DataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference",
    "DataplexDatascanDataProfileSpecPostScanActionsOutputReference",
    "DataplexDatascanDataQualityResult",
    "DataplexDatascanDataQualityResultDimensions",
    "DataplexDatascanDataQualityResultDimensionsList",
    "DataplexDatascanDataQualityResultDimensionsOutputReference",
    "DataplexDatascanDataQualityResultList",
    "DataplexDatascanDataQualityResultOutputReference",
    "DataplexDatascanDataQualityResultRules",
    "DataplexDatascanDataQualityResultRulesList",
    "DataplexDatascanDataQualityResultRulesOutputReference",
    "DataplexDatascanDataQualityResultRulesRule",
    "DataplexDatascanDataQualityResultRulesRuleList",
    "DataplexDatascanDataQualityResultRulesRuleNonNullExpectation",
    "DataplexDatascanDataQualityResultRulesRuleNonNullExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleRangeExpectation",
    "DataplexDatascanDataQualityResultRulesRuleRangeExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleRegexExpectation",
    "DataplexDatascanDataQualityResultRulesRuleRegexExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation",
    "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleSetExpectation",
    "DataplexDatascanDataQualityResultRulesRuleSetExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation",
    "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation",
    "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference",
    "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation",
    "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList",
    "DataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference",
    "DataplexDatascanDataQualityResultScannedData",
    "DataplexDatascanDataQualityResultScannedDataIncrementalField",
    "DataplexDatascanDataQualityResultScannedDataIncrementalFieldList",
    "DataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference",
    "DataplexDatascanDataQualityResultScannedDataList",
    "DataplexDatascanDataQualityResultScannedDataOutputReference",
    "DataplexDatascanDataQualitySpec",
    "DataplexDatascanDataQualitySpecOutputReference",
    "DataplexDatascanDataQualitySpecPostScanActions",
    "DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport",
    "DataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference",
    "DataplexDatascanDataQualitySpecPostScanActionsOutputReference",
    "DataplexDatascanDataQualitySpecRules",
    "DataplexDatascanDataQualitySpecRulesList",
    "DataplexDatascanDataQualitySpecRulesNonNullExpectation",
    "DataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesOutputReference",
    "DataplexDatascanDataQualitySpecRulesRangeExpectation",
    "DataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesRegexExpectation",
    "DataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesRowConditionExpectation",
    "DataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesSetExpectation",
    "DataplexDatascanDataQualitySpecRulesSetExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation",
    "DataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesTableConditionExpectation",
    "DataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference",
    "DataplexDatascanDataQualitySpecRulesUniquenessExpectation",
    "DataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference",
    "DataplexDatascanExecutionSpec",
    "DataplexDatascanExecutionSpecOutputReference",
    "DataplexDatascanExecutionSpecTrigger",
    "DataplexDatascanExecutionSpecTriggerOnDemand",
    "DataplexDatascanExecutionSpecTriggerOnDemandOutputReference",
    "DataplexDatascanExecutionSpecTriggerOutputReference",
    "DataplexDatascanExecutionSpecTriggerSchedule",
    "DataplexDatascanExecutionSpecTriggerScheduleOutputReference",
    "DataplexDatascanExecutionStatus",
    "DataplexDatascanExecutionStatusList",
    "DataplexDatascanExecutionStatusOutputReference",
    "DataplexDatascanTimeouts",
    "DataplexDatascanTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__f7d978d3a14103b3ef12c1f35fc9a0641f3a0e983ba57bcdb6a7dd8fa7392d37(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    data: typing.Union[DataplexDatascanData, typing.Dict[builtins.str, typing.Any]],
    data_scan_id: builtins.str,
    execution_spec: typing.Union[DataplexDatascanExecutionSpec, typing.Dict[builtins.str, typing.Any]],
    location: builtins.str,
    data_profile_spec: typing.Optional[typing.Union[DataplexDatascanDataProfileSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    data_quality_spec: typing.Optional[typing.Union[DataplexDatascanDataQualitySpec, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[DataplexDatascanTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__9e599fb759e13751ed4e9d77184f41e10d6c3e05dc3490fedfd53a40515ed90d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9177039bf399af0070309fe327788cbf0f4a3ba85ca45b30ca264e3821ebe69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7acddc10756adbd43ebd70f29476a8202acf88a6d91e235c4ceb847ca2e99d1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01402634ddabb6c346b4cb2c18c6624021a009b09431401735ca8c1d779f9d6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53f3d64f33812a62d780f892003e5f8802daa4860abf27562a4a358eb53e212c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8453c5d69cbc241fd463cde478b1c8b4320b9f09468b4be2f475d7f47adcc2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6e3f10a1999fb9aa8f39e401feeeb6b48be2e9b7d28ede14ab07b3a7571f19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59b584f3c2ab4707c1e0552da13804a76b02aef972499ba94c6adac30ad061a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data: typing.Union[DataplexDatascanData, typing.Dict[builtins.str, typing.Any]],
    data_scan_id: builtins.str,
    execution_spec: typing.Union[DataplexDatascanExecutionSpec, typing.Dict[builtins.str, typing.Any]],
    location: builtins.str,
    data_profile_spec: typing.Optional[typing.Union[DataplexDatascanDataProfileSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    data_quality_spec: typing.Optional[typing.Union[DataplexDatascanDataQualitySpec, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[DataplexDatascanTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__887b51eb9dc74c5797b8b0d833c1f65c3c1c65e4e91004ea510fa663bde76d5d(
    *,
    entity: typing.Optional[builtins.str] = None,
    resource: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d07a3087d95dce1b616a931956230cfd53d601f3db40f9da601a820db8924c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe8b1ee53c0d22ea8df64f3ec598e967dc156a10fed885a0f729cf7f651bdf06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d02c9fc495878cbebd90c932cc5aeefd43e50d9834c4799b71ac8a184cf05d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ecfe3da18a82a79c7d4e90e51f374b6340929ff8062d6c77258151ec9f7f51a(
    value: typing.Optional[DataplexDatascanData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26e3b467f2021fee7dc89df85d9ebd3d2cc78b2b9a16e9faaf5c0051676da26f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11b66833ff2b741c4b38df472871d50f6858c4c6b79255c71984e64322084788(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd6b514f7e3038389e0aee09831826d21dae1bb1db6cd33f5f26b1bb396c6ea5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__294fc7cbddb7d0a25b27aea945ac93d09e4e7a2bdb3a046c61ee39848b3bb896(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f65afb01bd5b7e7ddbe4d37302570c794df2863c8f28bb612e0e7b99b6cf10(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab66f1aef82de267bcd627a387b959c2eeb79fc0a4b86f3d12de27b52982516d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ab023f9059ca1892bb3b658f598c8e7b9d5ddfe138dc05d5463ecb0266a548(
    value: typing.Optional[DataplexDatascanDataProfileResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcc4f366f45ccc6fe4f290f954a95463f92dbd07bd32738b49eb84d640508c73(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03fc2178c7d0c30bb7bfd393de7c0e369248abc051259aa59b0a3c4c87f74516(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16143a38095dcf738a64171689439bf083a0c8f859a3351bd539ac7b3633ef6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab00cdf8ed11fdd127e6d632601b0fd9a07530645a95f0753fbcdf51fbd9b315(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc203b49df205d28079ed27f941ce94fe453faa8ce6badb0414d75ae594c2b30(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ac0332ba8735d3523ca65364903869fa85f8f7c58c96b28fb253363b55750fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85deac29e3b65d23fbb71c0d128cb0c3d25b6b6976d9414a18f382fe61e9ccf0(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8451bc250e4b108a20df2761cb59ecf4ef44ea3d0c8c441cd478f647e79b8d8d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff2a6762171eff0c19dfd025fc5c0db2e6e5ed484a1bde170dfa9f0d2a2025be(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a36520d7bada342b889fa3b068cf207b8b65ed8b4f82bbdfa67d6617f411eade(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0315497d98badbfdb477efddbcac334a796b5188df782e47cd026331a107c133(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05dc95c6faf2f069bea254710bf7a7bb35788786add0bc7fa073d83034b25f25(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06ff2a037d28853297eaba92971eae32fc90fa0bcbde1a2b95a1825b1e50bf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b186f05c66247c291e761ad2b3f4a4db13f4b1b6fc084f29ec91fbf856dd257d(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9af998b752df2b55f42530bdb3e02f8f810589f8f5e5d80bf88b288e9790b20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__909dcd897e286a866786e636f8cb00d17a1ae6e8bbfb0d9ae86073b18e399c6a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6b6a412a727483b5b86e5d260290157c49c97cd078de7841d9cf5e5f38e2ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60528c619946ec926cf1eba80b8d209cb6013d57b8d6b858a307ee3c62524da3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b714e846c51b1bd6e0320e70a83c75deb2e770749bd61ac91cd570b05a6aeb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3381b2cb69697ea9fd8e31203126bcffa81142ac55f8a6ffcebe90ae7721def1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a4790a25281b7e5f0f05b86eb6d2caec78f3c7b22bf4f297fded4844ea24c60(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26cc362fc01d8faaea1b1e831696ead7a9ad938e1f2c115f410e73036068560d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a98aec9ef8a20222be8978702faf9ff2e560ebc615e27c19e1ec3e7adf926d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__319eadda73579ff24698cec9f3ea800dc9a5b05f11d3c9ffb670a9af410e9d47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2a98c4321c3a023fdd77a79232f982b524938ddcd8a76bff66fa0e24d8f5d5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07690f3cf1dc64b46656654f995a1f24ab297968ff6ffd88166f21f68dc773be(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdabff3fd1ca871d6fdd97cc8e569d6ac4236850a5553441c87d0952031428d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db62f7bc153eb7339abcf49174ed471cf547ed733c84e9b25f56a0a28ad216f1(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e451a3060baa7114248de3eb0dd4bf8adebb2db2bddfe6c82323d425841ed39e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d760806f0b263138ba974c3eaae8a0e81fba84e9839cf2f7b01c8acbb559a91(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2049d9d2d08f5deb3700cf0b1eefe0a41f67524cf9bb169d270cbcbe5289a320(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90d9172a88e215dcf989750a688a9d7c8fd6bbebc14c51174adb6112669ce24d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e09ddf63d755ef729e9a6b66b2e95cce1fc4619d35bf712fa5c27762afd190f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9004ffe8f8e5214d437786516a133324638c109b7477b0aa261f9e3fcdab8a06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__804a47584025c53ef32ecd48430766480de042a0c5db2fc147b90cfe6d7a8d88(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileStringProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0d076b5e20d79b2c7cc962315cfe1f7ae800ab623f775749929004657f181a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e3ad39bc38afcf3c066e80edcbd01d8e6a96e108a91c7822b5b5405ebf8b96f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4439870f4f3e7c5c78ac35c7b22e37ba6a67d9bace9c1c27db01dbe52ca70138(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c2e71285afb6ee7e30f40d08f9b1020cc2a849616224370f889e11cc3a4015f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3487abbd458f47242f52a1fa40a9f6f0957623377f472bdaafbdeca3753c26(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a934767e18436ae480737fd6a0e9ff125e7a44653e7342348abf56054219788(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54815abd1472b134d809a5539f930e64285a627e7f475fb50f689c7d47e5ad16(
    value: typing.Optional[DataplexDatascanDataProfileResultProfileFieldsProfileTopNValues],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae22c78457c9f71bea6bef180e69389fe5465adc29eaf035c92cc1f10ab99f01(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a6d481c057dec1a88f5ca98d157c2002688c7020e255a31d9f4fa282ed5ec24(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e16970047a048fbad424620742740d97a4b032cb3c7cf0416840ef15862a9f46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da392bd693c1ff368d4c2c401fbc681f23b941d74663c5122bf99640704afe62(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09aa6bd668f2187b36f45402be4531433f67406f4d7914ad6ea4b5cbf726a83c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ee4e16381ea029a83469f1f69c20bbed658d369833568afc7dd09e2b7b2b99(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c015d769d468ac0a2d9002bb945ad8cc9c43f218cba2a116f8dc92e0524be0(
    value: typing.Optional[DataplexDatascanDataProfileResultProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__943b7ee7d2d635b4f91de7057d50b0218efeba8f47b80e356b92e788a93e64d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__941b8302c431e4b7f8467e1ac422009ee700621bcb862abd0887cecec01c0f89(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3039a012dd1f9d30f88ef39a706a1b666f49cc865435efa16b6d70a51bae0cae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5029a4185d9e5499a5bdb167a7d5ec59bf760ab26e21145e0022faeb0371412a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd21901eb268e122ae4877d6787006765603bca31e8da2c91254fa88a7a5c803(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c150c86abe5dff6871da611509e2517b7b3ea0b89a0b3c8695e74a0b81931ebb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fdab52235dceef7b9d099e69ee2119cbd8ec0e0250a9c69bf02205038ec0569(
    value: typing.Optional[DataplexDatascanDataProfileResultScannedDataIncrementalField],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13766f2e8ad40df9f06a8579749639af102623e65accc2ad6752a04b98dd1878(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e154cbde9e01cdbf2008feb5761f9f5ac0475c025db197fbc4d435cefb9aff(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c0965cb262695dba1ed8e8502d7fbfbf0044bb6a2a17d9a48a8bc00754b54e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a887dcd44f19b3521a52d8a7086c20076b133912c3dab668a1edb2310603d9bd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2122d4bf4c057a5860e10ec10903be645f9d002f2d938735c2f346190626dc63(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49da29bfc89ccad3a11e9127a1ec5cdda5183425e9b2a400c4c716cf259cdeb4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453eb12bfec1c69a72452f33873946a8034ce29d226fe5c2e1fa7e134cee41b4(
    value: typing.Optional[DataplexDatascanDataProfileResultScannedData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97359cc1586f9deb4de9c7e12f4682dac9e7dd4d4fca628be49da0ff075b12f8(
    *,
    exclude_fields: typing.Optional[typing.Union[DataplexDatascanDataProfileSpecExcludeFields, typing.Dict[builtins.str, typing.Any]]] = None,
    include_fields: typing.Optional[typing.Union[DataplexDatascanDataProfileSpecIncludeFields, typing.Dict[builtins.str, typing.Any]]] = None,
    post_scan_actions: typing.Optional[typing.Union[DataplexDatascanDataProfileSpecPostScanActions, typing.Dict[builtins.str, typing.Any]]] = None,
    row_filter: typing.Optional[builtins.str] = None,
    sampling_percent: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__317b91e781a70d6fad6013a374886068dda8ff121929bec9c8d0657b1c3d5c9d(
    *,
    field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab82f93c5b430d1788ef410438ff3eab940d106ffbb978fe7152cc4d80febe4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bdcac021b9965491bda49fa6b9d1406131d6d600cb12123b8c19c44c5395a09(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__514fe3bbc8323bba64096b62898c41318dc3be0ce5781178f037e79d6403a6cc(
    value: typing.Optional[DataplexDatascanDataProfileSpecExcludeFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12cc9d674cdfa8f3c1724cafe1f5a3fb480acc9c68cd6b5ddd424cfed9fa399f(
    *,
    field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31d1fb585271177c44c468dd93dcad4ad5389daaec077cbe2bbb1992aaa20e28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90af2e7104018dd67faba658bf81aa1f23ddf543605d7aae58e7263e7ce1311a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c4137798a894c7cadf23b6e98b2ce6982be340029ba4d8aac394476d64d9cc3(
    value: typing.Optional[DataplexDatascanDataProfileSpecIncludeFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__249c1b17060819390364350da4fc04f801484cad1eea5c334ddd06a25e947453(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7258d6e996ed8fc69dfd98fa4ea5915f2f62b8f0221713857a361f4c50a1f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3d642e4e66f780a58eed116cc3f089bd8e13713e1e836c1f427d6ea4b8edd6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ebfe7dbf82ace6f2dc587fc4a14e5eef3cdbe8a0d7af1cf282b0ec0e78fdba(
    value: typing.Optional[DataplexDatascanDataProfileSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca2420faf9c7d516a166319fa522692d6f12166431d6e6c3d20dc893e930b081(
    *,
    bigquery_export: typing.Optional[typing.Union[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ff25a7f34bc05f1c2964df3baba773c1bd7f5fd73c27abde8ff1d63ca483a1(
    *,
    results_table: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f2d719ea688fb37587f352bdc503c8570b92b2b73b01633d9c4fb5bd1238ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0523fdb60e6c58d72823452f982496b52d9bd851de801ee582959968a2ccb189(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1376163de2a44cd1f2ea700e708602a69aabb542d6697dd07af9f3842980d19f(
    value: typing.Optional[DataplexDatascanDataProfileSpecPostScanActionsBigqueryExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7e37c13b20d42c56e72f6294c14dd314bb931cf25dd59bfa022a8a963d77ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d8b9c26ad5ee444d69a6d0d5affdaa135f0cd75916453d317c13c29d7e23a7(
    value: typing.Optional[DataplexDatascanDataProfileSpecPostScanActions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3648bcd762471381f5e70730afd27c0a926c836f5ff09691fe58f75fcf646da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60a57beb6473505dbe3733831ded5a43f2626704c3b048de03946b799d6b217(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b39855c020ed5694a2ab5df8235c0395374f565ec6590f56e80979c05f3b7ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d2726d9b6a8f95d7a30035674e496b98424a0507a35aa38dad70b111782461(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bba5d100b401a54f18cec614cde46090335216a28cb7d0d621220f323caf0ab2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cabaf5a38d9a7cc909bb84d5f5cf89a8b646912f5404856dbaeea0e0b3cc946b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234058f62278a0913f884c4a472cdbcd57cc59111129772d3dba1d9b13fcf264(
    value: typing.Optional[DataplexDatascanDataQualityResultDimensions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3565fe2fb2c5dcae7399bbe70244ea77c9efc31ec47e9aad8405c28112c30ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a09a4a054942e93cac2a53397faad9459ec5f9f8ffdf0de9d44bf84cc03aa1a0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8820ac958e1ab897e78cf3276d98b060603f593ac5fb0b35f3a1f4089ed1ac8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__952b3c7c61b1da7b002fb6c0ff13f144721fc9dd8dc661cdf5a12b60e4f3dce4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82cd69ee1e3db666b70a48bbeb621c4b5d349d8b3a4fb684b470998b2be701e1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f590ff226f1de3af11df5056d3e7b4af46d88bd69c9b33a12d6621b309c27c58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd68929bbcbb0b3c0e4d5d81ebbfe513d341620c7e8aadb28c7928ead5b6749(
    value: typing.Optional[DataplexDatascanDataQualityResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32987e5d61a6d3c161ca05aab09712f68342d177db76853cf14a9b3b06e4f252(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec1a89757d530e15349a3ccb04ac4028bb48c51fe08e57c4aa46deb1aa457a56(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975de62a685a91966d5ee68b4c1e9ac823500e516bc6ab517ffe9b751c3a2eea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a63a3d1a5ffc165daac856a7b7456e588c91eb94f80ca30e2dca943349bd1a33(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__145fa5f88338e38557cd2b13a5614d24fdd02a1481d650b2bae588aa45803cee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9558c55f6ecda8d41e0df9f7677bece453992c86913b42d3f65350ea42eb2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7ed51a7d035ba32511413c1104a2e352af487de594749ce135ce394489dccaf(
    value: typing.Optional[DataplexDatascanDataQualityResultRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8a455bbbc9aab7c18b509f54eeade8df96769cfe47f96b9f494dbae7ec496d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d108b4c34535cc38c204083f2364edd400f6b1eccf6c67a5ba00e49f7158a0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06bd86bda327e30d4e9da8b8a0f21e366f18c67cba52b6e7de2b4e72b7e097c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197923fb8b46e010f8f607213663a776dbf7ceba36e430938dcaf71e84b1ec08(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c825fdb39bc375f188ac878b30899bc3c1299c5d7057d7408af855c402228d8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a3cdfbd501453b0970d47e4929c905903932c09215dfb88b448389aa85662b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1813fd171630b4a91eba7d11a2ee80383d7a1b7e20865eb2e6cf9ab1ab40fa19(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c298dc11c5e2ac9c5988fdab1a3f4561ae36a7ea34f956aa650f63432da14759(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00115d3558bd350d768dc166d2dd3fe31a2eadc8eaaf2f1dfbf58b482971fbda(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df677cdb19263e177199697bb9e8cc761f7d5f07980728f21d0a14cc4fddab1c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5c9758c576ec6b6e95d4f304552eb58f51de5f24879bee25f6a99419a2303e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d275db3494d1427adce59217816e8947628162217909da68aa68a618fc489f56(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleNonNullExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a546eaf3912ff49dc10fb8f5eb8618a734508ee607365468a60ab1ed925afdd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c30f90156f88d28965d3dcf00ffb37c7482eecdaa279d5db6f8b69554aa0bd7(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__240f6596fd209f7ba298a98e7550395516d3d72ad7c658758e258559f9fee85e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd850b0f343ea7ba8ae3f9c151ed98ecb7710dd40554370f0183f963fd1819e2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e598b864387f4e786da8ada19e0024d01ba1a14c13a6f527a452fc0035df966(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cee20d005c58fae9a1ce198d085b92306b9fac237a2fb2a98d55b77c10b6b5e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d8d252f367bf74eee1b29925e773fd128bc5868adf1abef243d0e9695e2c7d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ff7cb2ce44359378bf982b4b4c8b651f454b262ceeab63348ad4dedec6cfe0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655d29cef738da6197f0d81d3377276467746d29533e6cbb4a846bdb8d823eb0(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41982a269b038131c62ce5917319059652b30c798cef4ddd2d782fecc7509b41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f7ad04cff632b5c6e0bb343a6bacf1473423fb1fabd2811a7e33fe9f7fa3ae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97fb11268868b7e1c45fe1bc0e268c31fbb529f76cd9b7cb78871b416ab6c76d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc25dd5bbb9c15c89c3f059fe87339952dd0317162b73e191063aceecc6af358(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db788582109e7572431ac78d4042da7c834830fdec49f475db2fe1d5e78c53ca(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0076a18d5d45af397eb85a13c6fdf34f76191a4e8e70f060ecd67081629cca7a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fba36a282b784024139165bad9014418c538622d6425f91de4c2d3ecfab9f600(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRegexExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1237b709b5c917e9f24ef57985c270922c02649a81b68f88ffef54ed08eafc1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d95325c29eff370c108e390b2be4ccb2ccfd1f869260fb9807a06cc23fd85f0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c352b6a079a8fbcbf6a3a6479ef6ecf668693587281e3b80f0738f24325807a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d34e27bbfde9f3ab05a010676fb850f7467c77e10aa32670f1bb0b307b573b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9feb01ff8a4c50663ebe7563baab28785fc2924e0cef974f52a021b4bd4eb259(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf8b54dc01e1e083b8d92fcea63ac0dcb7731cbb90a98703e742a5bee9fa2185(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19aea8cadc2535952b016f4441f0dc7cdeba4778e44f2799ba02e90eec903c21(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleRowConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9824ca4923cfc4d83293da96f4c516bba8465e2c4678d50555a658be4ecf610(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9acbd71d542c349dbe98fd5367e14e773e9bdb23eb23afdd71c2a2b2c1f559f2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0618e969b8bfc83e0ac10288e52deaaa887635ddb55f16ac7135d5c4d9b907e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da253ba56f80c07b44d8cf75d4cb60121879f9cffcd72611c768afe4a8b6784a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a66b9ffdc99af020e043a08be04a1541b660c7be1cebee6faeeb22f4388c349e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b70e26fd8b7210ca4fcac97a99c256b27a2584392085d92ed1d0757960718b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3a8fc7c9867b98c991b032b7a6bdf88a023ebbab47ebd044286a57cc2d0773(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleSetExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0335de06e47b1defd41015b351ebcaf8f6e5963a955e5d903640211dd32eb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60a0a50ba008a98bd50f888939afd47323fc199e13f1f5b810b189371a603ae0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__325876c2483fe766764cc4ce1f879ff5e113d0bea53f4268518ee0df79f7b064(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89350774af7188cece13628b265ad75de4b72e17b3395091fee5266c1253278f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb9d97605cfe3b34225960a6707c8e937c8b460add99a9c359c24e7b8ce674f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1887d44fd8c07fdd7418b0c208d1ccd15be0ee0408e096f9efe2da853a3562bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13da13b4c3892019cd5f48c4685cfc58c41256e2d60555a9903b17752bf9819(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20de8463467128c676b5d44aa2f6bf348fd638684c9e7db2bbc0b8be812483a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6faba148cbe9fcbe6692e4f822158ad6dce3db7cb0f09b422b8f10c1e1cec8a0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5f05364dd99105fa923e5d6e5733c79ab320a8cff766a6307616338d1f74b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d964d6d27fa903e6e32ac306b97cbf7019f989c87c48b647fd819f5909408064(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__406eee650309c3700f4c953abd4c8a33262bbd2774a4554af8f875a542fb867e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea8d8c49d9cd32ea9ef8b919878211085d363523ca70fe7b844bef760fae4e3f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e47ab065c1ec6ea8d24b670e278e5c4112aa8150cc2ca0b0619aa513dd5c6584(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleTableConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a3b301bd2eb54ebb3f9651ff1d48a9236bb74b8ab936e6611bc945e9a8acc7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1497e44c0ab368bdd04e2e9b64cb5865e35f083ea63d3f515948061ff0a3f1f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e47cbcc488e2669da45222a341d8c6446e6484f72b47a003ccbe6b47fdae5267(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa89997a9afacd7344ca26b56461b80348f7fcb71baae0f205bc3cf79d14a84c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2715f92e57f236bda10f81a08ab8d85c183692fe0b600cc6faebfa0b957a5a19(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d74bd1c849491f1a71f3f235b72d8594b6fa0ab9d253bde406f0cf7bdc7a02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26ee377389501e9baf5023ac7aad712f718bf166b4bda62c3cc32714490e4e71(
    value: typing.Optional[DataplexDatascanDataQualityResultRulesRuleUniquenessExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f04e7422613d021a194e0bab8e5a508cb1b7e7029d0f63b67fbf3437ea9d220f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5a54543a79e75ee3cf77e3afb18fd06943fac88d62493222d5d2a4974b616d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ce6a953f962aa641e8bf6be480924444a73ae9c2ec14c7defa6b5246e4b203(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18cb720eafe0e4804895481cdf0cc48556afc1639b490407c17eece084b34a2f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8310b6201b81a1192ebd58ee63bc4c4b1fa741d59a0075fbca2216c00e8274f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__033733554bd4a4392adc538fec8aaa932bddf61370576f4aa6a342e05e3a48fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68fd44bd93701a142f6aa1696709f0fccc70e7e6658a5316ff3e7b68ac88006(
    value: typing.Optional[DataplexDatascanDataQualityResultScannedDataIncrementalField],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae65118a1f0de7cd0fa2e449a003e889ea3a17a35650fd8c2b373be8618b076(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e8418de531ce55580b734d4989b3ba4069530a4c25aada55acdbe3944b7176(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__288f0cc97b1630a9db667bace84e84a48e5580e28e599f523b8305de8be605f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea8ce19c3e0847f7bd9fcbf9a3615357f8dcab4eb24094b7969ff04c6ae4bdd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce9f35d1da4851e4a36982d3a300172ae61300bc4d350865ef08808af63f7b91(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c47a9caa7a824f18710b78481f502f3ceb822ad9614f5ed4e78bfd64f456cba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31929e026c6161221554d1b707170d6893081a113a42eab54c81049964d2c069(
    value: typing.Optional[DataplexDatascanDataQualityResultScannedData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85c98a56040ac5f9e591bba4e1a4fa0a58d92446f6282e22ad7ef9e5ead6bb80(
    *,
    post_scan_actions: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecPostScanActions, typing.Dict[builtins.str, typing.Any]]] = None,
    row_filter: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataplexDatascanDataQualitySpecRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    sampling_percent: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71887d414bfebf19c33160aca3d7a99a4057fb053019e41bade2100377d75079(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97e4645c0fdd4af9c8d94abd52201f612cfbfa74e577e76ff4fbf50d84f02469(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataplexDatascanDataQualitySpecRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e684f7a223bd3b8697103319d545d5f73bca5ac008fad80de4cc4771349e5a07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99d588c57dd79bf1e283d4a386394ec6a940747baec8dcf253f1b84e309d0f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97c50c625b58b82848acec8bc31b41279f7450881cce359286c40783633e1958(
    value: typing.Optional[DataplexDatascanDataQualitySpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88d4c425f3b0ef2a8bf372e542b1b79e03c2b5dd24990a7772494847d9bb38ad(
    *,
    bigquery_export: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1e32e88c2d9c7cd520d7abd11db51ab1b32ff1f7b952820017f0d4daff9d350(
    *,
    results_table: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41229a1a441415a484969f33dada1770a0fb2d61e0725348faa5589b289e36d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e7ae2abb3d11a2028b835c1fd6c58b13d7fcf533f62a55063d175fe4722b97d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f739184964e852d91eadef2fc4f35a73e0469d3c5f34f023cf0479e34316711(
    value: typing.Optional[DataplexDatascanDataQualitySpecPostScanActionsBigqueryExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ec4d4f2bc1503a9faf7d8be3e8d256c28eef9a3c72260b1f154ace0564aa77(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdb7c645be6acadab8d8cfd96c2cc485f3a057bf8c6fcae2bee9feb29607ccce(
    value: typing.Optional[DataplexDatascanDataQualitySpecPostScanActions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f31a3525e6b316fa85e52d9d95f27722bbbbeb6ecb5187454efa713bd2be01eb(
    *,
    dimension: builtins.str,
    column: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    ignore_null: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    non_null_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesNonNullExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    range_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesRangeExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    regex_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesRegexExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    row_condition_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesRowConditionExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    set_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesSetExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    statistic_range_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    table_condition_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesTableConditionExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    threshold: typing.Optional[jsii.Number] = None,
    uniqueness_expectation: typing.Optional[typing.Union[DataplexDatascanDataQualitySpecRulesUniquenessExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f6a501cf2ff5783ab6573f714638d827de167ccba2b5a70a7696032f776bf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1fcc45b0ed7e1e1cf1e37f592761f449a845a73c3ca5e397749e06fe0aa555a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff8668d815b6c8ee4e1a2eaa2532af3505c6ff1a1857d15702c367a61a0b0b62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__361e868f5fc2b28e7c42881dd07181155e351e9bf12e51f0e215207c6bbcfea2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f68d0f72f90e3e57736ddaa92ef1236e4788eb56b811ff69ff2eb95a5290559(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c64df4d8637ff6193481df214baf857507ab29651b730b860fd8631e35a1dca8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataplexDatascanDataQualitySpecRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3dfbe05de944fd068a47b5529354f9f73b3a6347629dd8c6b8e169870c5505f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8849d3bf809a221ce924ebb2c0f1c6a505fa0923bbfe7c73c078b94d769a3148(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesNonNullExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760ebc6a3289ef3333f8fbe92ff7f03a37bae78f9b3d33d7b73cc72482919682(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52047181638f5644a574c14b17beb5bcbd317c865a247170353629e24253f4db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb23ab7d88a75e61957d4e61cb08f4a0b45265454a5c7ea30046bf8ae768712(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa3219e0e4a1b50219d834a5a5c8c86b7f2e3bf5d1b7729947b7f2f43cc78cbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc0451e96f8f545004f44b04e92b7597de8201970d6739ba14f933614cc2034f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08cfc1422780d9cbd9366c99bc1217235ed3e6d081f7d2d9f1017a784dd8856a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6a5aa8d2de5e9e8af1810fecb00dff022dd56eb7064e652447ac2c9bc15697a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25ec6ab48b9f4324e4e1d654a33d91db63d358c80c0187abe2e74cc03952493d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanDataQualitySpecRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6bc64dcf4f7f09f45fe73068b2c630074f63d470317245ba2a680d12c56c1d(
    *,
    max_value: typing.Optional[builtins.str] = None,
    min_value: typing.Optional[builtins.str] = None,
    strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__759703238b5b0d1a3835089c0c71204d63a6a31f39c97f57b9ced2d8536fcec5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d3a9026c0215202dca02914dbdaa9cf1d2792ce6001755eb136f5a85b737005(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12abae15248ea3615e37306659e5bf80f36d56a94fb5f11a4e5f9865a2e4fbe8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a607fdaebb39b605219715663624e6bb2c3d5633dfd296aa771d67393d120d26(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e94da435a3316245418a11abcd0fbaa1ee9ae6201fcb4e8e3876ecacb7bcd8b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b8c6819f966ceef61ffa34b5a8788e0b0d240d62390c25fb4062afd194442e1(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d572b0255331e03ccc7577a2e8133353b531f411231808b1ded5ae16b165b4(
    *,
    regex: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__313b8a8891714003d03503677cfc9b8524bd53fb35f1155a99087a85f8efc796(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cea7c94bcdcae17875c5316055b54fa0200d0acf73f6a57c123789689f8d3b15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__475a09c26a9b7d34550a970d0233670a5fa5e0e0a026dc50558962b1e466798c(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesRegexExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94ad4aba19ee0e8a72b9600566e5aaab50eea58d6fee6f1451b2210ceb858889(
    *,
    sql_expression: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3585d17a97171b4d2226f21863be39b6882b7880be852b3f36abced064cf6885(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a45d7af9028a72e0eff6f708fd474122a85a1bdf0b78cfe2b3594c326683ac34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__425e669bfd65f764df50ea8c0778b1c2b453198f2008d3836d8a38bdcde536cd(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesRowConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c87bedf5b64085ec94bb7706f878c3c3db008d4c783a265f2009ba8315299b5(
    *,
    values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c453804a5e391cf62b798b805cb0df27c2e26acbcc062035dfd93abe6627de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8a2f911fa1c82f4b1c82be1cfd5e1d6013c3e1f95a73ba511aa8cf3756dc060(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2d8295163aa80ea21d497e6a6bfd05b2c03c9fa074f40dbbc0de90a8cdc1c7(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesSetExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b0a5aa73adb2ee9583a2361bd732522f3b3dc6d97169e30893463bb70d70b15(
    *,
    statistic: builtins.str,
    max_value: typing.Optional[builtins.str] = None,
    min_value: typing.Optional[builtins.str] = None,
    strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975d32301b3563a6ee53e9ea35860ae76ed71a942de71dfa2f6539a64db59acf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf1b9df4f4acbe6c8c40f4e9a180a2ab96e1f5fcec945af5072b185516903aee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd93fc38c3669a133ebb7fe4b55bc4c608e5c09ea6d4a01fab510b4abe81a5d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ba00dbd43a80b645f71245295ea4290c2b02aaee0c8cee01a0f43db50082b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d8d81305355619bc8c44b1303a525b01949934c01a2dc69651734abefe3832(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797c434697eb4e4d61ac5116af34212ab463c6c087edf28e28e77db13e64ef3f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__929fa9c246994fdaef6c453521d03b51cef32b3868bf3fbfdafe7e012a19ac75(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesStatisticRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46ef359ae5fae4724bfb144183e476594f79a5dae9d5269f2e5521757e32582a(
    *,
    sql_expression: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08943a8e396992a3a68166c3b89eec5abd11c659b0b2c0f9a27306d8e06d7045(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebfd3f38bb494bd76daa96d507b86916e2a785b837cbe1a229f9429e91a57c4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e31bc4a5a6ae2fb8b6909bf2677b8a9dbbe5dfc9d72e326032091ffba8c647(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesTableConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1806639908e2ddc758362aa1e6b7f35a6ad9f71c0d825ddc17056bd3ed079e19(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ff4cf9f9fe5e2387d40e51e7f1aac3f3b985dc5b2583111a77deeb60b231af4(
    value: typing.Optional[DataplexDatascanDataQualitySpecRulesUniquenessExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec8cc75270233134533a2ebea3761c0c9afbb2d5df361fc03ffa6e43a7424dbd(
    *,
    trigger: typing.Union[DataplexDatascanExecutionSpecTrigger, typing.Dict[builtins.str, typing.Any]],
    field: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46009e0440d7a7f337ba02f1c1aeda149ef4674d2c0c6cba5eb415cd9b33213(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e92371b04ff583d035d6fb435a3214c481e4f7b1ae8902310ca5ba4db9bb033(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40fcbea972db179740b8bbc2b444e7b2522f997b90d8da3644ae0cd870bab1e(
    value: typing.Optional[DataplexDatascanExecutionSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c326eb32426671157f23411fe7d5d60e206383138a9d0609e6b56135a5c8f47(
    *,
    on_demand: typing.Optional[typing.Union[DataplexDatascanExecutionSpecTriggerOnDemand, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[DataplexDatascanExecutionSpecTriggerSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e79b2992d91166f552b247e99d167026617ab696a992286451173260fe7d8474(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ac2dd2832e47bbd25099eab7c46c2998bc0dc3b1ee32223be731361b5edf70f(
    value: typing.Optional[DataplexDatascanExecutionSpecTriggerOnDemand],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af631a52da0b6f9c9527a1b4b147459b15214714a82a7fe79c65d4471218fc3b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf68f8ce2d89be025bfa54077b2ff8e615d4e89bb13858f171ab866b8344e0bc(
    value: typing.Optional[DataplexDatascanExecutionSpecTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d67af15409251f4fe8b14154bb5d82fdb50d31d9078d511db381dcf238b8fa15(
    *,
    cron: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76342835417c2ba3b6449ce682bbebb8a2bf2f1e3c01282eb313f49e2063f2b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0560f70824c04198cb1c6efe514a1edcc969529b4c7285ac0b6408ad207e74ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db5a250d239b798f9e07fc500c4cff6fdc847eb63081f3fed168948a965eb84d(
    value: typing.Optional[DataplexDatascanExecutionSpecTriggerSchedule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18f4fbf3a2ab3da0c905c4e58173fc4aced91b7399146dfe3b5367bbea675f0c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b85987651862b400eaca66b701c273e12846f41884c31ab1a05b6f8c18b676cb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf2820c64604b40cc3bede32da2b19364b4e5c3ba5617ad55fb7926fc5c3f67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ffac7a646f442a9ab8409e62881bd3b8ea38b79aeb4db8cd3003391e9b37cd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ec82fea6381ea48ecc94c1532c1f83b291ec95209592f4f3bcbcf7d128cfca4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__908b95b79615cb54c32444bd58ba85e978ba45d0b741ea925d37c6a1dec91b6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f44f24f13e6510f286786aee0fb68c01f6252572210f6ee6e372508451dc349(
    value: typing.Optional[DataplexDatascanExecutionStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9e767d17707360c1f5acec92641a1b9725c17bdddb5bfad21942bfaa7be421(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27eac39fe10f76a66c07edab1599b9046c39a7d5462689d4ec4f346fa3a2785f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e92ea2645f7fa6de5fe8cd3bd752a775b1a082f40ef49810a63b50b2bad12a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e692111a9603c4e81b1372ce4c8f4cd634021ee01e658a668b2dd253e5390d10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810f491654b4a796e2f9b5140e9ea1fe070ade83544bd5eea65c50a34babf380(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeace9f1ee313460a947488670405a304c37c3925c7e0d8985b31cd695c84412(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataplexDatascanTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
