#
# Downstream services require knowlege of 
# the apps home directory to load config
# This must be done prior to imports to assure 
# logging works properly.
#
import os
from utah.core.bootstrap import set_app_home
set_app_home(os.path.dirname(__file__))

# Assures the logger gets configured before any logging is done
import utah.core.utilities


# Perform remaining imports
import logging
from flask import Flask, render_template, session, request, g
from utah.core.authorize import ForbiddenException
from utah.core.authorize import UnauthorizedException
from utah.core.utilities import get_service_object
from utah.arches.webtools import UserAuthorizationBean
from utah.arches.webtools import AuthorizationRootNavigationBean
from utah.arches.webtools import get_user_id
from flask import before_render_template
from utah.arches.webtools import SkinService
from utah.arches.webtools import LayoutException
from utah.arches.webtools import LayoutNoMetadataDefinition
from utah.core.content import BaseContentService
from flask_babel import Babel, format_datetime
from utah.core.content import EHTMLDoc
from utah.core.content import METADATA_DOC_DIR
from utah.core.content import METADATA_DOC_NAME
from utah.core.utilities import delete_file
from flask_babel import format_datetime as babel_format_datetime
from utah.core.bootstrap import get_var_data_loc

logger = logging.getLogger(__name__)
if not __name__ == "__main__":
    main_logger = logging.getLogger("__main__")
    for handler in main_logger.handlers:
        logger.addHandler(handler)

    for log_filter in main_logger.filters:
        logger.addHandler(log_filter)

    logger.setLevel(main_logger.getEffectiveLevel())


# -----------------------------------------------------------------------------------
# admin_info.txt contains the username and installation generated password 
# of the arches admin account. On startup this information is removed for security 
# purposes.
# -----------------------------------------------------------------------------------
admin_info_path = "%s/%s/%s" % (get_var_data_loc(), "data", "admin_info.txt")
delete_file(admin_info_path)



content_service:BaseContentService = get_service_object("content")
nav_service = get_service_object("navigation")
authorization_service = get_service_object("uri_authorization")
layout_service = get_service_object("layout")
flask_config = get_service_object("flask_config")

logger.info("Instantiating flask app:[%s]" % __name__)
application = Flask(__name__)


application.jinja_env.globals.update(**flask_config.jinja_addl_functions())
babel = Babel(application)

application.config["BABEL_DEFAULT_LOCALE"] = flask_config.default_locale
application.config["BABEL_DEFAULT_TIMEZONE"] = flask_config.default_timezone
application.config["BABEL_TRANSLATION_DIRECTORIES"] = flask_config.translation_directories
application.config["BABEL_DOMAIN"] = flask_config.message_domain


@application.template_filter()
def format_datetime(value, format='medium'):
    return babel_format_datetime(value, format)

@application.template_filter()
def format_datetime_for_input(value):
    return babel_format_datetime(value, "YYYY-MM-ddTHH:mm")


def get_locale():
    return g.locale
    
def get_timezone():
    ret_timezone = None
    if "timezone" in session:
        ret_timezone = session["timezone"]
    else:
        ret_timezone = flask_config.default_timezone

    return ret_timezone

babel = Babel(application, locale_selector=get_locale, timezone_selector=get_timezone)

logger.info("Configure upload temp dir")
application.config['UPLOAD_FOLDER'] = flask_config.get_temp_download_path()

logger.info("setting secret key")
application.secret_key = flask_config.get_secret_key()


for blueprint_module_config in flask_config.get_flask_blueprint_modules():
    if blueprint_module_config.load_it:
        blueprint_module = blueprint_module_config.loaded_module
        if hasattr(blueprint_module, "app"):
            logger.info("Registering blueprint %s with uri prefix[%s]:" % (blueprint_module.app.name, blueprint_module.app.url_prefix))
            application.register_blueprint(blueprint_module.app)
        else:
            raise Exception("Could not find app variable in module:[%s]" % blueprint_module)
    else:
        logger.info("Blueprint module %s was skipped because load_it config attribute is set to false" % blueprint_module_config.class_name)




@application.before_request
def before_request():
    flask_config.prerequest_processor()


@application.errorhandler(Exception)
def basic_error(e):
    if type(e) == ForbiddenException:
        return render_http_error_doc(403)
    elif type(e) == UnauthorizedException:
        return render_http_error_doc(401)
    else:
        logger.exception(e)
        return render_http_error_doc(500)


def render_http_error_doc(status:int):
    doc                 = content_service.get_document("/%s/__system/error_pages/%s.html" % (content_service.get_main_microsite(), status), g.locale)
    resp_payload        = render_template('arches/content/ehtml_content.html', doc=doc)
    return resp_payload, status



def needed_beans(sender, template, context, **extra):
    nav_uri = None
    metadata_doc_path = None
    if "doc" in context:
        metadata_doc:EHTMLDoc = context["doc"]
        #nav_uri = metadata_doc.resource_header.uri
        nav_uri = request.path
    else:
        nav_uri = request.path
        metadata_doc = None

        try:
            metadata_doc_path:str = layout_service.get_metadata_doc_path(request.url_rule.rule)
            metadata_doc:EHTMLDoc = content_service.get_document(metadata_doc_path, g.locale)
            if not metadata_doc:
                metadata_doc:EHTMLDoc = content_service.get_document("/%s/%s/%s" % (content_service.get_main_microsite(), METADATA_DOC_DIR, METADATA_DOC_NAME), g.locale)
        except LayoutNoMetadataDefinition as e:
            logger.warning("No definition for url rule:[%s] in layout service definition" % request.url_rule.rule)
            metadata_doc:EHTMLDoc = content_service.get_document("/%s/%s/%s" % (content_service.get_main_microsite(), METADATA_DOC_DIR, METADATA_DOC_NAME), g.locale)

    if not metadata_doc:
        raise LayoutException("Could not find metadata doc [%s] and no alternate metadata was available" % metadata_doc_path)
        
    tmpl = layout_service.get_layout(metadata_doc.metadata.layout)["layout_path"]

    user_id = get_user_id()

    breadcrumb_chain = nav_service.get_breadcrumb_chain(nav_uri)
    user_authorization_bean = UserAuthorizationBean(user_id, authorization_service)
    nav_bean = AuthorizationRootNavigationBean(breadcrumb_chain, user_authorization_bean, g.locale)

    context["arches_theme_bean"] = metadata_doc
    context["arches_layout"] = tmpl
    context["arches_nav_bean"] = nav_bean


before_render_template.connect(needed_beans, application)


if __name__ == "__main__":
    logger.info("Starting application")
    application.run()