import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..util.redis import (
    get_device_state, set_device_variables, get_device_variables,
    reset_state_and_variables, get_device_variables_min_max, get_device_state_min_max
)

logger = logging.getLogger(__name__)

devices = Blueprint("devices", __name__)

@devices.route("/device/<device_id>/status", methods=["GET"])
@jwt_required
def get_device_status(device_id):
    """ Get the variables and state of a device from redis """

    variables = get_device_variables_min_max(device_id)
    state = get_device_state_min_max(device_id)

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

@devices.route("/device/<device_id>/reset", methods=["POST"])
@jwt_required
def reset(device_id):
    """ Reset State and Variables to default"""

    #variables = get_device_variables(device_id)
    # update from posted vars
    reset_state_and_variables(device_id)

    return jsonify(None), 201
