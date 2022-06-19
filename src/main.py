# import libraries
import flask
from flask_cors import CORS
from models.models import db, Role
import os
from dotenv import load_dotenv

# import routes
from liveliness.liveliness import liveliness_blueprint
from auth.auth import auth_blueprint
from users.users import users_blueprint
from role.role import role_blueprint
from permission.permission import permission_blueprint


# Load env variables
load_dotenv()
DB_URL = os.getenv('DB_URL')
DB_DBNAME = os.getenv('DB_DBNAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')


app = flask.Flask(__name__)
api_cors_headers = {
    "origins": [
        "localhost:3000",
        "http://localhost:3000",
    ],
    "methods": ["OPTIONS", "DELETE", "GET", "POST"],
    "allow_headers": ["Authorization", "Content-Type"]
}
cors = CORS(app, resources={"/*": api_cors_headers}, supports_credentials=True)  # nopep8


@app.before_first_request
def startup_project():
    db.create_all()
    # pre-create user and admin roles
    try:
        # check if admin role exists
        role = Role.query.filter_by(name="admin").first()
        if (not role):
            role = Role(
                id=1,
                name='admin',
                namePretty='Administrator',
                permissions=[]
            )
            db.session.add(role)
            db.session.commit()

        # check if user role exists
        role = Role.query.filter_by(name="user").first()
        if (not role):
            role = Role(
                id=2,
                name='user',
                namePretty='User',
                permissions=[]
            )
            db.session.add(role)
            db.session.commit()

    except:
        db.session.rollback()


# define routes
@app.route('/', methods=['GET'])
def home():
    return {
        "data": {
            "message": "Currently supported endpoints",
            "endpoints": ["/liveliness, /role, /permission, /auth, /users"]
        },
        "status": 200
    }


app.register_blueprint(liveliness_blueprint, url_prefix='/liveliness')
app.register_blueprint(role_blueprint, url_prefix='/role')
app.register_blueprint(permission_blueprint, url_prefix='/permission')
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(users_blueprint, url_prefix='/users')


app.config["DEBUG"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DB_USER+':'+DB_PASS+'@'+DB_URL+'/'+DB_DBNAME  # nopep8
db.init_app(app)

if __name__ == "__main__":
    # set up app variables for development
    # the production entrypoint for the project is the wsgi.py file in this dir

    print(app.url_map)
    app.run(port=8002)
    db.create_all()
