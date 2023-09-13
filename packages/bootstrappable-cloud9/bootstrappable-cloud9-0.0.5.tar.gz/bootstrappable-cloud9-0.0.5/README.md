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
