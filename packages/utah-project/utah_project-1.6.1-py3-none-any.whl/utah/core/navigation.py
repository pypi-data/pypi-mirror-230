import json
import re
from functools import lru_cache
from threading import Thread
from threading import Event
import logging
from utah.core.utilities import Locale

logger = logging.getLogger(__name__)

class NavigationLoadException(Exception):
    """ Error to be thrown when the Navigation tree cannot be loaded """
    pass

class NavigationReferenceException(Exception):
    pass

""" Class representing any navigation item with children """
class ParentNavItem():
    def __init__(self, description:str, uri:str):
        self.description = description
        self.uri=uri
        self.children=[]

    """ add a child item to this navigation item """
    def add_child(self, child):
        self.children.append(child)

    """ Method is called any time this node is added to another parent as a child """
    def child_added(self, child):
        pass

    """ Method used to add this node as a breadcrumb is being built """
    def build_breadcrumb(self, breadcrumb:list):
        breadcrumb.insert(0, self)



""" Class representing any navigation item which can be a child """
class ChildNavItem(ParentNavItem):
    def __init__(self, description:str, uri:str, parent:ParentNavItem):
        ParentNavItem.__init__(self, description, uri)
        self.parent = parent
        self.parent.add_child(self)
        self.child_added(self)


    """ Method is called any time this node is added to another parent as a child """
    def child_added(self, child):
        self.parent.child_added(child)

    
    """ Method used to add this node as a breadcrumb is being built """
    def build_breadcrumb(self, breadcrumb:list):
        ParentNavItem.build_breadcrumb(self, breadcrumb)
        self.parent.build_breadcrumb(breadcrumb)



""" Class representing the root of a navigation tree """
class RootNavItem(ParentNavItem):
    def __init__(self, description:str, uri:str, translation_map:dict={}):
        ParentNavItem.__init__(self, description, uri)
        self.uri_map = {}
        self.translation_map = translation_map


    """ Method is called any time this node is added to another parent as a child 
        In this instance it will throw an exception as that is not permitted on 
        a root """
    def child_added(self, child):
        if not child.uri == "#":
            if child.uri in self.uri_map:
                raise NavigationLoadException("Duplicate URI:[%s] found in navigation tree" % child.uri)

            self.uri_map[child.uri] = child


    @lru_cache(100)
    def get_translations(self, locale_str:str):
        ret_translations = None
        locale = Locale(locale_str)
        for locale_option in locale.options:
            if locale_option in self.translation_map:
                ret_translations = self.translation_map[locale_option]

        return ret_translations


""" Class used to represent an navigation item for display. It brings in common display elements 
    such as breadcrumbs and whether the node is to be considered selected. Node are considered selected
    when there is no break in navigation item continuity. IE: If document /a/b/c.html is being displayed
    nav items a, b, and c.html will all be considered "selected"
"""
class NavigationBean():
    def __init__(self, nav_item:ParentNavItem, breadcrumb_chain:list, locale_str=None):

        self.breadcrumb_chain = breadcrumb_chain
        self.nav_item = nav_item
        self.locale_str = locale_str

    """ Get the URI for the nav node being displayed """
    def get_uri(self):
        return self.nav_item.uri


    """ Get the description of the nav node being displayed """
    def get_description(self):
        ret_desc = self.nav_item.description
        if self.locale_str:
            translations = self.breadcrumb_chain[0].get_translations(self.locale_str)
            if translations and ret_desc in translations:
                temp_ret_desc = translations[ret_desc]
                if temp_ret_desc:
                    ret_desc = temp_ret_desc

        return ret_desc


    """ return a boolean indicating whether or not this node is to be considered selected """
    def is_selected(self):
        ret_value = False
        if self.nav_item in self.breadcrumb_chain:
            ret_value = True

        return ret_value


    """ When displaying a breadcrum this indicator is used to assert this node is representing the last in the chain
        IE: /a/b/c.html The breadcrumb will contain nodes for a and b but only c.html will return a true
    """
    def is_last_in_breadcrumb(self):
        ret_value = False
        if self.nav_item == self.breadcrumb_chain[len(self.breadcrumb_chain)-1]:
            ret_value = True

        return ret_value


    """ Indicate whether or not the node being represented by this bean has children """
    def has_children(self):
        ret_value = False
        if len(self.nav_item.children) > 0:
            ret_value = True

        return ret_value


    """ returns the children of this bean as additional NavigationBeans """
    def get_children(self):
        ret_list = []

        for child_nav_item in self.nav_item.children:
            child_bean = self.create_nav_bean(child_nav_item, self.breadcrumb_chain, self.locale_str)
            if child_bean:
                ret_list.append(child_bean)

        return ret_list


    def create_nav_bean(self, nav_item, breadcrumb_chain, locale_str):
        return NavigationBean(nav_item, breadcrumb_chain, locale_str)


""" Class representing the root of a navigation tree as a Navigation bean """
class RootNavigationBean(NavigationBean):
    def __init__(self, breadcrumb_chain:list, locale_str=None):
        NavigationBean.__init__(self, breadcrumb_chain[0], breadcrumb_chain, locale_str)


    """ Return the breadcrumb chain for this navigation bean """
    def get_breadcrumb(self):
        ret_list = []
        for nav_item in self.breadcrumb_chain:
            ret_list.append(self.create_nav_bean(nav_item, self.breadcrumb_chain, self.locale_str))

        return ret_list




class BaseNavigationService():
    def __init__(self, main_microsite:str, reload_interval_secs:int):
        self.nav_tree = None
        self.bad_tree = False
        self.main_microsite = main_microsite
        self.microsite_regex = re.compile("/([^\/]*)/?(.)*")
        self.reload_interval_secs = reload_interval_secs

        try:
            self.nav_tree = self.load_nav_tree()
        except Exception as e:
            logger.exception(e)
            self.nav_tree = RootNavItem("!Navigation Load Error!", "#", {})

        self.timer_event = Event()
        nav_loader_thread = Thread(target=BaseNavigationService.reload_nav_tree, name="navloader", args=(self, self.timer_event), daemon=True)
        nav_loader_thread.start()


    def __del__(self):
        self.timer_event.set()


    def off_time_nav_tree_load(self):
        new_nav_tree = self.load_nav_tree()
        self.nav_tree = new_nav_tree


    def reload_nav_tree(self, timer_event):
        logger.info("Start nav tree loader thread")
        keep_running = True
        while keep_running:
            event_set = timer_event.wait(self.reload_interval_secs)
            if not event_set:
                try:
                    logger.info("Attempting to load nav tree")
                    new_nav_tree = self.load_nav_tree()
                    self.nav_tree = new_nav_tree
                    logger.info("nav tree loaded")
                except Exception as e:
                    logger.error(e)
                    
            else:
                logger.info("Nav loader shutting down")
                keep_running = False

    def get_nav_tree(self):
        return self.nav_tree





    def get_node_header(self, microsite, curr_json_node):

        if not "description" in curr_json_node:
            raise NavigationLoadException("Microsite:[%s] contains a navigation node:[%s] which is missing a description" % (microsite, curr_json_node))

        if not "uri" in curr_json_node:
            raise NavigationLoadException("Microsite:[%s] contains a navigation node:[%s] which is missing a uri" % (microsite, curr_json_node))

        description = curr_json_node["description"]
        uri = curr_json_node["uri"]

        microsite = self.get_microsite_from_uri(uri, microsite)

        return (microsite, description, uri)


    def get_children(self, microsite:str, description:str, uri:str, curr_json_node:dict):
        if not "children" in curr_json_node:
            return

        children = curr_json_node["children"]

        if not type(children) == list:
            raise NavigationLoadException("Error in navigation tree for microsite:[%s], chidlren must be a list, uri:[%s], description:[%s]" % (microsite, uri, description))

        return children


    def get_microsite_from_uri(self, uri:str, parent_microsite:str):
        microsite = None
        if not (uri == "#" or uri.startswith("https://") or uri.startswith("http://")) :
            match = self.microsite_regex.match(uri)
            if not match:
                raise NavigationLoadException("Malformed uri:[%s] (pattern match failed) was found in navigation tree for microsite:[%s]" % (uri, parent_microsite))

            microsite = match.group(1)
            if not microsite:
                raise NavigationLoadException("Malformed uri:[%s] (could not locate microsite) was found in navigation tree for microsite:[%s]" % (uri, parent_microsite))
        
        return microsite


    def get_breadcrumb_chain(self, uri:str):
        matching_nav_node = None
        nav_tree = self.get_nav_tree()
        uri_map = nav_tree.uri_map

        if uri in uri_map:
            matching_nav_node = uri_map[uri]
        else:
            segs = uri.split("/")
            for i in range(len(segs), 0, -1):
                key = "/".join(segs[0:i])
                if key in uri_map:
                    matching_nav_node = uri_map[key]

        if not matching_nav_node:
            matching_nav_node = nav_tree

        chain = [] 
        curr_working_node = matching_nav_node
        while not type(curr_working_node) == RootNavItem:
            chain.insert(0, curr_working_node)
            curr_working_node = curr_working_node.parent

        chain.insert(0, curr_working_node)

        return chain


    def load_nav_tree(self):
        raise NavigationLoadException("An attempt was made to use the base class for the navigation service without extending it. Extend the base class and override the load_nav_tree() method to implement or use an existing implementation")