from utah.core.utilities import get_dict_from_json_file, write_dict_to_json_file
from utah.core.profile import ProfileInfo
from utah.core.profile import BaseProfileService
from utah.core.utilities import delete_file
import os

class JsonProfileService(BaseProfileService):
    def __init__(self, profile_directory_path:str):
        super(JsonProfileService, self).__init__()
        self.profile_directory_path = profile_directory_path


    def profile_info_path(self, user_id):
        return "%s/%s.json" % (self.profile_directory_path, user_id)


    def get_profile_info(self, user_id):
        ret_profile = None
        try:
            json_info = get_dict_from_json_file(self.profile_info_path(user_id))
            ret_profile = ProfileInfo(json_info["user_id"], json_info["email_address"], json_info["first_name"], json_info["last_name"], json_info["timezone"])
        except FileNotFoundError:
            pass

        return ret_profile


    def delete_profile_info(self, user_id):
        ret_profile = self.get_profile_info(user_id)
        delete_file(self.profile_info_path(user_id))
        return ret_profile


    def get_all_profiles(self):
        file_list = os.listdir(self.profile_directory_path)
        ret_list = []
        for filename in file_list:
            user_id = filename.replace(".json", "")
            profile = self.get_profile_info(user_id)
            ret_list.append(profile)

        return ret_list


    def write_profile_info(self, profile_info:ProfileInfo):
        obj = { "user_id":profile_info.user_id,
                "email_address" : profile_info.email_address,
                "first_name" : profile_info.first_name,
                "last_name" : profile_info.last_name,
                "timezone" : profile_info.timezone,
                }

        write_dict_to_json_file("%s/%s.json" % (self.profile_directory_path, profile_info.user_id), obj)