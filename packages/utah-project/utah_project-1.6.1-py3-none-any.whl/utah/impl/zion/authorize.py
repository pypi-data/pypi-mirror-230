from utah.core.authorize import BaseGroupService
from utah.core.authorize import Group
from utah.core.authorize import NoSuchGroupException
from utah.core.authorize import DuplicateGroupException
from utah.core.authorize import URIAccessRight
from utah.core.authorize import DuplicateRight
from utah.core.authorize import BaseURIAuthorizationService
from utah.core.utilities import get_service_object
from threading import Lock
from utah.core.utilities import get_dict_from_json_file
from utah.core.utilities import write_dict_to_json_file
import logging
from time import time
from functools import lru_cache

logger = logging.getLogger(__name__)

class GroupService(BaseGroupService):
    def __init__(self, default_anonymous_groups:list, default_logged_in_groups:list, group_config_path:str, enrollments_config_path:str, cache_timeout_secs=300):
        BaseGroupService.__init__(self, default_anonymous_groups, default_logged_in_groups)

        self.group_config_path = group_config_path
        self.enrollments_config_path = enrollments_config_path
        self.cache_timeout_secs = cache_timeout_secs
        self.lock = Lock()


    def read_group_names_for_user(self, user_id:str):
        ret_list = None
        user_mappings = self.get_all_user_mappings()
        if user_id in user_mappings:
            ret_list = user_mappings[user_id]

        return ret_list


    def get_groups(self):
        ret_groups = []

        jgroups = get_dict_from_json_file(self.group_config_path)


        for name in jgroups:
            desc = jgroups[name]
            group = Group(name, desc)

            ret_groups.append(group)


        return ret_groups


    def get_group(self, name:str):
        ret_group = None

        jgroups = get_dict_from_json_file(self.group_config_path)

        if name in jgroups:
            ret_group = Group(name, jgroups[name])

        return ret_group



    def get_group_members(self, group_name:str):
        ret_list = []

        all_user_mappings = get_dict_from_json_file(self.enrollments_config_path)

        for user_id in all_user_mappings:
            groups = all_user_mappings[user_id]
            if group_name in groups:
                ret_list.append(user_id)

        return ret_list




    def update_group(self, group:Group):
        self.lock.acquire()

        jgroups = get_dict_from_json_file(self.group_config_path)

        if not group.name in jgroups:
            raise NoSuchGroupException("Group:[%s] does not exist" % group.name)

        jgroups[group.name] = group.description

        write_dict_to_json_file(self.group_config_path, jgroups)

        self.lock.release()


    def add_group(self, group:Group):
        self.lock.acquire()

        jgroups = get_dict_from_json_file(self.group_config_path)

        if group.name in jgroups:
            raise DuplicateGroupException("Group:[%s] already exists" % group.name)

        jgroups[group.name] = group.description

        write_dict_to_json_file(self.group_config_path, jgroups)

        self.lock.release()


    def delete_group(self, name:str):
        self.lock.acquire()

        ret_group = None

        jgroups = get_dict_from_json_file(self.group_config_path)

        if not name in jgroups:
            raise NoSuchGroupException("Group:[%s] does not exist" % name)

        description = jgroups[name]

        ret_group = Group(name, description)        

        del jgroups[name]

        write_dict_to_json_file(self.group_config_path, jgroups)

        all_user_mappings = get_dict_from_json_file(self.enrollments_config_path)
        for user_id in all_user_mappings:
            users_groups = all_user_mappings[user_id]
            if name in users_groups:
                users_groups.remove(name)

        write_dict_to_json_file(self.enrollments_config_path, all_user_mappings)

        self.lock.release()

        return ret_group


    def update_groups_for_user(self, user_id:str, groups:list):
        self.lock.acquire()

        all_user_mappings = self.get_all_user_mappings()

        if len(groups) == 0:
            if user_id in all_user_mappings:
                del all_user_mappings[user_id]
        else:
            all_user_mappings[user_id] = groups

        write_dict_to_json_file(self.enrollments_config_path, all_user_mappings)

        self.lock.release()



    def get_all_user_mappings(self):
        return self.__get_all_user_mappings(ttl_hash=self.get_ttl_hash())


    @lru_cache(1, True)
    def __get_all_user_mappings(self, ttl_hash:int):
        logger.info("group cache load")

        all_user_mappings = get_dict_from_json_file(self.enrollments_config_path)

        return all_user_mappings


    def get_ttl_hash(self):
        """Return the same value withing `seconds` time period"""
        return round(time() / self.cache_timeout_secs)




class URIAuthorizationService(BaseURIAuthorizationService):
    def __init__(self, group_service_name:str, authorization_config_path:str, cache_timeout_secs=300, environment_type:str="FULL", available_environment_types:str="FULL"):
        BaseURIAuthorizationService.__init__(self, group_service_name, cache_timeout_secs, environment_type, available_environment_types)

        self.group_service_name = group_service_name
        self.cache_timeout_secs = cache_timeout_secs
        self.authorization_config_path = authorization_config_path
        self.lock = Lock()
        

    def get_all_authorizations(self):
        ret_authorizations = []
        self.lock.acquire()
        raw_authorizations = get_dict_from_json_file(self.authorization_config_path)
        self.set_disabled_flag(raw_authorizations)
        self.lock.release()

        for raw_authorization in raw_authorizations:
            uri_access_right = URIAccessRight(**raw_authorization)
            ret_authorizations.append(uri_access_right)


        return ret_authorizations


    def find_authorization(self, category:str, right_name:str):
        ret_uri_access_right = None
        all_authorizations = get_dict_from_json_file(self.authorization_config_path)
        for authorization in all_authorizations:
            if authorization["category"] == category and authorization["right_name"] == right_name:
                ret_uri_access_right = URIAccessRight(**authorization)

        return ret_uri_access_right


    def get_authorization(self, id:str):
        ret_uri_access_right = None
        self.lock.acquire()
        all_authorizations = get_dict_from_json_file(self.authorization_config_path)
        self.set_disabled_flag(all_authorizations)
        self.lock.release()

        for authorization in all_authorizations:
            if authorization["id"] == id:
                ret_uri_access_right = URIAccessRight(**authorization)
                break

        return ret_uri_access_right


    def update_authorization_io(self, uri_access_right:URIAccessRight):
        self.lock.acquire()

        all_authorizations = get_dict_from_json_file(self.authorization_config_path)

        for authorization in all_authorizations:
            if authorization["id"] == uri_access_right.id:
                authorization["category"] = uri_access_right.category
                authorization["right_name"] = uri_access_right.right_name
                authorization["uri"] = uri_access_right.uri
                authorization["filters"] = uri_access_right.filters
                authorization["methods"] = uri_access_right.methods
                authorization["authorized_groups"] = uri_access_right.authorized_groups
                authorization["permitted_environments"] = uri_access_right.permitted_environments
                break

        write_dict_to_json_file(self.authorization_config_path, all_authorizations)

        self.lock.release()


    def add_authorization_io(self, uri_access_right:URIAccessRight):
        self.lock.acquire()

        all_authorizations = get_dict_from_json_file(self.authorization_config_path)

        for authorization in all_authorizations:
            if authorization["category"] == uri_access_right.category and authorization["right_name"] == uri_access_right.right_name:
                self.lock.release()
                raise DuplicateRight("Duplicate right %s::%s" % (uri_access_right.category, uri_access_right.right_name))

        authorization = {}

        authorization["id"] = uri_access_right.id
        authorization["category"] = uri_access_right.category
        authorization["right_name"] = uri_access_right.right_name
        authorization["uri"] = uri_access_right.uri
        authorization["filters"] = uri_access_right.filters
        authorization["methods"] = uri_access_right.methods
        authorization["authorized_groups"] = uri_access_right.authorized_groups
        authorization["permitted_environments"] = uri_access_right.permitted_environments

        all_authorizations.append(authorization)

        write_dict_to_json_file(self.authorization_config_path, all_authorizations)

        self.lock.release()


    def delete_authorization_io(self, id:str):
        self.lock.acquire()

        ret_authorization = None

        all_authorizations = get_dict_from_json_file(self.authorization_config_path)
        for ptr in range(0, len(all_authorizations)):
            authorization = all_authorizations[ptr]
            if authorization["id"] == id:
                ret_authorization = URIAccessRight(**authorization)
                del all_authorizations[ptr]
                break

        if ret_authorization:
            remaining_uri_count = 0

            for ptr in range(0, len(all_authorizations)):
                authorization = all_authorizations[ptr]
                if authorization["uri"] == ret_authorization.uri:
                    remaining_uri_count = remaining_uri_count + 1


            if remaining_uri_count == 0:
                for ptr in range(0, len(all_authorizations)):
                    authorization = all_authorizations[ptr]
                    if ret_authorization.uri in authorization["filters"]:
                        authorization["filters"].remove(ret_authorization.uri)

        write_dict_to_json_file(self.authorization_config_path, all_authorizations)

        self.lock.release()

        return ret_authorization


    def remove_group_from_authorizations_io(self, group_name):
        self.lock.acquire()
        
        a_list = get_dict_from_json_file(self.authorization_config_path)
        for authorization in a_list:
            authorized_groups = authorization["authorized_groups"]
            if group_name in authorized_groups:
                del authorized_groups[group_name]

        write_dict_to_json_file(self.authorization_config_path, a_list)

        self.lock.release()


    def get_access_rights_for_uri_io(self, uri):
        authorizations = self.get_mapped_authorizations()
        ret_list = None
        if uri in authorizations:
            ret_list = authorizations[uri]

        return ret_list


    def get_mapped_authorizations(self):
        return self.__get_mapped_authorizations(ttl_hash=self.get_ttl_hash())


    def set_disabled_flag(self, raw_authorizations:list):
        for raw_authorization in raw_authorizations:
            if not raw_authorization["permitted_environments"] or self.environment_type in raw_authorization["permitted_environments"]:
                raw_authorization["disabled"] = False
            else:
                raw_authorization["disabled"] = True


    @lru_cache(1, True)
    def __get_mapped_authorizations(self, ttl_hash:int):
        logger.info("authorization cache load")
        raw_authorizations = get_dict_from_json_file(self.authorization_config_path)
        self.set_disabled_flag(raw_authorizations)

        mapped_authorizations = {}
        
        for authorization in raw_authorizations:
            access_right = URIAccessRight(**authorization)
            if not access_right.uri in mapped_authorizations:
                mapped_authorizations[access_right.uri] = []

            mapped_authorizations[access_right.uri].append(access_right)

        return mapped_authorizations
