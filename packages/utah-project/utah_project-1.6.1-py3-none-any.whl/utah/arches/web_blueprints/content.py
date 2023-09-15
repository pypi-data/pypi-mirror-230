from flask import Blueprint, render_template, request, send_file, Response, session, redirect, g

import time
import logging
import uuid

from utah.core.content import BaseContentService, MicrositeNotFound
from utah.core.content import BasePromotionService, PromotionRequest, RepoInventoryDiff, RepoInventoryItem, PromotionRequestNotFound
from utah.core.content import EHTMLDoc
from utah.core.content import TextDoc
from utah.core.content import ResourceHeader
from utah.core.content import EHTMLMetaData
from utah.core.content import DocumentNotFound
from utah.core.content import create_dict_from_metadata
from utah.core.content import create_metadata_from_dict
from utah.core import content
from utah.core.bootstrap import get_text_encoding
from utah.core.utilities import get_service_object
from utah.arches.webtools import get_user_id
from utah.core.authorize import URIAccessRight
from utah.arches.webtools import uri_authorized
from utah.core.authorize import BaseURIAuthorizationService
from utah.core.authorize import BaseGroupService
from utah.core.authorize import Group
from utah.arches.webtools import SkinService
from flask_babel import gettext
from flask_babel import lazy_gettext
from flask_babel import format_datetime
from flask_babel import format_number
#from utah.core.taskpool import WorkItem
#from utah.core.taskpool import ProcessingPool
import os
import zipfile

from utah.core.content import FOLDER_INVALIDATION_REGEX
from flask_restful import Resource, Api

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY


logger = logging.getLogger(__name__)

authorization_service:BaseURIAuthorizationService = get_service_object("uri_authorization")
group_service:BaseGroupService =  get_service_object("group_service")


all_promoter_roles = ["content_promoter-%s", "content_manager-%s", "content_approver-%s", "content_restorer-%s"]
default_group_names = group_service.get_default_group_names()
group_descriptions = {
    "content_promoter-%s": "Content Promoter for Microsite %s",
    "content_manager-%s": "Content Editor for Microsite %s",
    "content_approver-%s": "Content Approver for Microsite %s",
    "content_restorer-%s": "Content Restorer for Microsite %s"
}

content_mgmt_rights_definitions = [
("content_mgmt",      "load_navigation",              "/arches/navigation/load",                                  [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "show_utility",                 "/arches/content/manage/microsites",                        [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "get_layouts",                  "/arches/content/manage/microsites/api/layouts_info",       [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "get_layout",                   "/arches/content/manage/microsites/api/layout",             [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "get_managable_microsites",     "/arches/content/manage/microsites/api/manageable_microsites", [], ["GET"],                    ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-read_document",          "/%s",                                                      [], ["GET"],                       default_group_names    ),
("content_mgmt",      "ms-%s-archive",                "/arches/content/manage/archive/%s",                        [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-review_doc",             "/arches/content/manage/review_doc/%s",                     [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-modify_documents",       "/arches/content/manage/api/document/%s",                   [], ["GET","POST","PUT","DELETE"], ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-get_inherited_metadata", "/arches/content/manage/api/inherited_metadata/%s",         [], ["GET"],                       ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-create_delete_folders",  "/arches/content/manage/api/folder/%s",                     [], ["GET","POST","DELETE"],       ["content_manager-%s"] ),
("content_mgmt",      "ms-%s-move_resources",         "/arches/content/manage/api/resource/move/%s",              [], ["POST"],                      ["content_manager-%s"] ),
("content_promotion", "show_utility",                 "/arches/content/promotion/show_utility",                   [], ["GET"],                       all_promoter_roles     ),
("content_promotion", "ms-%s-view_jobs",              "/arches/content/promotion/%s/view_jobs",                   [], ["GET"],                       all_promoter_roles     ),
("content_promotion", "ms-%s-selected_promote",       "/arches/content/promotion/%s/local_to_downstream/promote", [], ["GET","POST"],                ["content_promoter-%s"]),
("content_mgmt",      "ms-%s-restore_document",       "/arches/content/promotion/%s/downstream_to_local/promote", [], ["GET","POST"],                ["content_manager-%s"] ),
("content_promotion", "ms-%s-sync_microsite",         "/arches/content/promotion/%s/local_to_downstream/sync",    [], ["GET","POST"],                ["content_approver-%s"]),
("content_promotion", "ms-%s-restore_microsite",      "/arches/content/promotion/%s/downstream_to_local/sync",    [], ["GET","POST"],                ["content_restorer-%s"])
]

CONTENT_DEPLOY_MODEL_RIGHTS_RESTRICTIONS = [
    ("content_mgmt",        "load_navigation",              [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "show_utility",                 [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "get_layouts",                  [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "get_layout",                   [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "get_managable_microsites",     [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-read_document",          [[],       [],                    []]),
    ("content_mgmt",        "ms-%s-archive",                [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-review_doc",             [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-modify_documents",       [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-get_inherited_metadata", [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-create_delete_folders",  [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-move_resources",         [[],       ["IST","CD"],          ["IST","CD"]]),
    ("content_promotion",   "show_utility",                 [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]]),
    ("content_promotion",   "ms-%s-view_jobs",              [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]]),
    ("content_promotion",   "ms-%s-selected_promote",       [["NONE"], ["IST","CD"],          ["IST","CD"]]),
    ("content_mgmt",        "ms-%s-restore_document",       [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]]),
    ("content_promotion",   "ms-%s-sync_microsite",         [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]]),
    ("content_promotion",   "ms-%s-restore_microsite",      [["NONE"], ["IST","CD"],          ["IST","CD","UAT"]])
]

errors = {
    'UnauthorizedException': {
        'error_code':'UnauthorizedException',
        'message': gettext("User Not logged in"),
        'status': 401
    },
    'ForbiddenException': {
        'error_code':'ForbiddenException',
        'message': gettext("Authorization Error"),
        'status': 403
    },
    'FolderDoesNotExist' : {
        'error_code':'FolderDoesNotExist',
        'message': gettext("Folder does not exist"),
        'status': 404
    },
    'FolderAlreadyExists' : {
        'error_code':'FolderAlreadyExists',
        'message': gettext("Folder by that name already exists within parent folder"),
        'status': 409
    },
    'DocumentNotFound' : {
        'error_code':'DocumentNotFound',
        'message': gettext("Document does not exist"),
        'status': 404
    },
    'DocumentAlreadyExists' : {
        'error_code':'DocumentAlreadyExists',
        'message': gettext("Folder by that name already exists within parent folder"),
        'status': 409
    },
    'InvalidDocTypeException' : {
        'error_code':'InvalidDocTypeException',
        'message': gettext("Cannot load binary documents via the API"),
        'status': 409
    },
    'InvalidApiParameter' : {
        'error_code':'InvalidApiParameter',
        'message': gettext("An invalid parameter was supplied to the API"),
        'status': 409
    },
    'MicrositeAlreadyExists' : {
        'error_code':'MicrositeAlreadyExists',
        'message': gettext("Microsite Already Exists"),
        'status': 409
    },
    'MicrositeNotFound' : {
        'error_code':'MicrositeNotFound',
        'message': gettext("Microsite does not exist"),
        'status': 404
    },
    'DeleteMainMicrositeAttempted' : {
        'error_code':'DeleteMainMicrositeAttempted',
        'message': gettext("Cannot delete main microsite"),
        'status': 409
    }
}

PROMOTION_STATUS_MESSAGE_TRANSLATIONS = {
    PromotionRequest.MSGTKN_PROMOTION_STARTED: lazy_gettext("Promotion Started"),
    PromotionRequest.MSGTKN_MICROSITE_WAS_DELETED: lazy_gettext("Microsite %s was deleted"),
    PromotionRequest.MSGTKN_MICROSITE_DELETION_FAILED: lazy_gettext("Microsite %s deletion failed"),
    PromotionRequest.MSGTKN_MICROSITE_WAS_CREATED: lazy_gettext("Microsite %s was created"),
    PromotionRequest.MSGTKN_MICROSITE_CREATION_FAILED: lazy_gettext("Microsite %s creation failed"),
    PromotionRequest.MSGTKN_FOLDER_WAS_CREATED: lazy_gettext("Folder %s was created"),
    PromotionRequest.MSGTKN_FOLDER_WAS_DELETED: lazy_gettext("Folder %s was deleted"),
    PromotionRequest.MSGTKN_CREATE_FOLDER_FOLDER_ALREADY_EXISTS: lazy_gettext("Attempt was made to create folder %s, a folder by name name already exists in remote repo"),
    PromotionRequest.MSGTKN_DOCUMENT_WAS_WRITTEN: lazy_gettext("Document %s was written"),
    PromotionRequest.MSGTKN_DOCUMENT_WAS_DELETED: lazy_gettext("Document %s was deleted"),
    PromotionRequest.MSGTKN_PROMOTE_DOC_MISSING_SRC_REPO: lazy_gettext("Attempt was made to promote document %s but document is no longer in source repo"),
    PromotionRequest.MSGTKN_DEL_FOLDER_NO_LONGER_IN_DEST_REPO: lazy_gettext("Attempt was made to delete folder %s but folder is no longer in destination repo"),
    PromotionRequest.MSGTKN_DEL_DOC_NO_LONGER_IN_DEST_REPO: lazy_gettext("Attempt was made to delete document %s but document is no longer in destination repo"),
    PromotionRequest.MSGTKN_PROMOTION_RUN_CONCLUDED: lazy_gettext("Promotion run concluded")
}


PROMOTION_STATUS_TRANSLATIONS = {
    PromotionRequest.STATUS_SUBMITTED: lazy_gettext("Submitted"),
    PromotionRequest.STATUS_RUNNING: lazy_gettext("Running"),
    PromotionRequest.STATUS_COMPLETED_WITH_ERRORS: lazy_gettext("Completed with Errors"),
    PromotionRequest.STATUS_COMPLETED_SUCCESSFULLY: lazy_gettext("Completed Successfully"),
    PromotionRequest.STATUS_FAILED: lazy_gettext("Failed"),
}

PROMOTION_REPO_TRANSLATIONS = {
    "local" : lazy_gettext("Local"),
    "downstream" : lazy_gettext("Downstream")
}

class InvalidInputException(Exception):
    pass

class InvalidDocTypeException(Exception):
    pass

class InvalidApiParameter(Exception):
    pass


def render_ehtml(doc, document_path):
    resp_payload = render_template('arches/content/ehtml_content.html', doc=doc)
    return resp_payload, False


def render_text(doc, document_path):
    return doc.text, True


def render_binary(doc, document_path):
    return doc.doc_bytes, True


app = Blueprint('content_manage', __name__,url_prefix="/arches/content")
api = Api(app, errors=errors)


RENDERERS = {   content.RENDER_TYPE_BINARY:render_binary,
                content.RENDER_TYPE_TEXT:render_text,
                content.RENDER_TYPE_EHTML:render_ehtml
}


content_service:BaseContentService = get_service_object("content")
promotion_service:BasePromotionService = get_service_object("promotion")
layout_service:SkinService = get_service_object("layout")
#task_service:ProcessingPool = get_service_object("task")

def process_microsite_text_template(template, microsite):
    ret_value = template
    if template.find("%s") > -1:
        ret_value = template % microsite
    return ret_value


def __get_right_env_restriction(right_category, right_name_pattern, right_env_filter_data):
    env_restriction = None
    key = (right_category, right_name_pattern)
    if key in right_env_filter_data:
        env_restriction = right_env_filter_data[key]
    else:
        logger.warn("Right is being written with no env restriction data mapped: right_category:[%s], right_name_pattern:[%s]" % key)
        env_restriction = []

    return env_restriction


def __get_right_env_filter_data():
    deployment_model = content_service.deployment_model
    ret_filter_data = {}
    for fd in CONTENT_DEPLOY_MODEL_RIGHTS_RESTRICTIONS:
        (category, right_template, env_restrictions) = fd
        ret_filter_data[(category, right_template)] = env_restrictions[deployment_model]

    return ret_filter_data


def create_entitlement(microsite, entitlement_info, right_env_filter_data):
    (category, right_name_template, uri_template, filters, methods, groups_templates) = entitlement_info

    permitted_environments = __get_right_env_restriction(category, right_name_template, right_env_filter_data)

    group_names = []
    for group_template in groups_templates:
        group_name = process_microsite_text_template(group_template, microsite)
        group_names.append(group_name)

        if not group_name in default_group_names:
            group = group_service.get_group(group_name)
            if not group:
                group_description = group_descriptions[group_template] % microsite
                group = Group(group_name, group_description)
                group_service.add_group(group)

    right_name = process_microsite_text_template(right_name_template, microsite)
    right = authorization_service.find_authorization(category, right_name)
    if not right:
        uri = process_microsite_text_template(uri_template, microsite)
        new_right = URIAccessRight(category, right_name, uri, methods, filters, group_names, permitted_environments)
        authorization_service.add_authorization(new_right)
    else:
        right.authorized_groups = right.authorized_groups + group_names
        authorization_service.update_authorization(right)


def create_microsite(microsite:str):
    right_env_filter_data = __get_right_env_filter_data()

    content_service.create_microsite(microsite)

    for entitlement_info in content_mgmt_rights_definitions:
        create_entitlement(microsite, entitlement_info, right_env_filter_data)


def delete_entitlement(microsite, entitlement_info):
    (category, right_name_template, uri_template, filters, methods, groups_templates) = entitlement_info

    group_names = []
    for group_template in groups_templates:
        group_name = process_microsite_text_template(group_template, microsite)
        group_names.append(group_name)
        if group_name != group_template:
            if not group_name in default_group_names:
                group = group_service.get_group(group_name)
                if group:
                    group_service.delete_group(group_name)

    right_name = process_microsite_text_template(right_name_template, microsite)
    if right_name != right_name_template:
        right = authorization_service.find_authorization(category, right_name)
        if right:
            authorization_service.delete_authorization(right.id)
    else:
        right = authorization_service.find_authorization(category, right_name)
        for group_name in group_names:
            if group_name in right.authorized_groups:
                right.authorized_groups.remove(group_name)

        authorization_service.update_authorization(right)


def delete_microsite(microsite:str):
    for entitlement_info in content_mgmt_rights_definitions:
        delete_entitlement(microsite, entitlement_info)

    content_service.delete_microsite(microsite)


def doc_to_json(doc):
    ret_json = None
    if doc.resource_header.render_type == content.RENDER_TYPE_TEXT:
        ret_json = {"text" : doc.text}

    elif doc.resource_header.render_type == content.RENDER_TYPE_EHTML:
        ret_json = {"text" : doc.text, "metadata" : create_dict_from_metadata(doc.metadata)}

    else:
        ret_json = {
            "size" : format_number(len(doc.doc_bytes))
        }

    ret_json["last_modified_date"] = format_datetime(doc.last_modified_date, "medium")

    return ret_json





class LayoutsInfo(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        i18n_layouts = {}
        i18n_aux_content_types = {}

        ret_value = {}
        ret_value["layouts"] = i18n_layouts
        ret_value["aux_content_types"] = i18n_aux_content_types
        ret_value["default_layout"] = layout_service.get_default_layout()
        ret_value["default_aux_content_type"] = layout_service.get_default_aux_content_type()

        layouts = layout_service.get_layouts()

        for key in layouts.keys():
            i18n_layout = {}
            i18n_layout["description"] = gettext(layouts[key]["description"])
            i18n_layout["supported_aux_content_types"] = layouts[key]["supported_aux_content_types"]
            i18n_layouts[key] = i18n_layout


        aux_content_types = layout_service.get_aux_content_types()

        for key in aux_content_types.keys():
            i18n_aux_content_types[key] = gettext(aux_content_types[key])

        return ret_value


class MicrositeList(Resource):
    @uri_authorized(URIUSE_ANY)
    def delete(self, microsite):
        delete_microsite(microsite)
        return {"status" : "deleted"}


    @uri_authorized(URIUSE_ANY)
    def post(self, microsite):
        create_microsite(microsite)

        microsite_path = "/%s" % microsite
        content_service.create_folder(microsite_path, "__system")
        content_service.create_folder(microsite_path, "js")
        content_service.create_folder(microsite_path, "css")
        content_service.create_folder(microsite_path, "images")
        content_service.create_folder(microsite_path, "spiffs")

        metadata_doc = EHTMLDoc(ResourceHeader("/%s/__system/metadata.html" % microsite), EHTMLMetaData(), "", get_text_encoding())
        content_service.create_document(metadata_doc)


        nav_text = '{"uri":"%s", "description":"%s", "translations":{}}' % (microsite_path, microsite)
        navigation_doc = TextDoc(ResourceHeader("/%s/__system/navigation.json" % microsite), nav_text, get_text_encoding())
        content_service.create_document(navigation_doc)

        return {"status" : "created"}


def authorized_microsites(uri_patterns:list, method:str):
    microsite_names = content_service.get_microsite_names()
    user_id = get_user_id()
    ret_list = []
    microsite_names = content_service.get_microsite_names()
    for microsite_name in microsite_names:
        for uri_pattern in uri_patterns:
            if authorization_service.is_authorized_request(user_id, uri_pattern % microsite_name, method):
                ret_list.append(microsite_name)
                break
    return ret_list


class ManageableMicrosites(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        user_id = get_user_id()
        method = "POST"

        microsite_names = content_service.get_microsite_names()

        ret_uris = []

        for microsite_name in microsite_names:
            if authorization_service.is_authorized_request(user_id, "/arches/content/manage/api/document/" + microsite_name, method):
                ret_uris.append("/" + microsite_name)

        ret_uris.sort()

        return ret_uris


def get_locale_str():
    locale_str = None

    if "locale" in request.args:
        locale_str = request.args["locale"]
    else:
        locale_str = g.locale

    return locale_str


class InheritedMetadata(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self, document):

        locale_str = get_locale_str()

        main_microsite = content_service.get_main_microsite()
        segs = document.split("/")

        uri = None
        doc = None
        # Are we getting inherited data for a metadata doc
        if document.endswith("/" + content.METADATA_DOC_DIR + "/" + content.METADATA_DOC_NAME):
            # Are we getting inherited data for the main microsite metadata doc
            if segs[0] == main_microsite:
                ret_json = {    "text" : "", 
                                "metadata" : {
                                    "layout" : "",
                                    "title" : "",
                                    "keywords" : "",
                                    "suppress_inheritance" : False,
                                    "extended_attributes" : {},
                                    "description" : "",
                                    "aux_content_refs" : [],
                                    "scripts" : [],
                                    "links" : []
                                }}
            else:
                uri = "/%s/%s/%s" % (main_microsite, content.METADATA_DOC_DIR, content.METADATA_DOC_NAME)
                doc = content_service.get_uncached_document(uri, locale_str)
                ret_json = doc_to_json(doc)
        else:
            uri = "/%s/%s/%s" % (segs[0], content.METADATA_DOC_DIR, content.METADATA_DOC_NAME)
            doc = content_service.get_uncached_document(uri, locale_str)
            ret_json = doc_to_json(doc)


        return ret_json


class Layout(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self, name):
        ret_value = {}
        ret_value["name"] = name
        tmpl = layout_service.get_layout(name)
        ret_value["description"] = tmpl["description"]
        all_aux_content_types = layout_service.get_aux_content_types()

        supported_aux_content_types = []
        for aux_content_type in tmpl["supported_aux_content_types"]:
            supported_aux_content_types.append({"type":aux_content_type, "description":all_aux_content_types[aux_content_type]})

        ret_value["supported_aux_content_types"] = supported_aux_content_types

        return ret_value


class Folder(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self, folder):
        folder_obj = content_service.get_folder("/" + folder)

        file_list = []

        ret_dict = {
            "child_folders" : folder_obj.child_folders,
            "files" : file_list,
        }

        for file_resource_header in folder_obj.file_resource_headers:
            file_dict = {
                "uri":file_resource_header.uri,
                "mimetype":file_resource_header.mimetype,
                "resource_id":file_resource_header.resource_id,
                "render_type":file_resource_header.render_type            
            }

            file_list.append(file_dict)

        return ret_dict

    @uri_authorized(URIUSE_ANY)
    def post(self, folder):
        last_slash = folder.rfind("/")
        parent_folder = "/" + folder[:last_slash]
        folder_name = folder[last_slash+1:]

        content_service.create_folder(parent_folder, folder_name)


    @uri_authorized(URIUSE_ANY)
    def delete(self, folder):
        content_service.delete_folder("/" + folder)


class Document(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self, document):
        uri = "/" + document
        locale_str = get_locale_str()

        if not "option" in request.args:
            option = "raw"
        else:
            option = request.args.get("option")

        doc = None
        if option == "raw":
            doc = content_service.get_raw_document(uri, locale_str=None)

        elif option == "cached":
            doc = content_service.get_document(uri, locale_str=locale_str)

        elif option == "uncached":
            locale_str = get_locale_str()
            doc = content_service.get_uncached_document(uri, locale_str, locale_str=locale_str)

        else:
            raise InvalidApiParameter("option must be one of the following values:['raw','cached','uncached']")


        if not doc:
            raise DocumentNotFound("")

        return doc_to_json(doc)


    @uri_authorized(URIUSE_ANY)
    def delete(self, document):
        uri = "/" + document
        content_service.delete_document(uri)

        return {"status":"ok"}


    @uri_authorized(URIUSE_ANY)
    def post(self, document):
        uri = "/" + document

        if 'file' not in request.files:
            request_payload = request.get_json()
            resource_header = ResourceHeader(uri)
            new_doc = None

            if resource_header.render_type == content.RENDER_TYPE_EHTML:
                metadata = EHTMLMetaData()
                new_doc = EHTMLDoc(resource_header, None, "", get_text_encoding())

            elif resource_header.render_type == content.RENDER_TYPE_TEXT:
                new_doc = TextDoc(resource_header, "", get_text_encoding())
            else:
                raise InvalidInputException("System cannot create a document of type:[%s] uri passed was:[%s]" % (resource_header.mimetype, uri))


            self.update_doc_from_json(new_doc, request_payload)

            content_service.create_document(new_doc)
        else:
            file = request.files['file']
            unpack_zip = False
            if request.args.get('unpack_zip') == "y":
                unpack_zip = True

            if not (uri.endswith('.zip') and unpack_zip):
                content_service.write_file(uri, file)
            else:
                save_file_path = get_service_object('flask_config').temp_download_path + '/' + str(uuid.uuid4()) + '.tmp'
                file.save(save_file_path)
                parent_folder = uri[:uri.rfind('/')]
                #zip_upload_workitem = ZipUploadWI(parent_folder, save_file_path, content_service, get_user_id())
                #task_service.add_work_item(zip_upload_workitem)

                folders = [parent_folder]

                with zipfile.ZipFile(save_file_path) as z:
                    for filename in z.namelist():
                        if not filename.endswith('/'):
                            # read the file
                            with z.open(filename) as zf:
                                uri = parent_folder + '/' + filename

                                # Assure the folder is there before uploading
                                file_parent_folder = uri[:uri.rfind('/')]
                                if not content_service.uri_is_folder(file_parent_folder):
                                    file_segs = file_parent_folder[1:].split('/')
                                    for i in range(1, len(file_segs)+1):
                                        prosp_folder = '/' + '/'.join(file_segs[:i])
                                        if not content_service.uri_is_folder(prosp_folder):
                                            prosp_parent_folder = '/' + '/'.join(file_segs[:i-1])
                                            content_service.create_folder(prosp_parent_folder, file_segs[i-1])

                                content_service.write_file(uri, zf)
                    z.close()
                    os.remove(save_file_path)


        return {"status":"ok"}


    @uri_authorized(URIUSE_ANY)
    def put(self, document):
        uri = "/" + document

        doc = content_service.get_raw_document(uri)
        if not doc:
            raise DocumentNotFound("Not document was found at uri:[%s]" % uri)


        request_payload = request.get_json()

        self.update_doc_from_json(doc, request_payload)

        content_service.update_document(doc)

        return {"status":"ok"}


    def update_doc_from_json(self, doc, request_payload):
        if doc.resource_header.render_type == content.RENDER_TYPE_TEXT:
            doc.text = request_payload["text"]

        elif doc.resource_header.render_type == content.RENDER_TYPE_EHTML:
            doc.text = request_payload["text"]
            metadata = create_metadata_from_dict(request_payload["metadata"])
            doc.metadata = metadata
        else:
            raise InvalidDocTypeException("Cannot write binary document via this API")


class Mover(Resource):
    @uri_authorized(URIUSE_ANY)
    def post(self, microsite):
        #raise DocumentAlreadyExists("ugh!!")
        request_payload = request.get_json()
        if request_payload["is_folder"]:
            content_service.move_folder(request_payload["from_uri"], request_payload["to_uri"])
        else:
            content_service.move_document(request_payload["from_uri"], request_payload["to_uri"])

        return {"status":"ok"}


# Admin for adding and removing microsites
api.add_resource(MicrositeList, '/microsite/api/microsite_list/<microsite>')

# Common Utilities for content management
api.add_resource(LayoutsInfo, '/manage/microsites/api/layouts_info')
api.add_resource(Layout, '/manage/microsites/api/layout/<name>')
api.add_resource(ManageableMicrosites, '/manage/microsites/api/manageable_microsites')

# Microsite editing specific
api.add_resource(Document, '/manage/api/document/<path:document>')
api.add_resource(InheritedMetadata, '/manage/api/inherited_metadata/<path:document>')
api.add_resource(Folder, '/manage/api/folder/<path:folder>')
api.add_resource(Mover, '/manage/api/resource/move/<microsite>')


# -----------------------------------------------------------------------------
# ASYNC Tasks
# -----------------------------------------------------------------------------
'''
class ZipUploadWI(WorkItem):
    def __init__(self, parent_folder, zipfile_path, content_service:BaseContentService, user_id) -> None:
        super().__init__(tags={"task_type":"zip_upload", "user_id":user_id, "parent_folder":parent_folder})
        self.uploaded_zipfile_path = zipfile_path
        self.content_service:BaseContentService = content_service
        self.parent_folder = parent_folder

    def execute(self):
        folders = [self.parent_folder]

        with zipfile.ZipFile(self.uploaded_zipfile_path) as z:
            for filename in z.namelist():
                if not os.path.isdir(filename):
                    # read the file
                    with z.open(filename) as zf:
                        uri = self.parent_folder + '/' + filename

                        # Assure the folder is there before uploading
                        file_parent_folder = uri[:uri.rfind('/')]
                        if not self.content_service.uri_is_folder(file_parent_folder):
                            file_segs = file_parent_folder[1:].split('/')
                            for i in range(1, len(file_segs)+1):
                                prosp_folder = '/' + '/'.join(file_segs[:i])
                                if not self.content_service.uri_is_folder(prosp_folder):
                                    prosp_parent_folder = '/' + '/'.join(file_segs[:i-1])
                                    self.content_service.create_folder(prosp_parent_folder, file_segs[i-1])
                                    self.add_log_entry(r'create folder %(foldername)s', {'foldername':file_segs[i-1]})                        

                        self.add_log_entry(r'uploading %(filename)s', {'filename':uri})                        
                        self.content_service.write_file(uri, zf)
            z.close()
            os.remove(self.uploaded_zipfile_path)
'''

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/manage/microsites", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def manage_microsite():
    return render_template('arches/content/manage_microsites.html')


@app.route("/manage/archive/<microsite>", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def archive_microsite(microsite):
    try:
        reader=content_service.create_microsite_archive(microsite)
        return Response(reader, content_type="application/zip")

    except MicrositeNotFound as e:
        status = 404
        path = "/%s/%s" % (content_service.get_main_microsite(), "/__system/error_pages/404.html")
        doc = content_service.get_document(path, g.locale)

        (resp_payload, ok_to_cache) = render_ehtml(doc, path)

        resp = Response(
            response=resp_payload,
            status=status)

        return resp


@app.route("/manage/review_doc/<path:document_path>.html", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def review_doc(document_path):
    document_path = "/%s.html" % document_path

    doc=content_service.get_uncached_document(document_path, get_locale_str())

    (payload, layed_out) = render_ehtml(doc, document_path)

    return payload


def get_repo_dir(direction):
    if direction == "local_to_downstream":
        source_repo = "local"
        dest_repo = "downstream"

    elif direction == "downstream_to_local":
        source_repo = "downstream"
        dest_repo = "local"

    else:
        raise DocumentNotFound("A bad direction:[%s] was provided" % direction)

    return (source_repo, dest_repo)


def get_all_involved_paths(uri:str)->list:
    paths = []
    segs = uri.split("/")
    for i in range(len(segs), 1, -1): 
        paths.append("/" + "/".join(segs[1:i])) 

    return paths



# --------------------------------------------
# This method displays the promotion utility
# --------------------------------------------
@app.route("/promotion/show_utility", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def view_promotion_utility():
    uri_patterns = [
    "/arches/content/promotion/%s/view_jobs",
    "/arches/content/promotion/%s/local_to_downstream/promote",
    "/arches/content/promotion/%s/downstream_to_local/promote",
    "/arches/content/promotion/%s/local_to_downstream/sync",
    "/arches/content/promotion/%s/downstream_to_local/sync"
    ]

    available_microsites = authorized_microsites(uri_patterns, "GET")

    diff_counts = {}
    for microsite in available_microsites:
        diff_counts[microsite] = len(promotion_service.compare_microsite("local", "downstream", microsite))

    return render_template('arches/content/promotion_util.html', microsites=available_microsites, diff_counts=diff_counts)


# -----------------------------------------------------
# These methods displays promotion history and details
# -----------------------------------------------------
@app.route("/promotion/<microsite>/view_jobs", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def display_promotion_job_list(microsite):
    all_promotion_requests = promotion_service.get_promotion_history()


    uri_patterns = [
    "/arches/content/promotion/%s/view_jobs",
    "/arches/content/promotion/%s/local_to_downstream/promote",
    "/arches/content/promotion/%s/downstream_to_local/promote",
    "/arches/content/promotion/%s/local_to_downstream/sync",
    "/arches/content/promotion/%s/downstream_to_local/sync"
    ]

    available_microsites = authorized_microsites(uri_patterns, "GET")

    promotion_requests = []
    for promotion_request in all_promotion_requests:
        if promotion_request.microsite in available_microsites and microsite == promotion_request.microsite:
            promotion_requests.append(promotion_request)

    promotion_requests.sort(key=lambda o: o.start_timestamp, reverse=True)

    return render_template('arches/content/promotion_requests.html', promotion_requests=promotion_requests, promotion_status_translations=PROMOTION_STATUS_TRANSLATIONS, microsite=microsite)


@app.route("/promotion/<microsite>/view_jobs/<promotion_id>", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def display_promotion_job(microsite, promotion_id):
    uri_patterns = [
    "/arches/content/promotion/%s/view_jobs",
    "/arches/content/promotion/%s/local_to_downstream/promote",
    "/arches/content/promotion/%s/downstream_to_local/promote",
    "/arches/content/promotion/%s/local_to_downstream/sync",
    "/arches/content/promotion/%s/downstream_to_local/sync"
    ]

    available_microsites = authorized_microsites(uri_patterns, "GET")
    promotion_request = None
    try:
        promotion_request = promotion_service.get_promotion(promotion_id)
        if not promotion_request.microsite in available_microsites:
            promotion_request = None

    except PromotionRequestNotFound as e:
        pass


    if promotion_request:
        return render_template( "arches/content/promotion_request.html", 
                                promotion_request=promotion_request, 
                                promotion_status_translations=PROMOTION_STATUS_TRANSLATIONS,
                                promotion_status_message_translations=PROMOTION_STATUS_MESSAGE_TRANSLATIONS,
                                promotion_repo_translations=PROMOTION_REPO_TRANSLATIONS
                                )
    else:
        return render_template('arches/login/message.html', message=gettext("Promotion was not found"))


# -----------------------------------------------------
# These methods promote content
# -----------------------------------------------------
@app.route("/promotion/<microsite>/<direction>/promote/differences", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def view_differences(microsite, direction):
    (source_repo, dest_repo) = get_repo_dir(direction)

    differences = promotion_service.compare_microsite(source_repo, dest_repo, microsite)

    return render_template( "arches/content/microsite_differences.html", 
                            differences=differences, 
                            microsite=microsite, 
                            source_repo_desc=PROMOTION_REPO_TRANSLATIONS[source_repo], 
                            dest_repo_desc=PROMOTION_REPO_TRANSLATIONS[dest_repo])


@app.route("/promotion/<microsite>/<direction>/promote/", methods=['POST'])
@uri_authorized(URIUSE_SESSION_ONLY)
def submit_promotion_request(microsite, direction):
    (source_repo, dest_repo) = get_repo_dir(direction)

    differences = promotion_service.compare_microsite(source_repo, dest_repo, microsite)
    filtered_diffs = []
    actions_index = []

    actions=request.form.getlist('actions')
    for a in actions:
        (str_action,str_is_folder,uri)=a.split(":")
        action = int(str_action)
        is_folder = bool(str_is_folder)

        if action == RepoInventoryDiff.ACTION_ADD:
            paths = get_all_involved_paths(uri)
            for path in paths:
                actions_index.append((action, path))
        elif action == RepoInventoryDiff.ACTION_UPDATE:
            actions_index.append((action, uri))

        elif action == RepoInventoryDiff.ACTION_DELETE:
            actions_index.append((action, uri))


    for diff in differences:
        diff:RepoInventoryDiff

        from_inv_item:RepoInventoryItem = diff.from_inv_item
        to_inv_item:RepoInventoryItem = diff.to_inv_item

        if (diff.action == RepoInventoryDiff.ACTION_ADD or diff.action == RepoInventoryDiff.ACTION_UPDATE) and (diff.action, from_inv_item.uri) in actions_index:
            filtered_diffs.append(diff)

        elif diff.action == RepoInventoryDiff.ACTION_DELETE:
            paths = get_all_involved_paths(to_inv_item.uri)
            add_it = False
            for path in paths:
                if (diff.action, path) in actions_index:
                    add_it = True
                    break
            if add_it:
                filtered_diffs.append(diff)

    promo_request = promotion_service.start_promotion(source_repo, dest_repo, microsite, filtered_diffs, {"user_id" : session["user_id"]})

    return redirect("/arches/content/promotion/%s/view_jobs/%s" % (microsite, promo_request.id))



# -----------------------------------------------------
# These methods sync content
# -----------------------------------------------------
@app.route("/promotion/<microsite>/<direction>/sync/differences", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def sync_view_differences(microsite, direction):
    (source_repo, dest_repo) = get_repo_dir(direction)

    differences = promotion_service.compare_microsite(source_repo, dest_repo, microsite)

    return render_template( "arches/content/sync_microsite_differences.html", 
                            differences=differences, 
                            microsite=microsite, 
                            source_repo_desc=PROMOTION_REPO_TRANSLATIONS[source_repo], 
                            dest_repo_desc=PROMOTION_REPO_TRANSLATIONS[dest_repo])


@app.route("/promotion/<microsite>/<direction>/sync/", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def sync_microsite(microsite, direction):
    (source_repo, dest_repo) = get_repo_dir(direction)
    differences = promotion_service.compare_microsite(source_repo, dest_repo, microsite)

    promo_request = promotion_service.start_promotion(source_repo, dest_repo, microsite, differences, {"user_id" : session["user_id"]})

    return redirect("/arches/content/promotion/%s/view_jobs/%s" % (microsite, promo_request.id))
