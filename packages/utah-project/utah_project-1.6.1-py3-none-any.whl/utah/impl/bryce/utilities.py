import pymongo
from utah.core.utilities import RWD as CoreRWD, RWDInvalidKey, RWDNotFound, DecodeError
import logging

logger = logging.getLogger(__name__)


class ConnectionDefinition():
    def __init__(self, connection_url:str, db_name:str):
        self.mongo_url = connection_url
        self.db_name = db_name

    def get_client(self):
        return pymongo.MongoClient(self.mongo_url)

    def get_database(self):
        return self.get_client()[self.db_name]



class RWD(CoreRWD):
    def __init__(self, mongo_db_info:dict, collection:str):
        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)
        self.collection = collection

    def get_collection(self):
        logger.debug("RWD.get_collection()")
        return self.conn_def.get_database()[self.collection]


    def read(self, key) -> object:
        self.key_parse(key)

        ret_obj = self.get_collection().find_one({"key" : key})
        if not ret_obj:
            raise RWDNotFound("key:[%s]" % key)

        return ret_obj


    def write(self, obj: object):
        if 'key' in obj:
            key = obj['key']
        else:
            raise RWDInvalidKey('id attribute missing from object')

        (namespace, id) = self.key_parse(key)
        
        coll = self.get_collection()

        ret_obj = self.get_collection().find_one({"key" : key})
        if not ret_obj:
            coll.insert_one(obj)
        else:
            coll.update_one({"key" : key}, {"$set" : obj})

    
    def delete(self, key) -> object:
        obj = self.read(key)

        self.get_collection().delete_one({"key" : key})

        return obj


    def get_all_keys(self, namespace='/') -> list:
        match_string='^\/'
        if not namespace=='/':
            segs=namespace.split('/')
            match_string='^' + '\/'.join(segs) + '\/'

        ret_list = []

        for obj in self.get_collection().find({'key':{'$regex':match_string}}):
            ret_list.append(obj['key'])

        return ret_list