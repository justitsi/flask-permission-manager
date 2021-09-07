from flask import Blueprint
import psutil
import time

liveliness_blueprint = Blueprint('liveliness', __name__)


@liveliness_blueprint.route('/', methods=['GET'])
def liveliness():
    p = psutil.Process()

    return {
        "status": "200",
        "uptime": time.time() - p.create_time()
    }
