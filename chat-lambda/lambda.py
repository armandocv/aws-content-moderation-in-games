from __future__  import print_function  # Python 2/3 compatibility

import os
import base64
import json
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

def lambda_handler(event, context):
    print(event)
    for record in event['Records']:
        data_bytes = base64.b64decode(record["kinesis"]["data"])
        print("Decoded payload: " + str(data_bytes))
        data = json.loads(data_bytes)

        if (data['eventName'] == 'INSERT'):
            source = data['dynamodb']['NewImage']['GamerAlias']['S']
            target = data['dynamodb']['NewImage']['target']['S']
            game = data['dynamodb']['NewImage']['game']['S']

            # Find people involved in message and add them as vertices if they don't exist
            findAndAddPerson(source)
            findAndAddPerson(target)

            # Link people involved in conversation to game
            addPlays(source, game)
            addPlays(target, game)

            addChat(source, target, game)

    print('Successfully processed %s records.' % str(len(event['Records'])))

def findAndAddPerson(person):
    print('person: ' + person)
    person_result = g.V(person).toList()
    print(person_result)
    if (len(person_result) == 0):
        g.addV('person').property(T.id, person).next()
        print('Added: ' + person)
    else:
        print('Already exists:' + person)

def addPlays(person, game):
    print('person: ' + person)
    print('game: ' + game)
    plays_result = g.V(person).out('plays').hasId(game).toList()
    if (len(plays_result) == 0):
        g.V(person).addE('plays').to(g.V(game).next()).next()
        print('Added: ' + person + ' to ' + game)
    else:
        print(person + ' already plays ' + game)

def addChat(source, target, game):
    compositeId = source + ':' + target + ':' + game
    chat_result = g.E(compositeId).toList()
    if (len(chat_result) == 0):
        g.V(source).addE('chats').to(g.V(target).next()).property(T.id, compositeId).next()
        print('Added: ' + compositeId)
    else:
        print('Already exists: ' + compositeId)
