from utah.impl.zion.utilities import RWD
from utah.core.taskpool import ProcessingPool as CoreProcessingPool
from utah.core.taskpool import WorkItemStatus
from utah.core.taskpool import dict_to_status
from utah.core.taskpool import status_to_dict


class ProcessingPool(CoreProcessingPool, RWD):
    def __init__(self, total_threads:int, gc_secs:int, status_retention_days:int, upd_timeout_secs:int, task_timeout_secs:int, base_path:str):
        CoreProcessingPool.__init__(self, total_threads, gc_secs, status_retention_days, upd_timeout_secs, task_timeout_secs)
        RWD.__init__(self, base_path)


    def _build_key(self, id):
        return "/" + id


    def write_work_item_status_io(self, work_item_status:WorkItemStatus):
        write_dict = status_to_dict(work_item_status)
        write_dict['key'] = self._build_key(work_item_status.id)
        self.write(write_dict)


    def read_work_item_status_io(self, id:str)->WorkItemStatus:
        status_dict = self.read(self._build_key(id))
        del status_dict['key']
        return dict_to_status(status_dict)


    def del_work_item_status_io(self, id:str)->WorkItemStatus:
        self.delete(self._build_key(id))


    def get_all_work_item_ids_io(self)->list:
        ret_ids = []
        all_keys = self.get_all_keys()

        for key in all_keys:
            ret_ids.append(key[1:])

        return ret_ids


