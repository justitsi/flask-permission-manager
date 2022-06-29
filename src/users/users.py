from email.policy import default
from flask import Blueprint, request
from models.models import User, Role, db
from util import generateError, generateResponse, validateJWT, userIsAdmin

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/register', methods=['POST'])
def registerUsers():
    try:
        valid = validateJWT(request)
    except:
        return generateError(500, "Could not validate jwt_token")

    if (not valid):
        return generateError(400, "Invalid jwt_token")
    if (not userIsAdmin(valid["userID"])):
        return generateError(403, "User is not admin")

    try:
        usersToAdd = request.json["users"]
        registeredUsers = []

        defaultUserRoles = [Role.query.filter_by(name='user').first()]

        for userIDToAdd in usersToAdd:
            # check if user already exists
            userEntry = User.query.filter_by(id=userIDToAdd).first()
            if not userEntry:
                userEntry = User(
                    id=userIDToAdd,
                    roles=defaultUserRoles
                )
                db.session.add(userEntry)
                registeredUsers.append(userIDToAdd)

        db.session.commit()
        return generateResponse({
            "users": registeredUsers
        })
    except:
        return generateError(500, "Could not proccess request")


@users_blueprint.route('/unregister', methods=['POST'])
def unregisterUsers():
    try:
        valid = validateJWT(request)
    except:
        return generateError(500, "Could not validate jwt_token")

    if (not valid):
        return generateError(400, "Invalid jwt_token")
    if (not userIsAdmin(valid["userID"])):
        return generateError(403, "User is not admin")

    try:
        users_to_delete = request.json["users"]
        unregistered_users = []

        for user_id in users_to_delete:
            if (not userIsAdmin(user_id)):
                user_entry = User.query.filter_by(id=user_id).first()
                if (user_entry):
                    unregistered_users.append(user_entry.id)
                    db.session.delete(user_entry)

        db.session.commit()

        return generateResponse({
            "users": unregistered_users
        })
    except:
        return generateError(500, "Could not proccess request")


@users_blueprint.route('/bind/<role_id>', methods=['POST'])
def bindRoleToUsers(role_id):
    try:
        valid = validateJWT(request)
    except:
        return generateError(500, "Could not validate jwt_token")

    if (not valid):
        return generateError(400, "Invalid jwt_token")
    if (not userIsAdmin(valid["userID"])):
        return generateError(403, "User is not admin")

    try:
        role_id = int(role_id)
        role = Role.query.filter_by(id=role_id).first()
        if (not role):
            return generateError(404, 'Role not found')

        action = request.json["action"]
        users_to_add = request.json["users"]
        users_added = []

        # sanitize "action" field
        if (action != "add"):
            if (action != "remove"):
                return generateError(400, 'Valid values for the `action` field are `add` and `remove`')

        # admins cannot remove their own admin role
        if (role.name == "admin"):
            users_to_add.remove(valid["userID"])

        # figure out user information
        for user_id in users_to_add:
            user_db_entry = User.query.filter_by(id=user_id).first()
            if (user_db_entry):
                # check if role is already set for that user
                role_set = False
                for user_role in user_db_entry.roles:
                    if (user_role.id == role_id):
                        role_set = True
                # handle adding or removing role for user
                if (action == "add"):
                    if (role_set == False):
                        user_db_entry.roles.append(role)
                        db.session.add(user_db_entry)
                        users_added.append(user_db_entry.id)

                if (action == "remove"):
                    if (role_set == True):
                        user_db_entry.roles.remove(role)
                        db.session.add(user_db_entry)
                        users_added.append(user_db_entry.id)

        db.session.commit()

        return generateResponse({
            "role": Role.jsonify(role),
            "action": action,
            "users": users_added
        })
    except:
        return generateError(500, "Could not proccess request")


@users_blueprint.route('/byRole/<role_id>', methods=['GET'])
def getUsersByRole(role_id):
    try:
        valid = validateJWT(request)
    except:
        return generateError(500, "Could not validate jwt_token")

    if (not valid):
        return generateError(400, "Invalid jwt_token")
    if (not userIsAdmin(valid["userID"])):
        return generateError(403, "User is not admin")

    try:
        role_id = int(role_id)
        role = Role.query.filter_by(id=role_id).first()

        if (not role):
            return generateError(404, "Role not found")

        users_db = User.query.filter(User.roles.any(id=role.id)).all()
        users_list = []
        for user in users_db:
            users_list.append(user.id)

        return generateResponse({
            "role": Role.jsonify(role),
            "users": users_list
        })
    except:
        return generateError(500, "Could not proccess request")


@users_blueprint.route('/all/<page_size>/<page_num>', methods=['GET'])
def getUsersList(page_size, page_num):
    try:
        valid = validateJWT(request)
    except:
        return generateError(500, "Could not validate jwt_token")

    if (not valid):
        return generateError(400, "Invalid jwt_token")
    if (not userIsAdmin(valid["userID"])):
        return generateError(403, "User is not admin")

    try:
        # clean up paramaters
        page_size = int(page_size)
        page_num = int(page_num)
        if page_size > 200:
            page_size = 100
        if page_size < 1:
            page_size = 100

        # paginate
        users_db = User.query.all()
        paged_results = list(paginateArray(users_db, page_size))
        users_db = paged_results[page_num]

        # format data and return
        users_json = []
        for user in users_db:
            users_json.append(User.jsonify(user))

        return generateResponse({
            "pageSize": page_size,
            "pageNum": page_num,
            "nextPage": (page_num < (len(paged_results)-1)),
            "users": users_json
        })
    except:
        return generateError(500, "Could not proccess request")


# helper function to paginate results array
def paginateArray(array, pageSize):
    for i in range(0, len(array), pageSize):
        yield array[i:i + pageSize]
