import email
from utah.core.utilities import get_service_object

from utah.core.utilities import ServiceFactory
from utah.core.authentication import BaseAuthenticationService
from utah.core.authentication import generate_password
from utah.core.authentication import AuthenticationInfo
from utah.core.authorize import BaseGroupService, BaseURIAuthorizationService
from utah.core.authorize import Group
from utah.core.authorize import URIAccessRight

from utah.core.content import BaseContentService
from utah.impl.zion.content import ContentService as SrcContentService
from utah.core.content import ResourceHeader
from utah.core.content import Folder

from utah.core.profile import BaseProfileService
from utah.core.profile import ProfileInfo
from utah.core import bootstrap
from importlib import import_module
import os

import logging

_logger = logging.getLogger(__name__)
security_rights = []

def create_directory(path):
    _logger.info("Attempt to create directory: %s" % path)

    path = path.replace('\\', '\/')

    segs = path.split("/")
    if segs[0] == "":
        del segs[0]

    for i in range(0, len(segs)+1):
        first_char=""
        if path[0] == "/":
            first_char = "/"

        curr_path = first_char + "/".join(segs[0:i+1])

        if not os.path.exists(curr_path):

            os.mkdir(curr_path)

            _logger.info("directory:%s was created" % curr_path)
        else:
            _logger.debug("directory:%s exists, skipping" % curr_path)


DEPLOY_MODEL_NONE = 0
DEPLOY_MODEL_DEV_PROD = 1
DEPLOY_MODEL_DEV_UAT_PROD = 2

DEPLOY_MODEL_RIGHTS_RESTRICTIONS = [
    ("authentication",      "login",                        [[],       [],                    []]),
    ("authentication",      "logout",                       [[],       [],                    []]),
    ("registration",        "password_change",              [[],       [],                    []]),
    ("registration",        "profile",                      [[],       [],                    []]),
    ("registration",        "tokens",                       [[],       [],                    []]),
    ("content_mgmt",        "ms-%s-read_document",          [[],       [],                    []]),
    ("admin",               "app_log_viewer",               [[],       [],                    []]),
    ("admin",               "general_admin",                [[],       [],                    []]),
    ("admin",               "access_mgmt_rights",           [[],       ["IST","CD"],          ["IST","CD"]]),
    ("admin",               "promote_access_rights",        [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]]),
    ("admin",               "access_mgmt_users",            [[],       ["IST","CD"],          ["IST","CD","STF"]]),
    ("admin",               "all_content_mgmt",             [[],       ["IST","CD"],          ["IST","CD"]]),
    ("admin",               "all_promotion",                [["NONE"], ["IST","CD","UAT"],    ["IST","CD","UAT"]]),
    ("admin",               "load_navigation",              [[],       ["IST","CD"],          ["IST","CD"]]),
    ("admin",               "register_users",               [[],       ["IST","CD","STF"],    ["IST","CD","UAT", "LT", "STF"]]),
    ("registration",        "register",                     [[],       ["IST","CD","PUB"],    []])
]


class InitializationException(Exception):
    pass

class BaseUtahInititializer():

    def __init__(self, src_repo_loc:str, deployment_model=DEPLOY_MODEL_NONE):
        os.environ["UTAH_DEPLOYMENT_MODEL"] = str(deployment_model)

        self.src_repo_loc = src_repo_loc
        self.right_env_filter_data = {}

        for deploy_model_rights_restriction in DEPLOY_MODEL_RIGHTS_RESTRICTIONS:
            right_category, right_name_pattern,env_restriction_options = deploy_model_rights_restriction
            self.right_env_filter_data[(right_category, right_name_pattern)] = env_restriction_options[deployment_model]


    def __get_right_env_restriction(self, right_category, right_name_pattern):
        env_restriction = None
        key = (right_category, right_name_pattern)
        if key in self.right_env_filter_data:
            env_restriction = self.right_env_filter_data[key]
        else:
            _logger.warn("Right is being written with no env restriction data mapped: right_category:[%s], right_name_pattern:[%s]" % key)
            env_restriction = []

        return env_restriction


    def write_initial_data(self):
        # This create_microsite function has to be dynamically imported to avoid 
        # sequencing issues with the service object manager
        # its a chicken and egg thing
        module = import_module("utah.arches.web_blueprints.content")
        create_microsite = getattr(module, "create_microsite")

        create_directory("%s/temp" % bootstrap.get_var_data_loc())

        authentication_service:BaseAuthenticationService = get_service_object("authentication")
        admin_username = "admin@localhost"
        admin_password = generate_password(pwd_min_length=25)

        logged_admin_credentials_file = "%s/data/admin_info.txt" % bootstrap.get_var_data_loc()
        
        f = open(logged_admin_credentials_file, 'w')
        f.write("***********************************************************************\n")
        f.write(" Admin account username:  %s    password:  %s\n" % (admin_username, admin_password))
        f.write("***********************************************************************\n")

        _logger.info("Created admin account, review file:[%s] for credentials. DELETE THIS FILE AFTER CREDENTIALS HAVE BEEN RETRIEVED" % logged_admin_credentials_file)
        status = authentication_service.add_authentication_info(admin_username, admin_password, True)
        if not status:
            raise InitializationException("Did not create admin account")

        group_service:BaseGroupService = get_service_object("group_service")

        _logger.info("Create admin group")
        group_service.add_group(Group(name="admin", description="Site administrators"))

        _logger.info("Enroll admin user into admin group")
        group_service.update_groups_for_user("admin@localhost", ["admin"])


        _logger.info("Create admin profile")
        profile_service:BaseProfileService = get_service_object("profile")
        profile_service.add_profile_info(ProfileInfo(user_id="admin@localhost", email_address="admin@localhost", first_name="Arches", last_name="Admin"))


        _logger.info("Create core access rights")

        authorization_service:BaseURIAuthorizationService = get_service_object("uri_authorization")
    
        #filters = ['/security/login', '/security/logout', '/security/password_change', '/security/profile', '/security/verify']

        authorization_service.add_authorization(URIAccessRight("admin","general_admin", "/arches/admin", ['GET'], [], ['admin'], self.__get_right_env_restriction("admin","general_admin")))

        authorization_service.add_authorization(URIAccessRight("admin","access_mgmt_rights", "/arches/access_mgmt", ['GET','POST'], ["/arches/access_mgmt/users","/arches/access_mgmt/uri_access_rights/promote_access_rights"], ['admin'], self.__get_right_env_restriction("admin","access_mgmt_rights")))
        authorization_service.add_authorization(URIAccessRight("admin","access_mgmt_users", "/arches/access_mgmt/users", ['GET','POST'], [], ['admin'], self.__get_right_env_restriction("admin","access_mgmt_users")))
        authorization_service.add_authorization(URIAccessRight("admin","promote_access_rights", "/arches/access_mgmt/uri_access_rights/promote_access_rights", ['GET'], [], ['admin'], self.__get_right_env_restriction("admin","promote_access_rights")))

        authorization_service.add_authorization(URIAccessRight("admin","app_log_viewer", "/arches/log_viewer", ['GET'], [], ['admin'], self.__get_right_env_restriction("admin","app_log_viewer")))
        authorization_service.add_authorization(URIAccessRight("admin","register_users", "/arches/registration/register/admin", ['GET','POST'], [], ['admin'], self.__get_right_env_restriction("admin","register_users")))
        authorization_service.add_authorization(URIAccessRight("admin","all_content_mgmt", "/arches/content", ['GET','POST', "PUT", "DELETE"], ["/arches/content/promotion"], ['admin'], self.__get_right_env_restriction("admin","all_content_mgmt")))
        authorization_service.add_authorization(URIAccessRight("admin","load_navigation", "/arches/navigation/load", ['GET'], [], ['admin'], self.__get_right_env_restriction("admin","load_navigation")))
        authorization_service.add_authorization(URIAccessRight("admin","all_promotion", "/arches/content/promotion", ['GET','POST'], [], ['admin'], self.__get_right_env_restriction("admin","all_promotion")))

        authorization_service.add_authorization(URIAccessRight("registration","register", "/arches/registration/register/public", ['GET','POST'], [], ['__anonymous__'], self.__get_right_env_restriction("registration","register")))
        authorization_service.add_authorization(URIAccessRight("authentication","login", "/arches/authentication/login", ['GET','POST'], [], ['__anonymous__'], self.__get_right_env_restriction("authentication","login")))

        authorization_service.add_authorization(URIAccessRight("authentication","logout", "/arches/authentication/logout", ['GET'], [], ['__logged_in__'], self.__get_right_env_restriction("authentication","logout")))

        authorization_service.add_authorization(URIAccessRight("registration","password_change", "/arches/registration/password_change", ['GET','POST'], [], ['__logged_in__'], self.__get_right_env_restriction("registration","password_change")))
        authorization_service.add_authorization(URIAccessRight("registration","profile", "/arches/registration/profile", ['GET','POST'], [], ['__logged_in__'], self.__get_right_env_restriction("registration","profile")))

        authorization_service.add_authorization(URIAccessRight("registration","tokens", "/arches/registration/tokens", ['GET','POST'], [], [], self.__get_right_env_restriction("registration","tokens")))



        source_repo = self.get_source_repo()
        dest_repo = get_service_object("content")

        for microsite in source_repo.get_microsite_names():
            create_microsite(microsite)
            self.load_folder("/%s" % microsite, source_repo, dest_repo)




    def load_folder(self, folder_uri:str, source_repo:BaseContentService, dest_repo:BaseContentService):
        _logger.info("Loading content folder [%s]" % folder_uri)
        source_folder:Folder = source_repo.get_folder(folder_uri)
        for rh in source_folder.file_resource_headers:
            rh:ResourceHeader
            doc = source_repo.get_raw_document(rh.uri)
            dest_repo.create_document(doc)
            _logger.info("Document [%s] was created" % rh.uri)

        for new_folder_name in source_folder.child_folders:
            new_folder_uri = "%s/%s" % (folder_uri, new_folder_name)
            dest_repo.create_folder(folder_uri, new_folder_name)
            self.load_folder(new_folder_uri, source_repo, dest_repo)


    def get_source_repo(self):
        fconfig = {
            "filesystem_root": self.src_repo_loc,
            "main_microsite": "main",
            "archive_temp_dir" : "./data/temp",
            "default_doc_name": "default.html",
            "cache_timeout_secs": 300
        }
        
        return SrcContentService(**fconfig)



    def initialize(self):
        self.prepare()
        self.write_initial_data()

    def prepare(self):...

    create_directory("%s/data/stash" % bootstrap.get_var_data_loc())

    plaintext_stash_filename = "%s/data/stash/plaintext_stash.txt" % bootstrap.get_var_data_loc()
    encoded_stash_filename = "%s/data/stash/encoded_stash.txt" % bootstrap.get_var_data_loc()

    open(plaintext_stash_filename, 'w').close()
    open(encoded_stash_filename, 'w').close()