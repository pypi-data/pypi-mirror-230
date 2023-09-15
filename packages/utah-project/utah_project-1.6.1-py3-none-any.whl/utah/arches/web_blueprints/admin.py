from flask import Blueprint, render_template, session
from utah.arches.webtools import uri_authorized
from utah.core.utilities import get_service_object
from utah.core.content import BaseContentService

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY

app = Blueprint('admin', __name__, url_prefix="/arches/admin")

content_service:BaseContentService = get_service_object("content")

@app.route("/show_admin_page", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def show_admin_page():
    user_id = session["user_id"]
    microsite_names=content_service.get_microsite_names()
    return render_template('arches/application_admin/admin.html', microsite_names=microsite_names)
