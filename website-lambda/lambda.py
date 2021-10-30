from __future__  import print_function  # Python 2/3 compatibility

import os
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

CLUSTER_SOCKETADDRESS = os.environ['CLUSTER_SOCKETADDRESS']

def lambda_handler(event, context):
    graph = Graph()

    path = event['path']

    remoteConn = DriverRemoteConnection('wss://' + CLUSTER_SOCKETADDRESS + '/gremlin','g')
    g = graph.traversal().withRemote(remoteConn)

    result = {}
    result['statusCode'] = 200
    result['headers'] = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        "Access-Control-Allow-Credentials" : True
    }

    if (path == '/nodes'):
        result['body'] = str(g.V().toList())
    if (path == '/edges'):
        result['body'] = str(g.E().toList())

    print(result)
    return result
