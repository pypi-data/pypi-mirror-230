import uuid
from collections import namedtuple

class Utils():
    
    @classmethod
    def get_guid(self):
        Guid = uuid.uuid4().hex
        return Guid
    
    @classmethod
    def custom_entity_decoder(self, entityDictionary):
        return namedtuple('X', entityDictionary.keys())(*entityDictionary.values())
