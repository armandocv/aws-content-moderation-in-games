import * as cdk from '@aws-cdk/core';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as neptune from '@aws-cdk/aws-neptune';

export class IngestStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'ContentModerationVPC', {
       cidr: "10.0.0.0/16"
    })

    const cluster = new neptune.DatabaseCluster(this, 'ModerationDatabase', {
      vpc,
      instanceType: neptune.InstanceType.T3_MEDIUM
    });
  }
}
