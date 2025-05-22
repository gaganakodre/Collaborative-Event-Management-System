from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.rds_helper import RDSHelper

collaboration = Blueprint('collaboration', __name__,url_prefix="/api/events")



@collaboration.route("/<int:event_id>/share", methods=["POST"])
@jwt_required()
def share_event(event_id):
    data = request.get_json()
    db = RDSHelper()
    db.execute_command(
        "INSERT INTO event_permissions (event_id, user_id, role) VALUES (%s, %s, %s)",
        (event_id, data.get("user_id"), data.get("role")),
    )
    return jsonify({"message": "Event shared"}), 200


@collaboration.route("/<int:event_id>/permissions", methods=["GET"])
@jwt_required()
def list_permissions(event_id):
    db = RDSHelper()
    permissions = db.execute_query("SELECT * FROM event_permissions WHERE event_id = %s", (event_id,))
    return jsonify(permissions), 200


@collaboration.route("/<int:event_id>/permissions/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_permission(event_id, user_id):
    data = request.get_json()
    db = RDSHelper()
    db.execute_command(
        "UPDATE event_permissions SET role = %s WHERE event_id = %s AND user_id = %s",
        (data.get("role"), event_id, user_id),
    )
    return jsonify({"message": "Permission updated"}), 200


@collaboration.route("/<int:event_id>/permissions/<int:user_id>", methods=["DELETE"])
@jwt_required()
def remove_permission(event_id, user_id):
    db = RDSHelper()
    db.execute_command(
        "DELETE FROM event_permissions WHERE event_id = %s AND user_id = %s", (event_id, user_id)
    )
    return jsonify({"message": "Permission removed"}), 200