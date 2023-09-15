import re
import mimetypes
import os
from datetime import datetime
import uuid
from utah.core.bootstrap import get_text_encoding
from utah.core.utilities import func_logger, get_service_object
from functools import lru_cache
import time
import subprocess
import logging
import shutil
from threading import Lock
import json
from utah.core.utilities import Locale
from io import BufferedReader
from utah.core.utilities import PlainObjConverter
from threading import Thread
from datetime import timedelta


class SelfCleaningBufferedReader(BufferedReader):
    def __init__(self, buffered_reader:BufferedReader):
        BufferedReader.__init__(self, raw=buffered_reader.raw)
        self.buffered_reader = buffered_reader

    def __getattr__(self, attr):
        return getattr(self.buffered_reader, attr)

    def close(self):
        self.buffered_reader.close()
        os.remove(self.buffered_reader.name)

logger = logging.getLogger(__name__)

FOLDER_INVALIDATION_REGEX = '^(\.|\.\.)$'

missing_needed_mimetypes = [("application/yaml", ".yaml"), ("application/yaml", ".yml")]
for (mimetype, extension) in missing_needed_mimetypes:
    if extension not in mimetypes.types_map:
        (check_mimetype, check_encoding) = mimetypes.guess_type(extension)
        if not check_mimetype:
            mimetypes.add_type(mimetype, extension)

TEXT_MIME_TYPES = ["text/plain",
                    "application/javascript",
                    "application/json",
                    "application/yaml",
                    "text/css",
                    "text/csv",
                    "text/html",
                    "text/plain",
                    "text/richtext",
                    "text/tab-separated-values",
                    "text/x-python",
                    "text/x-setext",
                    "text/x-sgml",
                    "text/x-sgml",
                    "text/x-vcard",
                    "text/xml"]


METADATA_DOC_NAME = "metadata.html"
METADATA_DOC_DIR = "__system"

RENDER_TYPE_EHTML = 1
RENDER_TYPE_TEXT = 2
RENDER_TYPE_BINARY = 3

PLT_REPOPOS_FIRST = 1
PLT_REPOPOS_SECOND = 2
PLT_REPOPOS_LAST = 3
PLT_REPOPOS_OTHER = 4



class ContentSystemException(Exception):
    pass

class ForbiddenPathException(Exception):
    pass

class BadPathException(Exception):
    pass

class MicrositeNotFound(Exception):
    pass

class MicrositeAlreadyExists(Exception):
    pass

class DeleteMainMicrositeAttempted(Exception):
    pass

class URIIsDirectory(Exception):
    pass

class DocumentNotFound(Exception):
    pass

class DocumentAlreadyExists(Exception):
    pass

class FolderAlreadyExists(Exception):
    pass

class FolderDoesNotExist(Exception):
    pass

class RelativeReferenceNotPermitted(Exception):
    pass

class PromotionRequestNotFound(Exception):
    pass

class PromotionRequestAlreadyExists(Exception):
    pass

class PLTRepoNotFound(Exception):
    pass

class RepoInventoryItem():
    def __init__(self, is_folder:bool, uri:str, last_modified_date:int, size: int) -> None:
        self.is_folder = is_folder
        self.uri = uri
        self.last_modified_date = last_modified_date
        self.size = size


    def __str__(self):
        return "uri:%s, is_folder:%s, last_modified_date:%s, size:%s" % (self.uri, self.is_folder, self.last_modified_date, self.size)
    

    def __eq__(self, o):
        ret_value = True

        if o==None:
            ret_value = False
        
        elif self.is_folder:
            if not self.uri == o.uri:
                ret_value = False

        else:
            if not (self.uri == o.uri and self.size == o.size and self.last_modified_date == o.last_modified_date):
                ret_value = False

        return ret_value




class RepoInventoryDiff():
    ACTION_ADD = 0
    ACTION_UPDATE = 1
    ACTION_DELETE = 2

    ACTION_DESC = {ACTION_ADD : "Add", ACTION_UPDATE:"Update", ACTION_DELETE:"Delete"}

    def __init__(self, action:int, from_inv_item:RepoInventoryItem=None, to_inv_item:RepoInventoryItem=None) -> None:
        self.action = action
        self.from_inv_item = from_inv_item
        self.to_inv_item = to_inv_item
    def __str__(self):
        return "Action:[%s], from_inv_item[%s], to_inv_item:[%s]" % (RepoInventoryDiff.ACTION_DESC[self.action], str(self.from_inv_item), str(self.to_inv_item))
             


class UriSearch():
    def __init__(self, uri, locale:Locale):
        last_period = uri.rfind(".")
        if last_period > -1:
            self.prefix = uri[0:last_period]
            self.suffix = uri[last_period+1:len(uri)]
        else:
            self.prefix = uri
            self.suffix = ""

        self.locale = locale

        self.curr_try = 0

    def next_variant(self):
        ret_value = None
        if self.curr_try < len(self.locale.options):
            option = self.locale.options[self.curr_try]
            separator = ""
            if option:
                separator = "-"
            
            ret_value = self.prefix + separator + self.locale.options[self.curr_try] + "." + self.suffix
            self.curr_try = self.curr_try + 1

        return ret_value


def inv_difference_sort_key(diff_item:RepoInventoryDiff):
    is_folder = None
    repo_inv_item:RepoInventoryItem = None

    if diff_item.action == RepoInventoryDiff.ACTION_DELETE:
        repo_inv_item = diff_item.to_inv_item
    else:
        repo_inv_item = diff_item.from_inv_item

    if repo_inv_item.is_folder:
        is_folder = "0"
    else:
        is_folder = "1"

    ret_key = "%s%s%s" % (is_folder, diff_item.action, repo_inv_item.uri)
    
    return ret_key


def parse_path(path:str):
    file_path_parser = re.compile("^(.*)/(.*?)(-((aa|ab|ae|af|ak|am|an|ar|as|av|ay|az|ba|be|bg|bi|bm|bn|bo|br|bs|ca|ce|ch|co|cr|cs|cu|cv|cy|da|de|dv|dz|ee|el|en|eo|es|et|eu|fa|ff|fi|fj|fo|fr|fy|ga|gd|gl|gn|gu|gv|ha|he|hi|ho|hr|ht|hu|hy|hz|ia|id|ig|ii|ik|io|is|it|iu|jv|ka|kg|ki|kj|kk|kl|km|kn|kr|kv|kw|ky|la|lb|lg|li|ln|lo|lt|lv|mg|mh|mi|mk|ml|mn|mr|mt|my|na|nb|nd|ne|ng|nl|nn|no|nr|nv|ny|oc|oj|om|or|os|pi|pl|ps|pt|qu|rm|rn|ro|ru|rw|sc|se|sg|si|sk|sl|sm|sn|so|sq|sr|ss|st|su|sv|sw|ta|te|th|ti|tk|tl|tn|to|tr|ts|tw|ty|uk|ur|ve|vi|vo|wa|wo|xh|yi|yo|za|zu)(_([A-Z]{2})(_(.*))?)?))?\.(.*)$")
    match = file_path_parser.match(path)
    return (match.group(1), match.group(2), match.group(4), match.group(10))


@func_logger
def get_parent_folder_path(path:str):
    rslash_pos = path.rfind("/")

    if rslash_pos < 2:
        raise BadPathException("Could not parse a parent folder out of uri:[%s]" % path)

    parent_folder_path = path[0:rslash_pos]

    return parent_folder_path


@func_logger
def parse_microsite_name(uri):
    segs = uri.split("/")
    if len(segs) < 2 or not segs[0] == "":
        raise BadPathException("a bad uri:[%s] was provided" % uri)

    return segs[1]




class AuxContentRef():
    @func_logger
    def __init__(self, aux_content_type:str, uri:str):
        self.aux_content_type = aux_content_type
        self.uri = uri

    def __eq__(self, other):
        ret_value = False

        if other==None:
            ret_value = False

        elif self.aux_content_type == other.aux_content_type and \
            self.uri == other.uri:
            ret_value = True

        return ret_value


    def get_size(self):
        return len(self.aux_content_type) + len(self.uri)


class ResourceHeader():
    @func_logger
    def __init__(self, uri:str):
        self.uri = uri
        self.mime_encoding = None

        (self.mimetype, self.mime_encoding) = mimetypes.guess_type(uri, True)

        logger.debug("uri:[%s] mimetype:[%s]" % (self.uri, self.mimetype))

        self.resource_id = self.uri[self.uri.rfind("/")+1:]

        if self.uri.endswith(".html") and not self.mime_encoding:
            self.render_type = RENDER_TYPE_EHTML
        elif self.mimetype in TEXT_MIME_TYPES and not self.mime_encoding:
            self.render_type = RENDER_TYPE_TEXT
        else:
            self.render_type = RENDER_TYPE_BINARY


    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            self.uri == other.uri and \
            self.mimetype == other.mimetype and \
            self.resource_id == other.resource_id and \
            self.render_type == other.render_type:
            ret_value = True

        return ret_value

    def get_size(self):
        return len(self.uri) + len(self.mime_encoding) + len(self.resource_id) + 4

class FolderBreadcrumb():
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name


    def __eq__(self, other):
        ret_value = False

        if (not other == None) and \
            self.uri == other.uri and \
            self.name == other.name:
            ret_value = True

        return ret_value


class Folder():
    def __init__(self, uri, child_folders:list=[], file_names:list=[]):
        self.child_folders = child_folders
        self.file_resource_headers = []
        self.breadcrumb_trail = []

        temp_uri = uri
        last_slash = temp_uri.rfind("/")
        while temp_uri:
            folder_breadcrumb = FolderBreadcrumb(temp_uri, temp_uri[temp_uri.rfind("/")+1: len(temp_uri)])
            self.breadcrumb_trail.insert(0, folder_breadcrumb)
            if last_slash > 0:
                temp_uri = temp_uri[:last_slash]
                last_slash = temp_uri.rfind("/")
            else:
                temp_uri = ""

        self.name = self.breadcrumb_trail[len(self.breadcrumb_trail) -1].name
        self.uri = self.breadcrumb_trail[len(self.breadcrumb_trail) -1].uri


        for file_name in file_names:
            uri = "%s/%s" % (self.uri, file_name)
            self.file_resource_headers.append(ResourceHeader(uri))


class Link():
    @func_logger
    def __init__(self, **kwargs):
        self.rel = kwargs["rel"]
        self.type = kwargs["type"]
        self.href = kwargs["href"]
        self.media = kwargs["media"]


    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            self.rel == other.rel and \
            self.type == other.type and \
            self.href == other.href and \
            self.media == other.media:
            ret_value = True

        return ret_value

    def get_size(self):
        return len(self.rel) + len(self.type) + len(self.href) + len(self.media)


class Doc():
    @func_logger
    def __init__(self, resource_header:ResourceHeader):
        self.resource_header = resource_header
        self.last_modified_date = None
        self.base_last_modified_date = None

    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            self.resource_header == other.resource_header and \
            self.last_modified_date == other.last_modified_date and \
            self.base_last_modified_date == other.base_last_modified_date:
            ret_value = True

        return ret_value
    def get_size(self) -> int:...



class BinaryDoc(Doc):
    @func_logger
    def __init__(self, resource_header:ResourceHeader, doc_bytes:bytearray):
        Doc.__init__(self, resource_header)
        self.doc_bytes = doc_bytes


    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            Doc.__eq__(self, other) and \
            self.doc_bytes == other.doc_bytes:
            ret_value = True

        return ret_value


    def get_size(self) -> int:
        return len(self.doc_bytes)


class TextDoc(Doc):
    @func_logger
    def __init__(self, resource_header:ResourceHeader, text:str, text_encoding:str):
        Doc.__init__(self, resource_header)
        self.text_encoding = text_encoding
        self.text = text

    
    def __eq__(self, other):
        ret_value = False

        if (not other == None) and \
            Doc.__eq__(self, other) and \
            self.text == other.text:
            ret_value = True

        return ret_value


    def get_size(self) -> int:
        return len(self.text)



class EHTMLMetaData():
    @func_logger
    def __init__(self):
        self.layout=""
        self.title=""
        self.keywords=""
        self.description=""
        self.suppress_inheritance=False
        self.extended_attributes={}
        self.description=None
        self.scripts=[] 
        self.aux_content_refs=[]
        self.links=[]

    def add_length(self, curr_length, str_item):
        if str_item:
            curr_length = curr_length + len(str_item)

        return curr_length


    def get_size(self):
        ret_length = 0
        ret_length = self.add_length(ret_length, self.layout)
        ret_length = self.add_length(ret_length, self.title)
        ret_length = self.add_length(ret_length, self.keywords)
        ret_length = self.add_length(ret_length, self.description)
        ret_length = ret_length + 1 # supress

        for key in self.extended_attributes.keys():
            ret_length = ret_length + len(key)
            v = self.extended_attributes[key]
            if v:
                ret_length = ret_length + len(v)

        for script in self.scripts:
            ret_length = ret_length + len(script)

        for acr in self.aux_content_refs:
            ret_length = ret_length + acr.get_size()

        for lr in self.links:
            ret_length = ret_length + lr.get_size()

        return ret_length


    def inherit(self, metadata):
        if self.suppress_inheritance:
            raise ContentSystemException("An attempt was made to inherit data when the suppress inheritance flag was set")

        self.layout = self.pick_string(self.layout, metadata.layout)
        self.title = self.pick_string(self.title, metadata.title)
        self.keywords = self.pick_string(self.keywords, metadata.keywords)
        self.description = self.pick_string(self.description, metadata.description)

        if self.suppress_inheritance:
            self.suppress_inheritance = metadata.suppress_inheritance

        for key in metadata.extended_attributes.keys():
            if not key in self.extended_attributes:
                self.extended_attributes[key] = metadata.extended_attributes[key]

        self.prepend_list(self.scripts, metadata.scripts)
        self.prepend_list(self.aux_content_refs, metadata.aux_content_refs)
        self.prepend_list(self.links, metadata.links)

    def pick_string(self, old_string:str, new_string:str):
        if not old_string:
            return new_string
        else:
            return old_string


    def prepend_list(self, doc_list, microsite_metadata_list):
        for i in range(len(microsite_metadata_list)-1, -1, -1):
            doc_list.insert(0, microsite_metadata_list[i])


    def get_extended_attribute(self, attr:str):
        ret_item = ""
        if attr in self.extended_attributes:            
            ret_item = self.extended_attributes[attr]

        return ret_item




    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            self.layout == other.layout and \
            self.title == other.title and \
            self.keywords == other.keywords and \
            self.description == other.description and \
            self.suppress_inheritance == other.suppress_inheritance and \
            self.extended_attributes == other.extended_attributes and \
            self.scripts == other.scripts and \
            self.aux_content_refs == other.aux_content_refs and \
            self.links == other.links:
            ret_value = True

        return ret_value



@func_logger
def create_metadata_from_dict(metadata_dict:dict):
    metadata = EHTMLMetaData()

    metadata.layout = get_data_from_dict(metadata_dict, "layout", False, "")
    metadata.title = get_data_from_dict(metadata_dict, "title", False, "")
    metadata.keywords = get_data_from_dict(metadata_dict, "keywords", False, "")
    metadata.description = get_data_from_dict(metadata_dict, "description", False, "")
    metadata.suppress_inheritance = get_data_from_dict(metadata_dict, "suppress_inheritance", False, False)
    metadata.extended_attributes = get_data_from_dict(metadata_dict, "extended_attributes", False, {})
    metadata.scripts = get_data_from_dict(metadata_dict, "scripts", False, metadata.scripts)

    aux_content_refs= get_data_from_dict(metadata_dict, "aux_content_refs", False, metadata.aux_content_refs)
    for dict_aux_content_item in aux_content_refs:
        aci = AuxContentRef(**dict_aux_content_item)
        metadata.aux_content_refs.append(aci)

    links = get_data_from_dict(metadata_dict, "links", False, metadata.links)
    for dict_link in links:
        link = Link(**dict_link)
        metadata.links.append(link)

    return metadata


def get_data_from_dict(_dict:dict, key:str, required:bool, default_value):
    ret_value = None
    if key in _dict:
        ret_value = _dict[key]
    else:
        if not required:
            ret_value = default_value
        else:
            raise KeyError("Required key:[%s] is missing" % key)
    return ret_value


def create_dict_from_metadata(metadata:EHTMLMetaData):
    ret_dict = {}

    ret_dict["layout"] = metadata.layout
    ret_dict["title"] = metadata.title
    ret_dict["keywords"] = metadata.keywords
    ret_dict["description"] = metadata.description
    ret_dict["suppress_inheritance"] = metadata.suppress_inheritance
    ret_dict["extended_attributes"] = metadata.extended_attributes
    ret_dict["scripts"] = metadata.scripts

    aux_content_refs = []
    ret_dict["aux_content_refs"] = aux_content_refs

    for acr in metadata.aux_content_refs:
        aux_content_refs.append({"aux_content_type": acr.aux_content_type, "uri" : acr.uri})
        
    links = []
    ret_dict["links"] = links

    for link in metadata.links:
        links.append({
                        "rel": link.rel,
                        "type": link.type,
                        "href": link.href,
                        "media": link.media
                    })
        
    return ret_dict



class EHTMLDoc(TextDoc):
    @func_logger
    def __init__(self, resource_header:ResourceHeader, metadata:EHTMLMetaData, text:str, text_encoding:str):
        TextDoc.__init__(self, resource_header, text, text_encoding)
        self.metadata = metadata
        self.aux_content_docs = {}
        self.missing_aux_content = []


    def get_size(self):
        return super().get_size() + self.metadata.get_size()
        

    @func_logger
    def addAuxContentDoc(self, aux_doc_type:str, doc:TextDoc):
        aux_list = None
        if aux_doc_type in self.aux_content_docs:
            aux_list = self.aux_content_docs[aux_doc_type]
        else:
            aux_list = []
            self.aux_content_docs[aux_doc_type] = aux_list
        
        aux_list.append(doc)


    @func_logger
    def get_aux_content_docs(self, aux_doc_type:str):
        ret_list = None
        if aux_doc_type in self.aux_content_docs:
            ret_list = list(self.aux_content_docs[aux_doc_type])
        else:
            ret_list = []

        return ret_list

    @func_logger
    def get_last_aux_content_doc(self, aux_doc_type:str):
        ret_item = None
        if aux_doc_type in self.aux_content_docs:
            doc_list = list(self.aux_content_docs[aux_doc_type])
            ret_item = doc_list[len(doc_list)-1]

        return ret_item


    def __eq__(self, other):
        ret_value = False
        if (not other == None) and \
            TextDoc.__eq__(self, other) and \
            self.metadata == other.metadata and \
            self.aux_content_docs == other.aux_content_docs and \
            self.missing_aux_content == other.missing_aux_content:
            ret_value = True

        return ret_value


    def string_output(self):
            metadata_json = json.dumps(create_dict_from_metadata(self.metadata), indent=4)
            output_string = "<!-- METADATA\n%s\nMETADATA -->\n%s" % (metadata_json, self.text)
            return output_string



class BaseContentService():
    @func_logger
    def __init__(self, main_microsite:str, default_doc_name:str="default.html", cache_timeout_secs:int=60, deployment_model:int=0):
        self.main_microsite = main_microsite
        self.default_doc_name = default_doc_name
        self.cache_timeout_secs = cache_timeout_secs
        self.main_microsite_metadata_uri = "/" + self.main_microsite + "/" + METADATA_DOC_DIR + "/" + METADATA_DOC_NAME
        self.deployment_model = deployment_model

    def get_main_microsite(self):
        return self.main_microsite


    @func_logger
    def get_microsite_metadata_doc(self, microsite:str, locale_str:str=None):
        uri = "/%s/%s/%s" % (microsite, METADATA_DOC_DIR, METADATA_DOC_NAME)
        #doc = self.get_raw_document(uri, locale_str)
        doc = self.get_document(uri, locale_str)
        return doc


    @func_logger
    def enhance_last_modified_date(self, base_doc:Doc, compare_doc:Doc):
        if base_doc.last_modified_date < compare_doc.last_modified_date:
            base_doc.last_modified_date = compare_doc.last_modified_date


    def get_ttl_hash(self):
        """Return the same value withing `seconds` time period"""
        return round(time.time() / self.cache_timeout_secs)


    @func_logger
    def get_document(self, uri:str, locale_str:str=None):
        return self.__get_document(uri, locale_str, ttl_hash=self.get_ttl_hash())


    @func_logger
    def update_document(self, doc:Doc):
        if not self.document_exists(doc.resource_header):
            raise DocumentNotFound("Document at uri:[%s] could not be located" % doc.resource_header.uri)

        self.write_document(doc)


    @func_logger
    def create_document(self, doc:Doc):
        if self.document_exists(doc.resource_header):
            raise DocumentAlreadyExists("Document at uri:[%s] already exists" % doc.resource_header.uri)

        self.write_document(doc)



    @func_logger
    @lru_cache(200, False)
    def get_locale_object(self, locale_str:str):
        return Locale(locale_str)



    @func_logger
    @lru_cache(1000, False)
    def __get_document(self, uri:str, locale_str=None, ttl_hash=None):
        return self.get_uncached_document(uri, locale_str, True)


    def get_uncached_document(self, uri:str, locale_str:str=None, to_be_cached:bool=False):
        doc = self.get_raw_document(uri, locale_str)

        if doc and doc.resource_header.render_type == RENDER_TYPE_EHTML:
            second_slash = doc.resource_header.uri.find("/", 1)
            microsite = None
            if second_slash > 1: 
                microsite = doc.resource_header.uri[1:second_slash]
            else:
                raise ForbiddenPathException("Path [%s] did contain a microsite" % uri)

            if not doc.metadata.suppress_inheritance and not (microsite == self.main_microsite or uri.endswith(METADATA_DOC_NAME)):
                microsite_metadata_doc = self.get_microsite_metadata_doc(microsite)
                self.enhance_last_modified_date(doc, microsite_metadata_doc)
                doc.metadata.inherit(microsite_metadata_doc.metadata)


            if not doc.metadata.suppress_inheritance and not (uri == self.main_microsite_metadata_uri):
                main_metadata_doc = self.get_microsite_metadata_doc(self.main_microsite)
                self.enhance_last_modified_date(doc, main_metadata_doc)
                doc.metadata.inherit(main_metadata_doc.metadata)

            if to_be_cached:
                for aux_content_ref in doc.metadata.aux_content_refs:
                    auxdoc = self.get_document(aux_content_ref.uri, locale_str)
                    if auxdoc:
                        doc.addAuxContentDoc(aux_content_ref.aux_content_type, auxdoc)
                        self.enhance_last_modified_date(doc, auxdoc)
                    else:
                        doc.missing_aux_content.append(aux_content_ref)
            else:
                for aux_content_ref in doc.metadata.aux_content_refs:
                    auxdoc = self.get_uncached_document(aux_content_ref.uri, locale_str)
                    if auxdoc:
                        doc.addAuxContentDoc(aux_content_ref.aux_content_type, auxdoc)
                        self.enhance_last_modified_date(doc, auxdoc)
                    else:
                        doc.missing_aux_content.append(aux_content_ref)

        return doc



    @func_logger
    def get_raw_document(self, uri, locale_str:str=None):
        if not uri[0] == "/":
            raise ForbiddenPathException("Path [%s] did not begin with a slash" % uri)

        doc = None

        if self.uri_is_folder(uri):
            uri = uri + "/" + self.default_doc_name

        doc = None
        if locale_str:
            locale = self.get_locale_object(locale_str)
            uri_search = UriSearch(uri, locale)
            attempt_uri = uri_search.next_variant()

            while not doc and attempt_uri:
                doc = self.read_document(attempt_uri)
                attempt_uri = uri_search.next_variant()
        else:
            doc = self.read_document(uri)

        return doc




    def create_microsite(self, microsite:str) -> None:
        raise NotImplemented()

    def delete_microsite(self, microsite:str) -> None:
        raise NotImplemented()

    def uri_is_folder(self, uri:str) -> bool:
        raise NotImplemented()

    def document_exists(self, resource_header:ResourceHeader) -> bool:
        raise NotImplemented()

    def read_document(self, uri:str) -> Doc:
        raise NotImplemented()


    def reload_source_repo(self):
        raise NotImplemented()

    def send_dest_repo(self):
        raise NotImplemented()

    def get_folder(self, uri:str) -> Folder:
        raise NotImplemented()


    def create_document(self, doc:Doc) -> None:
        raise NotImplemented()


    def move_document(self, old_uri:str, new_uri:str) -> None:
        raise NotImplemented()


    def delete_document(self, doc_uri:str) -> Doc:
        raise NotImplemented()


    def create_folder(self, parent_folder_uri:str, folder_name:str) -> None:
        raise NotImplemented()


    def move_folder(self, old_folder_uri:str, new_folder_uri:str) -> None:
        raise NotImplemented()


    def delete_folder(self, folder_uri:str) -> None:
        raise NotImplemented()


    def get_microsite_names(self) -> list:
        raise NotImplemented()


    def parse_ehtml_from_text(self, resource_header:ResourceHeader, text:str) -> EHTMLDoc:
        metadataRe      = re.compile(r"(\s*\n\s*)*(<!-- METADATA\s*\n(.*\n)*METADATA -->)?(\s*\n)?(((.*\n)|(.*))*)?")
        metadataMatch   = metadataRe.match(text)
        metadata_string = metadataMatch.group(2)
        metadata_string = metadata_string[14:-13]
        metadata        = create_metadata_from_dict(json.loads(metadata_string))
        text            = metadataMatch.group(5)

        ret_doc = EHTMLDoc(resource_header, metadata, text, get_text_encoding())

        return ret_doc


    def write_file(self, doc_uri, file) -> None:
        resource_header = ResourceHeader(doc_uri)
        doc = None
        doc_bytes = file.read()
        if resource_header.render_type == RENDER_TYPE_BINARY:
            doc = BinaryDoc(resource_header, doc_bytes)
        else:
            text = str(doc_bytes, get_text_encoding())
            if resource_header.render_type == RENDER_TYPE_TEXT:
                doc = TextDoc(resource_header, text, get_text_encoding())
            elif resource_header.render_type == RENDER_TYPE_EHTML:
                doc = self.parse_ehtml_from_text(resource_header, text)

        self.write_document(doc)


    def document_exists(self, resource_header:ResourceHeader) -> bool:
        raise NotImplemented()

    def write_document(self, doc:Doc, preserve_last_modified:bool=False) -> None:
        raise NotImplemented()

    def create_microsite_archive(self, microsite:str) -> BufferedReader:
        raise NotImplemented()

    def get_microsite_inventory(self, microsite:str) -> dict:
        raise NotImplemented()







class PTLRepo():
    def __init__(self, short_name:str, description:str, service_name:str):
        self.short_name     = short_name
        self.description    = description
        self.service_name   = service_name



class StatusMessage():
    def __init__(self, status_date:datetime, message_token:str, message_data:list):
        self.status_date = status_date
        self.message_token = message_token
        self.message_data = message_data


class PromotionRequest():
    STATUS_SUBMITTED = 0
    STATUS_RUNNING = 1
    STATUS_COMPLETED_WITH_ERRORS = 3
    STATUS_COMPLETED_SUCCESSFULLY = 4
    STATUS_FAILED = 5

    MSGTKN_PROMOTION_STARTED					= "promotion_started"
    MSGTKN_MICROSITE_WAS_DELETED				= "microsite_was_deleted"
    MSGTKN_MICROSITE_DELETION_FAILED			= "microsite_deletion_failed"
    MSGTKN_MICROSITE_WAS_CREATED				= "microsite_was_created"
    MSGTKN_MICROSITE_CREATION_FAILED			= "microsite_creation_failed"
    MSGTKN_FOLDER_WAS_CREATED				    = "folder_was_created"
    MSGTKN_FOLDER_WAS_DELETED				    = "folder_was_deleted"
    MSGTKN_CREATE_FOLDER_FOLDER_ALREADY_EXISTS	= "create_folder_folder_already_exists"
    MSGTKN_DOCUMENT_WAS_WRITTEN				    = "document_was_written"
    MSGTKN_DOCUMENT_WAS_DELETED				    = "document_was_deleted"
    MSGTKN_PROMOTE_DOC_MISSING_SRC_REPO		    = "promote_doc_missing_src_repo"
    MSGTKN_DEL_FOLDER_NO_LONGER_IN_DEST_REPO	= "del_folder_no_longer_in_dest"
    MSGTKN_DEL_DOC_NO_LONGER_IN_DEST_REPO		= "del_doc_no_longer_in_dest_repo"
    MSGTKN_PROMOTION_RUN_CONCLUDED				= "promotion_run_concluded"

    def __init__(self, source_repo:str, dest_repo:str, microsite:str, differences:list, status:int=STATUS_SUBMITTED, start_timestamp:datetime=None, status_messages:list=None, extended_attributes={}, id=None, register_method=None, deregister_method=None):
        self.source_repo = source_repo
        self.dest_repo = dest_repo
        self.microsite = microsite
        self.differences = differences
        self.status = status
        self.register_method = register_method
        self.deregister_method = deregister_method
        self.extended_attributes = extended_attributes

        if start_timestamp:
            self.start_timestamp = start_timestamp
        else:
            self.start_timestamp = datetime.utcnow()

        if status_messages:
            self.status_messages = status_messages
        else:
            self.status_messages = []

        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())

    def __enter__(self):
        if self.register_method:
            self.register_method(self)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value:
            logger.debug(exception_value)

        if self.deregister_method:
             self.deregister_method(self)



class BasePromotionService():
    def __init__(self, repo_list:list):
        converter = PlainObjConverter([("", lambda o : PTLRepo(**o) )])
        self.plt_repos = converter.convert_from_primative(repo_list)
        self.running_promotions = {}


    def register_running_promotion(self, promotion_request:PromotionRequest):
        self.running_promotions[promotion_request.id] = promotion_request


    def deregister_running_promotion(self, promotion_request:PromotionRequest):
        del self.running_promotions[promotion_request.id]


    def find_repo(self, short_name:str) -> int:
        ret_value = None
        for i in range(0, len(self.plt_repos)):
            if self.plt_repos[i].short_name == short_name:
                pos_flag = None
                if i == 0:
                    pos_flag = PLT_REPOPOS_FIRST
                elif i == 2:
                    pos_flag = PLT_REPOPOS_SECOND
                elif i == len(self.plt_repos)-1:
                    pos_flag = PLT_REPOPOS_LAST
                else:
                    pos_flag = PLT_REPOPOS_OTHER

                ret_value = (self.plt_repos[i], pos_flag, i)
                break

        if not ret_value:
            raise PLTRepoNotFound("PLTRepo:[%s] could not be found" % short_name)

        return ret_value


    def compare_microsite(self, source_plt_repo_key:str, dest_ptl_repo_key:str, microsite:str) -> list:

        source_ptl_repo:PTLRepo = self.find_repo(source_plt_repo_key)
        dest_ptl_repo:PTLRepo = self.find_repo(dest_ptl_repo_key)

        source_repo_svc:BaseContentService = get_service_object(source_ptl_repo[0].service_name)
        dest_repo_svc:BaseContentService = get_service_object(dest_ptl_repo[0].service_name)

        source_inv = source_repo_svc.get_microsite_inventory(microsite)
        dest_inv = dest_repo_svc.get_microsite_inventory(microsite)

        updates = []
        adds = []
        deletes = []

        for uri in source_inv:
            rii1 = source_inv[uri]
            rii2 = None
            if uri in dest_inv:
                rii2 = dest_inv[uri]
                if not (rii1 == rii2):
                    if not rii1.is_folder:
                        diff = RepoInventoryDiff(RepoInventoryDiff.ACTION_UPDATE, rii1, rii2)
                        updates.append(diff)
            else:
                diff = RepoInventoryDiff(RepoInventoryDiff.ACTION_ADD, rii1)
                adds.append(diff)

        for uri in dest_inv:
            rii2 = dest_inv[uri]

            if not uri in source_inv:
                diff = RepoInventoryDiff(RepoInventoryDiff.ACTION_DELETE, to_inv_item=rii2)
                deletes.append(diff)


        deletes.sort(key=lambda o:o.to_inv_item.uri, reverse=True)
        adds.sort(key=lambda o:o.from_inv_item.uri)
        updates.sort(key=lambda o:o.to_inv_item.uri)
        output_list = deletes + adds + updates

        return output_list


    def start_promotion(self, source_plt_repo_key:str, dest_ptl_repo_key:str, microsite:str, differences=None, extended_attributes={}) -> PromotionRequest:
        promotion_request = PromotionRequest(source_plt_repo_key, 
            dest_ptl_repo_key, 
            microsite, 
            differences, 
            extended_attributes=extended_attributes,
            register_method=self.register_running_promotion, 
            deregister_method=self.deregister_running_promotion)

        promotion_request.status_messages.append(StatusMessage(datetime.utcnow(), PromotionRequest.MSGTKN_PROMOTION_STARTED, []))

        self.create_promotion(promotion_request)

        args = [promotion_request]

        Thread(args=args, target=self.promote_content).start()

        return promotion_request


    def promote_content(self, promotion_request:PromotionRequest) -> None:
        with promotion_request:
            try:
                logger.info("starting promotion")
                minor_error_found = False
                dest_microsite_deleted = False
                differences = promotion_request.differences

                if not differences:
                    logger.info("Compare microsites")
                    differences = self.compare_microsite(promotion_request.source_repo, promotion_request.dest_repo, promotion_request.microsite)

                logger.info("Find source repo")
                source_ptl_repo:PTLRepo = self.find_repo(promotion_request.source_repo)
                logger.info("Find dest repo")
                dest_ptl_repo:PTLRepo   = self.find_repo(promotion_request.dest_repo)

                logger.info("get source repo service")
                source_repo_svc:BaseContentService  = get_service_object(source_ptl_repo[0].service_name)
                logger.info("get dest repo service")
                dest_repo_svc:BaseContentService    = get_service_object(dest_ptl_repo[0].service_name)

                logger.info("setup done get started")

                if not promotion_request.microsite in source_repo_svc.get_microsite_names():
                    dest_microsite_deleted = True
                    try:
                        dest_repo_svc.delete_microsite(promotion_request.microsite)
                        self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_MICROSITE_WAS_DELETED, [promotion_request.microsite])
                    except MicrositeNotFound:
                        promotion_request.status = PromotionRequest.STATUS_FAILED
                        self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_MICROSITE_DELETION_FAILED, [promotion_request.microsite])

                elif not promotion_request.microsite in dest_repo_svc.get_microsite_names(): 
                    try:
                        dest_repo_svc.create_microsite(promotion_request.microsite)
                        self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_MICROSITE_WAS_CREATED, [promotion_request.microsite])
                    except MicrositeAlreadyExists:
                        promotion_request.status = PromotionRequest.STATUS_FAILED
                        self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_MICROSITE_CREATION_FAILED, [promotion_request.microsite])

                if not promotion_request.status == PromotionRequest.STATUS_FAILED and not dest_microsite_deleted:
                    for diff in promotion_request.differences:
                        if diff.action == RepoInventoryDiff.ACTION_ADD:
                            inv_item = diff.from_inv_item
                            if inv_item.is_folder:
                                try:
                                    segs:list=inv_item.uri.split("/")
                                    
                                    parent_folder = "/".join(segs[0:len(segs)-1])
                                    new_folder = segs[-1:][0]

                                    dest_repo_svc.create_folder(parent_folder, new_folder)
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_FOLDER_WAS_CREATED, [inv_item.uri])
                                except FolderAlreadyExists:
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_CREATE_FOLDER_FOLDER_ALREADY_EXISTS, [inv_item.uri])
                                    minor_error_found = True
                            else:
                                
                                try:
                                    doc = source_repo_svc.get_raw_document(inv_item.uri)
                                    dest_repo_svc.write_document(doc, preserve_last_modified=True)
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_DOCUMENT_WAS_WRITTEN, [inv_item.uri])
                                except DocumentNotFound:
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_PROMOTE_DOC_MISSING_SRC_REPO, [inv_item.uri])
                                    minor_error_found = True

                        elif diff.action == RepoInventoryDiff.ACTION_UPDATE:
                            inv_item = diff.from_inv_item
                            try:
                                doc = source_repo_svc.get_raw_document(inv_item.uri)
                                dest_repo_svc.write_document(doc, preserve_last_modified=True)
                                self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_DOCUMENT_WAS_WRITTEN, [inv_item.uri])
                            except DocumentNotFound:
                                self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_PROMOTE_DOC_MISSING_SRC_REPO, [inv_item.uri])
                                minor_error_found = True

                        elif diff.action == RepoInventoryDiff.ACTION_DELETE:
                            inv_item = diff.to_inv_item
                            if inv_item.is_folder:
                                try:
                                    dest_repo_svc.delete_folder(inv_item.uri)
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_FOLDER_WAS_DELETED, [inv_item.uri])
                                except FolderDoesNotExist:
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_DEL_FOLDER_NO_LONGER_IN_DEST_REPO, [inv_item.uri])
                                    minor_error_found = True
                            else:
                                try:
                                    dest_repo_svc.delete_document(inv_item.uri)
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_DOCUMENT_WAS_DELETED, [inv_item.uri])
                                except DocumentNotFound:
                                    self.add_status_to_promotion(promotion_request, PromotionRequest.MSGTKN_DEL_DOC_NO_LONGER_IN_DEST_REPO, [inv_item.uri])
                                    minor_error_found = True


                promotion_request.status_messages.append(StatusMessage(datetime.utcnow(), PromotionRequest.MSGTKN_PROMOTION_RUN_CONCLUDED, []))
                if minor_error_found:
                    promotion_request.status = promotion_request.STATUS_COMPLETED_WITH_ERRORS
                else:
                    promotion_request.status = promotion_request.STATUS_COMPLETED_SUCCESSFULLY

            except Exception as e:
                promotion_request.status = promotion_request.STATUS_FAILED
                logger.fatal(e)
        logger.info("end promotion")
                
        self.update_promotion(promotion_request)


    def add_status_to_promotion(self, promotion_request:PromotionRequest, message_token:str, message_data:list=[]):
        promotion_request.status_messages.append(StatusMessage(datetime.utcnow(), message_token, message_data))
        self.update_promotion(promotion_request)


    def get_promotion_history(self) -> list:
        promotion_history = self.get_unpurged_promotion_history()
        ret_list = []
        for promotion_request in promotion_history:
            promotion_request:PromotionRequest
            date_boundary = datetime.utcnow() - timedelta(days=30)
            if promotion_request.start_timestamp < date_boundary:
                self.delete_promotion(promotion_request.id)
            else:
                ret_list.append(promotion_request)

        return ret_list


    def get_promotion(self, id) -> PromotionRequest:...

    def create_promotion(self, promotion_request:PromotionRequest):...

    def update_promotion(self, promotion_request:PromotionRequest):...

    def delete_promotion(self, id:str) -> PromotionRequest:...

    def get_unpurged_promotion_history(self) -> list:...