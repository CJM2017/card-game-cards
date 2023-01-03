import uuid
from marshmallow import Schema, fields

class Card(object):
    def __init__(self, userId, type, content):
        self.userId = userId
        self.type = type
        self.content = content
        
        self.cardId = str(uuid.uuid4())
        self.isOpen = False

class CardSchema(Schema):
    cardId = fields.Str()
    userId = fields.Str()
    type = fields.Str()
    content = fields.Str()
    isOpen = fields.Bool()
