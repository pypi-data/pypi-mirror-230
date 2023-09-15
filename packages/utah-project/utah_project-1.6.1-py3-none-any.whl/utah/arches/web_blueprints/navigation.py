from flask import Blueprint, render_template, request, g
from datetime import datetime
from utah.core.navigation import BaseNavigationService
from utah.core.utilities import get_service_object
from flask_babel import gettext
from utah.arches.webtools import uri_authorized
import logging

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY

logger = logging.getLogger(__name__)

app = Blueprint('navigation', __name__, url_prefix="/arches/navigation")

navigation_service:BaseNavigationService = get_service_object("navigation")

@app.route("/load")
@uri_authorized(URIUSE_SESSION_ONLY)
def load_navigation():
    try:
        navigation_service.off_time_nav_tree_load()
        message = gettext("Navigation was loaded successfully")
        successful = True
        
    except Exception as e:
        message = e.__class__.__name__ + ":" + str(e)
        successful = False
        logger.error(e)

    return render_template('arches/navigation/load_navigation.html', message=message, successful=successful)