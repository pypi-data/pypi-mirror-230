from utah.core.bootstrap import set_app_home
set_app_home(".")

import pymongo
import os
import argparse

from utah.core import bootstrap
import os
os.environ["ARCHES_SVC_LOAD_NAVIGATION"] = "false"

log_path = "%s/logs" % bootstrap.get_var_data_loc()
if not os.path.exists(log_path):
    os.mkdir(log_path)

from utah.core.setup import BaseUtahInititializer
from utah.core.setup import InitializationException
from utah.core.utilities import get_stash
from utah.core.utilities import date_to_string
from datetime import datetime

from utah.core.setup import DEPLOY_MODEL_NONE
from utah.core.setup import DEPLOY_MODEL_DEV_PROD
from utah.core.setup import DEPLOY_MODEL_DEV_UAT_PROD

import logging
_logger = logging.getLogger(__name__)



class UtahInitializer(BaseUtahInititializer):
    def __init__(self, src_repo_loc:str, mongo_admin_url:str, mongo_app_url:str, db_purpose:str, deploy_model:int):
        super().__init__(src_repo_loc, deploy_model)

        self.mongo_admin_url = mongo_admin_url
        self.mongo_app_url = mongo_app_url
        self.db_purpose = db_purpose

    def create_database(self):
        self.mongo_client = pymongo.MongoClient(self.mongo_admin_url)
        self.db_name = "%s_arches_app_db" % self.db_purpose

        _logger.info(self.mongo_client.list_database_names())
        if self.db_name in self.mongo_client.list_database_names():
            raise InitializationException("Database %s already exists" % self.db_name)

        mydb = self.mongo_client[self.db_name]
        coll = mydb["setup_info"]
        coll.insert_one({
            "database_type" : self.db_purpose,
            "setup_date" : date_to_string(datetime.utcnow())
        })
        


    def prepare(self):
        stash = get_stash()

        self.create_database()

        stash.write_value("MONGO_COMMON_CONNECTION_URL", self.mongo_app_url, True)
        stash.write_value("MONGO_DOWNSTREAM_CONNECTION_URL", self.mongo_app_url, True)
        stash.write_value("MONGO_LOCAL_CONNECTION_URL", self.mongo_app_url, True)

        stash.write_value("MONGO_COMMON_APP_DB", self.db_name, True)
        stash.write_value("MONGO_DOWNSTREAM_APP_DB", self.db_name, True)
        stash.write_value("MONGO_LOCAL_APP_DB", self.db_name, True)



if __name__ == "__main__":
    #mongodb://mongoadmin:secret@docker_bridge:27018/?authMechanism=DEFAULT&tls=false

    parser = argparse.ArgumentParser(description='Setup a new arches based workspace')
    parser.add_argument('--mongo_admin_url', dest='mongo_admin_url', action='store', required=True, help='Mongo admin url')
    parser.add_argument('--mongo_app_url', dest='mongo_app_url', action='store', required=True, help='Mongo application url')
    parser.add_argument('--db_purpose', dest='db_purpose', action='store', required=True, choices=["cmn", "sta", "dev", "uat", "prd"], help='Purpose for the database being populated')
    parser.add_argument('--deploy_model', dest='deploy_model', action='store', required=True, choices=["none", "dev_prod", "dev_uat_prod"], help='Deployment pattern for the database infrastructure')
    args = parser.parse_args()


    config_path = bootstrap.get_app_home() + "/config/utah_service_config.pp_txt"
    f = open(config_path)
    cfg = f.read()
    f.close()

    if cfg.find("/bryce/") == -1:
        raise Exception("System is not currently in bryce configuration. Confirm the correct utah_service_config file is in place")

    source_repo_path = bootstrap.get_app_home() + "/sample_content"

    if args.deploy_model == "none":
        deploy_model = DEPLOY_MODEL_NONE
    elif args.deploy_model == "dev_prod":
        deploy_model = DEPLOY_MODEL_DEV_PROD
    elif args.deploy_model == "dev_uat_prod":
        deploy_model = DEPLOY_MODEL_DEV_UAT_PROD

    initializer = UtahInitializer(source_repo_path, args.mongo_admin_url, args.mongo_app_url, args.db_purpose, deploy_model)

    _logger.info("Call initialize")

    initializer.initialize()

    _logger.info("finish")
