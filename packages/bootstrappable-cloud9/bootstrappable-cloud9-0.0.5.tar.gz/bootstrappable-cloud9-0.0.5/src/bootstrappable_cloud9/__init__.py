'''
# Bootstrappable Cloud9 Instance with SSM

Simple stack example:

```python
export class Cloud9EnvironmentExampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create L2 Cloud9 Environment
    const environment = new Cloud9Environment(this, "environment", {
      name: "example-environment",
      description: "An example environment",
      imageId: Cloud9AmiType.AMZN_LINUX_2,
      connectionType: Cloud9ConnectionType.SSM,
      ownerArn: "<YOUR_ARN>",
    });

    // Existing CodeCommit Repository
    const repository = Repository.fromRepositoryName(this, "test", "test-repo");
    // Clone Git Repositories within Cloud9 Environment
    environment.cloneCodeCommitRepo(repository, "test");
    environment.cloneGitRepo(
      "https://github.com/aws-samples/aws-copilot-pubsub",
      "copilot"
    );

    environment.addInitCommands(["sudo yum update -y", "sudo yum install -y jq"]);

    //-----------------------------------------------------
    //-                  Outputs                         -
    //-----------------------------------------------------
    new cdk.CfnOutput(this, "environmentUrl", {
      value: environment.environmentUrl,
      description: "The URL of the environment",
    });
  }
}
```
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
import aws_cdk.aws_cloud9 as _aws_cdk_aws_cloud9_ceddda9d
import aws_cdk.aws_codecommit as _aws_cdk_aws_codecommit_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="bootstrappable-cloud9.Cloud9AmiType")
class Cloud9AmiType(enum.Enum):
    AMZN_LINUX_2 = "AMZN_LINUX_2"
    '''Amazon Linux 2 AMI (recommended).

    :link: https://aws.amazon.com/amazon-linux-2/
    '''
    UBUNTU_22_04 = "UBUNTU_22_04"
    '''Ubuntu 22.04 LTS - Jammy Jellyfish.

    :link: https://aws.amazon.com/amazon-linux-2/
    '''
    AMZN_LINUX_1 = "AMZN_LINUX_1"
    '''Amazon Linux 1.

    - For new deployments prefer ``AMZN_LINUX_2``
    '''
    UBUNTU_18_04 = "UBUNTU_18_04"
    '''Ubuntu 18.04 LTS - Bionic Beaver. For new deployments prefer ``UBUNTU_22_04``.'''


@jsii.enum(jsii_type="bootstrappable-cloud9.Cloud9ConnectionType")
class Cloud9ConnectionType(enum.Enum):
    SSH = "SSH"
    '''This method accesses the environment using SSH and requires open inbound ports.'''
    SSM = "SSM"
    '''This method accesses the environment using SSM (Sytems Manager) without opening inbound ports.'''


class Cloud9Environment(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="bootstrappable-cloud9.Cloud9Environment",
):
    '''A Cloud 9 Environment with bootstrapping capabilities leveraging SSM automation.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection_type: Cloud9ConnectionType,
        automatic_stop_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        description: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[Cloud9AmiType] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        name: typing.Optional[builtins.str] = None,
        owner_arn: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param connection_type: The type of connection method to use. Default: Cloud9ConnectionType.SSM
        :param automatic_stop_time: The amount of time to wait for the environment to stop. Default: - 30 minutes
        :param description: The description of the environment. Default: - None
        :param image_id: The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance. Default: - Cloud9AmiType.AMZN_LINUX_2
        :param instance_type: The type of EC2 instance to use. Default: - t3.small
        :param name: The name of the environment. Default: - A Cloud9 -generated
        :param owner_arn: The Amazon Resource Name (ARN) of the environment owner. Default: - "This environment creator (careful, this might be the CloudFormation role!)"
        :param subnet: The subnet to use for the environment.
        :param tags: The tags to apply to the environment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__649b030c35bbcfb5024b846a01896aa7398ff10e725dc55442bb1ce6d34698de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Cloud9EnvironmentProps(
            connection_type=connection_type,
            automatic_stop_time=automatic_stop_time,
            description=description,
            image_id=image_id,
            instance_type=instance_type,
            name=name,
            owner_arn=owner_arn,
            subnet=subnet,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addInitCommands")
    def add_init_commands(self, commands: typing.Sequence[builtins.str]) -> None:
        '''Adds bash commands to the Cloud9 environment initialization script.

        Commands such as ``yum install <package>`` should include the sudo prefix.

        :param commands: bash commands to execute in the Cloud9 environment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d932d68ec0e1829e4f1cc30b546c7f2ee805dfe9e11a71b4194cd0fe5b01ec15)
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
        return typing.cast(None, jsii.invoke(self, "addInitCommands", [commands]))

    @jsii.member(jsii_name="cloneCodeCommitRepo")
    def clone_code_commit_repo(
        self,
        repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
        environment_path: builtins.str,
    ) -> None:
        '''Clones a Code Commit repository into the Cloud9 environment.

        :param repository: the CodeCommit repository.
        :param environment_path: the path within Cloud9 where it will be cloned.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae00d49d450d083535c457c45a0a0a524e14ad5521e11f05838c8ba3a1c816b)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument environment_path", value=environment_path, expected_type=type_hints["environment_path"])
        return typing.cast(None, jsii.invoke(self, "cloneCodeCommitRepo", [repository, environment_path]))

    @jsii.member(jsii_name="cloneGitRepo")
    def clone_git_repo(
        self,
        repository_url: builtins.str,
        environment_path: builtins.str,
    ) -> None:
        '''Clones a public GitHub repository into the Cloud9 environment.

        :param repository_url: the HTTPS URL of the repository.
        :param environment_path: the path within Cloud9 where it will be cloned.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1fd81e103453fd07a11331131365db80dbdd19154b6521a31217d45b6d2510)
            check_type(argname="argument repository_url", value=repository_url, expected_type=type_hints["repository_url"])
            check_type(argname="argument environment_path", value=environment_path, expected_type=type_hints["environment_path"])
        return typing.cast(None, jsii.invoke(self, "cloneGitRepo", [repository_url, environment_path]))

    @jsii.member(jsii_name="grantCollaboratorAccess")
    def grant_collaborator_access(
        self,
        user_arn: builtins.str,
        access_type: typing.Optional["CollaboratorAccessType"] = None,
    ) -> None:
        '''Gives access to collaborators to the Cloud9 environment.

        :param user_arn: the ARN of the user to give access.
        :param access_type: (optional) the type of access to give, default: ``CollaboratorAccessType.READ_WRITE``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45d2202f8be772f72fcdc602a49e3400f80ef37da688b5d5f650e63a5a49fdb)
            check_type(argname="argument user_arn", value=user_arn, expected_type=type_hints["user_arn"])
            check_type(argname="argument access_type", value=access_type, expected_type=type_hints["access_type"])
        return typing.cast(None, jsii.invoke(self, "grantCollaboratorAccess", [user_arn, access_type]))

    @jsii.member(jsii_name="resizeEbsVolumeTo")
    def resize_ebs_volume_to(self, size: jsii.Number) -> None:
        '''Resizes the EBS volume attached to the Cloud9 environment.

        :param size: The volume size, in Gibibytes (GiB).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c390355de00ee32ab77214e232d16a6dfc77396a5bf704f7f4bed7551f3f5f23)
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
        return typing.cast(None, jsii.invoke(self, "resizeEbsVolumeTo", [size]))

    @builtins.property
    @jsii.member(jsii_name="defaultEnvironmentPath")
    def default_environment_path(self) -> builtins.str:
        '''The default path within the Cloud9 environment: @default /home/ec2-user/environment.'''
        return typing.cast(builtins.str, jsii.get(self, "defaultEnvironmentPath"))

    @builtins.property
    @jsii.member(jsii_name="environmentArn")
    def environment_arn(self) -> builtins.str:
        '''The ARN of the Cloud9 environment, useful for limiting IAM policies.'''
        return typing.cast(builtins.str, jsii.get(self, "environmentArn"))

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        '''The ID of the Cloud9 environment.

        (e.g. ``0e19f1e459a44006a1ef37222561bcc6``)
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentId"))

    @builtins.property
    @jsii.member(jsii_name="environmentUrl")
    def environment_url(self) -> builtins.str:
        '''The HTTPS URL of the Cloud9 environment from which it can be accessed.'''
        return typing.cast(builtins.str, jsii.get(self, "environmentUrl"))

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''The ID of the underlying EC2 instance (e.g. ``i-0cdc52635e6b51069``).'''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM Role associated to this environment @default AWSCloud9SSMAccessRole.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "instanceRole"))

    @builtins.property
    @jsii.member(jsii_name="privateIp")
    def private_ip(self) -> builtins.str:
        '''The private IP address of the underlying EC2 instance (e.g. ``172.31.39.167``).'''
        return typing.cast(builtins.str, jsii.get(self, "privateIp"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2:
        '''The underlying CfnEnvironmentEC2 L1 resource.'''
        return typing.cast(_aws_cdk_aws_cloud9_ceddda9d.CfnEnvironmentEC2, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''The security group of the underlying EC2 instance.

        By default, SSM only allows outbound traffic.
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        '''The volume identifier of the underlying EBS volume in the instance (e.g. ``vol-0d1fadbf56e20a86e``).'''
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))


@jsii.data_type(
    jsii_type="bootstrappable-cloud9.Cloud9EnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "connection_type": "connectionType",
        "automatic_stop_time": "automaticStopTime",
        "description": "description",
        "image_id": "imageId",
        "instance_type": "instanceType",
        "name": "name",
        "owner_arn": "ownerArn",
        "subnet": "subnet",
        "tags": "tags",
    },
)
class Cloud9EnvironmentProps:
    def __init__(
        self,
        *,
        connection_type: Cloud9ConnectionType,
        automatic_stop_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        description: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[Cloud9AmiType] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        name: typing.Optional[builtins.str] = None,
        owner_arn: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param connection_type: The type of connection method to use. Default: Cloud9ConnectionType.SSM
        :param automatic_stop_time: The amount of time to wait for the environment to stop. Default: - 30 minutes
        :param description: The description of the environment. Default: - None
        :param image_id: The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance. Default: - Cloud9AmiType.AMZN_LINUX_2
        :param instance_type: The type of EC2 instance to use. Default: - t3.small
        :param name: The name of the environment. Default: - A Cloud9 -generated
        :param owner_arn: The Amazon Resource Name (ARN) of the environment owner. Default: - "This environment creator (careful, this might be the CloudFormation role!)"
        :param subnet: The subnet to use for the environment.
        :param tags: The tags to apply to the environment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1481e5ba6480c45544232fd32c404df3d20b57026f422935ec513a16c797ddf)
            check_type(argname="argument connection_type", value=connection_type, expected_type=type_hints["connection_type"])
            check_type(argname="argument automatic_stop_time", value=automatic_stop_time, expected_type=type_hints["automatic_stop_time"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument image_id", value=image_id, expected_type=type_hints["image_id"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner_arn", value=owner_arn, expected_type=type_hints["owner_arn"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_type": connection_type,
        }
        if automatic_stop_time is not None:
            self._values["automatic_stop_time"] = automatic_stop_time
        if description is not None:
            self._values["description"] = description
        if image_id is not None:
            self._values["image_id"] = image_id
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if name is not None:
            self._values["name"] = name
        if owner_arn is not None:
            self._values["owner_arn"] = owner_arn
        if subnet is not None:
            self._values["subnet"] = subnet
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def connection_type(self) -> Cloud9ConnectionType:
        '''The type of connection method to use.

        :default: Cloud9ConnectionType.SSM
        '''
        result = self._values.get("connection_type")
        assert result is not None, "Required property 'connection_type' is missing"
        return typing.cast(Cloud9ConnectionType, result)

    @builtins.property
    def automatic_stop_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The amount of time to wait for the environment to stop.

        :default: - 30 minutes
        '''
        result = self._values.get("automatic_stop_time")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the environment.

        :default: - None
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_id(self) -> typing.Optional[Cloud9AmiType]:
        '''The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance.

        :default: - Cloud9AmiType.AMZN_LINUX_2
        '''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[Cloud9AmiType], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''The type of EC2 instance to use.

        :default: - t3.small
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the environment.

        :default: - A Cloud9 -generated
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the environment owner.

        :default: - "This environment creator (careful, this might be the CloudFormation role!)"
        '''
        result = self._values.get("owner_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''The subnet to use for the environment.'''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''The tags to apply to the environment.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cloud9EnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="bootstrappable-cloud9.CollaboratorAccessType")
class CollaboratorAccessType(enum.Enum):
    '''The type of access to grant to collaborators of the environment.'''

    READ_ONLY = "READ_ONLY"
    '''Grants read-only access to the environment.'''
    READ_WRITE = "READ_WRITE"
    '''Grants read-write access to the environment.'''


@jsii.data_type(
    jsii_type="bootstrappable-cloud9.RepositoryCloneProps",
    jsii_struct_bases=[],
    name_mapping={
        "environment_path": "environmentPath",
        "repository_url": "repositoryUrl",
    },
)
class RepositoryCloneProps:
    def __init__(
        self,
        *,
        environment_path: builtins.str,
        repository_url: builtins.str,
    ) -> None:
        '''
        :param environment_path: 
        :param repository_url: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d284319f368720085837e3801094da62244fc6744606709cda6520c02b8c53a)
            check_type(argname="argument environment_path", value=environment_path, expected_type=type_hints["environment_path"])
            check_type(argname="argument repository_url", value=repository_url, expected_type=type_hints["repository_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment_path": environment_path,
            "repository_url": repository_url,
        }

    @builtins.property
    def environment_path(self) -> builtins.str:
        result = self._values.get("environment_path")
        assert result is not None, "Required property 'environment_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_url(self) -> builtins.str:
        result = self._values.get("repository_url")
        assert result is not None, "Required property 'repository_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryCloneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Cloud9AmiType",
    "Cloud9ConnectionType",
    "Cloud9Environment",
    "Cloud9EnvironmentProps",
    "CollaboratorAccessType",
    "RepositoryCloneProps",
]

publication.publish()

def _typecheckingstub__649b030c35bbcfb5024b846a01896aa7398ff10e725dc55442bb1ce6d34698de(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    connection_type: Cloud9ConnectionType,
    automatic_stop_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    description: typing.Optional[builtins.str] = None,
    image_id: typing.Optional[Cloud9AmiType] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    name: typing.Optional[builtins.str] = None,
    owner_arn: typing.Optional[builtins.str] = None,
    subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d932d68ec0e1829e4f1cc30b546c7f2ee805dfe9e11a71b4194cd0fe5b01ec15(
    commands: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae00d49d450d083535c457c45a0a0a524e14ad5521e11f05838c8ba3a1c816b(
    repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
    environment_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1fd81e103453fd07a11331131365db80dbdd19154b6521a31217d45b6d2510(
    repository_url: builtins.str,
    environment_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45d2202f8be772f72fcdc602a49e3400f80ef37da688b5d5f650e63a5a49fdb(
    user_arn: builtins.str,
    access_type: typing.Optional[CollaboratorAccessType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c390355de00ee32ab77214e232d16a6dfc77396a5bf704f7f4bed7551f3f5f23(
    size: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1481e5ba6480c45544232fd32c404df3d20b57026f422935ec513a16c797ddf(
    *,
    connection_type: Cloud9ConnectionType,
    automatic_stop_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    description: typing.Optional[builtins.str] = None,
    image_id: typing.Optional[Cloud9AmiType] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    name: typing.Optional[builtins.str] = None,
    owner_arn: typing.Optional[builtins.str] = None,
    subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d284319f368720085837e3801094da62244fc6744606709cda6520c02b8c53a(
    *,
    environment_path: builtins.str,
    repository_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
