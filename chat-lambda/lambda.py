from __future__  import print_function  # Python 2/3 compatibility

import os
import base64
import json
import boto3
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import Cardinality

CLUSTER_SOCKETADDRESS = os.environ['CLUSTER_SOCKETADDRESS']

comprehend_client = boto3.client('comprehend', region_name='us-west-2')
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
            gameId = data['dynamodb']['NewImage']['gameId']['S']
            message = data['dynamodb']['NewImage']['message']['S']

            # Add GameInstance (id:GameId) if it doesn't exist
            findAndAddGameInstance(gameId)

            # Find people involved in message and add them as vertices if they don't exist
            findAndAddPerson(source)

            # Add person vertex is the target is a specific person, else set the target to a game instance for the 'All' case
            if(target == 'All'):
                target = gameId
            else:
                findAndAddPerson(target)

            # Link people involved in conversation to game
            addPlays(source, game)

            # If the target is a person, add a 'plays' edge between them and the game.
            if(target != gameId):
                addPlays(target, game)

            score = scoreMsg(target, gameId, message)
            addChat(source, target, gameId, score)

    print('Successfully processed %s records.' % str(len(event['Records'])))

def scoreMsg(target, gameId, message):
    isSpecific = False
    response = comprehend_client.classify_document(
        Text=message,
        EndpointArn='arn:aws:comprehend:us-west-2:038505644587:document-classifier-endpoint/HarassmentClassifier'
    )
    print(response)
    score = 0
    labels = response['Labels']
    for label in labels:
        if((label['Name'] == 'IsAbusive') and (label['Score'] >= 0.80)):
            print('Abuse detected, feelings hurt :(') 
            score += 1
        if((label['Name'] == 'HasBadLanguage') and (label['Score'] >= 0.80)):
            print('Bad word detected') 
            score += 2
        if((label['Name'] == 'SpecificTarget') and (label['Score'] >= 0.80)):
            print("Specific target found") 
            isSpecific = True  
    
    # If the target isn't 'All', then it is specific by default (Direct Message)
    if(target != gameId):
        isSpecific = True

    if(isSpecific):
        score += 3
        
    print('Score is: ' + str(score))
    return score

def findAndAddGameInstance(gameId):
    print('gameId: ' + gameId)
    gameInstance_result = g.V(gameId).toList()
    print(gameInstance_result)
    if (len(gameInstance_result) == 0):
        g.addV('gameInstance').property(T.id, gameId).next()
        print('Added: ' + gameId)
    else:
        print('Already exists:' + gameId)
   
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

def addPlaysInstance(person, gameId):
    print('person: ' + person)
    print('gameId: ' + gameId)
    plays_result = g.V(person).out('plays').hasId(gameId).toList()
    if (len(plays_result) == 0):
        g.V(person).addE('plays').to(g.V(gameId).next()).next()
        print('Added: ' + person + ' to ' + gameId)
    else:
        print(person + ' already plays ' + gameId)

def addChat(source, target, gameId, score):
    if(target == gameId):
        compositeId = source + ':' + gameId
    else:
        compositeId = source + ':' + target + ':' + gameId

    chat_result = g.E(compositeId).toList()
    print(chat_result)
    if (len(chat_result) == 0):
        g.V(source).addE('chats').to(g.V(target)).property(T.id, compositeId).property(Cardinality.single, 'score', score).property(Cardinality.single, 'gameId', gameId).iterate()
        print('Added: ' + compositeId + ' with score: ' + str(score))
    else:
        ## Double check this... not sure if += will work. Desired behavior is, if the edge already exist, overwrite T.score property with T.score + score
        g.E(compositeId).property(Cardinality.single, 'score')
        print('Already exists: ' + compositeId)
