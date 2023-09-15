import logging
from utah.core.authorize import BaseURIAuthorizationService, Group
from utah.core.authorize import URIAccessRight
from utah.core.authorize import BaseGroupService
from utah.impl.bryce.utilities import ConnectionDefinition
from utah.core.utilities import func_logger

logger = logging.getLogger(__name__)

@func_logger
def obj_from_group(group:Group) -> dict:
    return {
        "name" : group.name,
        "description" : group.description
    }


@func_logger
def group_from_obj(obj:dict) -> Group:
    if obj:
        return Group(obj["name"], obj["description"])
    else:
        return None


@func_logger
def uri_access_right_from_obj(env_type:str, obj:dict) -> URIAccessRight:
    ret_right = None
    if obj:
        del obj["_id"]
        if not obj["permitted_environments"] or env_type in obj["permitted_environments"]:
            obj["disabled"] = False
        else:
            obj["disabled"] = True

        ret_right = URIAccessRight(**obj)

    return ret_right


@func_logger
def obj_from_uri_access_right(uri_access_right:URIAccessRight) -> dict:
    return {
        "id": uri_access_right.id, 
        "category": uri_access_right.category, 
        "right_name": uri_access_right.right_name, 
        "uri": uri_access_right.uri, 
        "methods": uri_access_right.methods, 
        "filters": uri_access_right.filters, 
        "authorized_groups": uri_access_right.authorized_groups, 
        "permitted_environments": uri_access_right.permitted_environments 
    }


class GroupService(BaseGroupService):
    @func_logger
    def __init__(self, mongo_db_info:dict, enrollments_mongo_db_info:dict, default_anonymous_groups:list, default_logged_in_groups:list):

        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)
        self.enrollments_conn_def:ConnectionDefinition = ConnectionDefinition(**enrollments_mongo_db_info)

        super(GroupService, self).__init__(default_anonymous_groups, default_logged_in_groups)


    @func_logger
    def get_enrollment_coll(self):
        logger.debug("GroupService.get_enrollment_coll()")
        return self.enrollments_conn_def.get_database()["enrollments"]


    @func_logger
    def get_group_coll(self):
        return self.conn_def.get_database()["groups"]


    @func_logger
    def read_group_names_for_user(self, user_id:str):
        logger.debug("GroupService.read_group_names_for_user()")
        enrollments = self.get_enrollment_coll().find_one({"user_id" : user_id})
        if enrollments:
            return enrollments["group_names"]
        else:
            return []


    @func_logger
    def get_groups(self):
        ret_groups = []
        for obj in self.get_group_coll().find():
            ret_groups.append(group_from_obj(obj))

        return ret_groups


    @func_logger
    def get_group(self, name:str):
        return group_from_obj(self.get_group_coll().find_one({"name":name}))


    @func_logger
    def get_group_members(self, group_name:str):
        logger.debug("GroupService.get_group_members()")
        ret_user_ids = []
        for obj in self.get_enrollment_coll().find({"group_names":group_name}):
            ret_user_ids.append(obj["user_id"])

        return ret_user_ids


    @func_logger
    def update_group(self, group:Group):
        self.get_group_coll().update_one({"name":group.name}, {"$set" : obj_from_group(group)})


    @func_logger
    def add_group(self, group:Group):
        self.get_group_coll().insert_one(obj_from_group(group))


    @func_logger
    def delete_group(self, name:str):
        logger.debug("GroupService.delete_group()")

        self.get_group_coll().delete_one({"name": name})
        self.get_enrollment_coll().update_many(
            {"group_names" : name},
            { "$pull": { "group_names": name } }
        )



    @func_logger
    def update_groups_for_user(self, user_id:str, groups:list):
        logger.debug("GroupService.update_groups_for_user()")
        coll = self.get_enrollment_coll()
        if coll.find_one({"user_id" : user_id}):
            coll.update_one({"user_id":user_id}, {"$set": {"user_id": user_id, "group_names" : groups} })
        else:
            coll.insert_one({"user_id": user_id, "group_names" : groups})



class URIAuthorizationService(BaseURIAuthorizationService):
    @func_logger
    def __init__(self, mongo_db_info:dict, group_service_name:str, cache_timeout_secs:int, environment_type:str="FULL", available_environment_types:str="FULL"):

        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)

        super(URIAuthorizationService, self).__init__(group_service_name, cache_timeout_secs, environment_type, available_environment_types)


    @func_logger
    def get_right_coll(self):
        logger.debug("URIAuthorizationService.get_right_coll()")
        return self.conn_def.get_database()["rights"]


    @func_logger
    def get_all_authorizations(self):
        ret_authorizations = []

        for obj in self.get_right_coll().find():
            ret_authorizations.append(uri_access_right_from_obj(self.environment_type, obj))

        return ret_authorizations


    @func_logger
    def get_authorization(self, id:str):
        return uri_access_right_from_obj(self.environment_type, self.get_right_coll().find_one({"id" : id}))


    @func_logger
    def find_authorization(self, category, right_name)->URIAccessRight:
        return uri_access_right_from_obj(self.environment_type, self.get_right_coll().find_one({"category" : category, "right_name": right_name}))


    @func_logger
    def update_authorization_io(self, uri_access_right:URIAccessRight):
        self.get_right_coll().update_one({"id" : uri_access_right.id }, {"$set" : obj_from_uri_access_right(uri_access_right)})


    @func_logger
    def add_authorization_io(self, uri_access_right:URIAccessRight):
        self.get_right_coll().insert_one(obj_from_uri_access_right(uri_access_right))


    @func_logger
    def delete_authorization_io(self, id:str):
        self.get_right_coll().delete_one({"id" : id})


    @func_logger
    def remove_group_from_authorizations_io(self, group_name):
        coll = self.get_right_coll()
        for obj in coll.find({"group_names":group_name}):
            obj["group_names"].remove(group_name)
            coll.update_one({"_id" : obj["_id"]}, obj)


    @func_logger
    def get_access_rights_for_uri_io(self, uri):
        ret_list = None
        for obj in self.get_right_coll().find({ "uri" : uri}):
            if ret_list == None:
                ret_list = []

            ret_list.append(uri_access_right_from_obj(self.environment_type, obj))

        return ret_list


