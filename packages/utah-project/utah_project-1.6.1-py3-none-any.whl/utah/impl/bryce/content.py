from asyncio.log import logger
from pickletools import read_decimalnl_long
from utah.core.content import BasePromotionService, DocumentAlreadyExists, EHTMLDoc, FolderAlreadyExists, FolderDoesNotExist, RepoInventoryDiff, RepoInventoryItem, TextDoc, BinaryDoc, ResourceHeader, Folder, Doc
from utah.core.content import BaseContentService
from utah.core.content import MicrositeAlreadyExists
from utah.core.content import MicrositeNotFound
from utah.core.content import DocumentNotFound
from utah.core.bootstrap import get_text_encoding
from utah.core.content import create_dict_from_metadata
from utah.core.content import create_metadata_from_dict
from utah.core.content import SelfCleaningBufferedReader
from utah.core.utilities import string_to_date
from utah.core.utilities import date_to_string
from utah.core.utilities import date_to_timestamp_string
from utah.core.utilities import PlainObjConverter
from utah.core.content import DeleteMainMicrositeAttempted
from utah.core.content import PromotionRequest
from utah.core.content import PromotionRequestNotFound
from utah.core.content import PromotionRequestAlreadyExists
from utah.core.content import StatusMessage

from io import BufferedReader
from utah.core.content import ForbiddenPathException

from utah.core.content import RENDER_TYPE_EHTML
from utah.core.content import RENDER_TYPE_TEXT
from utah.core.content import RENDER_TYPE_BINARY
from utah.core.utilities import string_to_timestamp

from utah.impl.bryce.utilities import ConnectionDefinition

from datetime import datetime

import zipfile
import logging

logger = logging.getLogger(__name__)

REPO_ITEM_TYPE_MICROSITE = 1
REPO_ITEM_TYPE_FOLDER = 2
REPO_ITEM_TYPE_DOCUMENT = 3
REPO_ITEM_TYPE_PROMOTION_REQUEST = 4


pr_cvts=[]
pr_cvts.append(  ("", lambda ro : PromotionRequest(**ro))  )
pr_cvts.append(  ("start_timestamp", lambda ro : string_to_date(ro))  )
pr_cvts.append(  ("status_messages", lambda ro : StatusMessage(**ro))  )
pr_cvts.append(  ("status_messages/status_date", lambda ro : string_to_date(ro))  )
pr_cvts.append(  ("differences", lambda ro : RepoInventoryDiff(**ro))  )
pr_cvts.append(  ("differences/from_inv_item", lambda ro : RepoInventoryItem(**ro))  )
pr_cvts.append(  ("differences/to_inv_item", lambda ro : RepoInventoryItem(**ro))  )

pr_converter = PlainObjConverter(converters=pr_cvts)
pr_cvts=None

def get_name_from_uri(uri:str):
    ret_name = None
    last_slash = uri.rfind("/")
    if last_slash > 0 and last_slash < len(uri):
        ret_name = uri[last_slash+1:]

    return ret_name

def get_folder_from_uri(uri:str):
    ret_folder = None
    last_slash = uri.rfind("/")
    if last_slash > 0 and last_slash < len(uri):
        ret_folder = uri[:last_slash]

    return ret_folder


def build_ehtml_doc_from_obj(obj, resource_header):
    metadata = create_metadata_from_dict(obj["metadata"])
    ret_doc = EHTMLDoc(resource_header, metadata, obj["text"], get_text_encoding())
    return ret_doc


def build_text_doc_from_obj(obj, resource_header):
    ret_doc = TextDoc(resource_header, obj["text"], get_text_encoding())
    return ret_doc


def build_binary_doc_from_obj(obj, resource_header):
    ret_doc = BinaryDoc(resource_header, bytearray(obj["doc_bytes"]))
    return ret_doc


def build_obj_from_ehtml_doc(doc:EHTMLDoc):
    ret_obj = {"metadata" : create_dict_from_metadata(doc.metadata), "text" : doc.text}
    return ret_obj


def build_obj_from_text_doc(doc:TextDoc):
    ret_obj = {"text" : doc.text}
    return ret_obj


def build_obj_from_binary_doc(doc:BinaryDoc):
    ret_obj = {"doc_bytes" : doc.doc_bytes}
    return ret_obj


def zi_tuple(date_time:datetime):
    return (
        date_time.year,
        date_time.month,
        date_time.day,
        date_time.hour,
        date_time.minute,
        date_time.second
    )

def write_ehtml_doc_to_zip(zip, doc:EHTMLDoc):
    path_offset = doc.resource_header.uri.find('/', 1) + 1
    zi = zipfile.ZipInfo(doc.resource_header.uri[path_offset:], zi_tuple(doc.last_modified_date))
    zip.writestr(zi, doc.string_output())


def write_text_doc_to_zip(zip, doc:TextDoc):
    path_offset = doc.resource_header.uri.find('/', 1) + 1
    zi = zipfile.ZipInfo(doc.resource_header.uri[path_offset:], zi_tuple(doc.last_modified_date))
    zip.writestr(zi, doc.text)


def write_binary_doc_to_zip(zip, doc:BinaryDoc):
    path_offset = doc.resource_header.uri.find('/', 1) + 1
    zi = zipfile.ZipInfo(doc.resource_header.uri[path_offset:], zi_tuple(doc.last_modified_date))
    zip.writestr(zi, doc.doc_bytes)


DOC_BUILDER_METHODS = {
    RENDER_TYPE_EHTML : build_ehtml_doc_from_obj,
    RENDER_TYPE_TEXT : build_text_doc_from_obj,
    RENDER_TYPE_BINARY : build_binary_doc_from_obj
}


OBJ_BUILDER_METHODS = {
    RENDER_TYPE_EHTML : build_obj_from_ehtml_doc,
    RENDER_TYPE_TEXT : build_obj_from_text_doc,
    RENDER_TYPE_BINARY : build_obj_from_binary_doc
}

ZIP_WRITER_METHODS = {
    RENDER_TYPE_EHTML : write_ehtml_doc_to_zip,
    RENDER_TYPE_TEXT : write_text_doc_to_zip,
    RENDER_TYPE_BINARY : write_binary_doc_to_zip
}


class ContentService(BaseContentService):
    def __init__(self, mongo_db_info:dict, temp_dir:str, main_microsite: str, default_doc_name: str = "default.html", cache_timeout_secs: int=60, deployment_model:int=0):

        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)
        self.temp_dir = temp_dir

        super().__init__(main_microsite, default_doc_name, cache_timeout_secs, deployment_model)


    def get_collection(self):
        logger.debug("ContentService.get_collection()")
        return self.conn_def.get_database()["content"]

    
    def create_microsite(self, microsite:str) -> None:
        uri = "/%s" % microsite
        coll = self.get_collection()

        if not coll.find_one({"uri":uri}):
            coll.insert_one({"uri" : "/%s" % microsite, "item_type" : REPO_ITEM_TYPE_MICROSITE })
        else:
            raise MicrositeAlreadyExists()


    def delete_microsite(self, microsite:str) -> None:
        if microsite == self.get_main_microsite():
            raise DeleteMainMicrositeAttempted()

        key_regex = "^/%s(/.*)?$" % microsite

        coll = self.get_collection()

        if coll.find_one({ "uri" : { "$regex" : key_regex } }):
            coll.delete_many({ "uri" : { "$regex" : key_regex } })
        else:
            raise MicrositeNotFound()

#
    def uri_is_folder(self, uri:str) -> bool:
        ret_value = False
        coll = self.get_collection()

        if coll.find_one({'uri': uri, "$or" : [{"item_type":REPO_ITEM_TYPE_MICROSITE}, {"item_type":REPO_ITEM_TYPE_FOLDER}] }):
            ret_value = True

        return ret_value


    def document_exists(self, resource_header:ResourceHeader) -> bool:
        ret_value = False
        coll = self.get_collection()

        if self.__read_document_object(coll, resource_header.uri):
            ret_value = True

        return ret_value


    def read_document(self, uri:str) -> Doc:
        ret_doc = None
        resource_header:ResourceHeader = ResourceHeader(uri)
        obj = self.__read_document_object(self.get_collection(), uri)
        if obj:
            ret_doc = DOC_BUILDER_METHODS[resource_header.render_type](obj, resource_header)
            ret_doc.last_modified_date = string_to_date(obj["last_modified_date"])
            ret_doc.base_last_modified_date = ret_doc.last_modified_date

        return ret_doc


    def get_folder(self, uri:str) -> Folder:
        ret_folder = None

        if self.uri_is_folder(uri):
            folder_list = []
            doc_list = []
            coll = self.get_collection()
            results = coll.find({"uri" : {"$regex" : '^%s\/[^/]*$' % uri}, "$or" : [{"item_type" : REPO_ITEM_TYPE_FOLDER}, {"item_type" : REPO_ITEM_TYPE_DOCUMENT } ] } )

            for result in results:
                result_name = get_name_from_uri(result["uri"])
                if result["item_type"] == REPO_ITEM_TYPE_DOCUMENT:
                    doc_list.append(result_name)
                else:
                    folder_list.append(result_name)

            ret_folder = Folder(uri, folder_list, doc_list)

        else:
            raise FolderDoesNotExist("uri:[%s]" % uri)


        return ret_folder


    def __microsite_exists(self, coll, uri) -> bool:
        ret_value = coll.find_one({"uri" : uri, "item_type" : REPO_ITEM_TYPE_MICROSITE })

        return ret_value

    def __read_document_object(self, coll, uri):
        return coll.find_one({"uri" : uri, "item_type" : REPO_ITEM_TYPE_DOCUMENT })


    def __folder_exists(self, coll, uri) -> bool:
        ret_value = coll.find_one({"uri" : uri, "$or" : [{'item_type': REPO_ITEM_TYPE_MICROSITE},{'item_type': REPO_ITEM_TYPE_FOLDER}] })

        return ret_value


    def create_document(self, doc:Doc) -> None:
        coll = self.get_collection()

        if not self.document_exists(doc.resource_header):
            obj = OBJ_BUILDER_METHODS[doc.resource_header.render_type](doc)

            obj["uri"] = doc.resource_header.uri

            if not doc.last_modified_date:
                doc.last_modified_date = datetime.utcnow()

            obj["last_modified_date"] = date_to_string(doc.last_modified_date)
            obj["size"] = doc.get_size()
            obj["item_type"] = REPO_ITEM_TYPE_DOCUMENT

            coll.insert_one(obj)
        else:
            raise DocumentAlreadyExists("uri:%s" % doc.resource_header.uri)


    def move_document(self, old_uri:str, new_uri:str) -> None:
        coll = self.get_collection()

        if self.__read_document_object(coll, new_uri):
            raise DocumentAlreadyExists("Cannot move document:[%s] to destination:[%s]. Destination document already exists" % (old_uri, new_uri))

        doc_obj = self.__read_document_object(coll, old_uri)
        if not doc_obj:
            raise DocumentNotFound("Could not move document:[%s]. It is not available in the repository" % old_uri)

        dest_folder_uri = get_folder_from_uri(new_uri)

        if not self.__folder_exists(coll, dest_folder_uri):
                raise FolderDoesNotExist("Destination folder:[%s] does not exist" % dest_folder_uri)

        doc_obj["uri"] = new_uri

        coll.update_one({"uri" : old_uri}, {"$set" : doc_obj})
        


    def delete_document(self, doc_uri:str) -> Doc:
        ret_doc = self.read_document(doc_uri)

        self.get_collection().delete_one({"uri" : doc_uri})

        return ret_doc


    def create_folder(self, parent_folder_uri:str, folder_name:str) -> None:
        uri = "%s/%s" % (parent_folder_uri, folder_name)
        coll = self.get_collection()

        if not self.__folder_exists(coll, parent_folder_uri):
            raise FolderDoesNotExist("The parent folder uri:[%s] does not exist" % parent_folder_uri)

        if self.__folder_exists(coll, uri):
            raise FolderAlreadyExists("The folder uri:[%s] already exists" % uri)

        elif self.__read_document_object(coll, uri):
            raise DocumentAlreadyExists("The uri:[%s] already existing in the repository as a document" % uri)

        self.get_collection().insert_one({"uri" : uri, "item_type" : REPO_ITEM_TYPE_FOLDER})


    def move_folder(self, old_folder_uri:str, new_folder_uri:str) -> None:
        coll = self.get_collection()
        if not self.__folder_exists(coll, old_folder_uri):
            raise FolderDoesNotExist("The folder uri:[%s] does not exist" % old_folder_uri)

        if self.__folder_exists(coll, new_folder_uri):
            raise FolderAlreadyExists("The folder uri:[%s] already exists" % new_folder_uri)

        elif self.__read_document_object(coll, new_folder_uri):
            raise DocumentAlreadyExists("The uri:[%s] already existing in the repository as a document" % new_folder_uri)

        #coll.update_many( { "uri" : { "$regex" : "^%s(/.*)?$" % old_folder_uri } }, { "$set" : { "uri": { "$replaceOne" : { "input" : "$uri", "find" : old_folder_uri, "replacement" : new_folder_uri } } } })

        coll.update_many(
            { "uri" : { "$regex" : "^%s(/.*)?$" % old_folder_uri } }, 
            [{
                "$set": { "uri": {
                "$replaceOne": { "input": "$uri", "find": old_folder_uri, "replacement": new_folder_uri }
                }}
            }]
            )



    def delete_folder(self, folder_uri:str) -> None:
        coll = self.get_collection()

        if not self.__folder_exists(coll, folder_uri):
            raise FolderDoesNotExist("Could not remove folder:[%s]. It is not available in the repository" % folder_uri)

        if len(folder_uri.split("/")) < 3:
            raise ForbiddenPathException("An attempt was made to delete the root path of a microsite. Path provided was:[%s]" % folder_uri)


        key_regex = "^%s(/.*)?$" % folder_uri

        coll.delete_many({ "uri" : { "$regex" : key_regex } })


    def get_microsite_names(self) -> list:
        ret_list = []

        microsite_obj_list = self.get_collection().find({"item_type" : REPO_ITEM_TYPE_MICROSITE})
        for ms_obj in microsite_obj_list:
            ret_list.append(ms_obj["uri"][1:])

        return ret_list


    def write_document(self, doc:Doc, preserve_last_modified:bool=False):
        coll = self.get_collection()

        obj = OBJ_BUILDER_METHODS[doc.resource_header.render_type](doc)

        obj["uri"] = doc.resource_header.uri

        if not preserve_last_modified:
            doc.last_modified_date = datetime.utcnow()

        obj["last_modified_date"] = date_to_string(doc.last_modified_date)
        obj["size"] = doc.get_size()
        obj["item_type"] = REPO_ITEM_TYPE_DOCUMENT

        if self.__read_document_object(coll, doc.resource_header.uri):            
            coll.update_one({"uri": doc.resource_header.uri, "item_type": REPO_ITEM_TYPE_DOCUMENT}, {"$set": obj})
        else:
            coll.insert_one(obj)


    def create_microsite_archive(self, microsite:str) -> BufferedReader:
        output_file_name = "%s/%s_%s.zip" % (self.temp_dir, microsite, date_to_timestamp_string(datetime.utcnow()))

        output_zipfile = zipfile.ZipFile(output_file_name, 'w', zipfile.ZIP_STORED, True, 9)

        ms_root_folder = self.get_folder("/%s" % microsite)
        self.__write_folder(output_zipfile, ms_root_folder)

        output_zipfile.close()

        f = open(output_file_name, 'rb')

        return SelfCleaningBufferedReader(f)



    def __write_folder(self, output_zipfile:zipfile, folder:Folder):
        for header in folder.file_resource_headers:
            doc = self.read_document(header.uri)
            if not doc:
                logger.debug("header.uri:[%s] doc not found" % header.uri)

            ZIP_WRITER_METHODS[doc.resource_header.render_type](output_zipfile, doc)

        for child_folder_name in folder.child_folders:
            child_folder = self.get_folder("%s/%s" % (folder.uri, child_folder_name) )
            self.__write_folder(output_zipfile, child_folder)


    def get_microsite_inventory(self, microsite:str) -> dict:
        uri_regex = "^/%s(/.*)?$" % microsite

        ret_results = {}
        query = {
            "$and" : [
                {"uri" : { "$regex" : uri_regex }},
                {
                    "$or" : [
                        {"item_type":REPO_ITEM_TYPE_FOLDER}, 
                        {"item_type":REPO_ITEM_TYPE_DOCUMENT}
                    ]
                }
            ]
        }

        results = self.get_collection().find(query)
        for item in results:
            if item["item_type"] == REPO_ITEM_TYPE_FOLDER:
                ret_results[item["uri"]] = RepoInventoryItem(True, item["uri"], 0, 0)
            else:
                lmd = int(string_to_timestamp(item["last_modified_date"]))
                size = item["size"]
                ret_results[item["uri"]] = RepoInventoryItem(False, item["uri"], lmd, size)

        return ret_results


class PromotionService(BasePromotionService):
    def __init__(self, mongo_db_info:dict, repo_list:list):
        
        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)

        super().__init__(repo_list)


    def get_collection(self):
        logger.debug("PromotionService.get_collection()")
        return self.conn_def.get_database()["promotion"]


    def get_promotion(self, id) -> PromotionRequest:
        coll = self.get_collection()

        raw_promo_req = coll.find_one({"id":id})

        if not raw_promo_req:
            raise PromotionRequestNotFound("Promotion id:%s was not found" % id)

        del raw_promo_req["_id"]
        ret_promo_req = pr_converter.convert_from_primative(raw_promo_req)
        
        return ret_promo_req


    def create_promotion(self, promotion_request:PromotionRequest):
        coll = self.get_collection()
        promo_request = self.demarshall_promo_request(promotion_request)
        coll.insert_one(promo_request)


    def demarshall_promo_request(self, promotion_request:PromotionRequest):
        promo_request = {}
        promo_request["id"] = promotion_request.id
        promo_request["source_repo"] = promotion_request.source_repo
        promo_request["dest_repo"] = promotion_request.dest_repo
        promo_request["status"] = promotion_request.status
        promo_request["extended_attributes"] = promotion_request.extended_attributes
        promo_request["microsite"] = promotion_request.microsite
        promo_request["differences"] = []

        for diff in promotion_request.differences:            
            fii = diff.from_inv_item
            raw_fii = None

            if fii:
                raw_fii = {"is_folder":fii.is_folder, 
                            "uri":fii.uri, 
                            "last_modified_date":fii.last_modified_date, 
                            "size":fii.size}

            tii = diff.to_inv_item
            raw_tii = None
            if tii:
                raw_tii = {"is_folder":tii.is_folder, 
                            "uri":tii.uri, 
                            "last_modified_date":tii.last_modified_date, 
                            "size":tii.size}


            raw_diff = {
                "action" : diff.action,
                "from_inv_item": raw_fii,
                "to_inv_item": raw_tii
            }

            promo_request["differences"].append(raw_diff)

        promo_request["start_timestamp"] = date_to_string(promotion_request.start_timestamp)

        status_messages = []
        promo_request["status_messages"] = status_messages
        for message in promotion_request.status_messages:
            dm_message = {}
            dm_message["status_date"] = date_to_string(message.status_date)
            dm_message["message_token"] = message.message_token
            dm_message["message_data"] = message.message_data
            status_messages.append(dm_message)

        return promo_request


    def update_promotion(self, promotion_request:PromotionRequest):
        json_obj = self.demarshall_promo_request(promotion_request)
        coll = self.get_collection()

        key = { "id":promotion_request.id }

        coll.update_one(key, {"$set":json_obj})


    def delete_promotion(self, id:str) -> PromotionRequest:
        coll = self.get_collection()
        key = { "id" : "%s" % id }

        if coll.find_one(key):
            coll.delete_one(key)


    def get_unpurged_promotion_history(self) -> list:
        coll = self.get_collection()
        key = { }

        raw_promo_req_list = coll.find(key)

        ret_list = []

        for raw_promo_req in raw_promo_req_list:
            del raw_promo_req["_id"]
            ret_list.append(pr_converter.convert_from_primative(raw_promo_req))

        return ret_list