import os
import random
import boto3

from models.card import CardSchema

from flask import Flask, jsonify, request
app = Flask(__name__)

CARDS_TABLE = os.environ['CARDS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')
 
if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')


@app.route("/cards", methods=["POST"])
def createCard():
    card = CardSchema().load(request.get_json())

    _ = client.put_item(
        TableName=CARDS_TABLE,
        Item={
            'cardId': {'S': card.cardId },
            'userId': {'S': card.userId },
            'type': {'S': card.type },
            'content': {'S': card.content },
            'opened': {'BOOL': card.isOpen },          
        }
    )
 
    return jsonify(card)


@app.route("/cards/<int:numCards>")
def getRandomCards(numCards):
    # get all cards
    cards = getAllCards()

    # filter cards for those which have not been open
    unOpenedCards = filter(lambda card: not card.isOpen, cards)

    # group cards by card type
    types = groupCardsByType(unOpenedCards)

    # get random cards grouped by type
    randomCards = getRandomCards(types, numCards)

    return jsonify(randomCards)


def getAllCards():
    response = client.scan(TableName=CARDS_TABLE)
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = client.scan(
            TableName=CARDS_TABLE,
            ExclusiveStartKey=response['LastEvaluatedKey'])
            
        data.extend(response['Items'])

    schema = CardSchema(many=True)
    cards = schema.dump(data)

    return cards


def groupCardsByType(cards):
    types = {}
    for card in cards:
        if card.type in types:
            types[card.type].append(card)
        else:
            types[card.type] = [card]


    return list(types.values())


def getRandomCards(types, numCards):
    typeIndex = 0
    numTypes = len(types)
    randomCards = []

    while numCards > 0 and types:
        options = types[typeIndex]
        optionCount = len(options)
        
        if optionCount == 0:
            continue

        optionIndex = random.randrange(optionCount)
        randomCards.append(options.pop(optionIndex))

        typeIndex = typeIndex + 1 % numTypes
        numCards -= 1

    return randomCards