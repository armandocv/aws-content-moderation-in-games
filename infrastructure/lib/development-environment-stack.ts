import * as cdk from '@aws-cdk/core';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as cloud9 from '@aws-cdk/aws-cloud9';

export interface DevelopmentEnvironmentStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
}

export class DevelopmentEnvironmentStack extends cdk.Stack {
  private vpc: ec2.Vpc;

  constructor(scope: cdk.Construct, id: string, props: DevelopmentEnvironmentStackProps) {
    super(scope, id, props);

    new cloud9.CfnEnvironmentEC2(this, 'Cloud9Env', {
      instanceType: 't3.small',
      subnetId: props.vpc.selectSubnets({ subnetType: ec2.SubnetType.PUBLIC }).subnetIds.shift(),
    });
  }
}
