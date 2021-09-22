from flask import Blueprint, request, make_response
from models.models import Permission, Role, User, db
from util import generateError, validateJWT, createJWTToken
from datetime import datetime, timedelta

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/', methods=['GET'])
def get_permissions():
    try:
        valid = validateJWT(request) 
    except:
        return generateError(500, "Could not validate jwt_token")
    
    if (not valid):
        return generateError(400, "Invalid jwt_token")

    try:
        # check if user entry exists, and create it if it doesn't
        user_entry = User.query.filter_by(id=valid["userID"]).first()   
        if (not user_entry):
            user_roles = [Role.query.filter_by(name='user').first()]

            # check if user database contains entries, and set user as admin if db is empty
            if (User.query.count() == 0):
                user_roles.append(Role.query.filter_by(name='admin').first())

            user_entry = User (
                id = valid["userID"],
                roles = user_roles
            )
            db.session.add(user_entry)
            db.session.commit()

        # format role and permission data for response and return
        roles = []
        for role in user_entry.roles:
            roles.append(Role.jsonify(role))
        
        # de-duplicate permissions
        permissions = []
        for role in user_entry.roles:
            for perm in role.permissions:
                exists = False
                for json_perm in permissions:
                    if (json_perm['id'] == perm.id):
                        exists = True
                        break

                if (exists == False):
                    permissions.append(Permission.jsonify(perm))
        
        roles_info_basic = []
        for role in roles:
            role_info = {
                'id': role['id'],
                'name': role['name'],
                'namePretty': role['namePretty']
            }
            roles_info_basic.append(role_info)

        token_issued_time = datetime.now()
        token_expiry_time = token_issued_time + timedelta(days=30)

        token = createJWTToken ({
            'permissions': permissions,
            'roles': roles_info_basic,
            'userID': valid["userID"],
            "issued": str(token_issued_time),
            "expires": str(token_expiry_time)
        })

        response = make_response({
            "data":{   
                "userID": valid["userID"],
                "roles": roles,
                "perms": permissions,
                "issued": str(token_issued_time),
                "expires": str(token_expiry_time),
                "token": token
            },
            "status": 200
        })
        response.set_cookie('jwt_permissions', token, max_age=timedelta(days=30))
        return response  
    except:
        return generateError(500, "Could not proccess request")
