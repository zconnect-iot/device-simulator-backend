import datetime
import logging

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from ..settings import get_settings
from ..util.json import CustomJSONEncoder
from ..util.logging import setup_logging

logger = logging.getLogger(__name__)

settings = get_settings()

setup_logging(__name__, 'server')

def create_app():
    logger.trace("Creating flask app.")
    new_app = Flask(__name__.split('.')[0])
    new_app.config["APPLICATION_ROOT"] = "/api/v1"
    new_app.debug = True
    new_app.config['SECRET_KEY'] = settings['auth']['jwt_secret_key']
    new_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=14)
    new_app.config['JWT_AUTH_URL_RULE'] = '/api/v1/auth'
    new_app.config['JWT_DEFAULT_REALM'] = 'Login Required'
    return new_app

app = create_app()

# pylint: disable=wrong-import-position
from .user import authentication

jwt = JWTManager(app)
CORS(app)

app.register_blueprint(provisioning_root, url_prefix='/api/v1')
app.register_blueprint(authentication, url_prefix='/api/v1')

app.json_encoder = CustomJSONEncoder

print("Flask app created with routes: {}".format(app.view_functions))
