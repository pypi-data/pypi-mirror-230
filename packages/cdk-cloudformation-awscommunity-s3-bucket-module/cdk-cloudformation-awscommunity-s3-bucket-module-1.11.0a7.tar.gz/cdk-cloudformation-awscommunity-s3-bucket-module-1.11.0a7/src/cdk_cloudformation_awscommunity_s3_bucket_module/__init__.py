'''
# awscommunity-s3-bucket-module

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::S3::Bucket::MODULE` v1.11.0.

## Description

Schema for Module Fragment of type AwsCommunity::S3::Bucket::MODULE

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::S3::Bucket::MODULE \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type MODULE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/module/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-S3-Bucket-MODULE \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::S3::Bucket::MODULE`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-s3-bucket-module+v1.11.0).
* Issues related to `AwsCommunity::S3::Bucket::MODULE` should be reported to the [publisher](undefined).

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


class CfnBucketModule(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModule",
):
    '''A CloudFormation ``AwsCommunity::S3::Bucket::MODULE``.

    :cloudformationResource: AwsCommunity::S3::Bucket::MODULE
    :link: http://unknown-url
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        parameters: typing.Optional[typing.Union["CfnBucketModulePropsParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        resources: typing.Optional[typing.Union["CfnBucketModulePropsResources", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::S3::Bucket::MODULE``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param parameters: 
        :param resources: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11c388f40e245dc0dff68a880d757ae7a942de6119ba89b7bf32cd190e4c6de6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnBucketModuleProps(parameters=parameters, resources=resources)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnBucketModuleProps":
        '''Resource props.'''
        return typing.cast("CfnBucketModuleProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModuleProps",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters", "resources": "resources"},
)
class CfnBucketModuleProps:
    def __init__(
        self,
        *,
        parameters: typing.Optional[typing.Union["CfnBucketModulePropsParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        resources: typing.Optional[typing.Union["CfnBucketModulePropsResources", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Schema for Module Fragment of type AwsCommunity::S3::Bucket::MODULE.

        :param parameters: 
        :param resources: 

        :schema: CfnBucketModuleProps
        '''
        if isinstance(parameters, dict):
            parameters = CfnBucketModulePropsParameters(**parameters)
        if isinstance(resources, dict):
            resources = CfnBucketModulePropsResources(**resources)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3d1c2ebded8e153814c8368cfdbafc89778b7aa90a8fe67b8412bbf65c33ee)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters is not None:
            self._values["parameters"] = parameters
        if resources is not None:
            self._values["resources"] = resources

    @builtins.property
    def parameters(self) -> typing.Optional["CfnBucketModulePropsParameters"]:
        '''
        :schema: CfnBucketModuleProps#Parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional["CfnBucketModulePropsParameters"], result)

    @builtins.property
    def resources(self) -> typing.Optional["CfnBucketModulePropsResources"]:
        '''
        :schema: CfnBucketModuleProps#Resources
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional["CfnBucketModulePropsResources"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsParameters",
    jsii_struct_bases=[],
    name_mapping={"bucket_name": "bucketName", "log_bucket_name": "logBucketName"},
)
class CfnBucketModulePropsParameters:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[typing.Union["CfnBucketModulePropsParametersBucketName", typing.Dict[builtins.str, typing.Any]]] = None,
        log_bucket_name: typing.Optional[typing.Union["CfnBucketModulePropsParametersLogBucketName", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the bucket.
        :param log_bucket_name: The name of the log bucket.

        :schema: CfnBucketModulePropsParameters
        '''
        if isinstance(bucket_name, dict):
            bucket_name = CfnBucketModulePropsParametersBucketName(**bucket_name)
        if isinstance(log_bucket_name, dict):
            log_bucket_name = CfnBucketModulePropsParametersLogBucketName(**log_bucket_name)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9a27a205b3adb31f73a28e54081fefdb83bb3f6aa7c3354f1b88c53c7a125d4)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument log_bucket_name", value=log_bucket_name, expected_type=type_hints["log_bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if log_bucket_name is not None:
            self._values["log_bucket_name"] = log_bucket_name

    @builtins.property
    def bucket_name(
        self,
    ) -> typing.Optional["CfnBucketModulePropsParametersBucketName"]:
        '''The name of the bucket.

        :schema: CfnBucketModulePropsParameters#BucketName
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional["CfnBucketModulePropsParametersBucketName"], result)

    @builtins.property
    def log_bucket_name(
        self,
    ) -> typing.Optional["CfnBucketModulePropsParametersLogBucketName"]:
        '''The name of the log bucket.

        :schema: CfnBucketModulePropsParameters#LogBucketName
        '''
        result = self._values.get("log_bucket_name")
        return typing.cast(typing.Optional["CfnBucketModulePropsParametersLogBucketName"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsParametersBucketName",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "type": "type"},
)
class CfnBucketModulePropsParametersBucketName:
    def __init__(self, *, description: builtins.str, type: builtins.str) -> None:
        '''The name of the bucket.

        :param description: 
        :param type: 

        :schema: CfnBucketModulePropsParametersBucketName
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c079d6730a9fb80b69481c3b122b85923141144c626aba72246e3e54174b17fb)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "type": type,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :schema: CfnBucketModulePropsParametersBucketName#Description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :schema: CfnBucketModulePropsParametersBucketName#Type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsParametersBucketName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsParametersLogBucketName",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "type": "type"},
)
class CfnBucketModulePropsParametersLogBucketName:
    def __init__(self, *, description: builtins.str, type: builtins.str) -> None:
        '''The name of the log bucket.

        :param description: 
        :param type: 

        :schema: CfnBucketModulePropsParametersLogBucketName
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__266b6e7080d60a195a09dc8781dc4b8fa8974f9907aa28343ba84b5cb20f08ab)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "type": type,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :schema: CfnBucketModulePropsParametersLogBucketName#Description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :schema: CfnBucketModulePropsParametersLogBucketName#Type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsParametersLogBucketName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsResources",
    jsii_struct_bases=[],
    name_mapping={"compliant_bucket": "compliantBucket", "log_bucket": "logBucket"},
)
class CfnBucketModulePropsResources:
    def __init__(
        self,
        *,
        compliant_bucket: typing.Optional[typing.Union["CfnBucketModulePropsResourcesCompliantBucket", typing.Dict[builtins.str, typing.Any]]] = None,
        log_bucket: typing.Optional[typing.Union["CfnBucketModulePropsResourcesLogBucket", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param compliant_bucket: 
        :param log_bucket: 

        :schema: CfnBucketModulePropsResources
        '''
        if isinstance(compliant_bucket, dict):
            compliant_bucket = CfnBucketModulePropsResourcesCompliantBucket(**compliant_bucket)
        if isinstance(log_bucket, dict):
            log_bucket = CfnBucketModulePropsResourcesLogBucket(**log_bucket)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e38126d2cb786d0d96c4ad550c3f7bd9eacc6a46244bd404c09aa4b9cfb4e7dc)
            check_type(argname="argument compliant_bucket", value=compliant_bucket, expected_type=type_hints["compliant_bucket"])
            check_type(argname="argument log_bucket", value=log_bucket, expected_type=type_hints["log_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if compliant_bucket is not None:
            self._values["compliant_bucket"] = compliant_bucket
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket

    @builtins.property
    def compliant_bucket(
        self,
    ) -> typing.Optional["CfnBucketModulePropsResourcesCompliantBucket"]:
        '''
        :schema: CfnBucketModulePropsResources#CompliantBucket
        '''
        result = self._values.get("compliant_bucket")
        return typing.cast(typing.Optional["CfnBucketModulePropsResourcesCompliantBucket"], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional["CfnBucketModulePropsResourcesLogBucket"]:
        '''
        :schema: CfnBucketModulePropsResources#LogBucket
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional["CfnBucketModulePropsResourcesLogBucket"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsResourcesCompliantBucket",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnBucketModulePropsResourcesCompliantBucket:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnBucketModulePropsResourcesCompliantBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4154e61731938a3f0d4184bc463e81fd7633bcc846b6f92a403c9236fcb8479f)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if properties is not None:
            self._values["properties"] = properties
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def properties(self) -> typing.Any:
        '''
        :schema: CfnBucketModulePropsResourcesCompliantBucket#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnBucketModulePropsResourcesCompliantBucket#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsResourcesCompliantBucket(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-s3-bucket-module.CfnBucketModulePropsResourcesLogBucket",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnBucketModulePropsResourcesLogBucket:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnBucketModulePropsResourcesLogBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792b2b102f6b9cdcb084cf7cd8b117330ee5dea75ba0114e625f2f5abdb6d281)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if properties is not None:
            self._values["properties"] = properties
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def properties(self) -> typing.Any:
        '''
        :schema: CfnBucketModulePropsResourcesLogBucket#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnBucketModulePropsResourcesLogBucket#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBucketModulePropsResourcesLogBucket(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnBucketModule",
    "CfnBucketModuleProps",
    "CfnBucketModulePropsParameters",
    "CfnBucketModulePropsParametersBucketName",
    "CfnBucketModulePropsParametersLogBucketName",
    "CfnBucketModulePropsResources",
    "CfnBucketModulePropsResourcesCompliantBucket",
    "CfnBucketModulePropsResourcesLogBucket",
]

publication.publish()

def _typecheckingstub__11c388f40e245dc0dff68a880d757ae7a942de6119ba89b7bf32cd190e4c6de6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    parameters: typing.Optional[typing.Union[CfnBucketModulePropsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    resources: typing.Optional[typing.Union[CfnBucketModulePropsResources, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3d1c2ebded8e153814c8368cfdbafc89778b7aa90a8fe67b8412bbf65c33ee(
    *,
    parameters: typing.Optional[typing.Union[CfnBucketModulePropsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    resources: typing.Optional[typing.Union[CfnBucketModulePropsResources, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a27a205b3adb31f73a28e54081fefdb83bb3f6aa7c3354f1b88c53c7a125d4(
    *,
    bucket_name: typing.Optional[typing.Union[CfnBucketModulePropsParametersBucketName, typing.Dict[builtins.str, typing.Any]]] = None,
    log_bucket_name: typing.Optional[typing.Union[CfnBucketModulePropsParametersLogBucketName, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c079d6730a9fb80b69481c3b122b85923141144c626aba72246e3e54174b17fb(
    *,
    description: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__266b6e7080d60a195a09dc8781dc4b8fa8974f9907aa28343ba84b5cb20f08ab(
    *,
    description: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e38126d2cb786d0d96c4ad550c3f7bd9eacc6a46244bd404c09aa4b9cfb4e7dc(
    *,
    compliant_bucket: typing.Optional[typing.Union[CfnBucketModulePropsResourcesCompliantBucket, typing.Dict[builtins.str, typing.Any]]] = None,
    log_bucket: typing.Optional[typing.Union[CfnBucketModulePropsResourcesLogBucket, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4154e61731938a3f0d4184bc463e81fd7633bcc846b6f92a403c9236fcb8479f(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792b2b102f6b9cdcb084cf7cd8b117330ee5dea75ba0114e625f2f5abdb6d281(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
