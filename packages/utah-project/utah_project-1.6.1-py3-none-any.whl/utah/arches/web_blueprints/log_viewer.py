from flask import Blueprint, render_template, request
from flask_restful import Resource, Api

from utah.arches.webtools import uri_authorized
from utah.core.utilities import get_service_object
from utah.core.utilities import LogReader
from utah.core.utilities import LogQuery

from datetime import datetime
from re import error as RegexError
from flask_babel import format_datetime
from flask_babel import gettext
from flask_babel import get_timezone

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY

app = Blueprint('log_viewer', __name__, url_prefix="/arches/log_viewer")

api = Api(app, errors={})

log_reader = get_service_object("log_reader")

errors = {
    'ValueError' : {
        'error_code':'InvalidApiParameter',
        'message': gettext("An invalid parameter was supplied to the API"),
        'status': 409
    }
}


def serialize_log_entries(log_entries:list):
    ret_list = []

    for log_entry in log_entries:
        ret_list.append( {
        "entry_number" : log_entry.entry_number,
        "entry_timestamp" : format_datetime(log_entry.entry_timestamp, "yyyy-MM-dd HH:mm:ss"),
        "severity" : log_entry.severity,
        "modulename" : log_entry.modulename,
        "message_lines" : log_entry.message_lines
    } )

    return ret_list



class ApplicationLogEntries(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        try:

            timezone = get_timezone()
            from_timestamp = request.args.get("from_timestamp", None)
            if from_timestamp:
                from_timestamp = datetime.strptime(from_timestamp, "%Y-%m-%d %H:%M:%S")
                from_timestamp = timezone.localize(from_timestamp)

            to_timestamp = request.args.get("to_timestamp", default=None)
            if to_timestamp:
                to_timestamp = datetime.strptime(to_timestamp, "%Y-%m-%d %H:%M:%S")
                to_timestamp = timezone.localize(to_timestamp)

            severity = request.args.get("severity", type=list)

            module_regex = request.args.get("module_regex")

            message_regex = request.args.get("message_regex")


            from_entry_number = request.args.get("from_entry_number", type=int)
            to_entry_number = request.args.get("to_entry_number", type=int)

            q = LogQuery(from_timestamp, to_timestamp, severity, module_regex, message_regex, from_entry_number, to_entry_number)

            return serialize_log_entries(log_reader.get_log_entries(q))

        except RegexError as e:

            raise ValueError


api.add_resource(ApplicationLogEntries, '/log_entries')



@app.route("/show_log_viewer", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def show_log_viewer():
    return render_template('arches/log_viewer/display.html')