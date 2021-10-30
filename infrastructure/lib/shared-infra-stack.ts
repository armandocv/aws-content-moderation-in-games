import * as cdk from '@aws-cdk/core';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as iam from '@aws-cdk/aws-iam';
import * as neptune from '@aws-cdk/aws-neptune';
import * as s3 from '@aws-cdk/aws-s3';

export class SharedInfraStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new ec2.Vpc(this, 'ContentModerationVPC', {
       cidr: "10.0.0.0/16"
    });
    this.vpc.addGatewayEndpoint('S3GatewayEndpoint', {
      service: new ec2.GatewayVpcEndpointAwsService('s3')
    });

    const dataBucket = new s3.Bucket(this, 'DataBucket');

    const neptuneRole = new iam.Role(this, 'NeptuneRole', {
      assumedBy: new iam.ServicePrincipal('rds.amazonaws.com')
    });
    dataBucket.grantRead(neptuneRole);

    const cluster = new neptune.DatabaseCluster(this, 'ModerationDatabase', {
      vpc: this.vpc,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      instanceType: neptune.InstanceType.T3_MEDIUM,
      associatedRoles: [neptuneRole]
    });

    new cdk.CfnOutput(this, 's3CopyCommand', {
      value: 'aws s3 cp vertex.txt s3://' + dataBucket.bucketName + '/vertex.txt && ' +
             'aws s3 cp edges.txt s3://' + dataBucket.bucketName + '/edges.txt'
    });

    new cdk.CfnOutput(this, 'neptuneS3LoadVertexCommand', {
      value: `curl -X POST -H 'Content-Type: application/json'
        https://${cluster.clusterEndpoint.hostname}:${cluster.clusterEndpoint.port}/loader -d '
          {
            "source" : "s3://${dataBucket.bucketName}/vertex.txt",
            "format" : "csv",
            "iamRoleArn" : "${neptuneRole.roleArn}",
            "region" : "${cdk.Stack.of(this).region}",
            "failOnError" : "FALSE",
            "parallelism" : "MEDIUM"
          }'`
    });

    new cdk.CfnOutput(this, 'neptuneS3LoadEdgesCommand', {
      value: `curl -X POST -H 'Content-Type: application/json'
        https://${cluster.clusterEndpoint.hostname}:${cluster.clusterEndpoint.port}/loader -d '
          {
            "source" : "s3://${dataBucket.bucketName}/edges.txt",
            "format" : "csv",
            "iamRoleArn" : "${neptuneRole.roleArn}",
            "region" : "${cdk.Stack.of(this).region}",
            "failOnError" : "FALSE",
            "parallelism" : "MEDIUM"
          }'`
    });
  }
}
