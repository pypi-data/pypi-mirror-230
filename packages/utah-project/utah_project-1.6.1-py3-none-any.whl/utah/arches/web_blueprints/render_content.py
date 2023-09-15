from flask import Blueprint, render_template, request, Response, g

import logging

from utah.core.content import BaseContentService
from utah.core.content import DocumentNotFound
from utah.core.content import parse_path
from utah.core import content
from jinja2.exceptions import TemplateNotFound
from utah.core.utilities import get_service_object
from utah.arches.webtools import uri_authorized
from utah.arches.webtools import SkinService
from flask_babel import gettext

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY


logger = logging.getLogger(__name__)

class InvalidInputException(Exception):
    pass

class InvalidDocTypeException(Exception):
    pass

class InvalidApiParameter(Exception):
    pass


def render_ehtml(doc, document_path):
    resp_payload = render_template('arches/content/ehtml_content.html', doc=doc)
    return resp_payload, False


def render_text(doc, document_path):
    return doc.text, True


def render_binary(doc, document_path):
    return doc.doc_bytes, True


app = Blueprint('content', __name__,url_prefix="/")

RENDERERS = {   content.RENDER_TYPE_BINARY:render_binary,
                content.RENDER_TYPE_TEXT:render_text,
                content.RENDER_TYPE_EHTML:render_ehtml
}

content_service:BaseContentService = get_service_object("content")
layout_service:SkinService = get_service_object("layout")



def get_locale_str():
    locale_str = None

    if "locale" in request.args:
        locale_str = request.args["locale"]
    else:
        locale_str = g.locale

    return locale_str


@app.route("/<path:document_path>", methods=['GET'])
@uri_authorized(URIUSE_SESSION_ONLY)
def getDocument(document_path):
    return _getDocument(document_path, get_locale_str())


def _getDocument(document_path, locale_str:str=None):
    status = None
    headers = {}
    resp_payload = None

    doc = None
    if "Referer" in request.headers:
        if not request.headers["Referer"].find("/arches/content/manage/review_doc/") == -1:
            (path, name, locale_str, extension) = parse_path(request.headers["Referer"])

    try:
        status = 200
        document_path = "/" + document_path
        doc = content_service.get_document(document_path, locale_str)

        if not doc:
            status = 404
            doc = content_service.get_document("/%s/%s" % (content_service.get_main_microsite(), "__system/error_pages/404.html"), locale_str)

        if not doc:
            raise DocumentNotFound()

        str_last_modified = doc.last_modified_date.strftime("%a, %d %b %Y %H:%M:%S UTC")

        im = None
        if "If-Modified-Since" in request.headers:
            im = request.headers["If-Modified-Since"]

        if im == str_last_modified and not doc.resource_header.render_type == content.RENDER_TYPE_EHTML:
            status = 304
            resp_payload = None
        else:
            resp_payload, ok_to_cache = RENDERERS[doc.resource_header.render_type](doc, document_path)
            headers["Content-Type"] = doc.resource_header.mimetype
            headers["Content-Encoding"] = doc.resource_header.mime_encoding
            if ok_to_cache:
                headers["Last-Modified"] = str_last_modified
            else:
                headers["Cache-Control"] = "no-cache"


    except TemplateNotFound as e:

        resp_payload = gettext("Could not find layout template at specified path for %(layout)s, review document [%(document_path)s]", layout=doc.metadata.layout, document_path=document_path)
        status = 500

    except Exception as e:
        logger.exception(e)
        resp_payload = """
        <html>
            <head>
                <title>%s</title>
            </head>
            <body style="background-color: brown; color:bisque;">
                %s
            </body>
        </html>
        """ % (gettext("Error Page"), gettext("Oh boy is our face red!!! This site cannot even display an error page properly at this time."))
        status = 500

    resp = Response(
            response=resp_payload,
            status=status,
            headers=headers
    )

    return resp