from flask import Blueprint, request, make_response
from models.models import Role, Permission, db
from util import generateResponse, generateError, validateJWT, userIsAdmin

role_blueprint = Blueprint('role', __name__)


@role_blueprint.route('/', methods=['GET'])
def get_all_roles():
    try:
        valid = validateJWT(request) 
    except:
        return generateError(500, "Could not validate jwt_token")
    
    if (not valid):
        return generateError(400, "Invalid jwt_token")
    
    try:
        db_roles = Role.query.all()
        roles = []

        for role in db_roles:
            roles.append(Role.jsonify(role))

        return generateResponse(roles)
    except:
        return generateError(500, "Could not proccess request")

@role_blueprint.route('/<role_id>', methods=['GET', 'POST', 'DELETE'])
def manage_roles(role_id):
    try:
        valid = validateJWT(request) 
    except:
        return generateError(500, "Could not validate jwt_token")
    
    if (not valid):
        return generateError(400, "Invalid jwt_token")
    # if (not userIsAdmin(valid["userID"])):
    #     return generateError(403, "User is not admin")

    try:
        if (request.method == 'GET'):
            role = Role.query.filter_by(id=role_id).first()

            if (role):
                return generateResponse(Role.jsonify(role))
            else:
                return generateError(404, "Role not found")
        if (request.method == 'POST'):
            valid_perms = getValidPermissions(request.json["role_permissions"])
            role = Role.query.filter_by(id=role_id).first()

            if (int(role_id) == 1 or int(role_id) == 2):
                if not (role.name == request.json["role_name"]):
                    return generateError(400, "Cannot change role names for protected roles user and admin")

            if (role):
                try:
                    role.name = request.json["role_name"]
                    role.namePretty = request.json["role_namePretty"]
                    role.permissions = valid_perms
                except:
                    return generateError(400, "Missing mandatory request paramaters in request body")

                db.session.commit()
                return generateResponse("Role modified")
            else:
                try:
                    role = Role(
                        id=role_id,
                        name=request.json["role_name"],
                        namePretty=request.json["role_namePretty"],
                        permissions = valid_perms
                    )
                except:
                    return generateError(400, "Missing mandatory request paramaters in request body")

                db.session.add(role)
                db.session.commit()
                return generateResponse("Role created")
        if (request.method == 'DELETE'):
            if (int(role_id) == 1 or int(role_id) == 2):
                return generateError (400, "Cannot delete protected roles user and admin")
            else:
                role = Role.query.filter_by(id=role_id).first()
                if (role):
                    db.session.delete(role)
                    db.session.commit()

                    return generateResponse("Role deleted")
                else:
                    return generateError(404, "Role not found")
    except:
        return generateError(500, "Could not proccess request")

def getValidPermissions(IDarr):
    perms = []

    for perm_id in IDarr:
        perm = Permission.query.filter_by(id=perm_id).first()

        if (not (perm is None)):
            perms.append(perm)

    return perms