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
            person = data['dynamodb']['NewImage']['person']['S']
            print('person: ' + person)

            person_result = g.V().has('person','GamerAlias',person).toList()
            print(person_result)
            if (len(person_result) == 0):
                g.addV('person').property(T.id, person).property('GamerAlias', person).next()
                print('Added: ' + person)

            game = data['dynamodb']['NewImage']['game']['S']
            print('game: ' + game)
            plays_result = g.V().has('person','GamerAlias',person).out('plays').has('game','GameTitle',game).toList()
            if (len(plays_result) == 0):
                plays_result = g.addE('plays').from(g.V(person)).to(g.V(game))
                print('Added: ' + plays_result)

            sequence_number = record['kinesis','sequenceNumber']
            message = data['dynamodb']['NewImage']['message']['S']
            chat_result = g.addV('chat').property(T.id, sequence_number).property('message', message).next()
            print('Added: ' + chat_result)
            chat_result = g.addE('says').from(g.V(person)).to(g.V(sequence_number))
            print('Added: ' + chat_result)


    # make this report each record
    print('Successfully processed %s records.' % str(len(event['Records'])))
