import re
from flask import request
from flask import session
from functools import wraps
from utah.core.utilities import get_service_object
from functools import lru_cache
from time import time
import logging
import uuid
from utah.core.utilities import lru_cache_with_ttl
from utah.core.utilities import func_logger

logger = logging.getLogger(__name__)

class AuthorizationSystemException(Exception):
    pass

class NoSuchGroupException(Exception):
    pass

class DuplicateGroupException(Exception):
    pass

class UnauthorizedException(Exception):
    pass

class ForbiddenException(Exception):
    pass

class AbstractClassReferenced(Exception):
    pass

class DuplicateRight(Exception):
    pass



class Group():
    @func_logger
    def __init__(self, name, description):
        self.name = name
        self.description = description


class BaseGroupService():
    @func_logger
    def __init__(self, default_anonymous_groups:list, default_logged_in_groups:list):
        self.default_anonymous_groups = []
        self.default_anonymous_group_names = []

        for g in default_anonymous_groups:
            self.default_anonymous_groups = Group(g["name"], g["description"])
            self.default_anonymous_group_names.append(g["name"])

        self.default_logged_in_groups = []
        self.default_logged_in_groups_names = []
        for g in default_logged_in_groups:
            self.default_logged_in_groups = Group(g["name"], g["description"])
            self.default_logged_in_groups_names.append(g["name"])


    @func_logger
    def get_default_group_names(self):
        return self.default_anonymous_group_names + self.default_logged_in_groups_names


    @func_logger
    def get_group_names_for_user(self, user_id:str):
        ret_list = None
        users_group_names = self.read_group_names_for_user(user_id)

        if users_group_names:
            ret_list = self.default_logged_in_groups_names + users_group_names
        elif user_id == "__anonymous__":
            ret_list = self.default_anonymous_group_names
        else:
            ret_list = self.default_logged_in_groups_names

        return ret_list


    def read_group_names_for_user(self, user_id:str):...


    def get_groups(self):...


    def get_group(self, name:str):...


    def get_group_members(self, group_name:str):...


    def update_group(self, group:Group):...


    def add_group(self, group:Group):...


    def delete_group(self, name:str):...

        
    def update_groups_for_user(self, user_id:str, groups:list):...


        
class URIAccessRight():
    @func_logger
    def __init__(self, category:str, right_name:str, uri:str, methods:list, filters:list, authorized_groups:list, permitted_environments=[], id:str=None, disabled:bool=False):
        if not id:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

        self.category = category
        self.right_name = right_name
        self.uri = uri
        self.methods = methods
        self.filters = filters
        self.authorized_groups = authorized_groups
        self.permitted_environments = permitted_environments
        self.disabled = disabled


    @func_logger
    def match(self, group:str, uri:str, method:str):
        ret_value = False

        if not self.disabled and group in self.authorized_groups and method in self.methods:
            ret_value = True
            for filter_uri in self.filters:
                if uri.startswith(filter_uri):
                    if len(filter_uri) == len(uri):
                        ret_value = False
                        break
                    elif uri[len(filter_uri) : len(filter_uri)+1] == "/":
                        ret_value = False
                        break
        else:
            ret_value = False

        return ret_value



class BaseURIAuthorizationService():
    @func_logger
    def __init__(self, group_service_name:str, cache_timeout_secs:int, environment_type:str, available_environment_types:str):
        self.group_service_name = group_service_name
        self.cache_timeout_secs = cache_timeout_secs
        self.possible_environments = ["FULL", "NONE", "IST", "CD", "UAT", "LT", "PUB", "STF"]
        self.available_environment_types = available_environment_types.strip().split(":")
        self.cache_force_expire_count = 0

        if available_environment_types.strip():
            for aet in self.available_environment_types:
                if not aet in self.possible_environments:
                    raise AuthorizationSystemException("invalid available_environment_type:[%s] was provided to the authorization service. Make sure envs are separated by :'s" % aet)
        else:
            raise AuthorizationSystemException("available_environment_types was not provided to the URIAuthorizationService")

        if not environment_type in self.available_environment_types:
            raise AuthorizationSystemException("environment_type:[%s] was configured but not available in evailable_environment_types:[%s] in the URIAuthorizationService" % (environment_type, available_environment_types))

        self.environment_type = environment_type

        

    @func_logger
    def get_ttl_hash(self):
        """Return the same value withing `seconds` time period"""
        return (round(time() / self.cache_timeout_secs), self.cache_force_expire_count)


    @func_logger
    def force_cache_expire(self):
        self.cache_force_expire_count = self.cache_force_expire_count + 1


    @func_logger
    def is_authorized_request(self, user_id:str, uri:str, method:str):
        ret_value = False

        users_group_membership = self.__get_group_names_for_user(user_id, self.get_ttl_hash())
        for group_name in users_group_membership:
            ret_value = self.is_group_authorized(group_name, uri, method)

            if ret_value:
                break

        return ret_value


    @lru_cache(1000, True)
    @func_logger
    def __get_group_names_for_user(self, user_id:str, ttl_hash:set):
        group_service = get_service_object(self.group_service_name)
        return group_service.get_group_names_for_user(user_id)


    @func_logger
    def is_group_authorized(self, group:str, uri:str, method:str):
        return self.__is_group_authorized(group, uri, method, self.get_ttl_hash())


    @lru_cache(1000, True)
    @func_logger
    def __is_group_authorized(self, group:str, uri:str, method:str, ttl_hash:set):
        ret_value = False

        working_uri = uri
        while working_uri:
            ret_value = self.__working_uri_check(working_uri, group, uri, method)
            if not ret_value:
                working_uri = working_uri[0:working_uri.rfind("/")]
            else:
                working_uri = None

        if not ret_value:
            ret_value = self.__working_uri_check("/", group, uri, method)

        return ret_value


    @func_logger
    def __working_uri_check(self, working_uri:str, group:str, uri:str, method:str):
        ret_value = False
        #authorizations = self.get_mapped_authorizations()

        access_rights = self.get_access_rights_for_uri(working_uri)

        if access_rights:
            for access_right in access_rights:
                ret_value = access_right.match(group, uri, method)
                if ret_value:
                    break

        return ret_value


    def get_all_authorizations(self):
        raise AbstractClassReferenced()


    def find_authorization(self, category, right_name)->URIAccessRight:
        raise AbstractClassReferenced()


    def get_authorization(self, id:str):
        raise AbstractClassReferenced()


    @func_logger
    def update_authorization(self, uri_access_right:URIAccessRight):
        self.update_authorization_io(uri_access_right)
        self.force_cache_expire()


    @func_logger
    def add_authorization(self, uri_access_right:URIAccessRight):
        self.add_authorization_io(uri_access_right)
        self.force_cache_expire()


    @func_logger
    def delete_authorization(self, id:str):
        self.delete_authorization_io(id)
        self.force_cache_expire()


    @func_logger
    def remove_group_from_authorizations(self, group_name):
        self.remove_group_from_authorizations_io(group_name)
        self.force_cache_expire()


    def update_authorization_io(self, uri_access_right:URIAccessRight):
        raise AbstractClassReferenced()


    def add_authorization_io(self, uri_access_right:URIAccessRight):
        raise AbstractClassReferenced()


    def delete_authorization_io(self, id:str):
        raise AbstractClassReferenced()


    def remove_group_from_authorizations_io(self, group_name):
        raise AbstractClassReferenced()


    @lru_cache_with_ttl(maxsize=1000, ttl=300)
    @func_logger
    def get_access_rights_for_uri(self, uri):
        ret_list = None
        if not uri == "/":
            ret_list = self.get_access_rights_for_uri_io(uri)
        else:
            group_service:BaseGroupService = get_service_object(self.group_service_name)

            all_authorizations = self.get_all_authorizations()
            filters_list = []
            for authorizarion in all_authorizations:
                authorization:URIAccessRight
                if not authorizarion.uri in filters_list:
                    filters_list.append(authorizarion.uri)

            authorized_groups = group_service.get_default_group_names()

            ret_list = [URIAccessRight("__SYSTEM__", "__root_path__", "/", ["GET"], filters_list, authorized_groups, [], "__root_path_allowance__", False) ]

        return ret_list

    def get_access_rights_for_uri_io(self, uri)->list:...








def authorize(resource_type, uri_parser, resource_loc, function_loc=None):

    def authorize_setup(f):

        authorization_service = get_service_object("authorization")

        @wraps(f)
        def decorated_function(*args, **kwargs):

            mapper_re = re.compile(uri_parser)

            uri = request.path

            match = mapper_re.match(uri)

            if not match:
                AuthorizationSystemException("Could not match URI with the provided pattern")

            groups = match.groups()

            largest_ptr = resource_loc
            if function_loc and function_loc > largest_ptr:
                largest_ptr = function_loc

            if len(groups)-1 < largest_ptr:
                AuthorizationSystemException("There were not enough groups for the specified locations")


            resource = groups[resource_loc]
            function = None
            if function_loc:
                function = groups[function_loc]


            if not authorization_service.is_authorized_request(session["user_id"], resource_type, resource, function, request.method):
                raise Exception("choke1")

            ret_value = f(*args, **kwargs)

            return ret_value

        return decorated_function

    return authorize_setup