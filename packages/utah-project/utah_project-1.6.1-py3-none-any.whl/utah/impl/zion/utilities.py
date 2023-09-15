from utah.core.utilities import RWD as CoreRWD, RWDInvalidKey, RWDNotFound, DecodeError
from utah.core import bootstrap
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)



class RWD(CoreRWD):
    encoding=bootstrap.get_text_encoding()

    def __init__(self, base_path) -> None:
        self.base_path = base_path


    def get_path(self, key):
        return "%s%s.json" % (self.base_path, key)


    def read(self, key):
        self.key_parse(key)
        path = self.get_path(key)

        with open(path, 'rb') as f:
            text_bytes = f.read()
            f.close()

            file_string = None

            try:
                file_string = text_bytes.decode(encoding=bootstrap.get_text_encoding())

                ret_obj = json.loads(file_string)

            except FileNotFoundError:
                raise RWDNotFound()
            
            except Exception as e:
                logger.exception(e)
                raise e

        return ret_obj

    def assure_namespace(self, namespace):
        path = self.base_path + namespace
        pathobj = Path(path)
        if not pathobj.is_dir():
            pathobj.mkdir( parents=True, exist_ok=True )


    def write(self, obj):
        if 'key' in obj:
            key = obj['key']
        else:
            raise RWDInvalidKey('id attribute missing from object')

        (namespace, id) = self.key_parse(key)
        if namespace:
            self.assure_namespace(namespace)

        path = self.get_path(key)

        with open(path, 'wb') as f:
            bytes_to_write = json.dumps(obj, indent=4, ensure_ascii=False).encode(encoding=bootstrap.get_text_encoding())
            f.write(bytes_to_write)
            f.close()


    def delete(self, key):
        (namespace, id) = self.key_parse(key)

        path = self.get_path(key)
        os.remove(path)

        if namespace:
            name_space_path = self.base_path + namespace
            with os.scandir(name_space_path) as it:
                if not any(it):
                    pathobj = Path(name_space_path)
                    pathobj.rmdir()

    def get_all_keys(self, namespace='/'):
        curr_path = namespace
        ret_keys = []
        self.accum_keys(curr_path, ret_keys)

        return ret_keys

    def accum_keys(self, path, keys):
        working_path = path
        if working_path == '/':
            working_path = ""

        filenames = os.listdir(self.base_path + path)

        for filename in filenames:            
            if os.path.isdir(self.base_path + path + filename):
                next_path = path + filename
                self.accum_keys(next_path, keys)
            else:
                keys.append(working_path + "/" + filename.replace('.json', ''))

