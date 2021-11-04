import * as cdk from '@aws-cdk/core';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as s3 from '@aws-cdk/aws-s3';
import * as s3deploy from '@aws-cdk/aws-s3-deployment';
import * as apigw from '@aws-cdk/aws-apigateway';
import * as lambda from '@aws-cdk/aws-lambda';
import * as path from 'path';

export interface WebViewStackProps extends cdk.StackProps {
  clusterSocketAddress: string;
  vpc: ec2.Vpc;
}

export class WebViewStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: WebViewStackProps) {
    super(scope, id, props);

    const websiteBucket = new s3.Bucket(this, 'WebsiteBucket', {
      autoDeleteObjects: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
    // websiteBucket.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);

    new s3deploy.BucketDeployment(this, 'DeployWebsiteFiles', {
      sources: [s3deploy.Source.asset('./../website/', { exclude: ['index.html'] })],
      destinationBucket: websiteBucket
    });

    const websiteLambda = new lambda.Function(this, 'WebsiteLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda.lambda_handler',
      code: lambda.Code.fromAsset('./../website-lambda/deployment.zip'),
      environment: {
        CLUSTER_SOCKETADDRESS: props.clusterSocketAddress
      },
      vpc: props.vpc,
      vpcSubnets: props.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE }),
    });

    new apigw.LambdaRestApi(this, 'WebSiteAPI', {
      handler: websiteLambda,
    });
  }
}
