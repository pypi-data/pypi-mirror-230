from flask import Blueprint, render_template, request, redirect, session, url_for
from utah.arches.webtools import validate_field
from utah.core.utilities import get_service_object, string_to_date
from utah.core.utilities import date_to_string
from utah.core.authentication import BaseAuthenticationService
from utah.core.authentication import AuthenticationInfo
from utah.core.utilities import Sendmail
from utah.core.authentication import AuthenticationInfo
from utah.core.authentication import AuthenticationToken
from utah.core.profile import BaseProfileService
from utah.core.profile import ProfileInfo
from utah.arches.webtools import uri_authorized
from utah.arches.webtools import get_user_id
from flask_restful import Resource, Api
from flask_babel import gettext
import json
import pytz
from pytz import timezone
from datetime import datetime, timedelta

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY


errors = {
    'UnauthorizedException': {
        'message': gettext("User Not logged in"),
        'status': 401
    },
    'ForbiddenException': {
        'message': gettext("Authorization Error"),
        'status': 403
    }
}

app = Blueprint('login', __name__, url_prefix="/arches/registration")
api = Api(app, errors=errors)


authentication_service:BaseAuthenticationService = get_service_object("authentication")
profile_service:BaseProfileService = get_service_object("profile")

account_verify_sendmail = None
if authentication_service.is_account_verification_required():
    account_verify_sendmail:Sendmail = get_service_object("account_verify_sendmail")



class Profile(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        profile = profile_service.get_profile_info(get_user_id())
        ret_dict = {"user_id" : profile.user_id,
                    "first_name" : profile.first_name,
                    "last_name" : profile.last_name,
                    "timezone" : profile.timezone
                    }
        return ret_dict
    @uri_authorized(URIUSE_ANY)
    def post(self):
        posted_profile = json.loads(request.data)

        profile = profile_service.get_profile_info(get_user_id())
        profile.last_name = posted_profile["last_name"]
        profile.first_name = posted_profile["first_name"]
        profile.timezone = posted_profile["timezone"]
        profile_service.update_profile_info(profile)

        session["timezone"] = profile.timezone

        return {"status" : "OK"}


class AuthenticationTokens(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        at_results = []
        ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
        for at in ai.authentication_tokens:
            at_results.append( { "description": at.description, "key": at.key, "expire_date": date_to_string(at.expire_date) } )

        return at_results


    @uri_authorized(URIUSE_ANY)
    def post(self):
        posted_token_info = json.loads(request.data)
        ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
        new_token:AuthenticationToken = ai.create_token(posted_token_info["description"], string_to_date(posted_token_info["expire_date"]))
        authentication_service.write_authentication_info(ai)

        return {"description": new_token.description, "expire_date": date_to_string(new_token.expire_date), "key": new_token.key}



class AuthenticationToken(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self, key):
        ret_value = None
        ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
        for at in ai.authentication_tokens:
            if at.key == key:
                ret_value = { "description": at.description, "key": at.key, "expire_date": date_to_string(at.expire_date) }

        return ret_value


    @uri_authorized(URIUSE_ANY)
    def delete(self, key):
        ret_value = None
        ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
        i=0
        for at in ai.authentication_tokens:
            if at.key == key:
                del ai.authentication_tokens[i]
                authentication_service.write_authentication_info(ai)

            i=i+1

        return ret_value


    @uri_authorized(URIUSE_ANY)
    def put(self, key):
        put_token_info = json.loads(request.data)

        ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
        i=0
        for at in ai.authentication_tokens:
            if at.key == key:
                at.description = put_token_info["description"]
                at.expire_date =  string_to_date(put_token_info["expire_date"])
                authentication_service.write_authentication_info(ai)
                break

            i=i+1


class Timezones(Resource):
    @uri_authorized(URIUSE_ANY)
    def get(self):
        return pytz.all_timezones



api.add_resource(Profile, '/profile/api/userinfo')
api.add_resource(Timezones, '/profile/api/timezones')
api.add_resource(AuthenticationTokens, '/api/authentication_tokens')
api.add_resource(AuthenticationToken, '/api/authentication_tokens/<key>')


@app.route("/register/public/form", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def register_form():
    return render_template('arches/registration/register_form.html', field_errors={}, message=gettext("Please enter your registration information"), admin_register=False)


@app.route("/register/public", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def register():
    return generic_register()


@app.route("/register/admin/form", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def admin_register_form():
    return render_template('arches/registration/register_form.html', field_errors={}, message=gettext("Please enter new user registration information"), admin_register=True)


@app.route("/register/admin", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def admin_register():
    return generic_register(True)


def generic_register(admin_register=False):
    user_id = request.form["user_id"]
    password = request.form["password"]
    repeat_password = request.form["repeat_password"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    rendering = None


    field_errors = {}

    validate_field(field_errors, "user_id", user_id, True, gettext("User ID is required"))
    validate_field(field_errors, "password", password, True, gettext("Password is required"))
    validate_field(field_errors, "repeat_password", repeat_password, True, gettext("Repeat password is required"))
    validate_field(field_errors, "first_name", first_name, True, gettext("First name is required"))
    validate_field(field_errors, "last_name", last_name, True, gettext("Last name is required"))

    if not "password" in field_errors and not "repeat_password" in field_errors and not password == repeat_password:
        field_errors["repeat_password"] = gettext("Password and repeat password do not match")

    if not "password" in field_errors and not authentication_service.is_password_complex_enough(password):
        field_errors["password"] = gettext("Password does not meet minimum complexity requirements")

    if len(field_errors) > 0:
        rendering = render_template('arches/registration/register_form.html', 
            message=gettext("Issues were found with this registration"), 
            user_id=user_id, 
            password=password, 
            repeat_password=repeat_password, 
            first_name=first_name, 
            last_name=last_name,
            field_errors=field_errors,
            error=True,
            admin_register=admin_register)

    else:
        ai:AuthenticationInfo  = authentication_service.add_authentication_info(user_id, password, no_verify=admin_register)
        if ai:
            profile_info = ProfileInfo(user_id, user_id, first_name, last_name)

            profile_service.add_profile_info(profile_info)

            if authentication_service.is_account_verification_required() and not admin_register:
                account_verify_sendmail.send_message(profile_info.email_address, {"verification_code":ai.verification_code})

                rendering = render_template('arches/registration/verify.html', message=gettext("Verification code was sent to your email address. Please enter for verification."), error=False, user_id=user_id, field_errors={})
            else:
                if not admin_register:
                    rendering = redirect("/")
                else:
                    rendering = redirect("/arches/access_mgmt/users")

        else:
            rendering = render_template('arches/registration/register_form.html', 
                message=gettext("Registration failed, email address may already be registered"), 
                user_id=user_id, 
                password=password, 
                repeat_password=repeat_password, 
                first_name=first_name, 
                last_name=last_name,
                field_errors=field_errors,
                error=True,
                admin_register=admin_register)

    return rendering


@app.route("/register/public/verify", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def verify_account():
    user_id = request.form["user_id"]
    verification_code = request.form["verification_code"]

    if authentication_service.verify(user_id, verification_code):
        rendering = render_template('arches/authentication/login_form.html', go_back="/", user_id=user_id, message=gettext("Your account is now verified. You may log in."), error=False)
    else:
        field_errors = {"verification_code" : gettext("An incorrect verification code was entred") }
        rendering = render_template('arches/registration/verify.html', message=gettext("The verification code entered was incorrect"), error=True, user_id=user_id, field_errors=field_errors)

    return rendering


@app.route("/register/public/verify/resend", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def resend_verification_code():
    user_id = request.args.get("user_id")
    ai = authentication_service.new_verification(user_id)

    account_verify_sendmail.send_message(user_id, {"verification_code":ai.verification_code})

    return render_template('arches/registration/verify.html', message=gettext("A new verification code was sent to your email address. Please enter for verification."), error=False, user_id=user_id, field_errors={})


@app.route("/password_change/form", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def change_password_form():
    return render_template('arches/registration/password_change_form.html')


@app.route("/password_change", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def change_password():
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    repeat_new_password = request.form["repeat_new_password"]
    user_id = session["user_id"]
    field_errors = {}

    validate_field(field_errors, "current_password", current_password, True, gettext("Current password is required"))
    validate_field(field_errors, "new_password", new_password, True, gettext("New password is required"))
    validate_field(field_errors, "repeat_new_password", repeat_new_password, True, gettext("Repeat new password is required"))
    
    if new_password == current_password:
        field_errors["new_password"] = gettext("Current password and new password are the same")

    if not new_password == repeat_new_password:
        field_errors["repeat_new_password"] = gettext("New password and repeat new password are different")

    if not "new_password" in field_errors and not authentication_service.is_password_complex_enough(new_password):
        field_errors["new_password"] = gettext("New password does not meet minimum complexity requirements")

    if len(field_errors) == 0:
        if not authentication_service.change_password(user_id, current_password, new_password):
            field_errors["current_password"] = "Incorrect password"

    if len(field_errors) > 0:
        rendering = render_template('arches//registration/password_change_form.html', message=gettext("Change password failure"), error=True, field_errors=field_errors)
    else:
        rendering = render_template('arches//common/message.html', message=gettext("Password change was sucessful"))

    return rendering


@app.route("/profile/form", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def profile_form():
    profile = profile_service.get_profile_info(session["user_id"])

    return render_template('arches/login/update_profile.html', profile=profile, field_errors={})



@app.route("/profile", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def update_profile():
    rendering = None

    profile = profile_service.get_profile_info(session["user_id"])

    profile.last_name = request.form["last_name"]
    profile.first_name = request.form["first_name"]

    field_errors = {}

    validate_field(field_errors, "first_name", profile.first_name, True, gettext("First name is required"))
    validate_field(field_errors, "last_name", profile.last_name, True, gettext("Last name is required"))

    if len(field_errors) == 0:
        profile_service.update_profile_info(profile)
        session["name"] = "%s %s" % (profile.first_name, profile.last_name)
        rendering = render_template('arches/login/update_profile.html', profile=profile, field_errors={}, error=False, message=gettext("Profile was updated sucessfully"))
    else:
        rendering = render_template('arches/login/update_profile.html', profile=profile, field_errors=field_errors, error=True, message=gettext("Error updating profile"))

    return rendering



@app.route("/tokens/_new", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def adding_new_token():
    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())

    expire_date = datetime.utcnow()
    expire_date = expire_date + timedelta(days=730)
    expire_date = expire_date.replace(tzinfo=pytz.UTC)

    description = gettext("Access token #%s") % str(len(ai.authentication_tokens) + 1)

    return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens, key="_new", description=description, expire_date=expire_date)



def validate_token_info(field_errors, description, expire_date):
    ret_data = False
    validate_field(field_errors, "description", description, True, gettext("Description is required"))
    indate = None
    try:
        indate = datetime.strptime(expire_date, "%Y-%m-%dT%H:%M")
        indate.replace(tzinfo=timezone(session["timezone"]))
        indate = indate.astimezone(pytz.UTC)
        ret_data = indate
    except:
        field_errors["expire_date"] = gettext("An invalid expire date was provided")


    if indate:
        must_be_past_date = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=2)
        if indate < must_be_past_date:
            field_errors["expire_date"] = gettext("Expire date must be at least 2 hours into the future")

    return ret_data


@app.route("/tokens/_new", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def add_new_token():
    description = request.form["description"]
    str_expire_date = request.form["expire_date"]

    field_errors={}
    expire_date = validate_token_info(field_errors, description, str_expire_date)


    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
    if len(field_errors) == 0:
        ai.create_token(description, expire_date)
        authentication_service.write_authentication_info(ai)

        return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens)
    else:
        return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens, key="_new", description=description, expire_date=str_expire_date, field_errors=field_errors)



@app.route("/tokens/<inkey>", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def updating_token(inkey):
    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
    for token in ai.authentication_tokens:
        if token.key == inkey:
            key=inkey
            description = token.description
            expire_date = token.expire_date
            break

    return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens, key=key, description=description, expire_date=expire_date)


@app.route("/tokens/<key>", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def update_token(key):

    description = request.form["description"]
    str_expire_date = request.form["expire_date"]

    field_errors={}
    expire_date = validate_token_info(field_errors, description, str_expire_date)

    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())

    if len(field_errors) == 0:
        for token in ai.authentication_tokens:
            if token.key == key:
                token.description = description
                token.expire_date = expire_date
                break
        authentication_service.write_authentication_info(ai)

        return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens)

    else:

        return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens, key=key, description=description, expire_date=expire_date, field_errors=field_errors)


@app.route("/tokens", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def token_list():
    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
    return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens)



@app.route("/tokens/<inkey>/_delete", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def get_delete_token(inkey):
    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
    for token in ai.authentication_tokens:
        if token.key == inkey:
            key = inkey
            delete = "y"

    return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens, key=key, delete=delete)



@app.route("/tokens/<key>/_delete", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def delete_token(key):
    ai:AuthenticationInfo = authentication_service.get_authentication_info(get_user_id())
    for token in ai.authentication_tokens:
        if token.key == key:
            ai.authentication_tokens.remove(token)
            authentication_service.write_authentication_info(ai)

    return render_template('arches//registration/token_list.html', authentication_tokens=ai.authentication_tokens)











