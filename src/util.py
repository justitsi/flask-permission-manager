import os.path as path
from flask import request
import jwt
from datetime import datetime
from models.models import User

rootDir = path.abspath(path.join(__file__, "./../../certs"))

JWT_PRIVATE_KEY = open(path.join(rootDir, "private.key")).read()
JWT_PUBLIC_KEY = open(path.join(rootDir, "public.pem")).read()

# helper functions for generating responses
def generateResponse(message):
    return {
        "status": "200",
        "data": message
    }


def generateError(code, message):
    return (
        {
            "status": code,
            "error": message
        },
        code
    )


# helper functions for authentication
def userIsAdmin (user_id):
    user = User.query.filter_by(id=user_id).first()
    if (user):
        return user.isAdmin
    else:
        return False


def validateJWT(request):
    try:
        token = request.cookies.get('jwt_token')
        payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=['RS512'])

        issuedTime = datetime.strptime(
            str(payload['issued']), '%Y-%m-%d %H:%M:%S.%f')
        # check issued time is in the past
        if not (issuedTime < datetime.now()):
            return False

        expiryTime = datetime.strptime(
            str(payload['expires']), '%Y-%m-%d %H:%M:%S.%f')
        # check expiry time is in the future
        if not (expiryTime > datetime.now()):
            return False

        return payload
    except:
        return False