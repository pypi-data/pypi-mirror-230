from threading import Lock
import os
import json
import re
import subprocess
import shutil
from datetime import datetime
import time
from dateutil import tz
from utah.core.utilities import func_logger
from utah.core.utilities import logging
from utah.core.utilities import get_text_from_file
from utah.core.utilities import get_dict_from_json_file
from utah.core.utilities import write_dict_to_json_file
from utah.core.utilities import string_to_date
from utah.core.utilities import date_to_string
from utah.core.bootstrap import get_text_encoding
from io import BufferedReader

from utah.core.content import RENDER_TYPE_BINARY, RENDER_TYPE_EHTML, RENDER_TYPE_TEXT, EHTMLMetaData
from utah.core.content import FOLDER_INVALIDATION_REGEX
from utah.core.content import BaseContentService
from utah.core.content import MicrositeNotFound
from utah.core.content import MicrositeAlreadyExists
from utah.core.content import DeleteMainMicrositeAttempted
from utah.core.content import BinaryDoc
from utah.core.content import TextDoc
from utah.core.content import EHTMLDoc
from utah.core.content import RepoInventoryItem
from utah.core.content import create_dict_from_metadata
from utah.core.content import create_metadata_from_dict
from utah.core.content import parse_microsite_name
from utah.core.content import DocumentAlreadyExists
from utah.core.content import DocumentNotFound
from utah.core.content import FolderDoesNotExist
from utah.core.content import FolderAlreadyExists
from utah.core.content import get_parent_folder_path
from utah.core.content import RelativeReferenceNotPermitted
from utah.core.content import ForbiddenPathException
from utah.core.content import Folder
from utah.core.content import Doc
from utah.core.content import ResourceHeader
from utah.core.content import URIIsDirectory
from utah.core.content import SelfCleaningBufferedReader
from utah.core.content import BasePromotionService 
from utah.core.content import PromotionRequest
from utah.core.content import PromotionRequestNotFound
from utah.core.content import PromotionRequestAlreadyExists
from utah.core.content import RepoInventoryDiff
from utah.core.content import StatusMessage


logger = logging.getLogger(__name__)

def absolute_reference_check(uri):
    if not uri[0] == "/" or uri.find("/..") > -1 or uri.find("*") > -1:
        raise RelativeReferenceNotPermitted("uri:[%s]" % uri)


def microsite_absolute_reference_check(microsite):
    if microsite.find("/") > -1 or microsite.find("*") > -1:
        raise RelativeReferenceNotPermitted("Microsite:[%s]" % microsite)



class ContentService(BaseContentService):
    @func_logger
    def __init__(self, filesystem_root:str, main_microsite:str, archive_temp_dir:str, default_doc_name:str="default.html", cache_timeout_secs:int=60, deployment_model:int=0):
        BaseContentService.__init__(self, main_microsite, default_doc_name, cache_timeout_secs, deployment_model)

        self.filesystem_root = filesystem_root
        self.archive_temp_dir = archive_temp_dir

        self.get_doc_methods = {
                RENDER_TYPE_BINARY : self.__getBinaryDoc,
                RENDER_TYPE_TEXT : self.__getTextDoc,
                RENDER_TYPE_EHTML : self.__getEHTMLDoc
        }

        self.write_doc_methods = {
                RENDER_TYPE_BINARY : self.__writeBinaryDoc,
                RENDER_TYPE_TEXT : self.__writeTextDoc,
                RENDER_TYPE_EHTML : self.__writeEHTMLDoc
        }


        self.lock = Lock()


    @func_logger
    def delete_microsite(self, microsite:str):
        microsite_absolute_reference_check(microsite)

        self.lock.acquire(True, 1)

        try:
            if microsite == self.get_main_microsite():
                raise DeleteMainMicrositeAttempted()

            microsite_path = "%s/%s" % (self.filesystem_root, microsite)
            if os.path.isdir(microsite_path):
                shutil.rmtree(microsite_path)
            else:
                raise MicrositeNotFound()
        finally:
            self.lock.release()


    @func_logger
    def create_microsite(self, microsite:str):
        microsite_absolute_reference_check(microsite)

        self.lock.acquire(True, 1)

        try:
            microsite_path = "%s/%s" % (self.filesystem_root, microsite)
            if not os.path.isdir(microsite_path):
                os.mkdir(microsite_path)
            else:
                raise MicrositeAlreadyExists()
        finally:
            self.lock.release()


    @func_logger
    def __folder_exists(self, folder_path:str):
        return os.path.isdir(folder_path)


    @func_logger
    def __file_exists(self, file_path:str):
        return os.path.isfile(file_path)


    @func_logger
    def get_full_path(self, uri):
        if not self.validate_microsite(uri):
            raise MicrositeNotFound("uri:[%s] is not part of a valid microsite" % uri)

        ret_path = "%s%s" % (self.filesystem_root, uri)

        return ret_path


    @func_logger
    def __getBinaryDoc(self, header:ResourceHeader, path:str):
        ret_doc = None
        try:
            with open(path, 'rb') as bites:
                doc_bytes = bites.read()
                ret_doc = BinaryDoc(header, doc_bytes)

        except FileNotFoundError as e:
            pass

        return ret_doc


    @func_logger
    def __getTextDoc(self, header:ResourceHeader, path:str):
        text = self.__getText(path)
        ret_doc = None
        if not text == None:
            ret_doc = TextDoc(header, text, get_text_encoding())

        return ret_doc


    @func_logger
    def __getEHTMLDoc(self, header:ResourceHeader, path:str):
        text = self.__getText(path)
        ret_doc = None
        if not text == None:
            metadataRe      = re.compile(r"(\s*\n\s*)*(<!-- METADATA\s*\n(.*\n)*METADATA -->)?(\s*\n)?(((.*\n)|(.*))*)?")
            metadataMatch   = metadataRe.match(text)
            metadata_string = metadataMatch.group(2)

            if metadata_string:
                metadata_string = metadata_string[14:-13]
                metadata        = create_metadata_from_dict(json.loads(metadata_string))
                text            = metadataMatch.group(5)
            else:
                metadata = EHTMLMetaData()
                text = text

            ret_doc = EHTMLDoc(header, metadata, text, get_text_encoding())

        return ret_doc


    @func_logger
    def __getText(self, path:str):
        text = None

        try:
            text = get_text_from_file(path)
        except FileNotFoundError as e:
            pass

        return text


    @func_logger
    def __writeBinaryDoc(self, binary_doc:BinaryDoc):
        file_path = "%s%s" % (self.filesystem_root, binary_doc.resource_header.uri)
        with open(file_path, 'wb') as binary_file:
            binary_file.write(binary_doc.doc_bytes)
            binary_file.close()
                        #os.utime(r'C:\my\file\path.pdf', (1602179630, 1602179630))

        os.utime(file_path, )



    @func_logger
    def __writeTextDoc(self, text_doc:TextDoc):
        file_path = "%s%s" % (self.filesystem_root, text_doc.resource_header.uri)
        with open(file_path, 'wb') as text_file:
            text_file.write(text_doc.text.encode(get_text_encoding()))
            text_file.close()


    @func_logger
    def __writeEHTMLDoc(self, ehtml_doc:EHTMLDoc):
        file_path = "%s%s" % (self.filesystem_root, ehtml_doc.resource_header.uri)
        with open(file_path, 'wb') as text_file:

            metadata_json = json.dumps(create_dict_from_metadata(ehtml_doc.metadata), indent=4)

            text_file.write('<!-- METADATA\n'.encode(get_text_encoding()))
            text_file.write(metadata_json.encode(get_text_encoding()))
            text_file.write('\n'.encode(get_text_encoding()))
            text_file.write('METADATA -->\n'.encode(get_text_encoding()))
            text_file.write(ehtml_doc.text.encode(get_text_encoding()))

            text_file.close()


    def set_file_last_modified(self, uri, last_modified:datetime):
        file_path = "%s%s" % (self.filesystem_root, uri)
        #logger.info(last_modified)
        #local_time_zone = tz.gettz(time.tzname[time.daylight])
        #local_last_modified = last_modified.astimezone(local_time_zone)

        #logger.info(last_modified)

        dt_epoch = last_modified.timestamp()
        os.utime(file_path, (dt_epoch, dt_epoch))


    @func_logger
    def reload_source_repo(self):
        ret_value = True
        p = subprocess.Popen(["git", "-C", self.filesystem_root, "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode:
            logger.error("Content Repo Reload failed: " + stderr.decode())
            ret_value = False

        return ret_value


    @func_logger
    def send_dest_repo(self):
        ret_value = True
        p = subprocess.Popen(["git", "-C", self.filesystem_root, "push"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode:
            logger.error("Send Content to Repo failed: " + stderr.decode())
            ret_value = False

        return ret_value


    @func_logger
    def get_microsite_names(self) -> list:
        """
        Return a list of all available microsite names
        """
        folder_validation_re = re.compile(FOLDER_INVALIDATION_REGEX)

        ret_list = next(os.walk(self.filesystem_root))[1]

        ptr = 0
        while ptr < len(ret_list):
            folder = ret_list[ptr]

            if folder_validation_re.match(folder):
                del ret_list[ptr]
            else:
                ptr = ptr + 1
                
        return ret_list


    @func_logger
    def validate_microsite(self, uri:str):
        microsite = parse_microsite_name(uri)

        microsites = self.get_microsite_names()

        return microsite in microsites


    @func_logger
    def create_document(self, doc:Doc) -> None:
        try:
            absolute_reference_check(doc.resource_header.uri)
 
            self.lock.acquire(True, 1)
            full_folder_path = self.get_full_path(doc.resource_header.uri)

            if self.__file_exists(full_folder_path):
                raise DocumentAlreadyExists("Document at path:[%s] already exists" % full_folder_path)

            self.write_doc_methods[doc.resource_header.render_type](doc)
            if doc.last_modified_date:
                self.set_file_last_modified(doc.resource_header.uri, doc.last_modified_date)
        finally:
            self.lock.release()

    @func_logger
    def move_document(self, old_uri:str, new_uri:str) -> None:

        absolute_reference_check(old_uri)
        absolute_reference_check(new_uri)

        try:
            self.lock.acquire(True, 1)

            full_old_path = self.get_full_path(old_uri)

            if not self.__file_exists(full_old_path):
                raise DocumentNotFound("Could not move document:[%s]. It is not available in the repository" % full_old_path)

            full_new_path = self.get_full_path(new_uri)

            full_new_parent_folder = get_parent_folder_path(full_new_path)

            if not self.__folder_exists(full_new_parent_folder):
                raise FolderDoesNotExist("Destination folder:[%s] does not exist" % full_new_parent_folder)

            if self.__file_exists(full_new_path):
                raise DocumentAlreadyExists("Cannot move document:[%s] to destination:[%s]. Destination document already exists" % (old_uri, new_uri))

            shutil.move(full_old_path, full_new_path)
        finally:
            self.lock.release()


    @func_logger
    def delete_document(self, doc_uri:str) -> Doc:
        absolute_reference_check(doc_uri)
        doc = None
        try:
            self.lock.acquire(True, 1)
            doc = self.get_raw_document(doc_uri)
            os.remove(self.get_full_path(doc_uri))
        finally:
            self.lock.release()

        return doc


    @func_logger
    def create_folder(self, parent_folder_uri:str, folder_name:str) -> None:
        new_folder_path = "%s/%s" % (self.get_full_path(parent_folder_uri), folder_name)

        absolute_reference_check("%s/%s" % (parent_folder_uri,folder_name))

        if self.__folder_exists(new_folder_path):
            raise FolderAlreadyExists("Could not create a directory at uri:[%s/%s] a file already exists by that name" % (parent_folder_uri, folder_name))
            
        if self.__file_exists(new_folder_path):
            raise DocumentAlreadyExists("Could not create a directory at uri:[%s/%s] a folder already exists by that name" % (parent_folder_uri, folder_name))

        os.mkdir(new_folder_path)


    @func_logger
    def move_folder(self, old_folder_uri:str, new_folder_uri:str) -> None:
        absolute_reference_check(old_folder_uri)
        absolute_reference_check(new_folder_uri)

        full_old_path = self.get_full_path(old_folder_uri)

        if not self.__folder_exists(full_old_path):
            raise DocumentNotFound("Could not move folder:[%s]. It is not available in the repository" % full_old_path)

        full_new_path = self.get_full_path(new_folder_uri)

        full_new_parent_folder = get_parent_folder_path(full_new_path)

        if not self.__folder_exists(full_new_parent_folder):
            raise FolderDoesNotExist("Destination folder:[%s] does not exist" % full_new_parent_folder)

        if self.__folder_exists(full_new_path):
            raise FolderAlreadyExists("Cannot move folder:[%s] to destination:[%s]. Folder by that names already exists at detination" % (old_folder_uri, new_folder_uri))

        shutil.move(full_old_path, full_new_path)


    @func_logger
    def delete_folder(self, folder_uri:str) -> None:
        absolute_reference_check(folder_uri)

        folder_path = self.get_full_path(folder_uri)

        if not self.__folder_exists(folder_path):
            raise DocumentNotFound("Could not remove folder:[%s]. It is not available in the repository" % folder_uri)

        if len(folder_uri.split("/")) < 3:
            raise ForbiddenPathException("An attempt was made to delete the root path of a microsite. Path provided was:[%s]" % folder_uri)

        shutil.rmtree(folder_path)


    @func_logger
    def get_folder(self, uri:str) -> Folder:
        absolute_reference_check(uri)

        full_path = "%s/%s" % (self.filesystem_root, uri)
        os_walk = os.walk(full_path)

        try:
            walk_path, folders, files = next(os_walk)
        except StopIteration as e:
            raise FolderDoesNotExist()

        return Folder(uri, folders, files)


    @func_logger
    def read_document(self, uri) -> Doc:
        absolute_reference_check(uri)

        return_doc = None
        if not self.uri_is_folder(uri):
            file_path = "%s%s" % (self.filesystem_root, uri)
            header = ResourceHeader(uri)
            return_doc = self.get_doc_methods[header.render_type](header, file_path)
            if return_doc:
                last_mod_secs_since_epoch           = os.path.getmtime(file_path)
                return_doc.last_modified_date       = datetime.fromtimestamp(last_mod_secs_since_epoch)
                return_doc.base_last_modified_date  = return_doc.last_modified_date

        else:
            raise URIIsDirectory("")

        return return_doc



    @func_logger
    def document_exists(self, resource_header:ResourceHeader) -> bool:
        absolute_reference_check(resource_header.uri)

        file_path = "%s%s" % (self.filesystem_root, resource_header.uri)
        return os.path.isfile(file_path)


    @func_logger
    def uri_is_folder(self, uri:str) -> bool:
        absolute_reference_check(uri)

        file_path = "%s%s" % (self.filesystem_root, uri)
        ret_value = False
        if os.path.isdir(file_path):
            ret_value = True

        return ret_value


    @func_logger
    def write_document(self, doc:Doc, preserve_last_modified:bool=False):
        absolute_reference_check(doc.resource_header.uri)

        file_path = "%s%s" % (self.filesystem_root, doc.resource_header.uri)
        return_doc = None

        if not os.path.isdir(file_path):
            try:
                self.lock.acquire(True, 1)
                if not preserve_last_modified:
                    doc.last_modified_date = datetime.utcnow()
                    
                self.write_doc_methods[doc.resource_header.render_type](doc)
                self.set_file_last_modified(doc.resource_header.uri, doc.last_modified_date)
            finally:
                self.lock.release()

        else:
            raise URIIsDirectory("")

        return return_doc


    #@func_logger
    #def write_file(self, uri:str, file) -> None:
    #    absolute_reference_check(uri)

    #    file_path = "%s%s" % (self.filesystem_root, uri)
    #    file.save(file_path)


    @func_logger
    def create_microsite_archive(self, microsite:str, suffix:str="") -> BufferedReader:
        microsite_path = "%s/%s" % (self.filesystem_root, microsite)
        if not os.path.isdir(microsite_path):
            raise MicrositeNotFound("Microsite:[%s] does not exist" % microsite)

        if not suffix:
            suffix = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')

        archive_name = "%s/%s_archive_%s" % (self.archive_temp_dir, microsite, suffix)

        output_file = shutil.make_archive(archive_name, "zip", self.filesystem_root + '/' + microsite, '.')

        f = open(output_file, 'rb')
        ret_file = SelfCleaningBufferedReader(f)

        return ret_file

    @func_logger
    def get_microsite_inventory(self, microsite:str) -> dict:
        microsite_path = "%s/%s" % (self.filesystem_root, microsite)
        root_len = len(self.filesystem_root)
        microsite_walk = os.walk(microsite_path)
        ret_dict = {}
        microsite_root = True
        while microsite_walk:
            try:
                (folder, sub_folders, files) = next(microsite_walk)
                if not microsite_root:
                    folder = folder.replace('\\', '/')
                    uri = folder[root_len:]

                    ret_dict[uri] = RepoInventoryItem(True, uri, os.path.getmtime(folder), os.path.getsize(folder))
                else:
                    microsite_root = False

                for filename in files:
                    full_filename = "%s/%s" % (folder, filename)
                    uri = full_filename[root_len:]
                    ret_dict[uri] = RepoInventoryItem(False, uri, int(os.path.getmtime(full_filename)), os.path.getsize(full_filename))

            except StopIteration:
                microsite_walk = None

        return ret_dict


class PromotionService(BasePromotionService):
    def __init__(self, repo_list: list, data_path:str):
        super().__init__(repo_list)
        self.data_path = data_path


    def obj_path(self, id):
        return "%s/%s.json" % (self.data_path, id)



    def get_promotion(self, id) -> PromotionRequest:
        try:
            obj = None
            attempts = 0
            load_exception = None
            while not obj and attempts < 3:
                try:
                    obj = get_dict_from_json_file(self.obj_path(id))
                except Exception as e:
                    time.sleep(2)
                    attempts = attempts + 1
                    load_exception = e

            if not obj:
                raise load_exception

            differences = []
            for obj_difference in obj["differences"]:
                obj_from_inv_item = obj_difference["from_inv_item"]
                from_inv_item = None
                if obj_from_inv_item:
                    from_inv_item = RepoInventoryItem(**obj_from_inv_item)

                obj_to_inv_item = obj_difference["to_inv_item"]
                to_inv_item = None
                if obj_to_inv_item:
                    to_inv_item = RepoInventoryItem(**obj_to_inv_item)

                differences.append(RepoInventoryDiff(action=obj_difference["action"], from_inv_item=from_inv_item, to_inv_item=to_inv_item))

            start_timestamp = string_to_date(obj["start_timestamp"])

            status_messages = []
            for obj_status_message in obj["status_messages"]:
                obj_status_message["status_date"] = string_to_date(obj_status_message["status_date"])
                status_messages.append(StatusMessage(**obj_status_message))


            obj["differences"] = differences
            obj["start_timestamp"] = start_timestamp
            obj["status_messages"] = status_messages

            ret_promotion_request = PromotionRequest(**obj)

        except FileNotFoundError as e:
            raise PromotionRequestNotFound("Promotion id:%s was not found" % id)

        return ret_promotion_request

    def repo_inv_item_to_obj(self, repo_inv_item:RepoInventoryItem):
        obj_from_inv_item = None
        if repo_inv_item:
            obj_from_inv_item = {   "is_folder":repo_inv_item.is_folder,
                                    "uri":repo_inv_item.uri,
                                    "last_modified_date": repo_inv_item.last_modified_date,
                                    "size": repo_inv_item.size
                                }
        return obj_from_inv_item


    def promotion_request_to_obj(self, promotion_request:PromotionRequest)->dict:
        ret_obj = {}
        ret_obj["id"] = promotion_request.id
        ret_obj["microsite"] = promotion_request.microsite
        ret_obj["source_repo"] = promotion_request.source_repo
        ret_obj["dest_repo"] = promotion_request.dest_repo
        ret_obj["status"] = promotion_request.status
        ret_obj["extended_attributes"] = promotion_request.extended_attributes
        ret_obj["start_timestamp"] = date_to_string(promotion_request.start_timestamp)

        obj_differences = []
        for difference in promotion_request.differences:
            difference:RepoInventoryDiff

            obj_difference = {  "action":difference.action, 
                                "from_inv_item": self.repo_inv_item_to_obj(difference.from_inv_item), 
                                "to_inv_item": self.repo_inv_item_to_obj(difference.to_inv_item)
                            }

            obj_differences.append(obj_difference)

        obj_status_messages = []
        for status_message in promotion_request.status_messages:
            status_message:StatusMessage

            obj_status_message = {"status_date":date_to_string(status_message.status_date), "message_token":status_message.message_token, "message_data":status_message.message_data }
            obj_status_messages.append(obj_status_message)


        ret_obj["differences"] = obj_differences
        ret_obj["status_messages"] = obj_status_messages

        return ret_obj


    def create_promotion(self, promotion_request:PromotionRequest):
        obj = self.promotion_request_to_obj(promotion_request)
        path = self.obj_path(promotion_request.id)
        if os.path.exists(path):
            PromotionRequestAlreadyExists("Promotion request:%s already exists" % promotion_request.id)

        write_dict_to_json_file(path, obj)


    def update_promotion(self, promotion_request:PromotionRequest):
        obj = self.promotion_request_to_obj(promotion_request)
        path = self.obj_path(promotion_request.id)
        if not os.path.exists(path):
            PromotionRequestAlreadyExists("Promotion request:%s does not exist" % promotion_request.id)

        write_dict_to_json_file(path, obj)


    def delete_promotion(self, id:str) -> PromotionRequest:
        path = self.obj_path(id)
        if not os.path.exists(path):
            PromotionRequestAlreadyExists("Promotion request:%s does not exist" % id)

        os.remove(path)


    def get_unpurged_promotion_history(self) -> list:
        files = os.listdir(self.data_path)
        ret_promos = []

        for file in files:
            id = file.replace(".json", "")
            ret_promos.append(self.get_promotion(id))

        return ret_promos