from flask import request, Response, render_template, session, g
from functools import wraps
from functools import lru_cache
from utah.core.utilities import get_service_object
from utah.core.content import parse_path
from utah.core.content import EHTMLDoc
from utah.core.navigation import ParentNavItem
from utah.core.navigation import RootNavigationBean
from utah.core.navigation import NavigationBean
from utah.core.authentication import BaseAuthenticationService
from utah.core.authorize import BaseURIAuthorizationService
from utah.core.authorize import UnauthorizedException
import werkzeug
from utah.core.utilities import func_logger
import logging
import re
import importlib
import uuid
from utah.core.utilities import Sendmail
from flask_babel import lazy_gettext
from flask_babel import gettext
from utah.core.utilities import get_service_object
from utah.core.authorize import ForbiddenException
from utah.impl.bryce.utilities import ConnectionDefinition as MongoConnectionDefinition

URIUSE_SESSION_ONLY:int = 1
URIUSE_TOKEN_ONLY:int = 2
URIUSE_ANY:int = 3

class LayoutException(Exception):
    pass

class LayoutNoMetadataDefinition(LayoutException):
    pass

class UserAuthorizationBean():
    def __init__(self, user_id:str, authorization_service:BaseURIAuthorizationService):
        self.user_id = user_id
        self.authorization_service = authorization_service

    def is_authorized(self, uri, method="GET"):
        return self.authorization_service.is_authorized_request(self.user_id, uri, method)


def check_nav_authorization(nav_item, user_authorization_bean):
    ret_bool = False

    if not nav_item.uri == "#":
        ret_bool = user_authorization_bean.is_authorized(nav_item.uri)
    else:
        for child in nav_item.children:
            if user_authorization_bean.is_authorized(child.uri):
                ret_bool = True
                break

    return ret_bool


class AuthorizationNavigationBean(NavigationBean):
    def __init__(self, nav_item:ParentNavItem, breadcrumb_chain:list, user_authorization_bean:UserAuthorizationBean, locale_str:str=None):
        self.user_authorization_bean = user_authorization_bean

        NavigationBean.__init__(self, nav_item, breadcrumb_chain, locale_str)


    def create_nav_bean(self, nav_item, breadcrumb_chain, locale_str:str=None):
        ret_bean = None

        if check_nav_authorization(nav_item, self.user_authorization_bean):
            ret_bean = AuthorizationNavigationBean(nav_item, breadcrumb_chain, self.user_authorization_bean, locale_str)

        return ret_bean


    def has_children(self):
        ret_bool = False

        for child in self.nav_item.children:
            if check_nav_authorization(child, self.user_authorization_bean):
                ret_bool = True
                break

        return ret_bool




class AuthorizationRootNavigationBean(RootNavigationBean):
    def __init__(self, breadcrumb_chain:list, user_authorization_bean:UserAuthorizationBean, locale_str:str=None):
        self.user_authorization_bean = user_authorization_bean
        RootNavigationBean.__init__(self, breadcrumb_chain, locale_str)


    def create_nav_bean(self, nav_item, breadcrumb_chain, locale_str:str=None):
        ret_bean = None

        if check_nav_authorization(nav_item, self.user_authorization_bean):
            ret_bean = AuthorizationNavigationBean(nav_item, breadcrumb_chain, self.user_authorization_bean, locale_str)

        return ret_bean


    def is_authorized(self, uri, method="GET"):
        return self.user_authorization_bean.is_authorized(uri, method)


    def has_children(self):
        ret_bool = False

        for child in self.nav_item.children:
            if check_nav_authorization(child, self.user_authorization_bean):
                ret_bool = True
                break

        return ret_bool





class SkinService():
    @func_logger
    def __init__(self, uri_to_metadata_mappings:list, layouts:dict, default_layout:str, aux_content_types:dict, default_aux_content_type:str):
        self.uri_metadata_map = {}

        for mapping in uri_to_metadata_mappings:
            if type(mapping) is dict:
                self.add_mapping(**mapping)

        self.aux_content_types = aux_content_types
        self.layouts = layouts


        for layout_name in self.layouts:
            layout = layouts[layout_name]

            if not "description" in layout:
                raise LayoutException("layout definition must contain a description key")

            if not "layout_path" in layout:
                raise LayoutException("layout definition must contain a layout_path key")

            if not "supported_aux_content_types" in layout:
                raise LayoutException("layout definition must contain a support_aux_content_types key")

            for aux_content_type in layout["supported_aux_content_types"]:
                if not aux_content_type in aux_content_types:
                    raise LayoutException("supported_aix_content_type:[%s] specified in layout:[%s] does not appear in the aux_content_types list" % (aux_content_type, layout["name"]))


        if not default_layout in layouts:
            raise LayoutException("default layout:[%s] is not listed in the layouts configuration" % default_layout)

        if not default_aux_content_type in aux_content_types:
            raise LayoutException("default aux_content_type:[%s] is not listed in the aux_content_types configuration" % default_aux_content_type)

        self.default_layout = default_layout
        self.default_aux_content_type = default_aux_content_type

    @func_logger
    def get_layouts(self):
        return self.layouts


    @func_logger
    def get_layout(self, name):
        if not name in self.layouts:
            raise LayoutException("Could not find a layout:[%s] in layout configuration" % name)

        return self.layouts[name]


    @func_logger
    def get_default_layout(self):
        return self.default_layout


    @func_logger
    def get_default_aux_content_type(self):
        return self.default_aux_content_type


    @func_logger
    def get_aux_content_types(self):
        return self.aux_content_types


    @func_logger
    def add_mapping(self, uri:str, metadata_path:str):
        self.uri_metadata_map[uri] = metadata_path


    @func_logger
    def get_metadata_doc_path(self, uri:str):
        if not uri in self.uri_metadata_map:
            raise LayoutNoMetadataDefinition("No mapping found for url:[%s]" % uri)

        return self.uri_metadata_map[uri]



def get_user_id(for_api=False):
    user_id = "__anonymous__"

    if "user_id" in session:
        user_id = session["user_id"]

    elif "api_key" in request.args:
        api_key = request.args.get('api_key')
        authentication_service:BaseAuthenticationService = get_service_object("authentication")
        user_id = authentication_service.get_user_id_from_token_key(api_key)

    return user_id




def validate_field(field_validation:dict, field_name:str, field_value:str, required:bool, required_message:str, regex_validation:str=None, validation_message:str=None):
    if required and not field_value:
        field_validation[field_name] = required_message
    elif regex_validation:
        regex = re.compile(regex_validation)
        match = regex.match(field_value)

        if not match:
            field_validation[field_name] = validation_message


class BlueprintModuleConfig():
    def __init__(self, class_name:str, load_it:bool):
        self.class_name = class_name
        self.load_it = load_it
        self.loaded_module = None


class BaseFlaskConfig():
    def __init__(self, blueprint_module_list:list, \
                temp_download_path:str, \
                default_locale:str, \
                supported_locales:list, \
                default_timezone:str, \
                translation_directories:str, \
                message_domain:str,
                host_to_locale_mappings:dict=None):


        self.blueprint_module_list = []
        for blueprint_module in blueprint_module_list:
            self.blueprint_module_list.append(BlueprintModuleConfig(**blueprint_module))

        self.temp_download_path = temp_download_path

        self.default_locale = default_locale
        self.default_timezone = default_timezone
        self.translation_directories = translation_directories
        self.message_domain = message_domain
        self.supported_locales = supported_locales
        if host_to_locale_mappings:
            self.locale_processor = self.locale_from_hostname
            self.host_to_locale_mappings = host_to_locale_mappings
        else:
            self.locale_processor = self.locale_from_headers


    def get_flask_blueprint_modules(self):
        for blueprint_module_config in self.blueprint_module_list:
            if blueprint_module_config.load_it and not blueprint_module_config.loaded_module:
                blueprint_module_config.loaded_module = importlib.import_module(blueprint_module_config.class_name)

        return self.blueprint_module_list

    def get_secret_key(self):...

    def generate_secret_key(self):
        return uuid.uuid4().hex

    def get_temp_download_path(self):
        return self.temp_download_path

    def prerequest_processor(self):
        if request.path.startswith("/arches/content/manage/review_doc"):
            (path, name, locale_str, extension) = parse_path(request.path)
        elif "Referer" in request.headers and request.headers["Referer"].find("/arches/content/manage/review_doc/") > -1:
            (path, name, locale_str, extension) = parse_path(request.headers["Referer"])
        else:
            locale_str = self.locale_processor()

        g.locale = locale_str


    def locale_from_hostname(self):
        if request.host in self.host_to_locale_mappings:
            return self.host_to_locale_mappings[request.host]
        else:
            return self.default_locale


    def locale_from_headers(self):
        raw_locale = request.headers.get('Accept-Language')
        processed_locale = ""
        if raw_locale:
            processed_locale = best_locale(raw_locale, self.supported_locales, self.default_locale)
        else:
            processed_locale = self.default_locale

        return processed_locale


    def jinja_addl_functions(self):
        return {
        }




class FlaskConfigFS(BaseFlaskConfig):
    def __init__(self, 
                secret_key_location:str, \
                new_secret_key_every_startup:bool, \
                blueprint_module_list:list, \
                temp_download_path:str, \
                default_locale:str, \
                supported_locales:list, \
                default_timezone:str, \
                translation_directories:str, \
                message_domain:str, \
                host_to_locale_mappings:dict=None):

        super().__init__(blueprint_module_list, temp_download_path, default_locale, supported_locales, default_timezone, translation_directories, message_domain, host_to_locale_mappings)

        self.secret_key_location = secret_key_location
        self.new_secret_key_every_startup = new_secret_key_every_startup

    def get_secret_key(self):
        ret_secret_key = None
        if self.new_secret_key_every_startup:
            ret_secret_key = self.generate_secret_key()
        else:
            try:
                f = open(self.secret_key_location)
                ret_secret_key = f.readline()
                f.close()
            except FileNotFoundError as e:
                ret_secret_key = self.generate_secret_key()
                f = open(self.secret_key_location, "w")
                f.write(ret_secret_key)
                f.close()

        return ret_secret_key



class FlaskConfigMongo(BaseFlaskConfig):
    def __init__(self, 
                mongo_url:str, \
                blueprint_module_list:list, \
                temp_download_path:str, \
                default_locale:str, \
                supported_locales:list, \
                default_timezone:str, \
                translation_directories:str, \
                message_domain:str, \
                host_to_locale_mappings:dict=None):

        super().__init__(blueprint_module_list, temp_download_path, default_locale, supported_locales, default_timezone, translation_directories, message_domain, host_to_locale_mappings)

        self.conndef = MongoConnectionDefinition(mongo_url)

    def get_coll(self):
        return self.conndef.get_database()["dynamic_config"]

    def get_secret_key(self):
        coll = self.get_coll()
        secret_key_doc = coll.find_one({"config_type":"secret_key"})
        if not secret_key_doc:
            secret_key_doc = {"config_type":"secret_key", "key": self.generate_secret_key()}
            coll.insert_one(secret_key_doc)

        ret_key = secret_key_doc["key"]

        return ret_key

        

def uri_authorized(use:int):

    def authorize_setup(f):

        authorization_service = get_service_object("uri_authorization")
        
        @wraps(f)
        def decorated_function(*args, **kwargs):

            uri = request.path

            user_id = "__anonymous__"

            if use == URIUSE_SESSION_ONLY:
                if "user_id" in session:
                    user_id = session["user_id"]
            elif use == URIUSE_TOKEN_ONLY:
                if "api_key" in request.args:
                    api_key = request.args.get('api_key')
                    authentication_service:BaseAuthenticationService = get_service_object("authentication")
                    user_id = authentication_service.get_user_id_from_token_key(api_key)
            elif use == URIUSE_ANY:
                if "user_id" in session:
                    user_id = session["user_id"]
                elif "api_key" in request.args:
                    api_key = request.args.get('api_key')
                    authentication_service:BaseAuthenticationService = get_service_object("authentication")
                    user_id = authentication_service.get_user_id_from_token_key(api_key)

            if not authorization_service.is_authorized_request(user_id, uri, request.method):
                raise ForbiddenException("Not authorized to access function")

            ret_value = f(*args, **kwargs)

            return ret_value

        return decorated_function

    return authorize_setup


@lru_cache(500, False)
def best_locale(raw_locale:str, supported_locales, default_locale):
    return_locale = None
    ranked_users_locales = raw_locale.split(",")
    for user_locale_and_rank in ranked_users_locales:
        user_locale = user_locale_and_rank.split(";")[0]
        if user_locale in supported_locales:
            return_locale = user_locale
            break
    if return_locale:
        return_locale = return_locale.replace("-", "_")
    else:
        return_locale = default_locale
    
    return return_locale

@lru_cache(50, False)
def double_stash(phrase:str):
    return "{{ %s }}" % phrase

class I18NSendmail(Sendmail):
    def __init__(self, host:str, user_account:str, password:str, port:int, from_addr:str, subject:str, body_template:str):
        Sendmail.__init__(self, host, user_account, password, port, from_addr, subject, body_template)
        self.subject = lazy_gettext(subject)
        self.body_template = lazy_gettext(body_template)