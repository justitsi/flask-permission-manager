from flask import Blueprint
import psutil
import time
from util import generateResponse

liveliness_blueprint = Blueprint('liveliness', __name__)


@liveliness_blueprint.route('/', methods=['GET'])
def liveliness():
    p = psutil.Process()

    return generateResponse({
        "uptime": time.time() - p.create_time()
    })
