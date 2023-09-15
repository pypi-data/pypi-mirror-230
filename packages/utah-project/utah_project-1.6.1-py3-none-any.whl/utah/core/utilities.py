#from calendar import month
#from curses import has_extended_color_support
from email.mime import text
import json
import sys
import importlib
import sys
import time
import threading
import logging
from logging import config
from inspect import signature
import functools
from functools import lru_cache, wraps
from utah.core import bootstrap

from datetime import datetime, tzinfo
import smtplib
from email.mime.text import MIMEText
import re
from datetime import datetime
import yaml
import os
from io import StringIO
import yaml
from yaml import loader
import pytz
import re
import base64
from time import monotonic


SVC_TYPE_KEY            = "type"
SVC_MUST_IMPLEMENT_KEY  = "must_implement"
SVC_LOAD_IT_KEY         = "load_it"
SVC_CONFIG_KEY          = "config"

UTAH_STRING_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
UTAH_STRING_TIMESTAMP_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"

TZ_UTC = pytz.timezone("UTC")

APP_HOME = bootstrap.get_app_home()

class FactoryServiceException(Exception):
    pass

class DecodeError(Exception):
    pass

class ConfigurationException(Exception):
    pass


def get_class_from_string(class_string):
    parsed_class_name   = class_string.split(".")
    package_name        = ".".join(parsed_class_name[0:-2])
    full_module_name    = ".".join(parsed_class_name[0:-1])
    module_name         = parsed_class_name[len(parsed_class_name)-2]
    class_name          = parsed_class_name[len(parsed_class_name)-1]
    module              = importlib.import_module(full_module_name)
    
    retClass            = getattr(module, class_name)

    return retClass


class UtahStash():
    def __init__(self):
        self.stash = self.initialize_stash()

    def initialize_stash(self):
        ret_stash = {
            "UTAH_APP_HOME" : bootstrap.get_app_home(),
            "UTAH_VARIABLE_DATA" : bootstrap.get_var_data_loc(),
            "UTAH_TEXT_ENCODING" : bootstrap.get_text_encoding()
        }

        for k,v in os.environ.items():
            ret_stash[k] = v

        ret_stash.update(self._load_properties("%s/data/stash/plaintext_stash.txt" % bootstrap.get_var_data_loc()))
        ret_stash.update(self._load_properties("%s/data/stash/encoded_stash.txt" % bootstrap.get_var_data_loc(), True))

        return ret_stash


    def key_in_stash(self, key:str):
        return key in self.stash


    def get_stash_value(self, key:str):
        ret_value = None
        if key in self.stash:
            ret_value = self.stash[key]
        else:
            raise ConfigurationException("Could not find key:[%s] in the utah system stash %s" % (key, self.stash))

        return ret_value


    def _load_properties(self, file_path, decode_values=False):

        matcher = re.compile("([a-z,A-Z,0-9,_,-]*)=(.*)") 
        return_dict = {}
        try:
            f = open(file_path)
            line = f.readline()
            while (line):
                m = matcher.match(line)
                if m:
                    g = m.groups()
                    value = g[1]
                    if decode_values:
                        value = base64.b64decode(bytes(value, bootstrap.get_text_encoding())).decode()

                    return_dict[g[0]] = value

                else:
                    raise ConfigurationException("Error parsing stash property file: %s. Entries must be in key=value format" % file_path)

                line = f.readline()

            f.close()

        except FileNotFoundError:
            pass

        return return_dict


    def write_value(self, key:str, value:str, encoded=False):
        file_path = None
        value_to_write = None
        if not encoded:
            file_path = "%s/data/stash/plaintext_stash.txt" % bootstrap.get_var_data_loc()
            value_to_write = value
        else:
            file_path = "%s/data/stash/encoded_stash.txt" % bootstrap.get_var_data_loc()
            value_to_write = base64.b64encode(bytes(value, bootstrap.get_text_encoding())).decode()

        f = open(file_path, 'a')
        with f:
            f.write("%s=%s\n" % (key, value_to_write))
            f.close()

        self.stash = self.initialize_stash()





# STASH is lazy loaded to allow setup scripts to work and 
# set up stash files prior to attempting to use. First 
# retrival of stash will load it
STASH = None
        
def get_stash():
    global STASH
    if not STASH:
        STASH = get_class_from_string(bootstrap.get_stash_class())()

    return STASH



def dict_from_date(dt:datetime):
    return {
        "year" : dt.year,
        "month" : dt.month,
        "day" : dt.day,
        "hour" : dt.hour,
        "minute" : dt.minute,
        "second" : dt.second
    }


def date_to_string(indatetime:datetime):
    ret_string = None

    if indatetime:
        ret_string = indatetime.strftime(UTAH_STRING_TIME_FORMAT)

    return ret_string
    

def date_to_timestamp_string(indatetime:datetime):
    ret_string = None

    if indatetime:
        ret_string = indatetime.strftime(UTAH_STRING_TIMESTAMP_FORMAT)

    return ret_string


def string_to_timestamp(instr:str):
    ret_timestamp = None
    cvt_date = string_to_date(instr)
    if cvt_date:
        ret_timestamp = cvt_date.replace(tzinfo=TZ_UTC).timestamp()

    return ret_timestamp



def string_to_date(instr:str):
    ret_date = None

    if instr:
        ret_date = datetime.strptime(instr, UTAH_STRING_TIME_FORMAT)

    return ret_date


def scrolled_output(output_string):
    myos = output_string.replace("...", "~")

    for c in myos:
        if c == "~":
            time.sleep(1)
        else:
            sys.stdout.write(c)
            sys.stdout.flush()
            time.sleep(.04)
    sys.stdout.write("\n")


def get_env_variable(variable_name:str, default=None):
    ret_value = default

    if variable_name in os.environ:
        ret_value = os.environ[variable_name]

    if not ret_value:
        ConfigurationException("Could not get environment variable:%s and no default was specified")

    return ret_value


def get_dict_from_json_file(path, text_pre_processor=None):
    config_text = get_text_from_file(path)

    if text_pre_processor:
        config_text = text_pre_processor(config_text)
    try:
        config = json.loads(config_text)
    except Exception as e:
        print(config_text)
        raise e

    return config


def get_preprocessed_text_from_file(path, text_pre_processor=None):
    config_text = get_text_from_file(path)

    if text_pre_processor:
        config_text = text_pre_processor(config_text)

    return config_text


def get_dict_from_yaml_file(path, text_pre_processor=None):
    config_text = get_text_from_file(path)

    if text_pre_processor:
        config_text = text_pre_processor(config_text)

    config_io_stream = StringIO(config_text)

    config = yaml.load(config_io_stream, Loader=loader.Loader)

    return config


def startup_text_pre_processor(config_text):
    config_text = config_text.replace(r'${APP_HOME}', bootstrap.get_app_home())
    config_text = config_text.replace(r'{% trans %}', '')
    config_text = config_text.replace(r'{% endtrans %}', '')

    env_variable_tag_re = r"(\$\{\s*([a-z,A-z]\w+)\s*(,\s*('(.*?)'))?\s*\})"
    tag_regex = re.compile(env_variable_tag_re)
    match = tag_regex.search(config_text)

    while match:
        groups = match.groups()
        default_value = ""

        if groups[4]:
            default_value = groups[4]

        stash = get_stash()
        key = groups[1]

        if stash.key_in_stash(key):
            replacement_value = get_stash().get_stash_value(key)
        else:
            if default_value:
                replacement_value = default_value
            else:
                raise ConfigurationException("Found replacement token %s in the configuration but it was not available in the utah stash and no default was specified" % groups[0])

        config_text = config_text.replace(groups[0], replacement_value)

        match = tag_regex.search(config_text)

    include_tag_re = r"(\^\{\s*([^,]+)\s*(,\s*('(.*?)'))?\s*\})"
    include_tag_regex = re.compile(include_tag_re)
    match = include_tag_regex.search(config_text, )
    while match:
        groups = match.groups()
        pre_value_if_text_available = ""

        if groups[4]:
            pre_value_if_text_available = groups[4]

        file_path = groups[1]
        replacement_value = get_text_from_file(file_path)
        replacement_value = startup_text_pre_processor(replacement_value)
        if replacement_value.rstrip():
            replacement_value = pre_value_if_text_available + replacement_value
        else:
            replacement_value = ""

        config_text = config_text.replace(groups[0], replacement_value)

        match = include_tag_regex.search(config_text)



    return config_text



def get_text_from_file(path, encoding=bootstrap.get_text_encoding()):
    with open(path, 'rb') as f:
        text_bytes = f.read()
        f.close()

        ret_string = None

        try:
            ret_string = text_bytes.decode(encoding=bootstrap.get_text_encoding())
        except UnicodeDecodeError as e:
            raise DecodeError("Could not decode file:[%s] to encoding:[%s]" % (path, bootstrap.get_text_encoding()))

        return ret_string



def write_dict_to_json_file(path, obj:dict):
    with open(path, 'wb') as f:
        bytes_to_write = json.dumps(obj, indent=4, ensure_ascii=False).encode(encoding=bootstrap.get_text_encoding())
        f.write(bytes_to_write)
        f.close()



logger_config = get_dict_from_json_file(bootstrap.get_app_home() + "/config/logger_config.json", startup_text_pre_processor)
logging.config.dictConfig(logger_config)

def log_value(v):
    if not v == None:
        v = str(v)
        if len(v) > 100:
            v = v[0:50] + "..."

        v = v.replace("\n", "\\n")
        v = v.replace("\r", "\\r")
        v = v.replace("\t", "\\t")
    return v


def func_logger(func):
    level = logging.DEBUG

    def logged_func_wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        if logger.getEffectiveLevel() <= level:
            ret_value = None

            p_list = []

            sig = signature(func)

            first_param = None

            p_count = 0
            for p in sig.parameters:
                if p_count == 0:
                    first_param = p

                if not p == "self":
                    v = None
                    if p_count < len(args):
                        v = args[p_count]
                    else:
                        if p in kwargs:
                            v = kwargs[p]

                    p_list.append("%s=%s" % (p, log_value(v)))
                p_count = p_count + 1

            if first_param == "self":
                class_name = args[0].__class__.__name__
                if func.__name__ == "__init__":
                    logger.log(level, "Object<%s> Construction: %s(%s)" % (id(args[0]), class_name, ", ".join(p_list)))
                else:
                    logger.log(level, "Object<%s> Function-entry: %s.%s(%s)" % (id(args[0]), class_name, func.__name__, ", ".join(p_list)))
            else:
                logger.log(level, "Function-entry: %s(%s)" % (func.__name__, ", ".join(p_list)))

            ret_value = func(*args, **kwargs)

            if first_param == "self":
                class_name = args[0].__class__.__name__
                if not func.__name__ == "__init__":
                    logger.log(level, "Object<%s> Function-exit: %s.%s return=%s" % (id(args[0]), class_name, func.__name__, log_value(ret_value)))
            else:
                logger.log(level, "Function-exit: %s return=%s" % (func.__name__, log_value(ret_value)))
        else:
            ret_value = func(*args, **kwargs)

        return ret_value

    return logged_func_wrapper


class RWDNotFound(Exception):
    pass

class RWDInvalidKey(Exception):
    pass


class RWD():
    key_re = re.compile('^((\/[0-9,a-z,A-Z,_,-]{1,}){0,})(\/([0-9,a-z,A-Z,_,-]{1,})){1,}$')
        
    def read(self, key)->object:...
    def write(self, obj:object):...
    def delete(self, key)->object:...
    def get_all_keys(self, namespace:str='/')->list:...

    def key_parse(self, key):
        matches = RWD.key_re.match(key)
        if not matches or not matches[4]:
            raise RWDInvalidKey("key:[%s]" % key)
        
        return (matches[1], matches[4])


class ServiceFactory():
    @func_logger
    def __init__(self, configFilePath):
        logger = logging.getLogger(__name__)


        system_config_text = get_preprocessed_text_from_file(configFilePath, startup_text_pre_processor)
        system_config_text = system_config_text.replace('\r', '')
        system_config_lines = system_config_text.split('\n')
        service_config_info = []

        for  config_line in system_config_lines:
            if config_line and config_line[0] != "#":
                service_config_info.append(config_line.split('='))


        self.services = {}
        for config_load_info in service_config_info:
            (service_name, config_filepath) = config_load_info
            service_type_config = get_dict_from_json_file(config_filepath, startup_text_pre_processor)
            if not SVC_LOAD_IT_KEY in service_type_config or service_type_config[SVC_LOAD_IT_KEY]:
                logger.info("Loading service %s" % service_name)
                service_object = self.init_service_object(service_name, service_type_config)
                self.services[service_name] = service_object
            else:
                logger.info("Skipping load of service %s, load_it flag is set to false" % service_name)

    @func_logger
    def get_service_object(self, name):
        if not name in self.services:
            raise FactoryServiceException("Invalid service name  was requested name:[%s]" % name)

        return self.services[name]


    @func_logger
    def init_service_object(self, name:str, service_type_config:dict):
        if not SVC_TYPE_KEY in service_type_config:
            raise FactoryServiceException("key:[%s] was not found in the service configuration for service:[%s]" % (SVC_TYPE_KEY, name))

        if not SVC_MUST_IMPLEMENT_KEY in service_type_config:
            raise FactoryServiceException("key:[%s] was not found in the service configuration for service:[%s]" % (SVC_MUST_IMPLEMENT_KEY, name))

        if not SVC_CONFIG_KEY in service_type_config:
            raise FactoryServiceException("key:[%s] was not found in the service configuration for service:[%s]" % (SVC_CONFIG_KEY, name))


        str_svc_type    = service_type_config[SVC_TYPE_KEY]
        must_implement  = get_class_from_string(service_type_config[SVC_MUST_IMPLEMENT_KEY])
        svc_type        = get_class_from_string(str_svc_type)
        config          = service_type_config[SVC_CONFIG_KEY]

        try:
            retObj = svc_type(**config)
        except TypeError as e:
            msg = str(e)

            fld_name = msg[msg.rfind(" ")+1:]
            if msg.startswith("__init__() got an unexpected keyword argument "):
                new_msg = "Configuration for service:[%s] provided a value:[%s] that is not in the service constructor for class:[%s]" % (name, fld_name, str_svc_type)
                raise FactoryServiceException(new_msg)

            elif msg.startswith("__init__() missing 1 required positional argument: "):
                new_msg = "Configuration for service:[%s] is missing a value:[%s] that is specified in the service constructor for class:[%s]" % (name, fld_name, str_svc_type)
                raise FactoryServiceException(new_msg)

            else:
                raise Exception("Could not instantiate service:[%s] error message:[%s]", (name, str(e)))

        if not isinstance(retObj, must_implement):
            try:
                raise FactoryServiceException("Service by name:[%s] is of type:[%s] but that type needed to implement type:[%s]" % (name, self.system_config[name][SVC_TYPE_KEY], self.system_config[name][SVC_MUST_IMPLEMENT_KEY]))
            except Exception as e:
                raise FactoryServiceException("Error trying to raise an error because the implementing class does not match the required type name:[%s], config:[%s]" % (name, str(self.system_config[name])))
        return retObj

__serviceFactory        = None
__serviceFactoryLock    = threading.Lock()


@func_logger
def get_service_object(name):
    serviceFactory = get_service_factory()
    return serviceFactory.get_service_object(name)


@func_logger
def get_service_factory(configFilePath=None):
    if not configFilePath:
        configFilePath = bootstrap.get_app_home() + "/config/utah_service_config.pp_txt"

    global __serviceFactory
    if not __serviceFactory:
        __serviceFactoryLock.acquire()
        if not __serviceFactory:
            __serviceFactory = ServiceFactory(configFilePath)
        __serviceFactoryLock.release()

    return __serviceFactory

@func_logger
def configure_service_factory(configFilePath=None):
    if not configFilePath:
        raise FactoryServiceException("Attempt to use a non-standard service factory config requires a config path and none was specified")

    if __serviceFactory:
        raise FactoryServiceException("Service factory was already started, it cannot be started with a non-standard configuration")

    get_service_factory(configFilePath)



class Sendmail():
    def __init__(self, host:str, user_account:str, password:str, port:int, from_addr:str, subject:str, body_template:str):
        self.host = host
        self.user_account = user_account
        self.password = password
        self.port = port
        self.from_addr = from_addr
        self.subject = subject
        self.body_template = body_template

    def send_message(self, to_email_address, variable_data:dict):

        msg = MIMEText(str(self.body_template) % variable_data)
        msg['Subject'] = str(self.subject)
        msg['From'] = self.from_addr
        msg['To'] = to_email_address

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user_account, self.password)
            server.sendmail(self.from_addr, to_email_address, msg.as_string())



class LogEntry():
    def __init__(self, entry_number, entry_timestamp:datetime, severity:str, modulename:str, message:str):
        self.entry_number = entry_number
        self.entry_timestamp = entry_timestamp
        self.severity = severity
        self.modulename = modulename
        self.message_lines = [message]


class PastToDate(Exception):
    pass


class MaxResultsExceeded(Exception):
    def __init__(self, gathered_results):
        Exception.__init__(self)
        self.gathered_results = gathered_results


def delete_file(path:str):
    if os.path.isfile(path):
        os.remove(path)


class LogQuery():
    def __init__(self, from_timestamp:datetime=None, to_timestamp:datetime=None, severity_list:list=None, module_regex:str=None, message_regex:str=None, from_entry_number:int=None, to_entry_number:int=None, max_ret_values:int=100):
        self.from_timestamp      = from_timestamp
        self.to_timestamp        = to_timestamp
        self.severity_list  = severity_list
        self.module_regex   = None
        self.message_regex  = None
        self.from_entry_number  = from_entry_number
        self.to_entry_number    = to_entry_number
        self.max_ret_values         = max_ret_values

        if module_regex:
            self.module_regex   = re.compile(module_regex, re.IGNORECASE)

        if message_regex:
            self.message_regex  = re.compile(message_regex, re.IGNORECASE)

    def match(self, log_entry:LogEntry):
        matched = False

        if ((self.to_timestamp) and log_entry.entry_timestamp > self.to_timestamp):
            raise PastToDate()

        if ((not self.from_timestamp) or log_entry.entry_timestamp >= self.from_timestamp) and \
            ((not self.severity_list) or log_entry.severity in self.severity_list) and \
            ((not self.module_regex) or self.module_regex.match(log_entry.modulename)) and \
            ((not self.message_regex) or self.line_match(log_entry.message_lines)) and \
            ((not self.from_entry_number) or log_entry.entry_number >= self.from_entry_number) and \
            ((not self.to_entry_number) or log_entry.entry_number <= self.to_entry_number):
            matched = True

        return matched

    def line_match(self, message_lines):
        ret_value = False
        for line in message_lines:
            if self.message_regex.match(line):
                ret_value = True
                break

        return ret_value



class LogReader():
    def __init__(self, file_name:str, header_match_regex:str, datetime_group:int, datetime_format:str, severity_group:int, module_group:int, text_group:int, max_query_results:int=100):
    #(20[0-9]{2}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2} [\+,\-][0-9]{4}) (INFO|DEBUG|WARN|ERROR|FATAL) ([^\s\\])* (.*)
        self.file_name = file_name
        self.header_match_regex = header_match_regex
        self.datetime_group = datetime_group
        self.datetime_format = datetime_format
        self.severity_group = severity_group
        self.module_group = module_group
        self.text_group = text_group
        self.max_query_results = max_query_results

    def get_log_entries(self, log_query:LogQuery):

        header_matcher = re.compile(self.header_match_regex)

        f = open(self.file_name, 'r')
        input_line = f.readline()

        ret_list = []
        curr_entry = None
        entry_number = 0
        keep_reading = True
        try:
            while input_line and keep_reading:
                match = header_matcher.match(input_line)
                if match:
                    entry_number = entry_number + 1
                    if curr_entry:
                        if log_query.match(curr_entry):
                            ret_list_len = len(ret_list)
                            if ret_list_len < self.max_query_results:
                                if ret_list_len < log_query.max_ret_values:
                                    ret_list.append(curr_entry)
                                else:
                                    keep_reading = False
                            else:
                                raise MaxResultsExceeded(ret_list)

                    entry_timestamp = datetime.strptime(match.group(self.datetime_group), self.datetime_format)

                    curr_entry = LogEntry(entry_number, entry_timestamp, match.group(self.severity_group), match.group(self.module_group), match.group(self.text_group))

                else:
                    if curr_entry:
                        curr_entry.message_lines.append(input_line[:-1])

                input_line = f.readline()

        except PastToDate as e:
            curr_entry = None

        finally:
            if curr_entry and log_query.match(curr_entry):
                ret_list_len = len(ret_list)
                if ret_list_len < self.max_query_results:
                    if ret_list_len < log_query.max_ret_values:
                        ret_list.append(curr_entry)
                else:
                    raise MaxResultsExceeded(ret_list)

        f.close()

        return ret_list



class Locale():
    def __init__(self, locale_str:str):
        self.options = []
        segs = locale_str.split("_")
        for i in range(len(segs), 0, -1):
            self.options.append("_".join(segs[0:i]))

        self.options.append("")





class PlainObjConverter():
    def __init__(self, converters:list):
        self.converters_from_primative = {}

        for converter in converters:
            (key, func_from_primative) = converter
            self.converters_from_primative[key] = func_from_primative


    def convert_from_primative(self, primative_obj):
        return self._convert_from_primative(primative_obj)


    def _single_convert_from_primative(self, obj, full_key, key=None):
        ret_obj = None

        if obj:
            full_key_str = "/".join(full_key)
            if full_key_str in self.converters_from_primative:
                ret_obj = self.converters_from_primative[full_key_str](obj)
            else:
                ret_obj = obj

        return ret_obj



    def _convert_from_primative(self, obj, full_key=[], key=None):
        ret_obj = None

        if key:
            full_key.append(key)

        if isinstance(obj, dict):
            tmp_obj = {}

            for attr_key in obj.keys():
                next_obj = obj[attr_key]
                cvt_obj = self._convert_from_primative(next_obj, full_key, attr_key)
                tmp_obj[attr_key] = cvt_obj

            ret_obj = self._single_convert_from_primative(tmp_obj, full_key, None)

        elif isinstance(obj, list):
            ret_obj = []

            for next_obj in obj:
                ret_obj.append(self._convert_from_primative(next_obj, full_key, None))

        else:
            ret_obj = self._single_convert_from_primative(obj, full_key, key)

        if key:
            del full_key[len(full_key)-1]

        return ret_obj


def lru_cache_with_ttl(maxsize=128, typed=False, ttl=60):
    """Least-recently used cache with time-to-live (ttl) limit."""

    class Result:
        __slots__ = ('value', 'death')

        def __init__(self, value, death):
            self.value = value
            self.death = death

    def decorator(func):
        @lru_cache(maxsize=maxsize, typed=typed)
        def cached_func(*args, **kwargs):
            value = func(*args, **kwargs)
            death = monotonic() + ttl
            return Result(value, death)

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            if result.death < monotonic():
                result.value = func(*args, **kwargs)
                result.death = monotonic() + ttl
            return result.value

        wrapper.cache_clear = cached_func.cache_clear
        return wrapper

    return decorator