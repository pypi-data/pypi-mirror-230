from utah.core.bootstrap import set_app_home
set_app_home(".")

from utah.core import bootstrap
import os
os.environ["ARCHES_SVC_LOAD_NAVIGATION"] = "false"

log_path = "%s/logs" % bootstrap.get_var_data_loc()
if not os.path.exists(log_path):
    os.mkdir(log_path)


import os
import sys
import argparse

from utah.core.setup import BaseUtahInititializer
from utah.core.setup import create_directory
from utah.core.setup import InitializationException

import logging

_logger = logging.getLogger(__name__)

class UtahInitializer(BaseUtahInititializer):
    def __init__(self, data_loc:str, src_repo_loc:str, dest_repo_loc:str):
        super().__init__(src_repo_loc)

        self.data_loc = data_loc
        self.src_repo_loc = src_repo_loc
        self.dest_repo_loc = dest_repo_loc


    def initialize_file(self, path:str, data:str):
        f = open(path, 'w')
        f.write(data)
        f.close


    def prepare(self):
        create_directory("%s/authentication" % self.data_loc)
        create_directory("%s/authentication/accounts" % self.data_loc)
        create_directory("%s/authentication/tokens" % self.data_loc)
        create_directory("%s/promotion" % self.data_loc)
        create_directory("%s/authorization" % self.data_loc)
        create_directory("%s/task" % self.data_loc)
        self.initialize_file("%s/authorization/groups.json" % self.data_loc, "{}")
        self.initialize_file("%s/authorization/enrollments.json" % self.data_loc, "{}")
        self.initialize_file("%s/authorization/access_rights.json" % self.data_loc, "[]")
        create_directory("%s/profile" % self.data_loc)

        if os.path.exists(self.dest_repo_loc):
            raise InitializationException("dest_repo_loc path:[%s] already exists" % self.dest_repo_loc)

        create_directory(self.dest_repo_loc)




if __name__ == "__main__":
    # --------------------------------------------------------------------------------
    # Parse arguements
    # --------------------------------------------------------------------------------
    #parser = argparse.ArgumentParser(prog='utah.bryce.setup', description='Setup a new arches based workspace')
    #parser.add_argument('-d', '--data_path', dest='data_path', action='store', required=True, default="./data", help='Directory path for your data')
    #parser.add_argument('-s', '--source_repo_path', dest='source_repo_path', action='store', required=True, default="./sample_content", help='Directory containing sample content')  
    #parser.add_argument('-c', '--dest_content_path', dest='dest_content_path', action='store', required=True, default="./user_managed_content", help='Directory to write user managed content')

    #args = parser.parse_args()

    data_path = "%s/data" % bootstrap.get_var_data_loc()
    source_repo_path = "%s/sample_content" % bootstrap.get_app_home()
    dest_content_path = "%s/user_managed_content" % bootstrap.get_var_data_loc()

    initializer = UtahInitializer(data_path, source_repo_path, dest_content_path)

    _logger.info("Call initialize")

    initializer.initialize()

    _logger.info("finish")
