import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

logger = logging.getLogger(__name__)

devices = Blueprint("devices", __name__)

@devices.route("/device/<device_id>/status", methods=["GET"])
@jwt_required
def get_device_status(device_id):
    """ Get the variables and state of a device from redis """

    variables = {} #TODO
    state = {} # TODO

    response = {
        "variables": variables,
        "state": state,
    }
    return jsonify()


@devices.route("/device/<device_id>/variables", methods=["POST"])
@jwt_required
def update_variables(device_id):
    """ Update the simulation variables in redis"""

    variables = {}
    #TODO set in REDIS
