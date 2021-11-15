from flask import Flask,jsonify,make_response,request
import os
import boto3
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
CLUSTER_SOCKETADDRESS = os.environ['CLUSTER_SOCKETADDRESS']

remoteConn = DriverRemoteConnection('wss://' + CLUSTER_SOCKETADDRESS + '/gremlin','g')
graph = Graph()
g = graph.traversal().withRemote(remoteConn)

app = Flask(__name__)
USERS_TABLE = os.environ['USERS_TABLE']
client = boto3.client('dynamodb')


@app.route("/score")
def get_score(username):
    gameId = request.args.get('gameId')
    player = request.args.get('player')

    result = g.V(player).outE().has('gameId', gameId).valueMap('true').select('score').sum()
    print(result)

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')