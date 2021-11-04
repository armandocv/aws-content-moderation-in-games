import * as cdk from '@aws-cdk/core';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as ddb from '@aws-cdk/aws-dynamodb';
import * as kinesis from '@aws-cdk/aws-kinesis';
import * as lambda from '@aws-cdk/aws-lambda';
import * as lambdaSource from '@aws-cdk/aws-lambda-event-sources';
import * as ssm from '@aws-cdk/aws-ssm';

export interface GameIngestStackProps extends cdk.StackProps {
  clusterSocketAddress: string;
  vpc: ec2.Vpc;
}

export class GameIngestStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: GameIngestStackProps) {
    super(scope, id, props);

    const chatStream = new kinesis.Stream(this, 'GameChatStream', {
      streamName: 'game-chat-stream'
    });

    const chatTable = new ddb.Table(this, 'GameChatTable', {
      tableName: 'GameChat',
      partitionKey: { name: 'id', type: ddb.AttributeType.STRING },
      kinesisStream: chatStream,
      stream: ddb.StreamViewType.NEW_IMAGE,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const chatIngestLambda = new lambda.Function(this, 'ChatIngestLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda.lambda_handler',
      code: lambda.Code.fromAsset('./../chat-lambda'),
      environment: {
        CLUSTER_SOCKETADDRESS: props.clusterSocketAddress
      },
      vpc: props.vpc,
      vpcSubnets: props.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE }),
      layers: [lambda.LayerVersion.fromLayerVersionArn(this, 'BaseLayerFromArn',
        ssm.StringParameter.valueForStringParameter(this, '/layers/GremlinLambdaLayer'))],
    });

    chatIngestLambda.addEventSource(new lambdaSource.KinesisEventSource(chatStream, {
      startingPosition: lambda.StartingPosition.LATEST,
    }));
  }
}
