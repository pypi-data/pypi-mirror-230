import logging
from utah.core.navigation import NavigationLoadException
from utah.impl.bryce.utilities import ConnectionDefinition
import json
from utah.core.navigation import RootNavItem, ParentNavItem, ChildNavItem, BaseNavigationService


logger = logging.getLogger(__name__)

class NavigationService(BaseNavigationService):
    def __init__(self, mongo_db_info:dict, main_microsite:str="main", reload_interval_secs:int=900, nav_path_pattern:str="/%s/__system/navigation.json"):

        self.nav_path_pattern = nav_path_pattern

        self.conn_def:ConnectionDefinition = ConnectionDefinition(**mongo_db_info)

        BaseNavigationService.__init__(self, main_microsite, reload_interval_secs)


    def load_nav_tree(self):
        (raw_tree, raw_translations) = self.__load_raw_nav_tree(self.main_microsite)
        
        (microsite, description, uri) = self.get_node_header(self.main_microsite, raw_tree)

        if microsite != self.main_microsite:
            raise NavigationLoadException("Home uri's:[%s] microsite does not match microsite of navigation tree:[%s]" % (uri, self.main_microsite))

        translations = {}
        if raw_translations:
            self.add_raw_translations(translations, raw_translations)

        navItem = RootNavItem(raw_tree["description"], uri, translations)

        if "children" in raw_tree:
            self.process_children(microsite, navItem, raw_tree["children"], translations)

        return navItem

    def add_raw_translations(self, translations, raw_translations):
        for locale_key in raw_translations.keys():
            translation_table = None
            locales_raw_translations = raw_translations[locale_key]
            if locale_key in translations:
                translation_table = translations[locale_key]
            else:
                translation_table = {}
                translations[locale_key] = translation_table

            for base_text in locales_raw_translations.keys():
                translation_text = locales_raw_translations[base_text]

                if not base_text in translation_table:
                    translation_table[base_text] = translation_text

    def __load_raw_nav_tree(self, microsite:str, main_microsite=False):
        try:
            doc_uri     = self.nav_path_pattern % microsite
            doc         = self.conn_def.get_database()["content"].find_one({"uri":doc_uri, "item_type":3})
            if not doc:
                raise NavigationLoadException("Could not find navigation document:[%s]" % doc_uri)

            raw_tree    = json.loads(doc["text"])

            raw_translations = None
            if "translations" in raw_tree:
                raw_translations = raw_tree["translations"]
            else:
                raw_translations = {}

        except Exception as e:
            if main_microsite:
                raise NavigationLoadException("Malformed json navigation for microsite:[%s]" % microsite)
            else:
                raise e

        return (raw_tree, raw_translations)


    def process_children(self, microsite, curr_nav_item:ParentNavItem, raw_children:list, translations):
        for raw_child in raw_children:
            raw_to_process = raw_child
            microsite_being_processed = microsite

            if "microsite" in raw_child:
                microsite_being_processed = raw_child["microsite"]
                try:
                    raw_to_process = None
                    raw_translations = None
                    (raw_to_process, raw_translations) = self.__load_raw_nav_tree(microsite_being_processed)
                    if raw_translations:
                        self.add_raw_translations(translations, raw_translations)
                except FileNotFoundError as e:
                    logger.warning("Could not locate navigation.yaml for microsite:[%s]" % microsite_being_processed)
                    pass

            if raw_to_process:
                (child_microsite,  child_description, child_uri) = self.get_node_header(microsite, raw_to_process)
                child_nav_item = ChildNavItem(child_description, child_uri, curr_nav_item)

                if "children" in raw_to_process:
                    self.process_children(microsite_being_processed, child_nav_item, raw_to_process["children"], translations)

        return