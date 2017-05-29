import logging
from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify
from werkzeug.security import safe_str_cmp

logger = logging.getLogger(__name__)

authentication = Blueprint('authentication', __name__)


class User:
    def __init__(self, id, username, password):
        #pylint: disable=redefined-builtin
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='{}', username='{}')".format(self.id, self.username)


users = [
    User(1, 'admin', 'LetMeIn'),
    User(2, 'demo', 'demo'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token
@authentication.route('/auth', methods=['POST'])
def auth():
    body = request.get_json()
    username = body.get('username', None)
    password = body.get('password', None)
    user = username_table.get(username, None)
    if not user or not safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        logger.trace("Username and password did not match")
        return jsonify({"msg": "Bad username or password"}), 401

    ret = {'access_token': create_access_token(identity=username)}
    return jsonify(ret), 200
