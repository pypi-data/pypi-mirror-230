from utah.core.authentication import BaseAuthenticationService, AuthenticationInfo, AuthenticationToken
from utah.core.utilities import get_dict_from_json_file, write_dict_to_json_file, delete_file, date_to_string, string_to_date
import os

class JsonAuthenticationService(BaseAuthenticationService):
    def __init__(self, authentication_directory_path:str, token_cache_timeout_secs:int, account_verification_required:bool, pwd_min_upper_case:int=0, pwd_min_lower_case:int=0, pwd_min_numbers:int=0, pwd_min_special_chars:int=0, pwd_min_length:int=6):
        super(JsonAuthenticationService, self).__init__(token_cache_timeout_secs, account_verification_required, pwd_min_upper_case, pwd_min_lower_case, pwd_min_numbers, pwd_min_special_chars, pwd_min_length)
        
        self.authentication_directory_path = authentication_directory_path
        self.accounts_directory_path = authentication_directory_path + "/accounts"
        self.token_directory_path = authentication_directory_path + "/token"

    def authentication_info_path(self, user_id:str):
        ret_path = "%s/%s.json" % (self.accounts_directory_path, user_id)
        return ret_path


    def get_authentication_info(self, user_id):
        ret_ai = None
        try:
            json_info = get_dict_from_json_file(self.authentication_info_path(user_id))
            ret_ai = self.authentication_info_from_json_obj(json_info)
        except FileNotFoundError:
            pass

        return ret_ai
        

    def write_authentication_info(self, authentication_info:AuthenticationInfo):
        obj = self.json_obj_from_authentication_info(authentication_info)
        write_dict_to_json_file("%s/accounts/%s.json" % (self.authentication_directory_path, authentication_info.user_id), obj)


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
        auth_tokens = []

        for dict_token in json_obj["authentication_tokens"]:
            auth_tokens.append(AuthenticationToken(dict_token["user_id"], dict_token["description"], string_to_date(dict_token["expire_date"]), dict_token["key"]))

        ret_ai = AuthenticationInfo(json_obj["user_id"], bytearray(json_obj["salt"]), bytearray(json_obj["hashed_password"]), json_obj["verification_code"], auth_tokens)

        return ret_ai


    def delete_authentication_info(self, user_id:str):
        ret_info = self.get_authentication_info(user_id)
        json_obj_path = self.authentication_info_path(user_id)
        delete_file(json_obj_path)
        return ret_info


    def get_token_from_key(self, key:str):
        ret_token = None

        for entry in os.scandir(self.accounts_directory_path):
            user_id = entry.name[0:-5]
            ai = self.get_authentication_info(user_id)
            for at in ai.authentication_tokens:
                if at.key == key:
                    ret_token = at
                    break

            if ret_token:
                break

        return ret_token