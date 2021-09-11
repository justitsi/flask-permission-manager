# import libraries
import flask
from models.models import db
import os
from dotenv import load_dotenv

# import routes
from liveliness.liveliness import liveliness_blueprint
from role.role import role_blueprint
from permission.permission import permission_blueprint


# Load env variables
load_dotenv()
DB_URL = os.getenv('DB_URL')
DB_DBNAME = os.getenv('DB_DBNAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')


app = flask.Flask(__name__)

@app.before_first_request
def startup_project():
    db.create_all()


# define routes
@app.route('/', methods=['GET'])
def home():
    return {
        "message": "Currently supported endpoints",
        "endpoints": ["/liveliness, /role, /permission"]
    }


app.register_blueprint(liveliness_blueprint, url_prefix='/liveliness')
app.register_blueprint(role_blueprint, url_prefix='/role')
app.register_blueprint(permission_blueprint, url_prefix='/permission')


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
