import utah
from utah.core.bootstrap import set_app_home
import re

import os
os.environ["ARCHES_SVC_LOAD_NAVIGATION"] = "false"

def find_home(key_item):
    ret_path = None
    curr_path=os.path.abspath(__file__)
    curr_path = os.path.dirname(curr_path)
    last_path = ""

    while not last_path == curr_path and not ret_path:
        last_path = curr_path
        with os.scandir(curr_path) as dirs:
            for entry_in_dirs in dirs:
                if key_item == entry_in_dirs.name:
                    ret_path = curr_path
                    break
        if not ret_path:
            curr_path = os.path.abspath("%s/.." % curr_path)

    return ret_path


from utah.core.bootstrap import get_app_home
from glob import glob
import argparse
import shutil
import sys
import logging

def file_text_replacement(input_file, replacements):
    f=open(input_file, "r")
    text = f.read()
    f.close()

    for replacement in replacements:
        text = text.replace(replacement["old_value"], replacement["new_value"])
    
    f=open(input_file, "w")
    f.write(text)
    f.close

def find_line(input_file, key):

    ret_value = None
    f=open(input_file, "r")
    text = f.readline()
    while text:
        text = text[:-1]
        if not text.find(key) == -1:
            ret_value = text
            break

        text = f.readline()
    f.close()

    return ret_value


if __name__ == "__main__":
    _logger = logging.getLogger(__name__)

    main_logger = logging.getLogger("__main__")
    for handler in main_logger.handlers:
        _logger.addHandler(handler)

    for log_filter in main_logger.filters:
        _logger.addHandler(log_filter)

    _logger.setLevel(main_logger.getEffectiveLevel())




    # --------------------------------------------------------------------------------
    # Parse arguements
    # --------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Setup a new arches based workspace')
    parser.add_argument('--output_dir', dest='output_dir', action='store', default=".", help='Directory path for your new workspace')  
    parser.add_argument('--org_abbr', dest='org_abbr', action='store', required=True, help='Abbreviation for your organization (Used in file pathing)')  
    parser.add_argument('--app_abbr', dest='app_abbr', action='store', required=True, help='Abbreviation for your application name (Used in file pathing)')  
    parser.add_argument('--author', dest='author', action='store', required=True, help='Name of the application author')
    parser.add_argument('--short_desc', dest='short_desc', action='store', required=True, help='Short description of the application')

    args = parser.parse_args()


    # --------------------------------------------------------------------------------
    # Setup needed variables
    # --------------------------------------------------------------------------------

    arches_version_re = re.compile('version=([\'|"])(.*)\1', re.IGNORECASE)

    
    item_list = [
        "config",
        "server_config",
        "static",
        "templates",
        "sample_content",
        "arches-bootstrap.py",
        "setup.py",
        "babel.cfg",
        ".gitignore"
    ]

    empty_dirs = [
        "logs"
    ]

    setup_template = """
from setuptools import setup, find_packages

setup(name='%(app_abbr)s',
      version='0.1',
      description='%(short_desc)s',
      author='%(author)s',
      python_requires='>3.6',
      packages=['%(org_abbr)s.%(app_abbr)s'
                ],
      install_requires=[
          'utah_project==%(utah_version)s'
      ],
      include_package_data=True,
      zip_safe=False
      )
"""

    source_path = find_home("venv") + "/venv"

    python_project_path = find_home("site-packages") + "/site-packages"

    replacements = [
        {"input_file":"config/application/services/blueprint_modules.pp_json", 
        "replacements":[
            {"old_value":"utah.arches.web_blueprints.myapp", "new_value":"%s.%s.flask_blueprint" % (args.org_abbr, args.app_abbr)}
        ]},
        {"input_file":"server_config/centos8/etc/httpd/conf.d/%s-python-wsgi.conf" % args.app_abbr, 
        "replacements":[
            {"old_value":"arches", "new_value":args.app_abbr},
            {"old_value":"utah", "new_value":args.org_abbr}
        ]},
        {"input_file":"server_config/centos8/etc/profile.d/%s_%s_profile.sh" % (args.org_abbr, args.app_abbr), 
        "replacements":[
            {"old_value":"arches", "new_value":args.app_abbr},
            {"old_value":"utah", "new_value":args.org_abbr}
        ]},
        {"input_file":"server_config/centos8/build_script.sh", 
        "replacements":[
            {"old_value":"<<org>>", "new_value": args.org_abbr},
            {"old_value":"<<app>>", "new_value": args.app_abbr},
            {"old_value":"<<author>>", "new_value": args.author},
            {"old_value":"<<short_desc>>", "new_value": args.short_desc}
        ]}
    ]

    renames = [
        {"old_name":"server_config/centos8/etc/httpd/conf.d/arches-python-wsgi.conf", "new_name":"server_config/centos8/etc/httpd/conf.d/%s-python-wsgi.conf" % args.app_abbr},
        {"old_name":"server_config/centos8/etc/profile.d/utah_arches_profile.sh", "new_name":"server_config/centos8/etc/profile.d/%s_%s_profile.sh" % (args.org_abbr, args.app_abbr)},
        {"old_name":"arches-bootstrap.py", "new_name":"%s-bootstrap.py" % args.app_abbr}
    ]


    # --------------------------------------------------------------------------------
    # Copy workspace
    # --------------------------------------------------------------------------------
    for item in item_list:

        copy_source = source_path + "/" + item
        copy_dest = args.output_dir + "/" + item

        _logger.info("Copy %s to %s" % (copy_source, copy_dest))

        if os.path.isdir(copy_source):
            shutil.copytree(copy_source, copy_dest)
        elif os.path.isfile(copy_source):
            shutil.copyfile(copy_source, copy_dest)



    # --------------------------------------------------------------------------------
    # Create needed empty directories
    # --------------------------------------------------------------------------------
    empty_dirs.append(args.org_abbr)
    empty_dirs.append(args.org_abbr + "/" + args.app_abbr)


    for empty_dir in empty_dirs:
        new_dir = args.output_dir + "/" + empty_dir
        _logger.info("Create empty directory: %s" % new_dir)
        os.mkdir(new_dir)

    # --------------------------------------------------------------------------------
    # Create customizable flask blueprint
    # --------------------------------------------------------------------------------
    shutil.copyfile(python_project_path + "/utah/arches/web_blueprints/myapp.py", "%s/%s/%s/flask_blueprint.py" % (args.output_dir, args.org_abbr, args.app_abbr))


    # --------------------------------------------------------------------------------
    # Create setup.py
    # --------------------------------------------------------------------------------
    needed_values = {
        "org_abbr" : args.org_abbr,
        "app_abbr" : args.app_abbr,
        "author" : args.author,
        "short_desc" : args.short_desc,
        "utah_version" : utah.__version__
    }

    setup_program = setup_template % needed_values

    f=open(args.output_dir + "/setup.py", "w")
    f.write(setup_program)
    f.close


    # --------------------------------------------------------------------------------
    # Rename files
    # --------------------------------------------------------------------------------
    for rename in renames:
        src="%s/%s" % (args.output_dir, rename["old_name"])
        dest="%s/%s" % (args.output_dir, rename["new_name"])
        os.rename(src, dest)

    # --------------------------------------------------------------------------------
    # Process value replacements in files
    # --------------------------------------------------------------------------------
    for file_replacement in replacements:
        file_text_replacement(args.output_dir + "/" + file_replacement["input_file"], file_replacement["replacements"])


    shutil.copyfile("%s/config/utah_service_config_fs.pp_txt" % args.output_dir, "%s/config/utah_service_config.pp_txt" % args.output_dir)

    bootstrap_name = "%s-bootstrap.py" % args.app_abbr

    app_home = os.path.abspath(find_home(bootstrap_name))

    set_app_home(app_home)

    from utah.impl.zion.setup import UtahInitializer
    
    ui = UtahInitializer(dest_repo_loc="%s/user_managed_content" % args.output_dir , data_loc="%s/data" % args.output_dir, src_repo_loc="%s/sample_content" % args.output_dir)
    
    ui.initialize()