from flask import Flask, jsonify, make_response, request
import os
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


app = Flask(__name__)
statics.load_statics(globals())
CLUSTER_SOCKETADDRESS = "moderationdatabaseb61fc511-sgd87mxc1bgs.cluster-cutkucxw4vp4.us-west-2.neptune.amazonaws.com:8182" ## Make into environment variable
remoteConn = DriverRemoteConnection('wss://' + CLUSTER_SOCKETADDRESS + '/gremlin','g')
graph = Graph()
g = graph.traversal().withRemote(remoteConn)

@app.route("/score")
def get_score():
    gameId = request.args.get('gameId')
    player = request.args.get('player')
    print('gameId is: ' + gameId)
    print ('player is: ' + player)


    result = g.V(player).outE('chats').has('gameId', gameId).valueMap(True).select('score').sum().next()
    print(result)
    return make_response(jsonify(score=result), 200)

def get_scores():
    return 0

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
