from flask import Blueprint, request, make_response
from models.models import Permission, db
from util import generateResponse, generateError, validateJWT, userIsAdmin

permission_blueprint = Blueprint('permission', __name__)


@permission_blueprint.route('/', methods=['GET'])
def get_all_permissions():
    try:
        valid = validateJWT(request) 
    except:
        return generateError(500, "Could not validate jwt_token")
    
    if (not valid):
        return generateError(400, "Invalid jwt_token")
    
    try:
        db_perms = Permission.query.all()
        perms = []

        for perm in db_perms:
            perms.append(Permission.jsonify(perm))

        return generateResponse(perms)
    except:
        return generateError(500, "Could not proccess request")

@permission_blueprint.route('/<perm_id>', methods=['GET', 'POST', 'DELETE'])
def manage_permissions(perm_id):
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
            permission = Permission.query.filter_by(id=perm_id).first()

            if (permission):
                return generateResponse(Permission.jsonify(permission))
            else:
                return generateError(404, "Permission not found")
        if (request.method == 'POST'):
            permission = Permission.query.filter_by(id=perm_id).first()
            if (permission):
                try:
                    permission.name = request.json["perm_name"]
                    permission.namePretty = request.json["perm_namePretty"]
                except:
                    return generateError(400, "Missing mandatory request paramaters in request body")

                db.session.commit()
                return generateResponse("Permission modified")
            else:
                try:
                    permission = Permission(
                        id=perm_id,
                        name=request.json["perm_name"],
                        namePretty=request.json["perm_namePretty"]
                    )
                except:
                    return generateError(400, "Missing mandatory request paramaters in request body")

                db.session.add(permission)
                db.session.commit()

                return generateResponse("Permission created")
        if (request.method == 'DELETE'):
            permission = Permission.query.filter_by(id=perm_id).first()
            if (permission):
                db.session.delete(permission)
                db.session.commit()

                return generateResponse("Permission deleted")
            else:
                return generateError(404, "Permission not found")
    except:
        return generateError(500, "Could not proccess request")