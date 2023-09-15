from flask import Blueprint, render_template, request, session, redirect

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY
from utah.arches.webtools import uri_authorized
from utah.core.utilities import get_service_object
from utah.core.authentication import BaseAuthenticationService
from utah.core.profile import BaseProfileService
from flask_babel import gettext

authentication_service:BaseAuthenticationService = get_service_object("authentication")


app = Blueprint('authentication', __name__, url_prefix="/arches/authentication")
profile_service:BaseProfileService = get_service_object("profile")



@app.after_request
def after_request_func(response):
    response.headers["Cache-Control"] = "no-cache"
    return response



@app.route("/login/form", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def login_form():
    go_back = request.args.get("go_back")

    if not go_back:
        go_back = "/"

    return render_template('arches/authentication/login_form.html', go_back=go_back)



@app.route("/login", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def login():
    go_back = request.form.get("go_back")

    user_id = request.form["user_id"]
    password = request.form["password"]
    rendering = None

    if authentication_service.authenticate(user_id, password):
        ai = authentication_service.get_authentication_info(user_id)
        if not ai.verification_code:
            profile_info:ProfileInfo = profile_service.get_profile_info(user_id)

            session["user_id"] = user_id
            session["name"] = "%s %s" % (profile_info.first_name, profile_info.last_name)
            session["timezone"] = profile_info.timezone

            rendering = redirect(go_back)
        else:
            rendering = render_template('arches/registration/verify.html', message=gettext("This account is unverified. Please enter the verification code that was send to your registered email address."), error=True, user_id=user_id, field_errors={})

    else:
        rendering = render_template('arches/authentication/login_form.html', go_back=go_back, user_id=user_id, message=gettext("Login Failure"), error=True)

    return rendering


@app.route("/logout", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def logout():
    if "user_id" in session:
        del session["user_id"]

    if "name" in session:
        del session["name"]

    return redirect("/")
