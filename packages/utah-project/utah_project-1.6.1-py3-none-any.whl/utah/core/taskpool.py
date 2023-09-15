from threading import Thread
from threading import Condition
from threading import Lock
from datetime import datetime
from uuid import uuid4
import logging
import time
from functools import lru_cache
from utah.core.utilities import date_to_string
from utah.core.utilities import string_to_date

WORK_ITEM_STATUS_QUEUED=1
WORK_ITEM_STATUS_PROCESSING=2
WORK_ITEM_STATUS_COMPLETED=3
WORK_ITEM_STATUS_COMPLETED_WITH_ISSUES=4
WORK_ITEM_STATUS_ERROR=5
WORK_ITEM_STATUS_TIMEOUT=6

logger = logging.getLogger(__name__)

class LogEntry:
    def __init__(self, log_entry:str, log_entry_values:dict=dict(), log_datetime:datetime=None):
        if log_datetime:
            self.log_datetime = log_datetime
        else:
            self.log_datetime = datetime.utcnow()

        self.log_entry_values = log_entry_values
        self.log_entry = log_entry



class WorkItemStatus:
    def __init__(self, 
        id=None, 
        status=WORK_ITEM_STATUS_QUEUED, 
        errors_found=False,
        initiation_date=datetime.utcnow(), 
        start_date=None, 
        finish_date=None, 
        tags=dict(), 
        log_entries=list()) -> None:

        if id==None:
            self.id = str(uuid4())
        else:
            self.id = id

        self.status:int = status
        self.errors_found = errors_found
        self.initiation_date:datetime = initiation_date
        self.start_date:datetime = start_date
        self.finish_date:datetime = finish_date
        self.tags:dict = tags

        self.log_entries:list = []
        for log_entry in log_entries:
            self.log_entries.append(LogEntry(**log_entry))


def dict_to_status(status_dict:dict)->WorkItemStatus:
    status_dict['initiation_date'] = string_to_date(status_dict['initiation_date'])
    status_dict['start_date'] = string_to_date(status_dict['start_date'])
    status_dict['finish_date'] = string_to_date(status_dict['finish_date'])
    log_entries = status_dict['log_entries']

    for i in range(0, len(status_dict['log_entries'])):
        log_entries[i]['log_datetime'] = string_to_date(log_entries[i]['log_datetime'])

    return WorkItemStatus(**status_dict)


def status_to_dict(status:WorkItemStatus)->dict:
    ret_dict = {}

    ret_dict['id'] = status.id
    ret_dict['status'] = status.status
    ret_dict['errors_found'] = status.errors_found
    ret_dict['initiation_date'] = date_to_string(status.initiation_date)
    ret_dict['start_date'] = date_to_string(status.start_date)
    ret_dict['finish_date'] = date_to_string(status.finish_date)
    ret_dict['tags'] = status.tags

    log_entries = []

    ret_dict['log_entries'] = log_entries

    for log_entry in status.log_entries:
        log_entry:LogEntry
        log_entry_dict = {}
        log_entry_dict['log_datetime'] = date_to_string(log_entry.log_datetime)
        log_entry_dict['log_entry_values'] = log_entry.log_entry_values
        log_entry_dict['log_entry'] = log_entry.log_entry

        log_entries.append(log_entry_dict)

    return ret_dict

class WorkItem:
    def __init__(self, tags=dict()) -> None:
        self.work_item_status = WorkItemStatus(tags=tags)
        self.processing_pool:ProcessingPool = None

    def set_processing_pool(self, processing_pool):
        self.processing_pool:ProcessingPool = processing_pool

    def change_status(self, new_status:int):
        self.work_item_status.status = new_status
        self.processing_pool.write_work_item_status(self.work_item_status)

    def add_log_entry(self, log_entry:str, log_entry_values:dict={}):
        if not self.processing_pool.task_timed_out(self.work_item_status):
            self.work_item_status.log_entries.append(LogEntry(log_entry, log_entry_values))
            self.processing_pool.write_work_item_status(self.work_item_status)
        else:
            raise TimeoutError()


    def execute(self):...



class WorkItemStatusFilter():
    def match(self, work_item_status:WorkItemStatus)->bool:...



class ProcessingPool:
    def __init__(self, total_threads:int, gc_secs:int, status_retention_days:int, upd_timeout_secs:int, task_timeout_secs:int):
        self.running = True
        self.work_list_lock = Condition()
        self.work_items = []
        self.threads = []
        self.gc_secs = gc_secs
        self.status_retention_secs = status_retention_days*24*60*60
        self.task_timeout_secs = task_timeout_secs
        self.upd_timeout_secs = upd_timeout_secs
        self.last_ttl_hash = 0

        self.gc_thread = Thread(target=self._collect_garbage,daemon=True)
        self.gc_thread.start()

        for x in range(0, total_threads):
            my_thread = Thread(target=self.process_work,daemon=True)
            my_thread.start()
            self.threads.append(my_thread)


    def process_work(self):
        while self.running:
            with self.work_list_lock:
                self.work_list_lock.wait_for(self.an_item_is_available)
                work_item = self.get_an_available_item()

            try:
                work_item.work_item_status.status = WORK_ITEM_STATUS_PROCESSING
                work_item.work_item_status.start_date = datetime.utcnow()
                self.write_work_item_status(work_item.work_item_status)

                work_item.execute()
                if not work_item.work_item_status.errors_found:
                    work_item.work_item_status.status = WORK_ITEM_STATUS_COMPLETED
                else:
                    work_item.work_item_status.status = WORK_ITEM_STATUS_COMPLETED_WITH_ISSUES
                    
                work_item.work_item_status.finish_date = datetime.utcnow()
                self.write_work_item_status(work_item.work_item_status)

            except TimeoutError as e:
               work_item.work_item_status.status = WORK_ITEM_STATUS_TIMEOUT
               work_item.work_item_status.finish_date = datetime.utcnow()
               self.write_work_item_status(work_item.work_item_status)


            except Exception as e:
                work_item.work_item_status.status = WORK_ITEM_STATUS_ERROR
                work_item.work_item_status.finish_date = datetime.utcnow()
                self.write_work_item_status(work_item.work_item_status)

                logger.exception(e)


    def an_item_is_available(self):
        ret_value = False
        if len(self.work_items) > 0:
            ret_value = True

        return ret_value


    def get_an_available_item(self):
        return self.work_items.pop(0)


    def add_work_item(self, work_item:WorkItem):
        with self.work_list_lock:
            work_item.processing_pool = self
            self.work_items.append(work_item)
            self.work_list_lock.notify()
            self.write_work_item_status(work_item.work_item_status)


    def write_work_item_status(self, work_item_status:WorkItemStatus):
        self.write_work_item_status_io(work_item_status)


    def read_work_item_status(self, id)->WorkItemStatus:
        return self.read_work_item_status_io(id)
    

    def task_timed_out(self, status:WorkItemStatus, curr_time:datetime=None)->bool:
        ret_status = False
        if not curr_time:
            curr_time = datetime.utcnow()

        idx = len(status.log_entries)-1
        if idx > -1:
            td = curr_time - status.log_entries[idx].log_datetime

            if td.total_seconds() >= self.upd_timeout_secs:
                ret_status = True
            else:
                td = curr_time - status.start_date

                if td.total_seconds() >= self.task_timeout_secs:
                    ret_status = True

        return ret_status


    def _collect_garbage(self):
        while self.running:
            time.sleep(self.gc_secs)
            logger.info("gc")
            id = None
            try:
                curr_time = datetime.utcnow()
                all_ids = self.get_all_work_item_ids_io()
                for id in all_ids:
                    status = self.read_work_item_status_io(id)

                    if status.status == WORK_ITEM_STATUS_PROCESSING:
                        if self.task_timed_out(status, curr_time):
                            status.status = WORK_ITEM_STATUS_TIMEOUT
                            status.finish_date = datetime.utcnow()
                            self.write_work_item_status_io(status)

                    elif status.status > WORK_ITEM_STATUS_PROCESSING:
                        td = curr_time - status.finish_date

                        if td.total_seconds() >= self.status_retention_secs:
                            self.del_work_item_status_io(status.id)
            except Exception as e:
                logger.error("GC error on id:%s" % id)
                logger.exception(e)


    def get_work_item_statuses(self, work_item_status_filter:WorkItemStatusFilter):
        ids = self.get_all_work_item_ids_io()
        ret_status_list = []

        for id in ids:
            work_item_status:WorkItemStatus = self.read_work_item_status(id)
            if work_item_status_filter.match(work_item_status):
                ret_status_list.append(work_item_status)

        return ret_status_list


    def write_work_item_status_io(self, work_item_status:WorkItemStatus)->None:...
    def read_work_item_status_io(self, id:str)->WorkItemStatus:...
    def del_work_item_status_io(self, id:str)->WorkItemStatus:...
    def get_all_work_item_ids_io(self)->list:...