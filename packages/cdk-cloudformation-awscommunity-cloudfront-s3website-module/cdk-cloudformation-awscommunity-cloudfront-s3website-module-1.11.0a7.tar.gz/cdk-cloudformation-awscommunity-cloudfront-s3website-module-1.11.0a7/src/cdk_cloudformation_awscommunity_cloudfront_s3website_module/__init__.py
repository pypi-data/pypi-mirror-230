'''
# awscommunity-cloudfront-s3website-module

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `AwsCommunity::CloudFront::S3Website::MODULE` v1.11.0.

## Description

Schema for Module Fragment of type AwsCommunity::CloudFront::S3Website::MODULE

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name AwsCommunity::CloudFront::S3Website::MODULE \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type MODULE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/module/c830e97710da0c9954d80ba8df021e5439e7134b/AwsCommunity-CloudFront-S3Website-MODULE \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `AwsCommunity::CloudFront::S3Website::MODULE`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Fawscommunity-cloudfront-s3website-module+v1.11.0).
* Issues related to `AwsCommunity::CloudFront::S3Website::MODULE` should be reported to the [publisher](undefined).

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


class CfnS3WebsiteModule(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModule",
):
    '''A CloudFormation ``AwsCommunity::CloudFront::S3Website::MODULE``.

    :cloudformationResource: AwsCommunity::CloudFront::S3Website::MODULE
    :link: http://unknown-url
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        parameters: typing.Optional[typing.Union["CfnS3WebsiteModulePropsParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        resources: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResources", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Create a new ``AwsCommunity::CloudFront::S3Website::MODULE``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param parameters: 
        :param resources: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be47f54b3da5b2a4ffb9e947adf8b25f2ed0ec611c1498f301821cd3a063fd3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnS3WebsiteModuleProps(parameters=parameters, resources=resources)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnS3WebsiteModuleProps":
        '''Resource props.'''
        return typing.cast("CfnS3WebsiteModuleProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModuleProps",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters", "resources": "resources"},
)
class CfnS3WebsiteModuleProps:
    def __init__(
        self,
        *,
        parameters: typing.Optional[typing.Union["CfnS3WebsiteModulePropsParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        resources: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResources", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Schema for Module Fragment of type AwsCommunity::CloudFront::S3Website::MODULE.

        :param parameters: 
        :param resources: 

        :schema: CfnS3WebsiteModuleProps
        '''
        if isinstance(parameters, dict):
            parameters = CfnS3WebsiteModulePropsParameters(**parameters)
        if isinstance(resources, dict):
            resources = CfnS3WebsiteModulePropsResources(**resources)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a14e0a8db42ce5227ae9383da9d45537c7079dca35d94299ce3ebacac76153e)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters is not None:
            self._values["parameters"] = parameters
        if resources is not None:
            self._values["resources"] = resources

    @builtins.property
    def parameters(self) -> typing.Optional["CfnS3WebsiteModulePropsParameters"]:
        '''
        :schema: CfnS3WebsiteModuleProps#Parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsParameters"], result)

    @builtins.property
    def resources(self) -> typing.Optional["CfnS3WebsiteModulePropsResources"]:
        '''
        :schema: CfnS3WebsiteModuleProps#Resources
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResources"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsParameters",
    jsii_struct_bases=[],
    name_mapping={
        "acm_certificate_arn": "acmCertificateArn",
        "alias": "alias",
        "hosted_zone_id": "hostedZoneId",
    },
)
class CfnS3WebsiteModulePropsParameters:
    def __init__(
        self,
        *,
        acm_certificate_arn: typing.Optional[typing.Union["CfnS3WebsiteModulePropsParametersAcmCertificateArn", typing.Dict[builtins.str, typing.Any]]] = None,
        alias: typing.Optional[typing.Union["CfnS3WebsiteModulePropsParametersAlias", typing.Dict[builtins.str, typing.Any]]] = None,
        hosted_zone_id: typing.Optional[typing.Union["CfnS3WebsiteModulePropsParametersHostedZoneId", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param acm_certificate_arn: The ARN for the ACM Certificate to use.
        :param alias: The DNS name for the website.
        :param hosted_zone_id: The Route53 HostedZoneId to use for certificates and registering the website DNS Name.

        :schema: CfnS3WebsiteModulePropsParameters
        '''
        if isinstance(acm_certificate_arn, dict):
            acm_certificate_arn = CfnS3WebsiteModulePropsParametersAcmCertificateArn(**acm_certificate_arn)
        if isinstance(alias, dict):
            alias = CfnS3WebsiteModulePropsParametersAlias(**alias)
        if isinstance(hosted_zone_id, dict):
            hosted_zone_id = CfnS3WebsiteModulePropsParametersHostedZoneId(**hosted_zone_id)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c060172fc8490ec593e7f177df6f0133c5d3f46f0cfffacc15ad633443277572)
            check_type(argname="argument acm_certificate_arn", value=acm_certificate_arn, expected_type=type_hints["acm_certificate_arn"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument hosted_zone_id", value=hosted_zone_id, expected_type=type_hints["hosted_zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if acm_certificate_arn is not None:
            self._values["acm_certificate_arn"] = acm_certificate_arn
        if alias is not None:
            self._values["alias"] = alias
        if hosted_zone_id is not None:
            self._values["hosted_zone_id"] = hosted_zone_id

    @builtins.property
    def acm_certificate_arn(
        self,
    ) -> typing.Optional["CfnS3WebsiteModulePropsParametersAcmCertificateArn"]:
        '''The ARN for the ACM Certificate to use.

        :schema: CfnS3WebsiteModulePropsParameters#AcmCertificateArn
        '''
        result = self._values.get("acm_certificate_arn")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsParametersAcmCertificateArn"], result)

    @builtins.property
    def alias(self) -> typing.Optional["CfnS3WebsiteModulePropsParametersAlias"]:
        '''The DNS name for the website.

        :schema: CfnS3WebsiteModulePropsParameters#Alias
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsParametersAlias"], result)

    @builtins.property
    def hosted_zone_id(
        self,
    ) -> typing.Optional["CfnS3WebsiteModulePropsParametersHostedZoneId"]:
        '''The Route53 HostedZoneId to use for certificates and registering the website DNS Name.

        :schema: CfnS3WebsiteModulePropsParameters#HostedZoneId
        '''
        result = self._values.get("hosted_zone_id")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsParametersHostedZoneId"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsParametersAcmCertificateArn",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "type": "type"},
)
class CfnS3WebsiteModulePropsParametersAcmCertificateArn:
    def __init__(self, *, description: builtins.str, type: builtins.str) -> None:
        '''The ARN for the ACM Certificate to use.

        :param description: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsParametersAcmCertificateArn
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b4942e3ff5cdd44ae16c52727f38dcbcd733e3e3fa9ca87d47ae8d43aeb4d60)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "type": type,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersAcmCertificateArn#Description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersAcmCertificateArn#Type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsParametersAcmCertificateArn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsParametersAlias",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "type": "type"},
)
class CfnS3WebsiteModulePropsParametersAlias:
    def __init__(self, *, description: builtins.str, type: builtins.str) -> None:
        '''The DNS name for the website.

        :param description: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsParametersAlias
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2102e8fb436a74e37656e2324e9c36385df1e7228e05077f0a33e5e7017b98ac)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "type": type,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersAlias#Description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersAlias#Type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsParametersAlias(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsParametersHostedZoneId",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "type": "type"},
)
class CfnS3WebsiteModulePropsParametersHostedZoneId:
    def __init__(self, *, description: builtins.str, type: builtins.str) -> None:
        '''The Route53 HostedZoneId to use for certificates and registering the website DNS Name.

        :param description: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsParametersHostedZoneId
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73725bf3549dc629ad5701666a5c31a13b5dc1c1a5d84b61803d62ca7e91f70e)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "type": type,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersHostedZoneId#Description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :schema: CfnS3WebsiteModulePropsParametersHostedZoneId#Type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsParametersHostedZoneId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResources",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "bucket_policy": "bucketPolicy",
        "certificate": "certificate",
        "distribution": "distribution",
        "dns": "dns",
        "oac": "oac",
    },
)
class CfnS3WebsiteModulePropsResources:
    def __init__(
        self,
        *,
        bucket: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesBucket", typing.Dict[builtins.str, typing.Any]]] = None,
        bucket_policy: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesBucketPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        distribution: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesDistribution", typing.Dict[builtins.str, typing.Any]]] = None,
        dns: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesDns", typing.Dict[builtins.str, typing.Any]]] = None,
        oac: typing.Optional[typing.Union["CfnS3WebsiteModulePropsResourcesOac", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bucket: 
        :param bucket_policy: 
        :param certificate: 
        :param distribution: 
        :param dns: 
        :param oac: 

        :schema: CfnS3WebsiteModulePropsResources
        '''
        if isinstance(bucket, dict):
            bucket = CfnS3WebsiteModulePropsResourcesBucket(**bucket)
        if isinstance(bucket_policy, dict):
            bucket_policy = CfnS3WebsiteModulePropsResourcesBucketPolicy(**bucket_policy)
        if isinstance(certificate, dict):
            certificate = CfnS3WebsiteModulePropsResourcesCertificate(**certificate)
        if isinstance(distribution, dict):
            distribution = CfnS3WebsiteModulePropsResourcesDistribution(**distribution)
        if isinstance(dns, dict):
            dns = CfnS3WebsiteModulePropsResourcesDns(**dns)
        if isinstance(oac, dict):
            oac = CfnS3WebsiteModulePropsResourcesOac(**oac)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0a6df423f4fa2f86ac849bc180384687d4896a0c04607cc48ca8e1e3b4177ba)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument bucket_policy", value=bucket_policy, expected_type=type_hints["bucket_policy"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument dns", value=dns, expected_type=type_hints["dns"])
            check_type(argname="argument oac", value=oac, expected_type=type_hints["oac"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if bucket_policy is not None:
            self._values["bucket_policy"] = bucket_policy
        if certificate is not None:
            self._values["certificate"] = certificate
        if distribution is not None:
            self._values["distribution"] = distribution
        if dns is not None:
            self._values["dns"] = dns
        if oac is not None:
            self._values["oac"] = oac

    @builtins.property
    def bucket(self) -> typing.Optional["CfnS3WebsiteModulePropsResourcesBucket"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#Bucket
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesBucket"], result)

    @builtins.property
    def bucket_policy(
        self,
    ) -> typing.Optional["CfnS3WebsiteModulePropsResourcesBucketPolicy"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#BucketPolicy
        '''
        result = self._values.get("bucket_policy")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesBucketPolicy"], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional["CfnS3WebsiteModulePropsResourcesCertificate"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#Certificate
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesCertificate"], result)

    @builtins.property
    def distribution(
        self,
    ) -> typing.Optional["CfnS3WebsiteModulePropsResourcesDistribution"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#Distribution
        '''
        result = self._values.get("distribution")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesDistribution"], result)

    @builtins.property
    def dns(self) -> typing.Optional["CfnS3WebsiteModulePropsResourcesDns"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#Dns
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesDns"], result)

    @builtins.property
    def oac(self) -> typing.Optional["CfnS3WebsiteModulePropsResourcesOac"]:
        '''
        :schema: CfnS3WebsiteModulePropsResources#Oac
        '''
        result = self._values.get("oac")
        return typing.cast(typing.Optional["CfnS3WebsiteModulePropsResourcesOac"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesBucket",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesBucket:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__213303acfe94540227516607bde71d7ff124fce7b9b89d1feab8de90ae10905d)
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
        :schema: CfnS3WebsiteModulePropsResourcesBucket#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesBucket#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesBucket(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesBucketPolicy",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesBucketPolicy:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesBucketPolicy
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0529ff834025b04b70b29def0d224a615800a2fd2a0b26fd1d55a85c7ea97d23)
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
        :schema: CfnS3WebsiteModulePropsResourcesBucketPolicy#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesBucketPolicy#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesBucketPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesCertificate",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesCertificate:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesCertificate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955da1c6ae5c0cafd5d38f393a3e9ac96445b2171e7a4ffb7c2e28ff5673f1ba)
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
        :schema: CfnS3WebsiteModulePropsResourcesCertificate#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesCertificate#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesDistribution",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesDistribution:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesDistribution
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95be6d7a4aba9e3f6dad296f96af26d2d13d5414465293d52342bb4f483d534c)
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
        :schema: CfnS3WebsiteModulePropsResourcesDistribution#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesDistribution#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesDns",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesDns:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesDns
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__580e7a535c089446760a7de00a000275b929ee4bfff0d577cc0508091ee59369)
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
        :schema: CfnS3WebsiteModulePropsResourcesDns#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesDns#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdk-cloudformation/awscommunity-cloudfront-s3website-module.CfnS3WebsiteModulePropsResourcesOac",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties", "type": "type"},
)
class CfnS3WebsiteModulePropsResourcesOac:
    def __init__(
        self,
        *,
        properties: typing.Any = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param properties: 
        :param type: 

        :schema: CfnS3WebsiteModulePropsResourcesOac
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddb842d9d87c4976e7080b448f269ac7fd26b401de5b0496d891eaef6cd2ac57)
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
        :schema: CfnS3WebsiteModulePropsResourcesOac#Properties
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''
        :schema: CfnS3WebsiteModulePropsResourcesOac#Type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnS3WebsiteModulePropsResourcesOac(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnS3WebsiteModule",
    "CfnS3WebsiteModuleProps",
    "CfnS3WebsiteModulePropsParameters",
    "CfnS3WebsiteModulePropsParametersAcmCertificateArn",
    "CfnS3WebsiteModulePropsParametersAlias",
    "CfnS3WebsiteModulePropsParametersHostedZoneId",
    "CfnS3WebsiteModulePropsResources",
    "CfnS3WebsiteModulePropsResourcesBucket",
    "CfnS3WebsiteModulePropsResourcesBucketPolicy",
    "CfnS3WebsiteModulePropsResourcesCertificate",
    "CfnS3WebsiteModulePropsResourcesDistribution",
    "CfnS3WebsiteModulePropsResourcesDns",
    "CfnS3WebsiteModulePropsResourcesOac",
]

publication.publish()

def _typecheckingstub__6be47f54b3da5b2a4ffb9e947adf8b25f2ed0ec611c1498f301821cd3a063fd3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    parameters: typing.Optional[typing.Union[CfnS3WebsiteModulePropsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    resources: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResources, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a14e0a8db42ce5227ae9383da9d45537c7079dca35d94299ce3ebacac76153e(
    *,
    parameters: typing.Optional[typing.Union[CfnS3WebsiteModulePropsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    resources: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResources, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c060172fc8490ec593e7f177df6f0133c5d3f46f0cfffacc15ad633443277572(
    *,
    acm_certificate_arn: typing.Optional[typing.Union[CfnS3WebsiteModulePropsParametersAcmCertificateArn, typing.Dict[builtins.str, typing.Any]]] = None,
    alias: typing.Optional[typing.Union[CfnS3WebsiteModulePropsParametersAlias, typing.Dict[builtins.str, typing.Any]]] = None,
    hosted_zone_id: typing.Optional[typing.Union[CfnS3WebsiteModulePropsParametersHostedZoneId, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4942e3ff5cdd44ae16c52727f38dcbcd733e3e3fa9ca87d47ae8d43aeb4d60(
    *,
    description: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2102e8fb436a74e37656e2324e9c36385df1e7228e05077f0a33e5e7017b98ac(
    *,
    description: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73725bf3549dc629ad5701666a5c31a13b5dc1c1a5d84b61803d62ca7e91f70e(
    *,
    description: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a6df423f4fa2f86ac849bc180384687d4896a0c04607cc48ca8e1e3b4177ba(
    *,
    bucket: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesBucket, typing.Dict[builtins.str, typing.Any]]] = None,
    bucket_policy: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesBucketPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    distribution: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesDistribution, typing.Dict[builtins.str, typing.Any]]] = None,
    dns: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesDns, typing.Dict[builtins.str, typing.Any]]] = None,
    oac: typing.Optional[typing.Union[CfnS3WebsiteModulePropsResourcesOac, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__213303acfe94540227516607bde71d7ff124fce7b9b89d1feab8de90ae10905d(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0529ff834025b04b70b29def0d224a615800a2fd2a0b26fd1d55a85c7ea97d23(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955da1c6ae5c0cafd5d38f393a3e9ac96445b2171e7a4ffb7c2e28ff5673f1ba(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95be6d7a4aba9e3f6dad296f96af26d2d13d5414465293d52342bb4f483d534c(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__580e7a535c089446760a7de00a000275b929ee4bfff0d577cc0508091ee59369(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb842d9d87c4976e7080b448f269ac7fd26b401de5b0496d891eaef6cd2ac57(
    *,
    properties: typing.Any = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
