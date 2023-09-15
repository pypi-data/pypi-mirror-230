from flask import Blueprint, render_template, request, redirect
from utah.arches.webtools import validate_field
from utah.core.utilities import get_service_object
from utah.core.authentication import BaseAuthenticationService
from utah.core.profile import BaseProfileService
from utah.core.profile import ProfileInfo
from utah.core.authorize import Group
from utah.core.authorize import BaseGroupService
from utah.core.authorize import BaseURIAuthorizationService
from utah.core.authorize import URIAccessRight
from utah.core.authorize import DuplicateRight
from utah.core.authorize import NoSuchGroupException, DuplicateGroupException
from utah.arches.webtools import uri_authorized
from flask_babel import gettext
import logging

from utah.arches.webtools import URIUSE_ANY
from utah.arches.webtools import URIUSE_SESSION_ONLY
from utah.arches.webtools import URIUSE_TOKEN_ONLY

app = Blueprint('access_mgmt', __name__, url_prefix="/arches/access_mgmt")

authentication_service:BaseAuthenticationService = get_service_object("authentication")
profile_service:BaseProfileService = get_service_object("profile")
group_service:BaseGroupService = get_service_object("group_service")
uri_access_rights_service:BaseURIAuthorizationService = get_service_object("uri_authorization")

_logger = logging.getLogger(__name__)

class SelectedGroup(Group):
    def __init__(self, group:Group, selected:bool):
        super().__init__(group.name, group.description)
        self.selected = selected

class EnrolledProfileInfo(ProfileInfo):
    def __init__(self, profile:ProfileInfo, groups:list):
        super().__init__(profile.user_id, profile.email_address, profile.first_name, profile.last_name)
        self.groups = groups

class SelectableItem():
    def __init__(self, value, description, selected):
        self.value = value
        self.description = description
        self.selected = selected

class AccessRightBean():
    raw_methods = ["GET","POST","PUT","DELETE"]
    def __init__(self, uri_access_right, available_groups, available_filter_uris, available_environment_types):
        self.id = uri_access_right.id
        self.category = uri_access_right.category
        self.right_name = uri_access_right.right_name
        self.uri = uri_access_right.uri
        self.methods = self.build_selectable_list(uri_access_right.methods, AccessRightBean.raw_methods)
        self.filters = self.build_selectable_list(uri_access_right.filters, available_filter_uris)
        self.groups = self.build_selectable_list(uri_access_right.authorized_groups, available_groups)
        self.permitted_environments = self.build_selectable_list(uri_access_right.permitted_environments, available_environment_types)

    def build_selectable_list(self, selected_items, all_items):
        ret_list = []
        for raw_item in all_items:
            selected = False
            if raw_item in selected_items:
                selected = True

            ret_list.append(SelectableItem(raw_item, raw_item, selected))

        return ret_list


# ----------------------------------------------------------------------------------------
# Group Management methods
# ----------------------------------------------------------------------------------------
@app.route("/groups", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def list_groups():
    groups = group_service.get_groups()
    return render_template('arches/access_mgmt/group_list.html', groups=groups)



@app.route("/groups/__new", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def add_group():
    rendering = None

    group = Group(request.form["name"], request.form["description"])

    field_errors = {}

    validate_field(field_errors, "name", group.name, True, gettext("Name is required"))
    validate_field(field_errors, "description", group.description, True, gettext("Description is required"))

    group_authorizations = request.form.getlist("group_authorizations")

    if len(field_errors) == 0:
        try:
            group_service.add_group(group)

            for authorization_id in group_authorizations:
                authorization = uri_access_rights_service.get_authorization(authorization_id)
                authorization.authorized_groups.append(group.name)
                uri_access_rights_service.update_authorization(authorization)

            rendering = redirect("/arches/access_mgmt/groups")
        except DuplicateGroupException as e:
            field_errors["name"] = gettext("This name already exists")

    if not rendering:
        all_authorizations = uri_access_rights_service.get_all_authorizations()

        rendering = render_template('arches/access_mgmt/group_edit.html', function="add", group=group, all_authorizations=all_authorizations, group_authorizations=group_authorizations, field_errors=field_errors, error=True, message=gettext("Error adding group"))

    return rendering

def get_group_members(group_name):
    member_user_ids = group_service.get_group_members(group_name)

    members = []
    for user_id in member_user_ids:
        profile = profile_service.get_profile_info(user_id)
        if profile:
            members.append(profile)

    return members


@app.route("/groups/<group_name>", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def display_group_update(group_name):
    group = group_service.get_group(group_name)
    members = get_group_members(group_name)
    all_authorizations = uri_access_rights_service.get_all_authorizations()
    group_authorizations = []
    for authorization in all_authorizations:
        if group.name in authorization.authorized_groups:
            group_authorizations.append(authorization.id)

    return render_template('arches/access_mgmt/group_edit.html', 
                            function="update", 
                            all_authorizations=all_authorizations, 
                            group_authorizations=group_authorizations, 
                            members=members, group=group, 
                            field_errors={}, 
                            error=False, 
                            message="")
    

@app.route("groups/__new", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def display_group_add():
    group = Group("","")
    all_authorizations = uri_access_rights_service.get_all_authorizations()
    group_authorizations = []
    return render_template( 'arches/access_mgmt/group_edit.html', 
                            function="add", 
                            members=None, 
                            all_authorizations=all_authorizations, 
                            group_authorizations=group_authorizations, 
                            group=group, 
                            field_errors={}, 
                            error=False, 
                            message="")
    

@app.route("/groups/<group_name>/__delete", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def delete_group(group_name):
    try:
        group_service.delete_group(group_name)
        
    except NoSuchGroupException as e:
        pass

    return redirect("/arches/access_mgmt/groups")
    

@app.route("/groups/<group_name>", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def update_group(group_name):
    rendering = None

    group = Group(group_name, request.form["description"])
    group_authorizations = request.form.getlist("group_authorizations")
    field_errors = {}

    validate_field(field_errors, "description", group.description, True, gettext("Description is required"))

    if len(field_errors) == 0:
        group_service.update_group(group)

        for authorization in uri_access_rights_service.get_all_authorizations():
            if authorization.id in group_authorizations and not group.name in authorization.authorized_groups:
                authorization.authorized_groups.append(group.name)
                uri_access_rights_service.update_authorization( authorization)
            elif not authorization.id in group_authorizations and group.name in authorization.authorized_groups:
                authorization.authorized_groups.remove(group.name)
                uri_access_rights_service.update_authorization( authorization)


        rendering = redirect("/arches/access_mgmt/groups")
    else:
        members = get_group_members(group_name)
        rendering = render_template('arches/access_mgmt/group_edit.html', function="update", members=members, group=group, field_errors=field_errors, error=True, message=gettext("Error updating group"))

    return rendering



# ----------------------------------------------------------------------------------------
# User Management methods
# ----------------------------------------------------------------------------------------
@app.route("/users", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def get_users():
    raw_profiles = profile_service.get_all_profiles()
    profiles = []
    for raw_profile in raw_profiles:
        profile = EnrolledProfileInfo(raw_profile, group_service.get_group_names_for_user(raw_profile.user_id))
        profiles.append(profile)

    return render_template('arches/access_mgmt/user_list.html', profiles=profiles)


@app.route("/users/<user_id>/group_enrollments", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def update_group_enrollments(user_id):

    all_groups = group_service.get_groups()

    update_groups = []

    for group in all_groups:

        key = "group_%s" % group.name

        if key in request.form:
            update_groups.append(group.name)

    group_service.update_groups_for_user(user_id, update_groups)

    return redirect("/arches/access_mgmt/users")



@app.route("/users/<user_id>/group_enrollments", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def get_group_enrollments(user_id):

    profile = profile_service.get_profile_info(user_id)

    groups = []
    all_groups = group_service.get_groups()
    users_groups = group_service.get_group_names_for_user(user_id)

    for raw_group in all_groups:
        selected = False
        if raw_group.name in users_groups:
            selected = True

        group = SelectedGroup(raw_group, selected)

        groups.append(group)

    return render_template('arches/access_mgmt/group_enrollments.html', profile=profile, groups=groups)


@app.route("/users/delete_user", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def delete_user():
    user_id = request.args["user_id"]
    group_service.update_groups_for_user(user_id, [])
    profile_service.delete_profile_info(user_id)
    authentication_service.delete_authentication_info(user_id)
    return redirect("/arches/access_mgmt/users")


# ----------------------------------------------------------------------------------------
# URI Access Rights Management methods
# ----------------------------------------------------------------------------------------
@app.route("/uri_access_rights", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def get_uriaccess_rights():
    uri_access_rights = uri_access_rights_service.get_all_authorizations()
    if len(uri_access_rights_service.available_environment_types) > 1:
        render_env_col = True
    else:
        render_env_col = False

    uri_access_rights.sort(key=lambda e: (e.category, e.right_name))
    return render_template('arches/access_mgmt/rights_list.html', uri_access_rights=uri_access_rights, render_env_col=render_env_col)


@app.route("/uri_access_rights/<id>", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def edit_uriaccess_rights(id:str):
    uri_access_right = uri_access_rights_service.get_authorization(id)

    if uri_access_right:
        uri_access_right_bean = build_access_right_bean(uri_access_right)

        return render_template('arches/access_mgmt/right_form.html', uri_access_right=uri_access_right_bean, field_errors={}, function="update")
    else:
        return redirect("/arches/access_mgmt/uri_access_rights")


@app.route("/uri_access_rights/<id>", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def update_uriaccess_rights(id:str):
    uri_access_right = uri_access_rights_service.get_authorization(id)
    uri_access_right.category = request.form["category"]
    uri_access_right.right_name = request.form["right_name"]
    uri_access_right.uri = request.form["uri"]
    uri_access_right.methods = request.form.getlist("methods")
    uri_access_right.filters = request.form.getlist("filters")
    uri_access_right.authorized_groups = request.form.getlist("authorized_groups")
    uri_access_right.permitted_environments = request.form.getlist("permitted_environments")

    field_errors = {}

    validate_field(field_errors, "category", uri_access_right.category, True, gettext("Category is required"))
    validate_field(field_errors, "uri", uri_access_right.uri, True, gettext("URI is required"))
    validate_field(field_errors, "methods", uri_access_right.methods, True, gettext("At least one method must be selected"))

    if len(field_errors) == 0:
        uri_access_rights_service.update_authorization(uri_access_right)

        return redirect("/arches/access_mgmt/uri_access_rights")
    else:
        uri_access_right_bean = build_access_right_bean(uri_access_right)

        return render_template('arches/access_mgmt/right_form.html', uri_access_right=uri_access_right_bean, field_errors=field_errors, function="update")


@app.route("/uri_access_rights/__new", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def add_uriaccess_rights_form():
    uri_access_right_bean = init_access_right_bean()
    return render_template('arches/access_mgmt/right_form.html', uri_access_right=uri_access_right_bean, field_errors={}, function="add")


@app.route("/uri_access_rights/__new", methods=["POST"])
@uri_authorized(URIUSE_SESSION_ONLY)
def add_uriaccess_rights():
    uri_access_right = URIAccessRight(request.form["category"], request.form["right_name"], request.form["uri"], request.form.getlist("methods"), request.form.getlist("filters"), request.form.getlist("authorized_groups"))

    field_errors = {}

    validate_field(field_errors, "category", uri_access_right.category, True, gettext("Category is required"))
    validate_field(field_errors, "right_name", uri_access_right.category, True, gettext("Right name is required"))
    validate_field(field_errors, "uri", uri_access_right.uri, True, gettext("URI is required"))
    validate_field(field_errors, "methods", uri_access_right.methods, True, gettext("At least one method must be selected"))

    rendering = None

    if len(field_errors) == 0:
        try:
            uri_access_rights_service.add_authorization(uri_access_right)
            rendering = redirect("/arches/access_mgmt/uri_access_rights")

        except DuplicateRight as e:
            field_errors["right_name"] = gettext("Different access rights cannot share the same name")
            uri_access_right_bean = build_access_right_bean(uri_access_right)

            rendering = render_template('arches/access_mgmt/right_form.html', uri_access_right=uri_access_right_bean, field_errors=field_errors, function="add")
    else:
            uri_access_right_bean = build_access_right_bean(uri_access_right)

            rendering =  render_template('arches/access_mgmt/right_form.html', uri_access_right=uri_access_right_bean, field_errors=field_errors, function="add")


    return rendering


def init_access_right_bean():
    uri_access_right = URIAccessRight("", "", "", [], [], [], [], None)
    return build_access_right_bean(uri_access_right) 


def build_access_right_bean(uri_access_right:URIAccessRight):
    available_filters_uris = []
    all_uri_access_rights = uri_access_rights_service.get_all_authorizations()
    for uar in all_uri_access_rights:
        available_filters_uris.append(uar.uri)

    available_filters_uris = list(dict.fromkeys(available_filters_uris))
    available_filters_uris.sort()

    available_groups = group_service.get_groups()
    group_list = group_service.get_default_group_names()
    for ag in available_groups:
        group_list.append(ag.name)

    group_list.sort()

    available_environment_types = uri_access_rights_service.available_environment_types
    uri_access_right_bean = AccessRightBean(uri_access_right, group_list, available_filters_uris, available_environment_types)

    return uri_access_right_bean


@app.route("/uri_access_rights/<id>/__delete", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def delete_access_right(id):
    uri_access_rights_service.delete_authorization(id)
    return redirect("/arches/access_mgmt/uri_access_rights")


@app.route("/uri_access_rights/promote_access_rights", methods=["GET"])
@uri_authorized(URIUSE_SESSION_ONLY)
def promote_access_rights():

    all_rights = uri_access_rights_service.get_all_authorizations()
    downstream_uri_access_rights_service:BaseURIAuthorizationService = get_service_object("next_uri_authorization")

    for right in all_rights:
        _logger.info("Promote Rights: Checking %s, %s" % (right.category, right.right_name))
        next_right = downstream_uri_access_rights_service.find_authorization(right.category, right.right_name)

        if next_right:
            _logger.info("Promote Rights: Delete for update %s, %s" % (right.category, right.right_name))
            downstream_uri_access_rights_service.delete_authorization(next_right.id)

        _logger.info("Promote Rights: Adding %s, %s" % (right.category, right.right_name))
        downstream_uri_access_rights_service.add_authorization(right)


    all_downstream_rights = downstream_uri_access_rights_service.get_all_authorizations()
    for right in all_downstream_rights:
        prev_right = uri_access_rights_service.find_authorization(right.category, right.right_name)
        if not prev_right:
            _logger.info("Promote Rights: deleting %s, %s" % (right.category, right.right_name))
            downstream_uri_access_rights_service.delete_authorization(right.id)


    all_groups = group_service.get_groups()
    downstream_group_service:BaseGroupService = get_service_object("next_group_service")

    for group in all_groups:
        next_group = downstream_group_service.get_group(group.name)
        if not next_group:
            downstream_group_service.add_group(group)
        else:
            downstream_group_service.update_group(group)
        
    all_downstream_groups = downstream_group_service.get_groups()
    for group in all_downstream_groups:
        prev_group = group_service.get_group(group.name)
        if not prev_group:
            downstream_group_service.delete_group(group.name)

    return render_template('arches/access_mgmt/sync_rights_results.html')
