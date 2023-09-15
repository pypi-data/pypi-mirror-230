import logging
from datetime import datetime
from .utilities import ConnectionDefinition
from utah.core.authentication import AuthenticationInfo
from utah.core.authentication import AuthenticationToken
from utah.core.authentication import BaseAuthenticationService
from utah.core.utilities import date_to_string
from utah.core.utilities import string_to_date

logger = logging.getLogger(__name__)

class AuthenticationService(BaseAuthenticationService):
    def __init__(   self, 
                    mongo_db_info:dict, 
                    token_cache_timeout_secs:int, 
                    account_verification_required:False, 
                    pwd_min_upper_case:int=0, 
                    pwd_min_lower_case:int=0, 
                    pwd_min_numbers:int=0, 
                    pwd_min_special_chars:int=0, 
                    pwd_min_length:int=6):

        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)

        super(AuthenticationService, self).__init__(token_cache_timeout_secs, account_verification_required, pwd_min_upper_case, pwd_min_lower_case, pwd_min_numbers, pwd_min_special_chars, pwd_min_length)


    def get_collection(self):
        logger.debug("AuthenticationService.get_collection()")
        return self.conn_def.get_database()["authentication"]


    def json_obj_from_authentication_info(self, authentication_info:AuthenticationInfo):

        dict_tokens = []

        for token in authentication_info.authentication_tokens:
        
            dict_token = {}
            dict_token["user_id"] = token.user_id
            dict_token["description"] = token.description
            dict_token["key"] = token.key
            dict_token["expire_date"] = date_to_string(token.expire_date)

            dict_tokens.append(dict_token)


        obj = { "user_id":authentication_info.user_id,
                "salt" : list(authentication_info.salt),
                "hashed_password" : list(authentication_info.hashed_password),
                "verification_code" : authentication_info.verification_code,
                "authentication_tokens" : dict_tokens
        }

        return obj


    def authentication_info_from_json_obj(self, json_obj):
        ret_ai = None

        if json_obj:
            auth_tokens = []

            for dict_token in json_obj["authentication_tokens"]:
                auth_tokens.append(AuthenticationToken(dict_token["user_id"], dict_token["description"], string_to_date(dict_token["expire_date"]), dict_token["key"]))

            ret_ai = AuthenticationInfo(json_obj["user_id"], bytearray(json_obj["salt"]), bytearray(json_obj["hashed_password"]), json_obj["verification_code"], auth_tokens)

        return ret_ai



    def obj_query(self, authentication_info:AuthenticationInfo):
        return {"user_id" : authentication_info.user_id }


    def get_token_from_key(self, key:str):
        query = {"authentication_tokens.key":key}
        coll = self.get_collection()
        aiobj = coll.find_one(query)
        for tokenObj in aiobj["authentication_tokens"]:
            if tokenObj["key"] == key:
                return AuthenticationToken(tokenObj["user_id"], tokenObj["description"], string_to_date(tokenObj["expire_date"]), tokenObj["key"])


    def get_authentication_info(self, user_id:str):
        coll = self.get_collection()
        return self.authentication_info_from_json_obj(coll.find_one({"user_id" : user_id}))


    def write_authentication_info(self, authentication_info:AuthenticationInfo):
        coll = self.get_collection()
        json_obj = self.json_obj_from_authentication_info(authentication_info)
        query = self.obj_query(authentication_info)
        if not coll.find_one(query):
            coll.insert_one(json_obj)
        else:
            coll.update_one(query, {"$set":json_obj})


    def delete_authentication_info(self, user_id:str):
        coll = self.get_collection()
        coll.delete_one({"user_id" : user_id})
