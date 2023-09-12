'''
# `google_dataplex_datascan`

Refer to the Terraform Registory for docs: [`google_dataplex_datascan`](https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan).
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


class GoogleDataplexDatascan(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascan",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan google_dataplex_datascan}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        data: typing.Union["GoogleDataplexDatascanData", typing.Dict[builtins.str, typing.Any]],
        data_scan_id: builtins.str,
        execution_spec: typing.Union["GoogleDataplexDatascanExecutionSpec", typing.Dict[builtins.str, typing.Any]],
        location: builtins.str,
        data_profile_spec: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        data_quality_spec: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpec", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDataplexDatascanTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan google_dataplex_datascan} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: data block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data GoogleDataplexDatascan#data}
        :param data_scan_id: DataScan identifier. Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_scan_id GoogleDataplexDatascan#data_scan_id}
        :param execution_spec: execution_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#execution_spec GoogleDataplexDatascan#execution_spec}
        :param location: The location where the data scan should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#location GoogleDataplexDatascan#location}
        :param data_profile_spec: data_profile_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_profile_spec GoogleDataplexDatascan#data_profile_spec}
        :param data_quality_spec: data_quality_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_quality_spec GoogleDataplexDatascan#data_quality_spec}
        :param description: Description of the scan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#description GoogleDataplexDatascan#description}
        :param display_name: User friendly display name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#display_name GoogleDataplexDatascan#display_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#id GoogleDataplexDatascan#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User-defined labels for the scan. A list of key->value pairs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#labels GoogleDataplexDatascan#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#project GoogleDataplexDatascan#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#timeouts GoogleDataplexDatascan#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b75755b3c8adc167bae1e1f8a24d7bb2c1b6243910517d6f741f2aee0ba268b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleDataplexDatascanConfig(
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
        :param entity: The Dataplex entity that represents the data source(e.g. BigQuery table) for Datascan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#entity GoogleDataplexDatascan#entity}
        :param resource: The service-qualified full resource name of the cloud resource for a DataScan job to scan against. The field could be: (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#resource GoogleDataplexDatascan#resource}
        '''
        value = GoogleDataplexDatascanData(entity=entity, resource=resource)

        return typing.cast(None, jsii.invoke(self, "putData", [value]))

    @jsii.member(jsii_name="putDataProfileSpec")
    def put_data_profile_spec(
        self,
        *,
        exclude_fields: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecExcludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        include_fields: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecIncludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        post_scan_actions: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_fields: exclude_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#exclude_fields GoogleDataplexDatascan#exclude_fields}
        :param include_fields: include_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#include_fields GoogleDataplexDatascan#include_fields}
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        value = GoogleDataplexDatascanDataProfileSpec(
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
        post_scan_actions: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#rules GoogleDataplexDatascan#rules}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        value = GoogleDataplexDatascanDataQualitySpec(
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
        trigger: typing.Union["GoogleDataplexDatascanExecutionSpecTrigger", typing.Dict[builtins.str, typing.Any]],
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#trigger GoogleDataplexDatascan#trigger}
        :param field: The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time. If not specified, a data scan will run for all data in the table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field GoogleDataplexDatascan#field}
        '''
        value = GoogleDataplexDatascanExecutionSpec(trigger=trigger, field=field)

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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#create GoogleDataplexDatascan#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#delete GoogleDataplexDatascan#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#update GoogleDataplexDatascan#update}.
        '''
        value = GoogleDataplexDatascanTimeouts(
            create=create, delete=delete, update=update
        )

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
    def data(self) -> "GoogleDataplexDatascanDataOutputReference":
        return typing.cast("GoogleDataplexDatascanDataOutputReference", jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileResult")
    def data_profile_result(self) -> "GoogleDataplexDatascanDataProfileResultList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultList", jsii.get(self, "dataProfileResult"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileSpec")
    def data_profile_spec(
        self,
    ) -> "GoogleDataplexDatascanDataProfileSpecOutputReference":
        return typing.cast("GoogleDataplexDatascanDataProfileSpecOutputReference", jsii.get(self, "dataProfileSpec"))

    @builtins.property
    @jsii.member(jsii_name="dataQualityResult")
    def data_quality_result(self) -> "GoogleDataplexDatascanDataQualityResultList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultList", jsii.get(self, "dataQualityResult"))

    @builtins.property
    @jsii.member(jsii_name="dataQualitySpec")
    def data_quality_spec(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecOutputReference", jsii.get(self, "dataQualitySpec"))

    @builtins.property
    @jsii.member(jsii_name="executionSpec")
    def execution_spec(self) -> "GoogleDataplexDatascanExecutionSpecOutputReference":
        return typing.cast("GoogleDataplexDatascanExecutionSpecOutputReference", jsii.get(self, "executionSpec"))

    @builtins.property
    @jsii.member(jsii_name="executionStatus")
    def execution_status(self) -> "GoogleDataplexDatascanExecutionStatusList":
        return typing.cast("GoogleDataplexDatascanExecutionStatusList", jsii.get(self, "executionStatus"))

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
    def timeouts(self) -> "GoogleDataplexDatascanTimeoutsOutputReference":
        return typing.cast("GoogleDataplexDatascanTimeoutsOutputReference", jsii.get(self, "timeouts"))

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
    def data_input(self) -> typing.Optional["GoogleDataplexDatascanData"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanData"], jsii.get(self, "dataInput"))

    @builtins.property
    @jsii.member(jsii_name="dataProfileSpecInput")
    def data_profile_spec_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpec"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpec"], jsii.get(self, "dataProfileSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="dataQualitySpecInput")
    def data_quality_spec_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpec"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpec"], jsii.get(self, "dataQualitySpecInput"))

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
    def execution_spec_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanExecutionSpec"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanExecutionSpec"], jsii.get(self, "executionSpecInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleDataplexDatascanTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleDataplexDatascanTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataScanId")
    def data_scan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataScanId"))

    @data_scan_id.setter
    def data_scan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1487eaec96f2e492b2bc43261f8a86cb627fc93d5ca199343384412342422424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataScanId", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a56706c889c2452c3c5a2ce68c0caf2adc06a89572652f1dc03c4e1ab732c882)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2276e334fbf3a651534429d22bd47b54754f913ab18dd7b25799e22d6f5c7ae3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df77bf10b0bf3909950533b166bb7af59a46e0dd8152657a64fa1d97e5d4d017)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac6ca0c81605251cdad7d60e66e5874660bab42cc52ca5d25d4cd5637659a44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c78e451aa48de509e9aaef430a53ffa2e819243bd60fe824623fd44bd593ec4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f58a35f36b5857e569f0cb40b1d9d0dcd56105f641b7bc7bb30112ccffc636a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanConfig",
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
class GoogleDataplexDatascanConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        data: typing.Union["GoogleDataplexDatascanData", typing.Dict[builtins.str, typing.Any]],
        data_scan_id: builtins.str,
        execution_spec: typing.Union["GoogleDataplexDatascanExecutionSpec", typing.Dict[builtins.str, typing.Any]],
        location: builtins.str,
        data_profile_spec: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        data_quality_spec: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpec", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDataplexDatascanTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param data: data block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data GoogleDataplexDatascan#data}
        :param data_scan_id: DataScan identifier. Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_scan_id GoogleDataplexDatascan#data_scan_id}
        :param execution_spec: execution_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#execution_spec GoogleDataplexDatascan#execution_spec}
        :param location: The location where the data scan should reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#location GoogleDataplexDatascan#location}
        :param data_profile_spec: data_profile_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_profile_spec GoogleDataplexDatascan#data_profile_spec}
        :param data_quality_spec: data_quality_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_quality_spec GoogleDataplexDatascan#data_quality_spec}
        :param description: Description of the scan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#description GoogleDataplexDatascan#description}
        :param display_name: User friendly display name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#display_name GoogleDataplexDatascan#display_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#id GoogleDataplexDatascan#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: User-defined labels for the scan. A list of key->value pairs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#labels GoogleDataplexDatascan#labels}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#project GoogleDataplexDatascan#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#timeouts GoogleDataplexDatascan#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(data, dict):
            data = GoogleDataplexDatascanData(**data)
        if isinstance(execution_spec, dict):
            execution_spec = GoogleDataplexDatascanExecutionSpec(**execution_spec)
        if isinstance(data_profile_spec, dict):
            data_profile_spec = GoogleDataplexDatascanDataProfileSpec(**data_profile_spec)
        if isinstance(data_quality_spec, dict):
            data_quality_spec = GoogleDataplexDatascanDataQualitySpec(**data_quality_spec)
        if isinstance(timeouts, dict):
            timeouts = GoogleDataplexDatascanTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29bf5a36a233e10710bc2fa54eb590a6ee25dc382266c69ce4105fbf01fe14ac)
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
    def data(self) -> "GoogleDataplexDatascanData":
        '''data block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data GoogleDataplexDatascan#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast("GoogleDataplexDatascanData", result)

    @builtins.property
    def data_scan_id(self) -> builtins.str:
        '''DataScan identifier.

        Must contain only lowercase letters, numbers and hyphens. Must start with a letter. Must end with a number or a letter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_scan_id GoogleDataplexDatascan#data_scan_id}
        '''
        result = self._values.get("data_scan_id")
        assert result is not None, "Required property 'data_scan_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_spec(self) -> "GoogleDataplexDatascanExecutionSpec":
        '''execution_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#execution_spec GoogleDataplexDatascan#execution_spec}
        '''
        result = self._values.get("execution_spec")
        assert result is not None, "Required property 'execution_spec' is missing"
        return typing.cast("GoogleDataplexDatascanExecutionSpec", result)

    @builtins.property
    def location(self) -> builtins.str:
        '''The location where the data scan should reside.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#location GoogleDataplexDatascan#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_profile_spec(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpec"]:
        '''data_profile_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_profile_spec GoogleDataplexDatascan#data_profile_spec}
        '''
        result = self._values.get("data_profile_spec")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpec"], result)

    @builtins.property
    def data_quality_spec(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpec"]:
        '''data_quality_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#data_quality_spec GoogleDataplexDatascan#data_quality_spec}
        '''
        result = self._values.get("data_quality_spec")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpec"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the scan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#description GoogleDataplexDatascan#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''User friendly display name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#display_name GoogleDataplexDatascan#display_name}
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#id GoogleDataplexDatascan#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User-defined labels for the scan. A list of key->value pairs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#labels GoogleDataplexDatascan#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#project GoogleDataplexDatascan#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleDataplexDatascanTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#timeouts GoogleDataplexDatascan#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleDataplexDatascanTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanData",
    jsii_struct_bases=[],
    name_mapping={"entity": "entity", "resource": "resource"},
)
class GoogleDataplexDatascanData:
    def __init__(
        self,
        *,
        entity: typing.Optional[builtins.str] = None,
        resource: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param entity: The Dataplex entity that represents the data source(e.g. BigQuery table) for Datascan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#entity GoogleDataplexDatascan#entity}
        :param resource: The service-qualified full resource name of the cloud resource for a DataScan job to scan against. The field could be: (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#resource GoogleDataplexDatascan#resource}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__232fe999855133d6d7fe98d528ae2c1330797fd36d97e65b26b5da6f2e5b65d3)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#entity GoogleDataplexDatascan#entity}
        '''
        result = self._values.get("entity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource(self) -> typing.Optional[builtins.str]:
        '''The service-qualified full resource name of the cloud resource for a DataScan job to scan against.

        The field could be:
        (Cloud Storage bucket for DataDiscoveryScan)BigQuery table of type "TABLE" for DataProfileScan/DataQualityScan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#resource GoogleDataplexDatascan#resource}
        '''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__88d58e36161fce3ac6bb35c284a7365ee2d1f39e5852e21e1b536ae561e88597)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3116bb5ff0968f2f9e4c444578df05eca0f41d0efea09dd09abbad116026827e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entity", value)

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7b975a6a2b1f01a5376ebfe5be1006dee8ee322866cf6ef5b9625356a4762c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDataplexDatascanData]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea13e3372d0975e7ab4d5cb8a2f2a8e6f084369ce1fb16946086356f648f5a0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__219a665f84280a2c1a74587a8e66ba78c4d0f10efdffc2913561e9bd33378fc8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a9441091f6266bfab11937dccf3e0b02bbf651a34fedc43403c904f94261585)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__952373c20d22b48b63396c140caa01ca8fe3a6571cf8d5a0cd5a3abeae20a224)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10a6526a1d6ce77bd38232fa83db2501991825ef535522e3f50387d7f7df4e46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e6df302cfc622275d3a96f1ab453d3bce00ceabc7aeeaaec4d73a604dba4577)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58ba5f92ceb645904711a372993f84f9a6da8688c060efead520b4b72b6479d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> "GoogleDataplexDatascanDataProfileResultProfileList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileList", jsii.get(self, "profile"))

    @builtins.property
    @jsii.member(jsii_name="rowCount")
    def row_count(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rowCount"))

    @builtins.property
    @jsii.member(jsii_name="scannedData")
    def scanned_data(self) -> "GoogleDataplexDatascanDataProfileResultScannedDataList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultScannedDataList", jsii.get(self, "scannedData"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResult]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ba3f04afeda29e6008efa2a3d3c3f4b8f716400fca4b55b51c509f5956fad42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFields",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFields:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultProfileFieldsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5da0fbc02f0edeaf47dc1fed442aa77aec745a5fd521238c8fc862fef72ef04a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3dd51b67cc7318b2e6e6c7dbc766720860d386d3698f229ee9906d0ac09470e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd252d4d1a03c6937fea5d491b400c98fb020f8e8dacddc8a17617328bbb4452)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f8a022fe01793e26e4481ebf0218b58506e3011694496d96226997e73b31f58)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb5928a2efa691c8b00d754cdc014af5bdbcaba07e7768bc17990536db8ebee5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7aa3223ee045917338be8ac7759f0a0d3b10e108b4d614d5471811d66fc0f98d)
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
    def profile(
        self,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileList", jsii.get(self, "profile"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFields]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ca795b5f54cc29b19b429f01932ddc187cbb2814730590642b3797994984737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFieldsProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFieldsProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e64a6f92b240be3f0c30409775e6f25feed7b314a2fbd7122774a07ca2cc2b81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d15166afdec38847605dde23eca758778d4c16569a77c4bc5d837079f72981e0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4faafe0b0a2e0bda3d56dd417b7afc8320706ef525ecc5e54dc92361a84b08b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02c40e062bbaeded53b3c11ba711dd8d3af9ac6d6c8b7f9cf01bc83b08e44e67)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5eb22b9956500ac906e82deb5f55839553e5715a2493f4dedd05db73bad8d7cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1938f892b4da6880c26445d21046ab2782beea48b0692cdb6c1e15ab96ce2a12)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5c029a97183189910585e0c121b3a425ed41fd31874e494df7e291793f0ed15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0cd99e8605cf936054074d63918186c6998cd23fe649ef47a147885927242134)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4962877aa5f5a40e61bd595e57f753cc2d5c79a4c4ee7699f10b53b0cc350703)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4798740007177bbb1dee52fecc014fb2f4c38d98da1a87be185147c789ec37f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c320d5db3d127c3d4fd6a296e82b51b380032319caf4557655d444c1a86fec1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0beb6d5e30bbb39c805528304662011fff8c7417ad90e5db966fc020909fd5c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__afb55eb1c85c1a98c8d99ae46290934e72043ec2d77107d74b7de2edc5dd5084)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__806e2dfb1cd6064ab11037adccf47d7aa393b37029be9ed8b3dc49997d1f26cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__007294c1a32ab7b5b01372bdd422af7d0b0ee24e3c5485658aaa7555d9df319e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5df3227ff836573a93ce75d8676c659617001f82a1e77eacfdb98bba3950ce7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a46a1c42b631cd0f094d75174b74632069387606e6770ab398091135f884bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__be60db7da9f5af3b3362831842f6a6a2102f7bfc14b9cc35516b71a942c556af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a832ff0c5fdf98c503ab30abaf8d4eacb49951c2003de874c41670f130cb3e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af69ac2d9e77ce8ad1446f18486dd6839afcaa6377ac95f3df419edbc231003c)
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
    ) -> GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList:
        return typing.cast(GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList, jsii.get(self, "doubleProfile"))

    @builtins.property
    @jsii.member(jsii_name="integerProfile")
    def integer_profile(
        self,
    ) -> GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList:
        return typing.cast(GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList, jsii.get(self, "integerProfile"))

    @builtins.property
    @jsii.member(jsii_name="nullRatio")
    def null_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nullRatio"))

    @builtins.property
    @jsii.member(jsii_name="stringProfile")
    def string_profile(
        self,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList", jsii.get(self, "stringProfile"))

    @builtins.property
    @jsii.member(jsii_name="topNValues")
    def top_n_values(
        self,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList":
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList", jsii.get(self, "topNValues"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfile]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__559f4eaaa934d437bd0b57ec71be55ef18fba0e0164662eb945e68255556ab38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b43798393a5ee55226327d768315ec9b3925699b155483b86282e3757bb1ac6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b186f11a5adae26ff392893d8b3f29c909e71f893f4d6354c7dd3aa79ee3e37)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794e17dbb34638e8bb161614c8b9017d2fa9aed4e6dab5a882cba46d11b42316)
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
            type_hints = typing.get_type_hints(_typecheckingstub__93eb4562331f3570e7930b39f55e71845e5ae5dd129446d1521b93d848ff43ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2ebf04ead29ba2f363c9aa54f770d3cd0106359e1b4d959b04bc29830327214)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__102667e91f61f8d94f1e0be2f66ca6f7dcc2d263c7d27a567965c800bca96d1a)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ee1fe49f8db8c55674e9f6f478dc0585d790f6530a7d031bc5ab926bb70697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f056b75e4aabe1a5fb1f1e6a41cb802efa7931eabdd145e152220d7b0dc05f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00b0bfb275e3a287e8386cf1c78975c9d68796d63e491318cce975b6bad373e7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f8b577cd8cf6100f3268968d40d98f030d9b7b7c57eadbabefc0c95909868be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c6c7a0f6164d61347695c7a57da1b51f009121331da3ad9beb11d2ffb3bf2d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28ba161e1a810ebeb74c759bec112924b296e4893f68afa9091ed18b2c6f07ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a57b4da9789eb9978d52e39146f375b6d37547d711edff90afef3476bfa6054a)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb925339576ef7f1c884f19927089b586e25bb49e5ec3c0010ca42da76844055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataProfileResultProfileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5505f23a32055c4407df5bd0d06f3989464249633f677b0c8cfa796d8dcc333a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultProfileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9ecdfc4e1615d5c7b7f994a93d83ba4ff14a0cc87742c03ae46ea4fccc89426)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultProfileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c71312811d5f1e59e90a405290cff1799465216f598362ee243b2c661475703)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2062457488e8d54d1711515067d8496d6fc4c1012353ffe494ce2cabb8386d95)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10cd615937e20a72ac80c62554ad3044df0a800361e0b07b3b2ecf4be91f0907)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed55f148deb0642cc067e8140dfced91a62f2911cf072de5bf02cd7c0bdda533)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fields")
    def fields(self) -> GoogleDataplexDatascanDataProfileResultProfileFieldsList:
        return typing.cast(GoogleDataplexDatascanDataProfileResultProfileFieldsList, jsii.get(self, "fields"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultProfile]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b39cc041e71b50f12e470aa390b4436073c09adaf0dd5ba337f64c0776a688)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedData",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultScannedData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultScannedData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9c3861627c2a1a44f44ee0d6445f41e365600587ba1e0b661262cd25489e9f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b28fad4c4dbeb7d88b2122b74713b08e42b17c227e76e6cfd67b25906c3f48e1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a52adaf83331a0c00d2a009f4b7b037db304556a5ed52a0e85e4cb90dbd380e8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a249fc9bd8c627c7a4851e4cad02751d535a0e3d833f104e110ff2bb42411807)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f5e49a54968f545a6da079a5840ce4b212749938c53d3c3365f0fc3e2750636)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57dd95a45e5f3f6ad2633e22db9769a0f2c182a5ffa3f8f0acf0b68d47b0c3b9)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__362262306644e15f07bb0300d0e576dcef3fda135cd94aaae109a71b261885c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataProfileResultScannedDataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedDataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a78ae689121eb9f75e04e9d939288ac1769ef2db3cb0b18b49a1dccf362775d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataProfileResultScannedDataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__548e152beb83bf8e372b74d16534bc013f248d3f2b59813a5ac8a721ec9211fd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataProfileResultScannedDataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d130d472b384d45ab44a174102f31cbd18643085af92e57852a4ca747a47cbe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70621b260d37f2b0648d572183df525eb50bb2aaf0b8bc4c1014255841a8cc6e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__417d5d8cd747a19220de4fc3506d83004856aa4ed102bc1a532cf3bc637f8405)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataProfileResultScannedDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileResultScannedDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__112c094ec0ef17ff2abcd5718c819ac5238cd37c813c3d469c265e7a015ea021)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="incrementalField")
    def incremental_field(
        self,
    ) -> GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldList:
        return typing.cast(GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldList, jsii.get(self, "incrementalField"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileResultScannedData]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileResultScannedData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileResultScannedData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__747215d957c226e18aca2b4434d7a3d36ba105aebbcfab1c0c61a58d2f96de41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpec",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_fields": "excludeFields",
        "include_fields": "includeFields",
        "post_scan_actions": "postScanActions",
        "row_filter": "rowFilter",
        "sampling_percent": "samplingPercent",
    },
)
class GoogleDataplexDatascanDataProfileSpec:
    def __init__(
        self,
        *,
        exclude_fields: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecExcludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        include_fields: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecIncludeFields", typing.Dict[builtins.str, typing.Any]]] = None,
        post_scan_actions: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_fields: exclude_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#exclude_fields GoogleDataplexDatascan#exclude_fields}
        :param include_fields: include_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#include_fields GoogleDataplexDatascan#include_fields}
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        if isinstance(exclude_fields, dict):
            exclude_fields = GoogleDataplexDatascanDataProfileSpecExcludeFields(**exclude_fields)
        if isinstance(include_fields, dict):
            include_fields = GoogleDataplexDatascanDataProfileSpecIncludeFields(**include_fields)
        if isinstance(post_scan_actions, dict):
            post_scan_actions = GoogleDataplexDatascanDataProfileSpecPostScanActions(**post_scan_actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a51055e7828267c97aaa54c02d861769b5cf595e67db1313ae57329eea8156)
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
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpecExcludeFields"]:
        '''exclude_fields block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#exclude_fields GoogleDataplexDatascan#exclude_fields}
        '''
        result = self._values.get("exclude_fields")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpecExcludeFields"], result)

    @builtins.property
    def include_fields(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpecIncludeFields"]:
        '''include_fields block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#include_fields GoogleDataplexDatascan#include_fields}
        '''
        result = self._values.get("include_fields")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpecIncludeFields"], result)

    @builtins.property
    def post_scan_actions(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActions"]:
        '''post_scan_actions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        '''
        result = self._values.get("post_scan_actions")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActions"], result)

    @builtins.property
    def row_filter(self) -> typing.Optional[builtins.str]:
        '''A filter applied to all rows in a single DataScan job.

        The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        '''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sampling_percent(self) -> typing.Optional[jsii.Number]:
        '''The percentage of the records to be selected from the dataset for DataScan.

        Value can range between 0.0 and 100.0 with up to 3 significant decimal digits.
        Sampling is not applied if 'sampling_percent' is not specified, 0 or 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        result = self._values.get("sampling_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecExcludeFields",
    jsii_struct_bases=[],
    name_mapping={"field_names": "fieldNames"},
)
class GoogleDataplexDatascanDataProfileSpecExcludeFields:
    def __init__(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a193c088db579359dc7dfa6f1c9b20e61514e1bd98b89e007cda67bccc6ce1)
            check_type(argname="argument field_names", value=field_names, expected_type=type_hints["field_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if field_names is not None:
            self._values["field_names"] = field_names

    @builtins.property
    def field_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Expected input is a list of fully qualified names of fields as in the schema.

        Only top-level field names for nested fields are supported.
        For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        result = self._values.get("field_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileSpecExcludeFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileSpecExcludeFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecExcludeFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32d9924faf7fa246b468ce1611cb28caf0f8be4419263c32734d62f089d54936)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcbcc77baf394088c82f9ad5a21875ed3657fd2376373bdbc0940253492c0bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldNames", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f290f47e1eebf32bfe48c1099a75ce4a85646a9fa825a7f0ab7ed312121107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecIncludeFields",
    jsii_struct_bases=[],
    name_mapping={"field_names": "fieldNames"},
)
class GoogleDataplexDatascanDataProfileSpecIncludeFields:
    def __init__(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d9c3f5a0c27583808594eb832ec01d3eff6b1805052078d1de1d6d3afdf74a)
            check_type(argname="argument field_names", value=field_names, expected_type=type_hints["field_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if field_names is not None:
            self._values["field_names"] = field_names

    @builtins.property
    def field_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Expected input is a list of fully qualified names of fields as in the schema.

        Only top-level field names for nested fields are supported.
        For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        result = self._values.get("field_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileSpecIncludeFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileSpecIncludeFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecIncludeFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffa3259d8ae0197431d19f511490dd65b63cc096aa5af02c5814eeb33aa5e8fc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3d66efd627effb07b4f03aefa7a9d07f5698220fe1e90c594f8fe103ac4a1c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldNames", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02966e63e35bd012877e24a23b6093481451dbd1ff2dfb7594737d3cc8dea736)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataProfileSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__399de5748abecf07b0dc2baedd1baf6f0a1443d3e4e120083c38a52b528712f1)
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
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        value = GoogleDataplexDatascanDataProfileSpecExcludeFields(
            field_names=field_names
        )

        return typing.cast(None, jsii.invoke(self, "putExcludeFields", [value]))

    @jsii.member(jsii_name="putIncludeFields")
    def put_include_fields(
        self,
        *,
        field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param field_names: Expected input is a list of fully qualified names of fields as in the schema. Only top-level field names for nested fields are supported. For instance, if 'x' is of nested field type, listing 'x' is supported but 'x.y.z' is not supported. Here 'y' and 'y.z' are nested fields of 'x'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field_names GoogleDataplexDatascan#field_names}
        '''
        value = GoogleDataplexDatascanDataProfileSpecIncludeFields(
            field_names=field_names
        )

        return typing.cast(None, jsii.invoke(self, "putIncludeFields", [value]))

    @jsii.member(jsii_name="putPostScanActions")
    def put_post_scan_actions(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        value = GoogleDataplexDatascanDataProfileSpecPostScanActions(
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
    ) -> GoogleDataplexDatascanDataProfileSpecExcludeFieldsOutputReference:
        return typing.cast(GoogleDataplexDatascanDataProfileSpecExcludeFieldsOutputReference, jsii.get(self, "excludeFields"))

    @builtins.property
    @jsii.member(jsii_name="includeFields")
    def include_fields(
        self,
    ) -> GoogleDataplexDatascanDataProfileSpecIncludeFieldsOutputReference:
        return typing.cast(GoogleDataplexDatascanDataProfileSpecIncludeFieldsOutputReference, jsii.get(self, "includeFields"))

    @builtins.property
    @jsii.member(jsii_name="postScanActions")
    def post_scan_actions(
        self,
    ) -> "GoogleDataplexDatascanDataProfileSpecPostScanActionsOutputReference":
        return typing.cast("GoogleDataplexDatascanDataProfileSpecPostScanActionsOutputReference", jsii.get(self, "postScanActions"))

    @builtins.property
    @jsii.member(jsii_name="excludeFieldsInput")
    def exclude_fields_input(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields], jsii.get(self, "excludeFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeFieldsInput")
    def include_fields_input(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields], jsii.get(self, "includeFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="postScanActionsInput")
    def post_scan_actions_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActions"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActions"], jsii.get(self, "postScanActionsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__053d767626cf6e94f64bd044ead742767a5d97c5de6408015cc9cd635dc35482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rowFilter", value)

    @builtins.property
    @jsii.member(jsii_name="samplingPercent")
    def sampling_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingPercent"))

    @sampling_percent.setter
    def sampling_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2432fc32786757572a15ef847909774565e0c1701f725f9f12e00c6dfc327872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingPercent", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDataplexDatascanDataProfileSpec]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f3f90e3eb1d1a30e6f9992c1f44482212abdcd67bd8db317bbc243f9fab8955)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecPostScanActions",
    jsii_struct_bases=[],
    name_mapping={"bigquery_export": "bigqueryExport"},
)
class GoogleDataplexDatascanDataProfileSpecPostScanActions:
    def __init__(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        if isinstance(bigquery_export, dict):
            bigquery_export = GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(**bigquery_export)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5385f3c9814fce97c6d191a85b483b3d5c2fe85b2e304fbb164700c134839272)
            check_type(argname="argument bigquery_export", value=bigquery_export, expected_type=type_hints["bigquery_export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bigquery_export is not None:
            self._values["bigquery_export"] = bigquery_export

    @builtins.property
    def bigquery_export(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport"]:
        '''bigquery_export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        result = self._values.get("bigquery_export")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileSpecPostScanActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport",
    jsii_struct_bases=[],
    name_mapping={"results_table": "resultsTable"},
)
class GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport:
    def __init__(self, *, results_table: typing.Optional[builtins.str] = None) -> None:
        '''
        :param results_table: The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01b098c394196414410d25a073bca6df7125099da1e1bb817b929f6ff10a5147)
            check_type(argname="argument results_table", value=results_table, expected_type=type_hints["results_table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if results_table is not None:
            self._values["results_table"] = results_table

    @builtins.property
    def results_table(self) -> typing.Optional[builtins.str]:
        '''The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        result = self._values.get("results_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40eb1edc264383e48f92ea2cb895616fa32d27ad88e55771416a41bb2c53f2b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__43b750538cee11e551dcdc173ef75a7582bb4dbb2a6a906bbc6c9de7b8834661)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resultsTable", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d591d7aa3772437d125d2c4e1c1605c4adec99c0f99c5828f2b94685c37d3855)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataProfileSpecPostScanActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataProfileSpecPostScanActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a9b9d0b2ddfd5b991f0fe74d3ae52f701bffb42a1275c6b9a30bc08140bf945)
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
        :param results_table: The BigQuery table to export DataProfileScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        value = GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport(
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
    ) -> GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference:
        return typing.cast(GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference, jsii.get(self, "bigqueryExport"))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExportInput")
    def bigquery_export_input(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport], jsii.get(self, "bigqueryExportInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActions]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0348030eca89fe041798f21022b4824063a3b23f122f4a9af40a25bd749fc32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResult",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResult:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultDimensions",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultDimensions:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab0461962e9d9ea58805c204d3d44ba52f6251ed0f778174ffb1484750c5c3cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3199b8250af3f24dbd82da8e9735501f7da740a1e1c3aaf99a7ac2ff35f8e9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cd8a83debd8aa05b2bff30e925dc08f5f164a398a734cc00728095d4860e295)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d39e4d19dab3a71a6aec3664d6bc65c676d81bff58937868a4e623e1025c603)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d874d73217963ca062f1191a96d441ff58c19993653b82a72cd1aa95990873d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8478d5f0f70cbbd650ddeb6888f742d92339098e6bcf1713f792e4fd368aba85)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultDimensions]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultDimensions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultDimensions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebfedbb17d9f4a68cf4b0568f44c5cd747c13ed1f759f31ce7782c7ecdbebaba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataQualityResultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b822c4a5817fd277441d30f3a1da2da4e9ee830416f0e418d979a46efbd8b21d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d603a7db451acdf13efb1129c357719cd01902dc05c889bfc8668cc00ecc87)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b07e17dfa3ccf3fa08d9974c9581b01d1ed681e7c47d9921b9ab370b7eebe455)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92e293f9c5626ce52cf3d1892b7d701708ee2e954e6ab21828a9419c66e98939)
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
            type_hints = typing.get_type_hints(_typecheckingstub__754f978dea0347751b0fa01a6495ebb64ce7da735681b3700674e59b177c18b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__712a1eabc9be6e0f2d1c93e1213e242c185b96ca4362e44af6967180639fe03d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> GoogleDataplexDatascanDataQualityResultDimensionsList:
        return typing.cast(GoogleDataplexDatascanDataQualityResultDimensionsList, jsii.get(self, "dimensions"))

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
    def rules(self) -> "GoogleDataplexDatascanDataQualityResultRulesList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="scannedData")
    def scanned_data(self) -> "GoogleDataplexDatascanDataQualityResultScannedDataList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultScannedDataList", jsii.get(self, "scannedData"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResult]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResult], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResult],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccfed8229d78b684449be0d7e9a72397b627deee16f6fe07c40db5b9ef8beb9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e31fcf951ddf960ce4b7be0bc7b6e8af235334e6c21714e4cac6168517d57789)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd4bfcecb705057d9ac7f2c74489bbfd01218337003301f847921c0c29d5429e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b904887ecd173502751a200fc8a3065f1ae29e162f17a8231167918350009415)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3991c141c30db003d301b9752a1c0013372f1a28f6aea08d488b58ccfdb4ef1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a21c5d8d413f838df0820b8f79f1c08cf018d4117bb7f21aa9cd2b24b0f44c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1720cfd3f926e6771711f6013743574f0b0abfa2af2e230e76e31e3d55a83c6)
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
    def rule(self) -> "GoogleDataplexDatascanDataQualityResultRulesRuleList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleList", jsii.get(self, "rule"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRules]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9ab2e292a38b0553615ecc8fa38a12bf546a600828b99704849256dc5e85a28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRule",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRule:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b570b3d92f5422e0969c2c835a4ab50967f7e83548c33fdb8e06271b27561deb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__846923835cbbd0c93ff4c828d1d3a9325a7e56bb116de4967e6dde5d14349c72)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33813d6ad6bec88008c37b4fd4301bae904a34a3c68a60b68c6b1fe0994c76c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2456e5d6d1bf0428b14b4bac8225b1a3f55b944efc440c00e6c188c7928fc836)
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
            type_hints = typing.get_type_hints(_typecheckingstub__88549698945dbe83c0c2a8530fc3bd62879630daee3c03a47796b99bda29e115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfb3d8324bd7465d7287259c5e5c90d797fc44af05c61c43c55d82aa724bea3e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c3079322505f47d17936946628bea35ea7ab263a3dca91c2f40d3f562c4885)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8553575a51df9ea3ae388bc2d78f0ad3ca2cf9c5946b1682b6219abd62d37ea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2b372472412c092aa720596e57ab57e955910c9152aabbcbd032b2ffe2829f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7b5e28c331d3a2b3f5cda709140b1a8a2411891118554d69fc2aff89d8efcf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9718bb26a0f0b14446f748984fe45bd64c5ede9314adcfa492d1c88a111861a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b3a13727b6557a39af9ba48ae7ded2baea13faa643d3b6c67da4a7817857ddd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3d3d53ee4e819f34c723ae89ebac1f1d1a3ddf8380df720646cca3320802126)
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
    ) -> GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationList:
        return typing.cast(GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationList, jsii.get(self, "nonNullExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectation")
    def range_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationList", jsii.get(self, "rangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectation")
    def regex_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationList", jsii.get(self, "regexExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectation")
    def row_condition_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList", jsii.get(self, "rowConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="setExpectation")
    def set_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationList", jsii.get(self, "setExpectation"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectation")
    def statistic_range_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList", jsii.get(self, "statisticRangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectation")
    def table_condition_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList", jsii.get(self, "tableConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectation")
    def uniqueness_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList":
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList", jsii.get(self, "uniquenessExpectation"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRule]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3da35bfc526a820fb8e6d0f5a188dd5a11d898c09ca63f37d28a8d32fd200d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b995a928dcf885403159dd6f4940a181e91b5cba74dc8dce0b6f3b7fb3932f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__918df9568c615598a3db3c9b343c5a49866d514fdb9f28d12d32234e33e404d2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9437bb7402b09c575570acde276b0861a826e8fb152eb3cc74b9754304d10500)
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
            type_hints = typing.get_type_hints(_typecheckingstub__71031bf1199af740a5a74a9928a53bbe85c6ba448bdbc1ea253eee43169e9a28)
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
            type_hints = typing.get_type_hints(_typecheckingstub__15eaa30d363593b2dcf6fa47d4e7acc7d5fcb5252721335e48988e1eeabcb301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41cb26c60bdab35f115a142b0b4c74ff1b2b5848defc01caa0acd4b163fdb8cf)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__520077185a4f331a4bb32fb2044b7edaef79ba43f0b5fdad486f7106930f7f27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20ba550a2a75c9be71843898a08f05c59e5d4be70b4793752aa341fe2e82c0f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae3668c9aa78939f002e5d636149d620fc8fc660447b79bc1e0aa74a990b798d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3417faa92cc24a64089a3368d09babb0f334bbce8083f6dda72bc7f736f277bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb8cc35197ec98c5dc8b712c74ca4c0c9654d8d27a0abf57a8ba3eab0f34667c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48c499cd7b6c40d6c38aeba3d99b5e05dff836ea9a3968760b84048cdfdaf6c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9026b8449bdae14cf1aa711a47e0a87fa9c8a9cee8a1c4f6a9d9bda3e983a3d8)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73532953f2fe9877a4e133cfdbea95120cdcf6a21b9fca34955282992805b761)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7c9c107acc43d1ab2b7de0fed4e22cda176d0b23dbb8f3d04d7798e6dcecfa6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e739946ac586d70cab134588017557d530b5e475748a92c8919279bc9ffd0cb0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c3c9af68da84fcb44cb7fdd52c3e16acb339800711b9c94c11399415ec2f31a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2524e628e63e3283eb7e7d6f356350403e03650604bc7da51ea17ca87ee9e6a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38b4021aa9f0b11a310f9ca73348b940bd27193f4c99c66ab3ee6f3bf98ece9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8903d80ec5b644609f3972fa504999228b058eca2e30cc9a3f5cfe62bab5ece7)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b5ad85fe860609a879e06cb7208b4a49e0b2d7b413c7b5e25c7a6b24ace69e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c50d038d2b8c1192c324a6c1800c23e03357fae5a096f3d738eb05c15335fab2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b435e8176326b9ae7d2ca6137ff758e2107a4296617cb4dabd6be68271025bbe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506b2ab80660110f14aa6ffddb017e8259241485b7a6ca0f27702bb16ca9d916)
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
            type_hints = typing.get_type_hints(_typecheckingstub__247400a38763eeea92b487eb69ed5f84f1db085f4a970a59137b1931888ebfe3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1db30cd3116361ef626be5cd7192fbaabdd787118e833e86e6a1736c2ef6e7d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c9ecdcd9bb83a036df51f17d870d0df2f418824cf4110353b61001f7bef5836)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4070a5d78461ace2b1d72ab8df81d931c1219d979d6178487d2cbc4ba3ab0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07da7c418b4e9a6cdcad90c6241d88351fb803e71d257e6fc2f693c9b0c7a882)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6017075c20f2a4e59d3c0f13abc3b15df3943740d9da50d670180b491551292)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1ac4b8cbc0bfc84e0e3264b55709feb91ec03eaece5c3d26a01234903d046ad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00058d9c86ebaa7a98db790730c894f3741f18dccc5be0ed1de4bff1934836c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10bc23b9675ec09a25283e8bbf14fd927e4c25005ad51a9d692c3b8e40de79c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd88b0179384ceeb0946364f7a127349bbafc5a5705ddf228855358af5ce89d6)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42550a1659c7fafe0a0c51e2109b9ab9e6b90d9c3c3c3a1fbae21abc483f3a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e52864f6d0c8f54d6cdedd1afb07ca08b45897154c847becb12a16806b2aca88)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ad3e6450d4adb45f0bcfcd93812c35df867c01fc3b848187c42375d16c0b58d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d6eb8cc2b6186d95f43bcaf9dee81bfaa4d5061c73cf0fa4d943a51fa9bc571)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b331db61eb0d5f5c47d594785d91d7e1bad01650dcfed4b6b981516d5768293a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b9f1fd3affcbd106c08ae2fabd71794637138759cac45305f82a5a287d5a014)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b201d19dd345d8f332afdb8b8bf272e426923a6d1a89bbdecf51d7df287e942)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15591d144bc67b12016640d949de0bdd160b1dca1b93e8791a22defeb1b9659a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ff3bfb1531d7fb80dd3a6b9e95b9eacc55541cca555782ff63bee35b0f9867a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06693dfb87e380af6854a2602c1090548faf71975f3a1f603fa60d3b52e3da51)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e244b6c64006327145a93847ef54ab9f182be58cb6f9e83a9c2dde3656a7b1b9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e20110edd8cad0f75ee184e9659e4fb4c198509761595e76bc95b340d54f1ccc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2ea37285aa129f6021b47c091b19f23d4ad320b267963f290f4fb56570d760e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad7d2737262572f3f078c802ea0a067d466133c127968bd9c002979e1239ecfc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296b8266d7b1bc27357e6d4e24d35f3e2a250dc1900f82736336ebc291435acc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedData",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultScannedData:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultScannedData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa4b87cdb0a0c72c242306140341c72d860039df0996a54427dcb0cb30bf6193)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac23171e5383895dee4757a3eb68da0f92f193d0d8ba68a22450183f1cce72e4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a4a4121ab022ce319e6ccca8a969def1e0f232d51bf32e229e272467389bce0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3da3d798fe90aecf6ab0ae08ccff4d22047cd267d505d56d6da1e5cc9a4f70ad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__73e69178b2a7cdfcff33a0cccc9435a325c816e52b94cee5ca79d1e6256c37e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c87561ed5e7854c1031ab3201187331cbc19fe5c595c1b2bec321f883ceff1a5)
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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b45f65bdd366223ab402a6cc7c675a6239f56bf97d94d9b66f9ef98883a847ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataQualityResultScannedDataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedDataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1c2f7f64f203c6d9c238a4fb88869cec1826f8a640e9106ed7343010b21ccb6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualityResultScannedDataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd91e652084424ec8d8381e74e4563826d7b392a794253221a8bce6e5fb932ea)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualityResultScannedDataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__049a0c03dd2948fb8794f09e779947172eca5eb31795c586237c4b8db2fbc5ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfd59b7efcb07e1a36051b9c290ab6fa27309a65cb7520f6069889300bccb7f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca9b2d4eda99b8ea69bb971904b06cd4f20be668539a39742bfa319244a6fa13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanDataQualityResultScannedDataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualityResultScannedDataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6992ee6052318711542d0de3a2501c5e8778dba13686188fb9085332fdc872b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="incrementalField")
    def incremental_field(
        self,
    ) -> GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldList:
        return typing.cast(GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldList, jsii.get(self, "incrementalField"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualityResultScannedData]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualityResultScannedData], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualityResultScannedData],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9905a69e9ae6f01f3b117c0e9c746fd7be6fd625f9754650597c9ca50b1ad941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpec",
    jsii_struct_bases=[],
    name_mapping={
        "post_scan_actions": "postScanActions",
        "row_filter": "rowFilter",
        "rules": "rules",
        "sampling_percent": "samplingPercent",
    },
)
class GoogleDataplexDatascanDataQualitySpec:
    def __init__(
        self,
        *,
        post_scan_actions: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecPostScanActions", typing.Dict[builtins.str, typing.Any]]] = None,
        row_filter: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sampling_percent: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param post_scan_actions: post_scan_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        :param row_filter: A filter applied to all rows in a single DataScan job. The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#rules GoogleDataplexDatascan#rules}
        :param sampling_percent: The percentage of the records to be selected from the dataset for DataScan. Value can range between 0.0 and 100.0 with up to 3 significant decimal digits. Sampling is not applied if 'sampling_percent' is not specified, 0 or 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        if isinstance(post_scan_actions, dict):
            post_scan_actions = GoogleDataplexDatascanDataQualitySpecPostScanActions(**post_scan_actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82f6f9b2e3dd9e6ef61d466036972682a872613d0f2dab949a64eab1e4977eb8)
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
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActions"]:
        '''post_scan_actions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#post_scan_actions GoogleDataplexDatascan#post_scan_actions}
        '''
        result = self._values.get("post_scan_actions")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActions"], result)

    @builtins.property
    def row_filter(self) -> typing.Optional[builtins.str]:
        '''A filter applied to all rows in a single DataScan job.

        The filter needs to be a valid SQL expression for a WHERE clause in BigQuery standard SQL syntax. Example: col1 >= 0 AND col2 < 10

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_filter GoogleDataplexDatascan#row_filter}
        '''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDataplexDatascanDataQualitySpecRules"]]]:
        '''rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#rules GoogleDataplexDatascan#rules}
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDataplexDatascanDataQualitySpecRules"]]], result)

    @builtins.property
    def sampling_percent(self) -> typing.Optional[jsii.Number]:
        '''The percentage of the records to be selected from the dataset for DataScan.

        Value can range between 0.0 and 100.0 with up to 3 significant decimal digits.
        Sampling is not applied if 'sampling_percent' is not specified, 0 or 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sampling_percent GoogleDataplexDatascan#sampling_percent}
        '''
        result = self._values.get("sampling_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__775059a98ce65e4f0affacba4ba2710d7e003519f17ab4ae3316a68e7d2641f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPostScanActions")
    def put_post_scan_actions(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        value = GoogleDataplexDatascanDataQualitySpecPostScanActions(
            bigquery_export=bigquery_export
        )

        return typing.cast(None, jsii.invoke(self, "putPostScanActions", [value]))

    @jsii.member(jsii_name="putRules")
    def put_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDataplexDatascanDataQualitySpecRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d44d1c72321fa387e3a07748830ebeadc94997a7f06a8d3a4ebca3401ad3b4fa)
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
    ) -> "GoogleDataplexDatascanDataQualitySpecPostScanActionsOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecPostScanActionsOutputReference", jsii.get(self, "postScanActions"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "GoogleDataplexDatascanDataQualitySpecRulesList":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="postScanActionsInput")
    def post_scan_actions_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActions"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActions"], jsii.get(self, "postScanActionsInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilterInput")
    def row_filter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDataplexDatascanDataQualitySpecRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDataplexDatascanDataQualitySpecRules"]]], jsii.get(self, "rulesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ff9e18b8def8c706dff7b2f966af3691b24fc2a1ad876b5cf71fa956661d7ec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rowFilter", value)

    @builtins.property
    @jsii.member(jsii_name="samplingPercent")
    def sampling_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingPercent"))

    @sampling_percent.setter
    def sampling_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abd007d0903d76673de73e4e5158fdbc4a1d15699a26a54f50abd17fc763820c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingPercent", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDataplexDatascanDataQualitySpec]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39780b258628d7a453ef4d2f941dd50e8ef559c0e935ec86bd9c233a6a25ed02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecPostScanActions",
    jsii_struct_bases=[],
    name_mapping={"bigquery_export": "bigqueryExport"},
)
class GoogleDataplexDatascanDataQualitySpecPostScanActions:
    def __init__(
        self,
        *,
        bigquery_export: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bigquery_export: bigquery_export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        if isinstance(bigquery_export, dict):
            bigquery_export = GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(**bigquery_export)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__950de9465254aeb19d4268125ef75923d132f8889adbb11ad03586b9f864a3c8)
            check_type(argname="argument bigquery_export", value=bigquery_export, expected_type=type_hints["bigquery_export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bigquery_export is not None:
            self._values["bigquery_export"] = bigquery_export

    @builtins.property
    def bigquery_export(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport"]:
        '''bigquery_export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#bigquery_export GoogleDataplexDatascan#bigquery_export}
        '''
        result = self._values.get("bigquery_export")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecPostScanActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport",
    jsii_struct_bases=[],
    name_mapping={"results_table": "resultsTable"},
)
class GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport:
    def __init__(self, *, results_table: typing.Optional[builtins.str] = None) -> None:
        '''
        :param results_table: The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a989632fc2f5b26f7051778fdb3fab192b7a50e96b735e3e8bc5af89775f29d)
            check_type(argname="argument results_table", value=results_table, expected_type=type_hints["results_table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if results_table is not None:
            self._values["results_table"] = results_table

    @builtins.property
    def results_table(self) -> typing.Optional[builtins.str]:
        '''The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        result = self._values.get("results_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba8dc2375435f8e84caeecbf2e92138d08439bdac7d29b79092750561db3ecd5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47f7a70a14e98ee37eaa8a2ffdd9c975ae34aee5160c9046a9f9bd71ddf82ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resultsTable", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__267732bf0de95a3b611ea60a60ee06d0dc96fd82b9b7f4c30f2d5ec38c1bf629)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataQualitySpecPostScanActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecPostScanActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__994d2a37f002facfb57d8f0f11652bb15b5701381488ff8a5e298269f31d0885)
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
        :param results_table: The BigQuery table to export DataQualityScan results to. Format://bigquery.googleapis.com/projects/PROJECT_ID/datasets/DATASET_ID/tables/TABLE_ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#results_table GoogleDataplexDatascan#results_table}
        '''
        value = GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport(
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
    ) -> GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference:
        return typing.cast(GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference, jsii.get(self, "bigqueryExport"))

    @builtins.property
    @jsii.member(jsii_name="bigqueryExportInput")
    def bigquery_export_input(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport], jsii.get(self, "bigqueryExportInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActions]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b44627c4aa19deb5a0196b710ef953a8184d83e567a7913db41633e2cf2123)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRules",
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
class GoogleDataplexDatascanDataQualitySpecRules:
    def __init__(
        self,
        *,
        dimension: builtins.str,
        column: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        ignore_null: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        non_null_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        range_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        regex_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        row_condition_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        set_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesSetExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        statistic_range_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        table_condition_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
        threshold: typing.Optional[jsii.Number] = None,
        uniqueness_expectation: typing.Optional[typing.Union["GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dimension: The dimension a rule belongs to. Results are also aggregated at the dimension level. Supported dimensions are ["COMPLETENESS", "ACCURACY", "CONSISTENCY", "VALIDITY", "UNIQUENESS", "INTEGRITY"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#dimension GoogleDataplexDatascan#dimension}
        :param column: The unnested column which this rule is evaluated against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#column GoogleDataplexDatascan#column}
        :param description: Description of the rule. The maximum length is 1,024 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#description GoogleDataplexDatascan#description}
        :param ignore_null: Rows with null values will automatically fail a rule, unless ignoreNull is true. In that case, such null rows are trivially considered passing. Only applicable to ColumnMap rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#ignore_null GoogleDataplexDatascan#ignore_null}
        :param name: A mutable name for the rule. The name must contain only letters (a-z, A-Z), numbers (0-9), or hyphens (-). The maximum length is 63 characters. Must start with a letter. Must end with a number or a letter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#name GoogleDataplexDatascan#name}
        :param non_null_expectation: non_null_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#non_null_expectation GoogleDataplexDatascan#non_null_expectation}
        :param range_expectation: range_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#range_expectation GoogleDataplexDatascan#range_expectation}
        :param regex_expectation: regex_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#regex_expectation GoogleDataplexDatascan#regex_expectation}
        :param row_condition_expectation: row_condition_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_condition_expectation GoogleDataplexDatascan#row_condition_expectation}
        :param set_expectation: set_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#set_expectation GoogleDataplexDatascan#set_expectation}
        :param statistic_range_expectation: statistic_range_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#statistic_range_expectation GoogleDataplexDatascan#statistic_range_expectation}
        :param table_condition_expectation: table_condition_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#table_condition_expectation GoogleDataplexDatascan#table_condition_expectation}
        :param threshold: The minimum ratio of passing_rows / total_rows required to pass this rule, with a range of [0.0, 1.0]. 0 indicates default value (i.e. 1.0). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#threshold GoogleDataplexDatascan#threshold}
        :param uniqueness_expectation: uniqueness_expectation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#uniqueness_expectation GoogleDataplexDatascan#uniqueness_expectation}
        '''
        if isinstance(non_null_expectation, dict):
            non_null_expectation = GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation(**non_null_expectation)
        if isinstance(range_expectation, dict):
            range_expectation = GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation(**range_expectation)
        if isinstance(regex_expectation, dict):
            regex_expectation = GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation(**regex_expectation)
        if isinstance(row_condition_expectation, dict):
            row_condition_expectation = GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation(**row_condition_expectation)
        if isinstance(set_expectation, dict):
            set_expectation = GoogleDataplexDatascanDataQualitySpecRulesSetExpectation(**set_expectation)
        if isinstance(statistic_range_expectation, dict):
            statistic_range_expectation = GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(**statistic_range_expectation)
        if isinstance(table_condition_expectation, dict):
            table_condition_expectation = GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation(**table_condition_expectation)
        if isinstance(uniqueness_expectation, dict):
            uniqueness_expectation = GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation(**uniqueness_expectation)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e376f1c41b5978fa8a295c4026a5239bd024fa449e5f49061b3f011be9b68d19)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#dimension GoogleDataplexDatascan#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def column(self) -> typing.Optional[builtins.str]:
        '''The unnested column which this rule is evaluated against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#column GoogleDataplexDatascan#column}
        '''
        result = self._values.get("column")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the rule. The maximum length is 1,024 characters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#description GoogleDataplexDatascan#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_null(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Rows with null values will automatically fail a rule, unless ignoreNull is true.

        In that case, such null rows are trivially considered passing. Only applicable to ColumnMap rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#ignore_null GoogleDataplexDatascan#ignore_null}
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#name GoogleDataplexDatascan#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def non_null_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation"]:
        '''non_null_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#non_null_expectation GoogleDataplexDatascan#non_null_expectation}
        '''
        result = self._values.get("non_null_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation"], result)

    @builtins.property
    def range_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation"]:
        '''range_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#range_expectation GoogleDataplexDatascan#range_expectation}
        '''
        result = self._values.get("range_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation"], result)

    @builtins.property
    def regex_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation"]:
        '''regex_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#regex_expectation GoogleDataplexDatascan#regex_expectation}
        '''
        result = self._values.get("regex_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation"], result)

    @builtins.property
    def row_condition_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation"]:
        '''row_condition_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#row_condition_expectation GoogleDataplexDatascan#row_condition_expectation}
        '''
        result = self._values.get("row_condition_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation"], result)

    @builtins.property
    def set_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesSetExpectation"]:
        '''set_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#set_expectation GoogleDataplexDatascan#set_expectation}
        '''
        result = self._values.get("set_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesSetExpectation"], result)

    @builtins.property
    def statistic_range_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"]:
        '''statistic_range_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#statistic_range_expectation GoogleDataplexDatascan#statistic_range_expectation}
        '''
        result = self._values.get("statistic_range_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"], result)

    @builtins.property
    def table_condition_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation"]:
        '''table_condition_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#table_condition_expectation GoogleDataplexDatascan#table_condition_expectation}
        '''
        result = self._values.get("table_condition_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation"], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''The minimum ratio of passing_rows / total_rows required to pass this rule, with a range of [0.0, 1.0]. 0 indicates default value (i.e. 1.0).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#threshold GoogleDataplexDatascan#threshold}
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uniqueness_expectation(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation"]:
        '''uniqueness_expectation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#uniqueness_expectation GoogleDataplexDatascan#uniqueness_expectation}
        '''
        result = self._values.get("uniqueness_expectation")
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd8b5270b9482b6e386ae312db38951683bcb5df61daa473bcf073f1017252c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69e8cbef06a8ae3c8dd7fa7b47351c0e69d3a43a055607833d3316554a336a1a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26fe0341d3fbb025d31987651f167942aba2472d35f18b9fc4e6e7cc384e3d21)
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
            type_hints = typing.get_type_hints(_typecheckingstub__86037a8bd36b07b6f39c3d1e053471164930703f8c0db6004fbd856747ff0580)
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
            type_hints = typing.get_type_hints(_typecheckingstub__64d69afc8578765fd55a8354d7e7d46d0d36ec8f0c8e356b1639b063cf4e7204)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDataplexDatascanDataQualitySpecRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDataplexDatascanDataQualitySpecRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDataplexDatascanDataQualitySpecRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b6352d11edec9a922424e1844c1987d2e27b2fb328ad75044d3cbbf5d8d36f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef940f79c6fdbe1ae3f0720a76719cebae65d930192ac0eaa5b293dcfae91a02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d1d717f00cd039f5e8ba74df7a28f35e4aeb05deaec14d8a484345b910f116)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanDataQualitySpecRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d11168cf3e44f76466339e91fc88642cccf7a91a494627528fec7965ef284633)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNonNullExpectation")
    def put_non_null_expectation(self) -> None:
        value = GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation()

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
        :param max_value: The maximum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        :param min_value: The minimum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        :param strict_max_enabled: Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation(
            max_value=max_value,
            min_value=min_value,
            strict_max_enabled=strict_max_enabled,
            strict_min_enabled=strict_min_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putRangeExpectation", [value]))

    @jsii.member(jsii_name="putRegexExpectation")
    def put_regex_expectation(self, *, regex: builtins.str) -> None:
        '''
        :param regex: A regular expression the column value is expected to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#regex GoogleDataplexDatascan#regex}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation(regex=regex)

        return typing.cast(None, jsii.invoke(self, "putRegexExpectation", [value]))

    @jsii.member(jsii_name="putRowConditionExpectation")
    def put_row_condition_expectation(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation(
            sql_expression=sql_expression
        )

        return typing.cast(None, jsii.invoke(self, "putRowConditionExpectation", [value]))

    @jsii.member(jsii_name="putSetExpectation")
    def put_set_expectation(self, *, values: typing.Sequence[builtins.str]) -> None:
        '''
        :param values: Expected values for the column value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#values GoogleDataplexDatascan#values}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesSetExpectation(values=values)

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
        :param statistic: column statistics. Possible values: ["STATISTIC_UNDEFINED", "MEAN", "MIN", "MAX"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#statistic GoogleDataplexDatascan#statistic}
        :param max_value: The maximum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        :param min_value: The minimum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        :param strict_max_enabled: Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(
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
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        value = GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation(
            sql_expression=sql_expression
        )

        return typing.cast(None, jsii.invoke(self, "putTableConditionExpectation", [value]))

    @jsii.member(jsii_name="putUniquenessExpectation")
    def put_uniqueness_expectation(self) -> None:
        value = GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation()

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
    ) -> GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference:
        return typing.cast(GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference, jsii.get(self, "nonNullExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectation")
    def range_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference", jsii.get(self, "rangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectation")
    def regex_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference", jsii.get(self, "regexExpectation"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectation")
    def row_condition_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference", jsii.get(self, "rowConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="setExpectation")
    def set_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesSetExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesSetExpectationOutputReference", jsii.get(self, "setExpectation"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectation")
    def statistic_range_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference", jsii.get(self, "statisticRangeExpectation"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectation")
    def table_condition_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference", jsii.get(self, "tableConditionExpectation"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectation")
    def uniqueness_expectation(
        self,
    ) -> "GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference":
        return typing.cast("GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference", jsii.get(self, "uniquenessExpectation"))

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
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation], jsii.get(self, "nonNullExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="rangeExpectationInput")
    def range_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation"], jsii.get(self, "rangeExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="regexExpectationInput")
    def regex_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation"], jsii.get(self, "regexExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="rowConditionExpectationInput")
    def row_condition_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation"], jsii.get(self, "rowConditionExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="setExpectationInput")
    def set_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesSetExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesSetExpectation"], jsii.get(self, "setExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="statisticRangeExpectationInput")
    def statistic_range_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation"], jsii.get(self, "statisticRangeExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConditionExpectationInput")
    def table_condition_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation"], jsii.get(self, "tableConditionExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="uniquenessExpectationInput")
    def uniqueness_expectation_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation"], jsii.get(self, "uniquenessExpectationInput"))

    @builtins.property
    @jsii.member(jsii_name="column")
    def column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "column"))

    @column.setter
    def column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bf400fd2bec9551b6d2f51ef053a0d253a548b216a635c91cb302ea3bb7cdc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "column", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c82551e33daec270acdeb1e7416fb6bef46e9c369fa25ce56abf69cab8bf11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="dimension")
    def dimension(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dimension"))

    @dimension.setter
    def dimension(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae9caa52bd1cc2609624d3be9398a3cb51e73279f06a6949fbfecff42fe0e3c5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__046eba2767c71989670d72e46f855bd91a05be8efc514cb2913474c0c79158fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreNull", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d7c6f604d24f8a0847a020834e0df9cd3b6f97d5fe67e64d181f5458308f4fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f6fb671e29751d74b5c22fb21373625f33a09c4b42fc9ea87125e534e74e8d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanDataQualitySpecRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanDataQualitySpecRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanDataQualitySpecRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb241dab5dc33ac5bc3968a1797933ac1633700169cda4d6eda5e40f97ae3344)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={
        "max_value": "maxValue",
        "min_value": "minValue",
        "strict_max_enabled": "strictMaxEnabled",
        "strict_min_enabled": "strictMinEnabled",
    },
)
class GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation:
    def __init__(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
        strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param max_value: The maximum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        :param min_value: The minimum column value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        :param strict_max_enabled: Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4b414d3d7e333119b8e12c982673609d628702eed4b23ad0f50bab64adc424)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        '''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''The minimum column value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        '''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def strict_max_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether each value needs to be strictly lesser than ('<') the maximum, or if equality is allowed.

        Only relevant if a maxValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        '''
        result = self._values.get("strict_max_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def strict_min_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether each value needs to be strictly greater than ('>') the minimum, or if equality is allowed.

        Only relevant if a minValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        result = self._values.get("strict_min_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4dd5243f413a6df2840a10e6585af2b02c0ed2cb77219f83a4e613822cd83fb9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4b5f776d57f75e1404c24d5ec3cf9f5f5c2c86d28e4c869f57b068e543d604e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxValue", value)

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14f7174ff1155566d3459c3cf7aaecfe313eef3e930bb3577e60b66aa9e5b863)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e2aee641ebf6b38284c82c3557682aff9ab15a81267896193068333a50b38db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__958f2916c64dffc6ce244f7ed58d2bdcca85ce3260170a59bc6ecb10a50ed75c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMinEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c935b3ed3c157a69309d74a358def203213fdd1dfb2b688dd655a4a88be4164e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation",
    jsii_struct_bases=[],
    name_mapping={"regex": "regex"},
)
class GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation:
    def __init__(self, *, regex: builtins.str) -> None:
        '''
        :param regex: A regular expression the column value is expected to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#regex GoogleDataplexDatascan#regex}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc3a57da8b0146008969ed6441bc81c165bc7ca66b9fac88e4a61039328bc886)
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regex": regex,
        }

    @builtins.property
    def regex(self) -> builtins.str:
        '''A regular expression the column value is expected to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#regex GoogleDataplexDatascan#regex}
        '''
        result = self._values.get("regex")
        assert result is not None, "Required property 'regex' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00e8b9bf42b9775f4ef9c8b9d1124e94f6095e15b59255bdb1b273d8b77d3a09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb18a3b6cd0e5eca9b09395e01f29a1df5a26f0ee65360b05b9ec391710de38d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf1a1c2bebcd22d0158010e62477d5b11a036f4315d8af038956903c1f15dac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={"sql_expression": "sqlExpression"},
)
class GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation:
    def __init__(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a5f93314527070e833bb4afca8aae2bfb8490fea6dc2538826b57c2df97644)
            check_type(argname="argument sql_expression", value=sql_expression, expected_type=type_hints["sql_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sql_expression": sql_expression,
        }

    @builtins.property
    def sql_expression(self) -> builtins.str:
        '''The SQL expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        result = self._values.get("sql_expression")
        assert result is not None, "Required property 'sql_expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf3d6b81dfb49491ec32afe71931b4420b32833e4e3370374b3a27c3340f3b49)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce80b3f3833c3f0b7eea5bee8c0623b122400b2580601df52c9563b344eb9fac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlExpression", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33812848c8169e69522506323843708b1a854b5dfcf2a0f4f225b79bc8e1f1b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesSetExpectation",
    jsii_struct_bases=[],
    name_mapping={"values": "values"},
)
class GoogleDataplexDatascanDataQualitySpecRulesSetExpectation:
    def __init__(self, *, values: typing.Sequence[builtins.str]) -> None:
        '''
        :param values: Expected values for the column value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#values GoogleDataplexDatascan#values}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c643dfa7d06ad659dfa58e71e67f30f450602cc279de827c43ab9776875ec6c)
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "values": values,
        }

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Expected values for the column value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#values GoogleDataplexDatascan#values}
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesSetExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesSetExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesSetExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6f2eb73d5cb414facc8000ac24e39b91a674fe1ffefe9537c6f6d195c764811)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7c3adc2ffe604c19cbef2061f952e0219b1334abd1eeb856610059a439c84fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesSetExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesSetExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesSetExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc881f51ff32ec764eb9f37f4d8916d6aef7ca0ba5c76676d62d75efcc648eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation",
    jsii_struct_bases=[],
    name_mapping={
        "statistic": "statistic",
        "max_value": "maxValue",
        "min_value": "minValue",
        "strict_max_enabled": "strictMaxEnabled",
        "strict_min_enabled": "strictMinEnabled",
    },
)
class GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation:
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
        :param statistic: column statistics. Possible values: ["STATISTIC_UNDEFINED", "MEAN", "MIN", "MAX"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#statistic GoogleDataplexDatascan#statistic}
        :param max_value: The maximum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        :param min_value: The minimum column statistic value allowed for a row to pass this validation. At least one of minValue and maxValue need to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        :param strict_max_enabled: Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed. Only relevant if a maxValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        :param strict_min_enabled: Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed. Only relevant if a minValue has been defined. Default = false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3232af862ab588343e902bf04cea71f8fed66526f05b90d24fe281e2a76ff539)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#statistic GoogleDataplexDatascan#statistic}
        '''
        result = self._values.get("statistic")
        assert result is not None, "Required property 'statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_value(self) -> typing.Optional[builtins.str]:
        '''The maximum column statistic value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#max_value GoogleDataplexDatascan#max_value}
        '''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''The minimum column statistic value allowed for a row to pass this validation.

        At least one of minValue and maxValue need to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#min_value GoogleDataplexDatascan#min_value}
        '''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def strict_max_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether column statistic needs to be strictly lesser than ('<') the maximum, or if equality is allowed.

        Only relevant if a maxValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_max_enabled GoogleDataplexDatascan#strict_max_enabled}
        '''
        result = self._values.get("strict_max_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def strict_min_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether column statistic needs to be strictly greater than ('>') the minimum, or if equality is allowed.

        Only relevant if a minValue has been defined. Default = false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#strict_min_enabled GoogleDataplexDatascan#strict_min_enabled}
        '''
        result = self._values.get("strict_min_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92e0bb24272723da7a63fd637747765406c21ee999f9dfb5aee544d995c51044)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e04ec0dc296133d592ba6c05f26ca6287482504a7ac658dfcb3db9f1ed6e74f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxValue", value)

    @builtins.property
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4229f1f703fe4dce97c21f29bd720e42bbc4464c54789637429ee57dd942d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minValue", value)

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00a3e385e814c38ac13f1d8efd2dd76ac25bd50b798c4aa1de47694515b076fc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__83451d2589c49f8bba5c06bcb39df91b1f5e8d55ca0493db473cc2db6ee71a0e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa838ed813b6fd36a4d5666487c0fb7116dcb16ec4b4c098a3b6e9a5b53ea161)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strictMinEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a80b3f2c30d4e7b538482dcb4ae82b6b2ac6912fe314ee096da3c39d4147d9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation",
    jsii_struct_bases=[],
    name_mapping={"sql_expression": "sqlExpression"},
)
class GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation:
    def __init__(self, *, sql_expression: builtins.str) -> None:
        '''
        :param sql_expression: The SQL expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__835d51e0ab1bedb9a7885e9e5cf5e4eccb03360b8d37929babb04533bfde3eca)
            check_type(argname="argument sql_expression", value=sql_expression, expected_type=type_hints["sql_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sql_expression": sql_expression,
        }

    @builtins.property
    def sql_expression(self) -> builtins.str:
        '''The SQL expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#sql_expression GoogleDataplexDatascan#sql_expression}
        '''
        result = self._values.get("sql_expression")
        assert result is not None, "Required property 'sql_expression' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89771a66295f1e631b641c8e586d0c7266f66e89e5eb584f21a7928b8f78cb28)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5741a4b8ab3f8613ed076b8712f4c751911bed75c16d1d074a6ce9e7d09a8e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlExpression", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98aa5f646fb857c3b47f1a61c70d5fe4dc950322be4a935a0afc17af27bedc74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9595fc27e4b61f7574dbc2481e82267c6756483a0fe63edc3e5549dc71088c95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17bf9d73d310b362832d112aa0e4ffe46166c82661a05f20593747c66dc8bf57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpec",
    jsii_struct_bases=[],
    name_mapping={"trigger": "trigger", "field": "field"},
)
class GoogleDataplexDatascanExecutionSpec:
    def __init__(
        self,
        *,
        trigger: typing.Union["GoogleDataplexDatascanExecutionSpecTrigger", typing.Dict[builtins.str, typing.Any]],
        field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#trigger GoogleDataplexDatascan#trigger}
        :param field: The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time. If not specified, a data scan will run for all data in the table. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field GoogleDataplexDatascan#field}
        '''
        if isinstance(trigger, dict):
            trigger = GoogleDataplexDatascanExecutionSpecTrigger(**trigger)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab2cccb86f1095c5189e4bee722b6b30850fdca3d9509cea4751a599a1b8340e)
            check_type(argname="argument trigger", value=trigger, expected_type=type_hints["trigger"])
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "trigger": trigger,
        }
        if field is not None:
            self._values["field"] = field

    @builtins.property
    def trigger(self) -> "GoogleDataplexDatascanExecutionSpecTrigger":
        '''trigger block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#trigger GoogleDataplexDatascan#trigger}
        '''
        result = self._values.get("trigger")
        assert result is not None, "Required property 'trigger' is missing"
        return typing.cast("GoogleDataplexDatascanExecutionSpecTrigger", result)

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''The unnested field (of type Date or Timestamp) that contains values which monotonically increase over time.

        If not specified, a data scan will run for all data in the table.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#field GoogleDataplexDatascan#field}
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanExecutionSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanExecutionSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__295f3cb05a2febd68a2c4bb2040b4b91d8e9411aae9566407b2e216ed4c15824)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTrigger")
    def put_trigger(
        self,
        *,
        on_demand: typing.Optional[typing.Union["GoogleDataplexDatascanExecutionSpecTriggerOnDemand", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["GoogleDataplexDatascanExecutionSpecTriggerSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_demand: on_demand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#on_demand GoogleDataplexDatascan#on_demand}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#schedule GoogleDataplexDatascan#schedule}
        '''
        value = GoogleDataplexDatascanExecutionSpecTrigger(
            on_demand=on_demand, schedule=schedule
        )

        return typing.cast(None, jsii.invoke(self, "putTrigger", [value]))

    @jsii.member(jsii_name="resetField")
    def reset_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetField", []))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> "GoogleDataplexDatascanExecutionSpecTriggerOutputReference":
        return typing.cast("GoogleDataplexDatascanExecutionSpecTriggerOutputReference", jsii.get(self, "trigger"))

    @builtins.property
    @jsii.member(jsii_name="fieldInput")
    def field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerInput")
    def trigger_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanExecutionSpecTrigger"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanExecutionSpecTrigger"], jsii.get(self, "triggerInput"))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @field.setter
    def field(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cec770227190d2d092b97d3a603b1bc0a8b07529dc3f6fc545dea23c5d4326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "field", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDataplexDatascanExecutionSpec]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanExecutionSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d734ae4ee7cef69e3c30cf3e4381203dcaa804cf398cfafd5cf1efb2b5712587)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTrigger",
    jsii_struct_bases=[],
    name_mapping={"on_demand": "onDemand", "schedule": "schedule"},
)
class GoogleDataplexDatascanExecutionSpecTrigger:
    def __init__(
        self,
        *,
        on_demand: typing.Optional[typing.Union["GoogleDataplexDatascanExecutionSpecTriggerOnDemand", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[typing.Union["GoogleDataplexDatascanExecutionSpecTriggerSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param on_demand: on_demand block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#on_demand GoogleDataplexDatascan#on_demand}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#schedule GoogleDataplexDatascan#schedule}
        '''
        if isinstance(on_demand, dict):
            on_demand = GoogleDataplexDatascanExecutionSpecTriggerOnDemand(**on_demand)
        if isinstance(schedule, dict):
            schedule = GoogleDataplexDatascanExecutionSpecTriggerSchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dccafcabfad265695008687cd71967dece3226dc50cd484830e4a33839348a33)
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
    ) -> typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerOnDemand"]:
        '''on_demand block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#on_demand GoogleDataplexDatascan#on_demand}
        '''
        result = self._values.get("on_demand")
        return typing.cast(typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerOnDemand"], result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#schedule GoogleDataplexDatascan#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanExecutionSpecTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTriggerOnDemand",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanExecutionSpecTriggerOnDemand:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanExecutionSpecTriggerOnDemand(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanExecutionSpecTriggerOnDemandOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTriggerOnDemandOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad93d9fd51ff8465c0f704de65eab9fab725d4b6ec4c3ec4b3405ce0d6862e7e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaa5e3e115eddb48da606bd280f681d21e241ac5a23fc3b6e933c318f7f7aaa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDataplexDatascanExecutionSpecTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d15d67096ec5f36b2394e6ca3bf313ba737845fb77faf8227406c070f3df514)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOnDemand")
    def put_on_demand(self) -> None:
        value = GoogleDataplexDatascanExecutionSpecTriggerOnDemand()

        return typing.cast(None, jsii.invoke(self, "putOnDemand", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(self, *, cron: builtins.str) -> None:
        '''
        :param cron: Cron schedule for running scans periodically. This field is required for Schedule scans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#cron GoogleDataplexDatascan#cron}
        '''
        value = GoogleDataplexDatascanExecutionSpecTriggerSchedule(cron=cron)

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetOnDemand")
    def reset_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemand", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="onDemand")
    def on_demand(
        self,
    ) -> GoogleDataplexDatascanExecutionSpecTriggerOnDemandOutputReference:
        return typing.cast(GoogleDataplexDatascanExecutionSpecTriggerOnDemandOutputReference, jsii.get(self, "onDemand"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(
        self,
    ) -> "GoogleDataplexDatascanExecutionSpecTriggerScheduleOutputReference":
        return typing.cast("GoogleDataplexDatascanExecutionSpecTriggerScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="onDemandInput")
    def on_demand_input(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand], jsii.get(self, "onDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(
        self,
    ) -> typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerSchedule"]:
        return typing.cast(typing.Optional["GoogleDataplexDatascanExecutionSpecTriggerSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanExecutionSpecTrigger]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionSpecTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanExecutionSpecTrigger],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd2ef8a2af41d32bfd5ada6c0fc2f5375a193080292c25fbab2f21e1d7184340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTriggerSchedule",
    jsii_struct_bases=[],
    name_mapping={"cron": "cron"},
)
class GoogleDataplexDatascanExecutionSpecTriggerSchedule:
    def __init__(self, *, cron: builtins.str) -> None:
        '''
        :param cron: Cron schedule for running scans periodically. This field is required for Schedule scans. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#cron GoogleDataplexDatascan#cron}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bafbf847196351ee37c16744c5f4b467dae1055c2c3bf01f9a68f2635c2963b)
            check_type(argname="argument cron", value=cron, expected_type=type_hints["cron"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron": cron,
        }

    @builtins.property
    def cron(self) -> builtins.str:
        '''Cron schedule for running scans periodically. This field is required for Schedule scans.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#cron GoogleDataplexDatascan#cron}
        '''
        result = self._values.get("cron")
        assert result is not None, "Required property 'cron' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanExecutionSpecTriggerSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanExecutionSpecTriggerScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionSpecTriggerScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91dbd142508976f3f77a246d0fde6b1a02b89ba0abc37d54364b37acaa60ed55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__32b16a3d8e8a92af04b190a854e691e13944f3abc6e7c40b4ebe324051bc4721)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cron", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerSchedule]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerSchedule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a95a0eeb1bb19aee26ab08298e41449fe9040d750ceca50260811e0694db80b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class GoogleDataplexDatascanExecutionStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanExecutionStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanExecutionStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dc22b9b63c5ef1d28df72c29ef65fc99424ac52dc9734bd318ffc4b05b92ca4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDataplexDatascanExecutionStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ac60a4ce6d010a5cfa154406432a82e5bfc5260c000da5e41df2bdd308b1190)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDataplexDatascanExecutionStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad79775ea7d37d03500396ca75ec7f7058a478f06ab4a648ef4f3a900b3ae2c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8b57e2dc0c7e9c32d18774d3265aa5c927f17724011eb368c852c81e9449421)
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
            type_hints = typing.get_type_hints(_typecheckingstub__39739365ae08d8a951f94383dc9894c1330414e5ac1f0b3867c117dbfc05849f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class GoogleDataplexDatascanExecutionStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanExecutionStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50541958be153baa1f575e922a568b4f4700f39b959b54b49aaa3fcd124aeff6)
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
    def internal_value(self) -> typing.Optional[GoogleDataplexDatascanExecutionStatus]:
        return typing.cast(typing.Optional[GoogleDataplexDatascanExecutionStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDataplexDatascanExecutionStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07cfd8638887327f045148af648c9e8bdd95f87ec98eaa251e003cc27966d6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleDataplexDatascanTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#create GoogleDataplexDatascan#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#delete GoogleDataplexDatascan#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#update GoogleDataplexDatascan#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3780ff55a1ac6226caa9f36c297f313b1d2c5008bf37ea5094033bc964c4d88d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#create GoogleDataplexDatascan#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#delete GoogleDataplexDatascan#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.82.0/docs/resources/google_dataplex_datascan#update GoogleDataplexDatascan#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDataplexDatascanTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDataplexDatascanTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDataplexDatascan.GoogleDataplexDatascanTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66f13ff76172540ef7b56705d1491bf8829078e76e331edca21b0c712c86d63a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e417c1dea229e831995de0729ae4cb4394e91642862488a1cad722f9591e83ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2159c4446b0e3ba67a660c510c054c26ca6e59fe55a7b90f8d42449b8f131de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__111a7bb1a80cdc1120f5d0b99a519ae2419deb4bf72bb480f34b229b8a6e8bc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__260835a5be1fbeafee1df2b881eb9436567d581ba90170fadc358313317743f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleDataplexDatascan",
    "GoogleDataplexDatascanConfig",
    "GoogleDataplexDatascanData",
    "GoogleDataplexDatascanDataOutputReference",
    "GoogleDataplexDatascanDataProfileResult",
    "GoogleDataplexDatascanDataProfileResultList",
    "GoogleDataplexDatascanDataProfileResultOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfile",
    "GoogleDataplexDatascanDataProfileResultProfileFields",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfile",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfileOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfileOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfileOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesList",
    "GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValuesOutputReference",
    "GoogleDataplexDatascanDataProfileResultProfileList",
    "GoogleDataplexDatascanDataProfileResultProfileOutputReference",
    "GoogleDataplexDatascanDataProfileResultScannedData",
    "GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField",
    "GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldList",
    "GoogleDataplexDatascanDataProfileResultScannedDataIncrementalFieldOutputReference",
    "GoogleDataplexDatascanDataProfileResultScannedDataList",
    "GoogleDataplexDatascanDataProfileResultScannedDataOutputReference",
    "GoogleDataplexDatascanDataProfileSpec",
    "GoogleDataplexDatascanDataProfileSpecExcludeFields",
    "GoogleDataplexDatascanDataProfileSpecExcludeFieldsOutputReference",
    "GoogleDataplexDatascanDataProfileSpecIncludeFields",
    "GoogleDataplexDatascanDataProfileSpecIncludeFieldsOutputReference",
    "GoogleDataplexDatascanDataProfileSpecOutputReference",
    "GoogleDataplexDatascanDataProfileSpecPostScanActions",
    "GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport",
    "GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExportOutputReference",
    "GoogleDataplexDatascanDataProfileSpecPostScanActionsOutputReference",
    "GoogleDataplexDatascanDataQualityResult",
    "GoogleDataplexDatascanDataQualityResultDimensions",
    "GoogleDataplexDatascanDataQualityResultDimensionsList",
    "GoogleDataplexDatascanDataQualityResultDimensionsOutputReference",
    "GoogleDataplexDatascanDataQualityResultList",
    "GoogleDataplexDatascanDataQualityResultOutputReference",
    "GoogleDataplexDatascanDataQualityResultRules",
    "GoogleDataplexDatascanDataQualityResultRulesList",
    "GoogleDataplexDatascanDataQualityResultRulesOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRule",
    "GoogleDataplexDatascanDataQualityResultRulesRuleList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation",
    "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationList",
    "GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectationOutputReference",
    "GoogleDataplexDatascanDataQualityResultScannedData",
    "GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField",
    "GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldList",
    "GoogleDataplexDatascanDataQualityResultScannedDataIncrementalFieldOutputReference",
    "GoogleDataplexDatascanDataQualityResultScannedDataList",
    "GoogleDataplexDatascanDataQualityResultScannedDataOutputReference",
    "GoogleDataplexDatascanDataQualitySpec",
    "GoogleDataplexDatascanDataQualitySpecOutputReference",
    "GoogleDataplexDatascanDataQualitySpecPostScanActions",
    "GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport",
    "GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExportOutputReference",
    "GoogleDataplexDatascanDataQualitySpecPostScanActionsOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRules",
    "GoogleDataplexDatascanDataQualitySpecRulesList",
    "GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesRangeExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesRegexExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesSetExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesSetExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectationOutputReference",
    "GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation",
    "GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectationOutputReference",
    "GoogleDataplexDatascanExecutionSpec",
    "GoogleDataplexDatascanExecutionSpecOutputReference",
    "GoogleDataplexDatascanExecutionSpecTrigger",
    "GoogleDataplexDatascanExecutionSpecTriggerOnDemand",
    "GoogleDataplexDatascanExecutionSpecTriggerOnDemandOutputReference",
    "GoogleDataplexDatascanExecutionSpecTriggerOutputReference",
    "GoogleDataplexDatascanExecutionSpecTriggerSchedule",
    "GoogleDataplexDatascanExecutionSpecTriggerScheduleOutputReference",
    "GoogleDataplexDatascanExecutionStatus",
    "GoogleDataplexDatascanExecutionStatusList",
    "GoogleDataplexDatascanExecutionStatusOutputReference",
    "GoogleDataplexDatascanTimeouts",
    "GoogleDataplexDatascanTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__2b75755b3c8adc167bae1e1f8a24d7bb2c1b6243910517d6f741f2aee0ba268b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    data: typing.Union[GoogleDataplexDatascanData, typing.Dict[builtins.str, typing.Any]],
    data_scan_id: builtins.str,
    execution_spec: typing.Union[GoogleDataplexDatascanExecutionSpec, typing.Dict[builtins.str, typing.Any]],
    location: builtins.str,
    data_profile_spec: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    data_quality_spec: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpec, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDataplexDatascanTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1487eaec96f2e492b2bc43261f8a86cb627fc93d5ca199343384412342422424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a56706c889c2452c3c5a2ce68c0caf2adc06a89572652f1dc03c4e1ab732c882(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2276e334fbf3a651534429d22bd47b54754f913ab18dd7b25799e22d6f5c7ae3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df77bf10b0bf3909950533b166bb7af59a46e0dd8152657a64fa1d97e5d4d017(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac6ca0c81605251cdad7d60e66e5874660bab42cc52ca5d25d4cd5637659a44(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c78e451aa48de509e9aaef430a53ffa2e819243bd60fe824623fd44bd593ec4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f58a35f36b5857e569f0cb40b1d9d0dcd56105f641b7bc7bb30112ccffc636a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29bf5a36a233e10710bc2fa54eb590a6ee25dc382266c69ce4105fbf01fe14ac(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data: typing.Union[GoogleDataplexDatascanData, typing.Dict[builtins.str, typing.Any]],
    data_scan_id: builtins.str,
    execution_spec: typing.Union[GoogleDataplexDatascanExecutionSpec, typing.Dict[builtins.str, typing.Any]],
    location: builtins.str,
    data_profile_spec: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    data_quality_spec: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpec, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDataplexDatascanTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__232fe999855133d6d7fe98d528ae2c1330797fd36d97e65b26b5da6f2e5b65d3(
    *,
    entity: typing.Optional[builtins.str] = None,
    resource: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88d58e36161fce3ac6bb35c284a7365ee2d1f39e5852e21e1b536ae561e88597(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3116bb5ff0968f2f9e4c444578df05eca0f41d0efea09dd09abbad116026827e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7b975a6a2b1f01a5376ebfe5be1006dee8ee322866cf6ef5b9625356a4762c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea13e3372d0975e7ab4d5cb8a2f2a8e6f084369ce1fb16946086356f648f5a0e(
    value: typing.Optional[GoogleDataplexDatascanData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__219a665f84280a2c1a74587a8e66ba78c4d0f10efdffc2913561e9bd33378fc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a9441091f6266bfab11937dccf3e0b02bbf651a34fedc43403c904f94261585(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__952373c20d22b48b63396c140caa01ca8fe3a6571cf8d5a0cd5a3abeae20a224(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10a6526a1d6ce77bd38232fa83db2501991825ef535522e3f50387d7f7df4e46(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e6df302cfc622275d3a96f1ab453d3bce00ceabc7aeeaaec4d73a604dba4577(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58ba5f92ceb645904711a372993f84f9a6da8688c060efead520b4b72b6479d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ba3f04afeda29e6008efa2a3d3c3f4b8f716400fca4b55b51c509f5956fad42(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da0fbc02f0edeaf47dc1fed442aa77aec745a5fd521238c8fc862fef72ef04a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3dd51b67cc7318b2e6e6c7dbc766720860d386d3698f229ee9906d0ac09470e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd252d4d1a03c6937fea5d491b400c98fb020f8e8dacddc8a17617328bbb4452(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f8a022fe01793e26e4481ebf0218b58506e3011694496d96226997e73b31f58(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb5928a2efa691c8b00d754cdc014af5bdbcaba07e7768bc17990536db8ebee5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aa3223ee045917338be8ac7759f0a0d3b10e108b4d614d5471811d66fc0f98d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca795b5f54cc29b19b429f01932ddc187cbb2814730590642b3797994984737(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64a6f92b240be3f0c30409775e6f25feed7b314a2fbd7122774a07ca2cc2b81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d15166afdec38847605dde23eca758778d4c16569a77c4bc5d837079f72981e0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4faafe0b0a2e0bda3d56dd417b7afc8320706ef525ecc5e54dc92361a84b08b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02c40e062bbaeded53b3c11ba711dd8d3af9ac6d6c8b7f9cf01bc83b08e44e67(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb22b9956500ac906e82deb5f55839553e5715a2493f4dedd05db73bad8d7cd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1938f892b4da6880c26445d21046ab2782beea48b0692cdb6c1e15ab96ce2a12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5c029a97183189910585e0c121b3a425ed41fd31874e494df7e291793f0ed15(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileDoubleProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cd99e8605cf936054074d63918186c6998cd23fe649ef47a147885927242134(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4962877aa5f5a40e61bd595e57f753cc2d5c79a4c4ee7699f10b53b0cc350703(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4798740007177bbb1dee52fecc014fb2f4c38d98da1a87be185147c789ec37f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c320d5db3d127c3d4fd6a296e82b51b380032319caf4557655d444c1a86fec1e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0beb6d5e30bbb39c805528304662011fff8c7417ad90e5db966fc020909fd5c5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afb55eb1c85c1a98c8d99ae46290934e72043ec2d77107d74b7de2edc5dd5084(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__806e2dfb1cd6064ab11037adccf47d7aa393b37029be9ed8b3dc49997d1f26cf(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileIntegerProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__007294c1a32ab7b5b01372bdd422af7d0b0ee24e3c5485658aaa7555d9df319e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5df3227ff836573a93ce75d8676c659617001f82a1e77eacfdb98bba3950ce7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a46a1c42b631cd0f094d75174b74632069387606e6770ab398091135f884bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be60db7da9f5af3b3362831842f6a6a2102f7bfc14b9cc35516b71a942c556af(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a832ff0c5fdf98c503ab30abaf8d4eacb49951c2003de874c41670f130cb3e09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af69ac2d9e77ce8ad1446f18486dd6839afcaa6377ac95f3df419edbc231003c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__559f4eaaa934d437bd0b57ec71be55ef18fba0e0164662eb945e68255556ab38(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b43798393a5ee55226327d768315ec9b3925699b155483b86282e3757bb1ac6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b186f11a5adae26ff392893d8b3f29c909e71f893f4d6354c7dd3aa79ee3e37(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794e17dbb34638e8bb161614c8b9017d2fa9aed4e6dab5a882cba46d11b42316(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93eb4562331f3570e7930b39f55e71845e5ae5dd129446d1521b93d848ff43ae(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ebf04ead29ba2f363c9aa54f770d3cd0106359e1b4d959b04bc29830327214(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102667e91f61f8d94f1e0be2f66ca6f7dcc2d263c7d27a567965c800bca96d1a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ee1fe49f8db8c55674e9f6f478dc0585d790f6530a7d031bc5ab926bb70697(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileStringProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f056b75e4aabe1a5fb1f1e6a41cb802efa7931eabdd145e152220d7b0dc05f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00b0bfb275e3a287e8386cf1c78975c9d68796d63e491318cce975b6bad373e7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f8b577cd8cf6100f3268968d40d98f030d9b7b7c57eadbabefc0c95909868be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c6c7a0f6164d61347695c7a57da1b51f009121331da3ad9beb11d2ffb3bf2d7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ba161e1a810ebeb74c759bec112924b296e4893f68afa9091ed18b2c6f07ef(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a57b4da9789eb9978d52e39146f375b6d37547d711edff90afef3476bfa6054a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb925339576ef7f1c884f19927089b586e25bb49e5ec3c0010ca42da76844055(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfileFieldsProfileTopNValues],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5505f23a32055c4407df5bd0d06f3989464249633f677b0c8cfa796d8dcc333a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9ecdfc4e1615d5c7b7f994a93d83ba4ff14a0cc87742c03ae46ea4fccc89426(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c71312811d5f1e59e90a405290cff1799465216f598362ee243b2c661475703(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2062457488e8d54d1711515067d8496d6fc4c1012353ffe494ce2cabb8386d95(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10cd615937e20a72ac80c62554ad3044df0a800361e0b07b3b2ecf4be91f0907(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed55f148deb0642cc067e8140dfced91a62f2911cf072de5bf02cd7c0bdda533(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b39cc041e71b50f12e470aa390b4436073c09adaf0dd5ba337f64c0776a688(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c3861627c2a1a44f44ee0d6445f41e365600587ba1e0b661262cd25489e9f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b28fad4c4dbeb7d88b2122b74713b08e42b17c227e76e6cfd67b25906c3f48e1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a52adaf83331a0c00d2a009f4b7b037db304556a5ed52a0e85e4cb90dbd380e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a249fc9bd8c627c7a4851e4cad02751d535a0e3d833f104e110ff2bb42411807(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f5e49a54968f545a6da079a5840ce4b212749938c53d3c3365f0fc3e2750636(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57dd95a45e5f3f6ad2633e22db9769a0f2c182a5ffa3f8f0acf0b68d47b0c3b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__362262306644e15f07bb0300d0e576dcef3fda135cd94aaae109a71b261885c7(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultScannedDataIncrementalField],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78ae689121eb9f75e04e9d939288ac1769ef2db3cb0b18b49a1dccf362775d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548e152beb83bf8e372b74d16534bc013f248d3f2b59813a5ac8a721ec9211fd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d130d472b384d45ab44a174102f31cbd18643085af92e57852a4ca747a47cbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70621b260d37f2b0648d572183df525eb50bb2aaf0b8bc4c1014255841a8cc6e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__417d5d8cd747a19220de4fc3506d83004856aa4ed102bc1a532cf3bc637f8405(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__112c094ec0ef17ff2abcd5718c819ac5238cd37c813c3d469c265e7a015ea021(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__747215d957c226e18aca2b4434d7a3d36ba105aebbcfab1c0c61a58d2f96de41(
    value: typing.Optional[GoogleDataplexDatascanDataProfileResultScannedData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a51055e7828267c97aaa54c02d861769b5cf595e67db1313ae57329eea8156(
    *,
    exclude_fields: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpecExcludeFields, typing.Dict[builtins.str, typing.Any]]] = None,
    include_fields: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpecIncludeFields, typing.Dict[builtins.str, typing.Any]]] = None,
    post_scan_actions: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpecPostScanActions, typing.Dict[builtins.str, typing.Any]]] = None,
    row_filter: typing.Optional[builtins.str] = None,
    sampling_percent: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1a193c088db579359dc7dfa6f1c9b20e61514e1bd98b89e007cda67bccc6ce1(
    *,
    field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32d9924faf7fa246b468ce1611cb28caf0f8be4419263c32734d62f089d54936(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcbcc77baf394088c82f9ad5a21875ed3657fd2376373bdbc0940253492c0bef(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f290f47e1eebf32bfe48c1099a75ce4a85646a9fa825a7f0ab7ed312121107(
    value: typing.Optional[GoogleDataplexDatascanDataProfileSpecExcludeFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d9c3f5a0c27583808594eb832ec01d3eff6b1805052078d1de1d6d3afdf74a(
    *,
    field_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa3259d8ae0197431d19f511490dd65b63cc096aa5af02c5814eeb33aa5e8fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3d66efd627effb07b4f03aefa7a9d07f5698220fe1e90c594f8fe103ac4a1c0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02966e63e35bd012877e24a23b6093481451dbd1ff2dfb7594737d3cc8dea736(
    value: typing.Optional[GoogleDataplexDatascanDataProfileSpecIncludeFields],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__399de5748abecf07b0dc2baedd1baf6f0a1443d3e4e120083c38a52b528712f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__053d767626cf6e94f64bd044ead742767a5d97c5de6408015cc9cd635dc35482(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2432fc32786757572a15ef847909774565e0c1701f725f9f12e00c6dfc327872(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3f90e3eb1d1a30e6f9992c1f44482212abdcd67bd8db317bbc243f9fab8955(
    value: typing.Optional[GoogleDataplexDatascanDataProfileSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5385f3c9814fce97c6d191a85b483b3d5c2fe85b2e304fbb164700c134839272(
    *,
    bigquery_export: typing.Optional[typing.Union[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01b098c394196414410d25a073bca6df7125099da1e1bb817b929f6ff10a5147(
    *,
    results_table: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40eb1edc264383e48f92ea2cb895616fa32d27ad88e55771416a41bb2c53f2b6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43b750538cee11e551dcdc173ef75a7582bb4dbb2a6a906bbc6c9de7b8834661(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d591d7aa3772437d125d2c4e1c1605c4adec99c0f99c5828f2b94685c37d3855(
    value: typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActionsBigqueryExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9b9d0b2ddfd5b991f0fe74d3ae52f701bffb42a1275c6b9a30bc08140bf945(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0348030eca89fe041798f21022b4824063a3b23f122f4a9af40a25bd749fc32(
    value: typing.Optional[GoogleDataplexDatascanDataProfileSpecPostScanActions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0461962e9d9ea58805c204d3d44ba52f6251ed0f778174ffb1484750c5c3cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d3199b8250af3f24dbd82da8e9735501f7da740a1e1c3aaf99a7ac2ff35f8e9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cd8a83debd8aa05b2bff30e925dc08f5f164a398a734cc00728095d4860e295(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d39e4d19dab3a71a6aec3664d6bc65c676d81bff58937868a4e623e1025c603(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d874d73217963ca062f1191a96d441ff58c19993653b82a72cd1aa95990873d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8478d5f0f70cbbd650ddeb6888f742d92339098e6bcf1713f792e4fd368aba85(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebfedbb17d9f4a68cf4b0568f44c5cd747c13ed1f759f31ce7782c7ecdbebaba(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultDimensions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b822c4a5817fd277441d30f3a1da2da4e9ee830416f0e418d979a46efbd8b21d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d603a7db451acdf13efb1129c357719cd01902dc05c889bfc8668cc00ecc87(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b07e17dfa3ccf3fa08d9974c9581b01d1ed681e7c47d9921b9ab370b7eebe455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e293f9c5626ce52cf3d1892b7d701708ee2e954e6ab21828a9419c66e98939(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754f978dea0347751b0fa01a6495ebb64ce7da735681b3700674e59b177c18b4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712a1eabc9be6e0f2d1c93e1213e242c185b96ca4362e44af6967180639fe03d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccfed8229d78b684449be0d7e9a72397b627deee16f6fe07c40db5b9ef8beb9f(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31fcf951ddf960ce4b7be0bc7b6e8af235334e6c21714e4cac6168517d57789(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd4bfcecb705057d9ac7f2c74489bbfd01218337003301f847921c0c29d5429e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b904887ecd173502751a200fc8a3065f1ae29e162f17a8231167918350009415(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3991c141c30db003d301b9752a1c0013372f1a28f6aea08d488b58ccfdb4ef1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a21c5d8d413f838df0820b8f79f1c08cf018d4117bb7f21aa9cd2b24b0f44c3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1720cfd3f926e6771711f6013743574f0b0abfa2af2e230e76e31e3d55a83c6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9ab2e292a38b0553615ecc8fa38a12bf546a600828b99704849256dc5e85a28(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b570b3d92f5422e0969c2c835a4ab50967f7e83548c33fdb8e06271b27561deb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__846923835cbbd0c93ff4c828d1d3a9325a7e56bb116de4967e6dde5d14349c72(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33813d6ad6bec88008c37b4fd4301bae904a34a3c68a60b68c6b1fe0994c76c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2456e5d6d1bf0428b14b4bac8225b1a3f55b944efc440c00e6c188c7928fc836(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88549698945dbe83c0c2a8530fc3bd62879630daee3c03a47796b99bda29e115(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb3d8324bd7465d7287259c5e5c90d797fc44af05c61c43c55d82aa724bea3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c3079322505f47d17936946628bea35ea7ab263a3dca91c2f40d3f562c4885(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8553575a51df9ea3ae388bc2d78f0ad3ca2cf9c5946b1682b6219abd62d37ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b372472412c092aa720596e57ab57e955910c9152aabbcbd032b2ffe2829f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7b5e28c331d3a2b3f5cda709140b1a8a2411891118554d69fc2aff89d8efcf6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9718bb26a0f0b14446f748984fe45bd64c5ede9314adcfa492d1c88a111861a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b3a13727b6557a39af9ba48ae7ded2baea13faa643d3b6c67da4a7817857ddd(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleNonNullExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d3d53ee4e819f34c723ae89ebac1f1d1a3ddf8380df720646cca3320802126(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3da35bfc526a820fb8e6d0f5a188dd5a11d898c09ca63f37d28a8d32fd200d71(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b995a928dcf885403159dd6f4940a181e91b5cba74dc8dce0b6f3b7fb3932f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__918df9568c615598a3db3c9b343c5a49866d514fdb9f28d12d32234e33e404d2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9437bb7402b09c575570acde276b0861a826e8fb152eb3cc74b9754304d10500(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71031bf1199af740a5a74a9928a53bbe85c6ba448bdbc1ea253eee43169e9a28(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15eaa30d363593b2dcf6fa47d4e7acc7d5fcb5252721335e48988e1eeabcb301(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cb26c60bdab35f115a142b0b4c74ff1b2b5848defc01caa0acd4b163fdb8cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__520077185a4f331a4bb32fb2044b7edaef79ba43f0b5fdad486f7106930f7f27(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ba550a2a75c9be71843898a08f05c59e5d4be70b4793752aa341fe2e82c0f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3668c9aa78939f002e5d636149d620fc8fc660447b79bc1e0aa74a990b798d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3417faa92cc24a64089a3368d09babb0f334bbce8083f6dda72bc7f736f277bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8cc35197ec98c5dc8b712c74ca4c0c9654d8d27a0abf57a8ba3eab0f34667c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c499cd7b6c40d6c38aeba3d99b5e05dff836ea9a3968760b84048cdfdaf6c2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9026b8449bdae14cf1aa711a47e0a87fa9c8a9cee8a1c4f6a9d9bda3e983a3d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73532953f2fe9877a4e133cfdbea95120cdcf6a21b9fca34955282992805b761(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRegexExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c9c107acc43d1ab2b7de0fed4e22cda176d0b23dbb8f3d04d7798e6dcecfa6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e739946ac586d70cab134588017557d530b5e475748a92c8919279bc9ffd0cb0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c3c9af68da84fcb44cb7fdd52c3e16acb339800711b9c94c11399415ec2f31a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2524e628e63e3283eb7e7d6f356350403e03650604bc7da51ea17ca87ee9e6a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b4021aa9f0b11a310f9ca73348b940bd27193f4c99c66ab3ee6f3bf98ece9f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8903d80ec5b644609f3972fa504999228b058eca2e30cc9a3f5cfe62bab5ece7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b5ad85fe860609a879e06cb7208b4a49e0b2d7b413c7b5e25c7a6b24ace69e2(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleRowConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50d038d2b8c1192c324a6c1800c23e03357fae5a096f3d738eb05c15335fab2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b435e8176326b9ae7d2ca6137ff758e2107a4296617cb4dabd6be68271025bbe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506b2ab80660110f14aa6ffddb017e8259241485b7a6ca0f27702bb16ca9d916(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__247400a38763eeea92b487eb69ed5f84f1db085f4a970a59137b1931888ebfe3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db30cd3116361ef626be5cd7192fbaabdd787118e833e86e6a1736c2ef6e7d0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c9ecdcd9bb83a036df51f17d870d0df2f418824cf4110353b61001f7bef5836(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4070a5d78461ace2b1d72ab8df81d931c1219d979d6178487d2cbc4ba3ab0f(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleSetExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07da7c418b4e9a6cdcad90c6241d88351fb803e71d257e6fc2f693c9b0c7a882(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6017075c20f2a4e59d3c0f13abc3b15df3943740d9da50d670180b491551292(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1ac4b8cbc0bfc84e0e3264b55709feb91ec03eaece5c3d26a01234903d046ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00058d9c86ebaa7a98db790730c894f3741f18dccc5be0ed1de4bff1934836c9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10bc23b9675ec09a25283e8bbf14fd927e4c25005ad51a9d692c3b8e40de79c1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd88b0179384ceeb0946364f7a127349bbafc5a5705ddf228855358af5ce89d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42550a1659c7fafe0a0c51e2109b9ab9e6b90d9c3c3c3a1fbae21abc483f3a85(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleStatisticRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e52864f6d0c8f54d6cdedd1afb07ca08b45897154c847becb12a16806b2aca88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ad3e6450d4adb45f0bcfcd93812c35df867c01fc3b848187c42375d16c0b58d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d6eb8cc2b6186d95f43bcaf9dee81bfaa4d5061c73cf0fa4d943a51fa9bc571(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b331db61eb0d5f5c47d594785d91d7e1bad01650dcfed4b6b981516d5768293a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b9f1fd3affcbd106c08ae2fabd71794637138759cac45305f82a5a287d5a014(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b201d19dd345d8f332afdb8b8bf272e426923a6d1a89bbdecf51d7df287e942(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15591d144bc67b12016640d949de0bdd160b1dca1b93e8791a22defeb1b9659a(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleTableConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ff3bfb1531d7fb80dd3a6b9e95b9eacc55541cca555782ff63bee35b0f9867a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06693dfb87e380af6854a2602c1090548faf71975f3a1f603fa60d3b52e3da51(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e244b6c64006327145a93847ef54ab9f182be58cb6f9e83a9c2dde3656a7b1b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20110edd8cad0f75ee184e9659e4fb4c198509761595e76bc95b340d54f1ccc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2ea37285aa129f6021b47c091b19f23d4ad320b267963f290f4fb56570d760e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7d2737262572f3f078c802ea0a067d466133c127968bd9c002979e1239ecfc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296b8266d7b1bc27357e6d4e24d35f3e2a250dc1900f82736336ebc291435acc(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultRulesRuleUniquenessExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa4b87cdb0a0c72c242306140341c72d860039df0996a54427dcb0cb30bf6193(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac23171e5383895dee4757a3eb68da0f92f193d0d8ba68a22450183f1cce72e4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a4a4121ab022ce319e6ccca8a969def1e0f232d51bf32e229e272467389bce0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3da3d798fe90aecf6ab0ae08ccff4d22047cd267d505d56d6da1e5cc9a4f70ad(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e69178b2a7cdfcff33a0cccc9435a325c816e52b94cee5ca79d1e6256c37e5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c87561ed5e7854c1031ab3201187331cbc19fe5c595c1b2bec321f883ceff1a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b45f65bdd366223ab402a6cc7c675a6239f56bf97d94d9b66f9ef98883a847ca(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultScannedDataIncrementalField],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1c2f7f64f203c6d9c238a4fb88869cec1826f8a640e9106ed7343010b21ccb6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd91e652084424ec8d8381e74e4563826d7b392a794253221a8bce6e5fb932ea(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__049a0c03dd2948fb8794f09e779947172eca5eb31795c586237c4b8db2fbc5ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfd59b7efcb07e1a36051b9c290ab6fa27309a65cb7520f6069889300bccb7f2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9b2d4eda99b8ea69bb971904b06cd4f20be668539a39742bfa319244a6fa13(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6992ee6052318711542d0de3a2501c5e8778dba13686188fb9085332fdc872b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9905a69e9ae6f01f3b117c0e9c746fd7be6fd625f9754650597c9ca50b1ad941(
    value: typing.Optional[GoogleDataplexDatascanDataQualityResultScannedData],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82f6f9b2e3dd9e6ef61d466036972682a872613d0f2dab949a64eab1e4977eb8(
    *,
    post_scan_actions: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecPostScanActions, typing.Dict[builtins.str, typing.Any]]] = None,
    row_filter: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDataplexDatascanDataQualitySpecRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    sampling_percent: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__775059a98ce65e4f0affacba4ba2710d7e003519f17ab4ae3316a68e7d2641f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d44d1c72321fa387e3a07748830ebeadc94997a7f06a8d3a4ebca3401ad3b4fa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDataplexDatascanDataQualitySpecRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff9e18b8def8c706dff7b2f966af3691b24fc2a1ad876b5cf71fa956661d7ec2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abd007d0903d76673de73e4e5158fdbc4a1d15699a26a54f50abd17fc763820c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39780b258628d7a453ef4d2f941dd50e8ef559c0e935ec86bd9c233a6a25ed02(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__950de9465254aeb19d4268125ef75923d132f8889adbb11ad03586b9f864a3c8(
    *,
    bigquery_export: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a989632fc2f5b26f7051778fdb3fab192b7a50e96b735e3e8bc5af89775f29d(
    *,
    results_table: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba8dc2375435f8e84caeecbf2e92138d08439bdac7d29b79092750561db3ecd5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f7a70a14e98ee37eaa8a2ffdd9c975ae34aee5160c9046a9f9bd71ddf82ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__267732bf0de95a3b611ea60a60ee06d0dc96fd82b9b7f4c30f2d5ec38c1bf629(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActionsBigqueryExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__994d2a37f002facfb57d8f0f11652bb15b5701381488ff8a5e298269f31d0885(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b44627c4aa19deb5a0196b710ef953a8184d83e567a7913db41633e2cf2123(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecPostScanActions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e376f1c41b5978fa8a295c4026a5239bd024fa449e5f49061b3f011be9b68d19(
    *,
    dimension: builtins.str,
    column: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    ignore_null: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    non_null_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    range_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    regex_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    row_condition_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    set_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesSetExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    statistic_range_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    table_condition_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
    threshold: typing.Optional[jsii.Number] = None,
    uniqueness_expectation: typing.Optional[typing.Union[GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd8b5270b9482b6e386ae312db38951683bcb5df61daa473bcf073f1017252c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e8cbef06a8ae3c8dd7fa7b47351c0e69d3a43a055607833d3316554a336a1a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26fe0341d3fbb025d31987651f167942aba2472d35f18b9fc4e6e7cc384e3d21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86037a8bd36b07b6f39c3d1e053471164930703f8c0db6004fbd856747ff0580(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64d69afc8578765fd55a8354d7e7d46d0d36ec8f0c8e356b1639b063cf4e7204(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b6352d11edec9a922424e1844c1987d2e27b2fb328ad75044d3cbbf5d8d36f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDataplexDatascanDataQualitySpecRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef940f79c6fdbe1ae3f0720a76719cebae65d930192ac0eaa5b293dcfae91a02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d1d717f00cd039f5e8ba74df7a28f35e4aeb05deaec14d8a484345b910f116(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesNonNullExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11168cf3e44f76466339e91fc88642cccf7a91a494627528fec7965ef284633(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bf400fd2bec9551b6d2f51ef053a0d253a548b216a635c91cb302ea3bb7cdc8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c82551e33daec270acdeb1e7416fb6bef46e9c369fa25ce56abf69cab8bf11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae9caa52bd1cc2609624d3be9398a3cb51e73279f06a6949fbfecff42fe0e3c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__046eba2767c71989670d72e46f855bd91a05be8efc514cb2913474c0c79158fb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d7c6f604d24f8a0847a020834e0df9cd3b6f97d5fe67e64d181f5458308f4fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f6fb671e29751d74b5c22fb21373625f33a09c4b42fc9ea87125e534e74e8d9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb241dab5dc33ac5bc3968a1797933ac1633700169cda4d6eda5e40f97ae3344(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanDataQualitySpecRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4b414d3d7e333119b8e12c982673609d628702eed4b23ad0f50bab64adc424(
    *,
    max_value: typing.Optional[builtins.str] = None,
    min_value: typing.Optional[builtins.str] = None,
    strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd5243f413a6df2840a10e6585af2b02c0ed2cb77219f83a4e613822cd83fb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b5f776d57f75e1404c24d5ec3cf9f5f5c2c86d28e4c869f57b068e543d604e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f7174ff1155566d3459c3cf7aaecfe313eef3e930bb3577e60b66aa9e5b863(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2aee641ebf6b38284c82c3557682aff9ab15a81267896193068333a50b38db(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958f2916c64dffc6ce244f7ed58d2bdcca85ce3260170a59bc6ecb10a50ed75c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c935b3ed3c157a69309d74a358def203213fdd1dfb2b688dd655a4a88be4164e(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc3a57da8b0146008969ed6441bc81c165bc7ca66b9fac88e4a61039328bc886(
    *,
    regex: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e8b9bf42b9775f4ef9c8b9d1124e94f6095e15b59255bdb1b273d8b77d3a09(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb18a3b6cd0e5eca9b09395e01f29a1df5a26f0ee65360b05b9ec391710de38d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf1a1c2bebcd22d0158010e62477d5b11a036f4315d8af038956903c1f15dac3(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRegexExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a5f93314527070e833bb4afca8aae2bfb8490fea6dc2538826b57c2df97644(
    *,
    sql_expression: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3d6b81dfb49491ec32afe71931b4420b32833e4e3370374b3a27c3340f3b49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce80b3f3833c3f0b7eea5bee8c0623b122400b2580601df52c9563b344eb9fac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33812848c8169e69522506323843708b1a854b5dfcf2a0f4f225b79bc8e1f1b1(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesRowConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c643dfa7d06ad659dfa58e71e67f30f450602cc279de827c43ab9776875ec6c(
    *,
    values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f2eb73d5cb414facc8000ac24e39b91a674fe1ffefe9537c6f6d195c764811(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c3adc2ffe604c19cbef2061f952e0219b1334abd1eeb856610059a439c84fb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc881f51ff32ec764eb9f37f4d8916d6aef7ca0ba5c76676d62d75efcc648eb(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesSetExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3232af862ab588343e902bf04cea71f8fed66526f05b90d24fe281e2a76ff539(
    *,
    statistic: builtins.str,
    max_value: typing.Optional[builtins.str] = None,
    min_value: typing.Optional[builtins.str] = None,
    strict_max_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    strict_min_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e0bb24272723da7a63fd637747765406c21ee999f9dfb5aee544d995c51044(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e04ec0dc296133d592ba6c05f26ca6287482504a7ac658dfcb3db9f1ed6e74f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4229f1f703fe4dce97c21f29bd720e42bbc4464c54789637429ee57dd942d5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00a3e385e814c38ac13f1d8efd2dd76ac25bd50b798c4aa1de47694515b076fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83451d2589c49f8bba5c06bcb39df91b1f5e8d55ca0493db473cc2db6ee71a0e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa838ed813b6fd36a4d5666487c0fb7116dcb16ec4b4c098a3b6e9a5b53ea161(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a80b3f2c30d4e7b538482dcb4ae82b6b2ac6912fe314ee096da3c39d4147d9e(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesStatisticRangeExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__835d51e0ab1bedb9a7885e9e5cf5e4eccb03360b8d37929babb04533bfde3eca(
    *,
    sql_expression: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89771a66295f1e631b641c8e586d0c7266f66e89e5eb584f21a7928b8f78cb28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5741a4b8ab3f8613ed076b8712f4c751911bed75c16d1d074a6ce9e7d09a8e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98aa5f646fb857c3b47f1a61c70d5fe4dc950322be4a935a0afc17af27bedc74(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesTableConditionExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9595fc27e4b61f7574dbc2481e82267c6756483a0fe63edc3e5549dc71088c95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17bf9d73d310b362832d112aa0e4ffe46166c82661a05f20593747c66dc8bf57(
    value: typing.Optional[GoogleDataplexDatascanDataQualitySpecRulesUniquenessExpectation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab2cccb86f1095c5189e4bee722b6b30850fdca3d9509cea4751a599a1b8340e(
    *,
    trigger: typing.Union[GoogleDataplexDatascanExecutionSpecTrigger, typing.Dict[builtins.str, typing.Any]],
    field: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__295f3cb05a2febd68a2c4bb2040b4b91d8e9411aae9566407b2e216ed4c15824(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cec770227190d2d092b97d3a603b1bc0a8b07529dc3f6fc545dea23c5d4326(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d734ae4ee7cef69e3c30cf3e4381203dcaa804cf398cfafd5cf1efb2b5712587(
    value: typing.Optional[GoogleDataplexDatascanExecutionSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dccafcabfad265695008687cd71967dece3226dc50cd484830e4a33839348a33(
    *,
    on_demand: typing.Optional[typing.Union[GoogleDataplexDatascanExecutionSpecTriggerOnDemand, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[typing.Union[GoogleDataplexDatascanExecutionSpecTriggerSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad93d9fd51ff8465c0f704de65eab9fab725d4b6ec4c3ec4b3405ce0d6862e7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaa5e3e115eddb48da606bd280f681d21e241ac5a23fc3b6e933c318f7f7aaa8(
    value: typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerOnDemand],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d15d67096ec5f36b2394e6ca3bf313ba737845fb77faf8227406c070f3df514(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd2ef8a2af41d32bfd5ada6c0fc2f5375a193080292c25fbab2f21e1d7184340(
    value: typing.Optional[GoogleDataplexDatascanExecutionSpecTrigger],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bafbf847196351ee37c16744c5f4b467dae1055c2c3bf01f9a68f2635c2963b(
    *,
    cron: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91dbd142508976f3f77a246d0fde6b1a02b89ba0abc37d54364b37acaa60ed55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b16a3d8e8a92af04b190a854e691e13944f3abc6e7c40b4ebe324051bc4721(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a95a0eeb1bb19aee26ab08298e41449fe9040d750ceca50260811e0694db80b(
    value: typing.Optional[GoogleDataplexDatascanExecutionSpecTriggerSchedule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dc22b9b63c5ef1d28df72c29ef65fc99424ac52dc9734bd318ffc4b05b92ca4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ac60a4ce6d010a5cfa154406432a82e5bfc5260c000da5e41df2bdd308b1190(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad79775ea7d37d03500396ca75ec7f7058a478f06ab4a648ef4f3a900b3ae2c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8b57e2dc0c7e9c32d18774d3265aa5c927f17724011eb368c852c81e9449421(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39739365ae08d8a951f94383dc9894c1330414e5ac1f0b3867c117dbfc05849f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50541958be153baa1f575e922a568b4f4700f39b959b54b49aaa3fcd124aeff6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07cfd8638887327f045148af648c9e8bdd95f87ec98eaa251e003cc27966d6c(
    value: typing.Optional[GoogleDataplexDatascanExecutionStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3780ff55a1ac6226caa9f36c297f313b1d2c5008bf37ea5094033bc964c4d88d(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66f13ff76172540ef7b56705d1491bf8829078e76e331edca21b0c712c86d63a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e417c1dea229e831995de0729ae4cb4394e91642862488a1cad722f9591e83ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2159c4446b0e3ba67a660c510c054c26ca6e59fe55a7b90f8d42449b8f131de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__111a7bb1a80cdc1120f5d0b99a519ae2419deb4bf72bb480f34b229b8a6e8bc7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__260835a5be1fbeafee1df2b881eb9436567d581ba90170fadc358313317743f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDataplexDatascanTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
