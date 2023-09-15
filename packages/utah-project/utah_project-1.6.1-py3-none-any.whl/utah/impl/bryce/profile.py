from utah.core.profile import ProfileInfo
from utah.core.profile import BaseProfileService
from utah.impl.bryce.utilities import ConnectionDefinition
import logging

logger = logging.getLogger(__name__)

def obj_to_profile(obj):
    ret_profile = None

    if obj:
        ret_profile = ProfileInfo(
            obj["user_id"],
            obj["email_address"],
            obj["first_name"],
            obj["last_name"],
            obj["timezone"]
        )

    return ret_profile


def profile_to_obj(profile:ProfileInfo):
    return {
        "user_id": profile.user_id,
        "email_address": profile.email_address,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "timezone": profile.timezone
    }


class ProfileService(BaseProfileService):
    def __init__(self, mongo_db_info:dict):
        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)


    def get_collection(self):
        logger.debug("ProfileService.get_collection()")
        return self.conn_def.get_database()["profile"]


    def get_profile_info(self, user_id:str):
        return obj_to_profile(self.get_collection().find_one({"user_id" : user_id}))


    def delete_profile_info(self, user_id:str):
        return self.get_collection().delete_one({"user_id" : user_id})


    def write_profile_info(self, profile_info:ProfileInfo):
        coll = self.get_collection()
        obj = profile_to_obj(profile_info)

        if not self.get_profile_info(profile_info.user_id):
            coll.insert_one(obj)
        else:
            coll.update_one({"user_id" : profile_info.user_id}, {"$set" : obj})
    

    def get_all_profiles(self):
        ret_list = []

        for obj in self.get_collection().find():
            ret_list.append(obj_to_profile(obj))

        return ret_list


