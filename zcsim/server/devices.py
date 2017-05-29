import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..util.redis import (
    get_device_state, set_device_variables, get_device_variables
)

logger = logging.getLogger(__name__)

devices = Blueprint("devices", __name__)

@devices.route("/device/<device_id>/status", methods=["GET"])
@jwt_required
def get_device_status(device_id):
    """ Get the variables and state of a device from redis """

    variables = get_device_variables(device_id)
    state = get_device_state(device_id)

    response = {
        "variables": variables,
        "state": state,
    }
    return jsonify(response)


@devices.route("/device/<device_id>/variables", methods=["POST"])
@jwt_required
def update_variables(device_id):
    """ Update the simulation variables in redis"""

    variables = get_device_variables(device_id)
    # update from posted vars
    changes = request.get_json()
    variables.update(**changes)
    set_device_variables(device_id, variables)

    return jsonify(variables)
