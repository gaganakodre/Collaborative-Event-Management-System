from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.rds_helper import RDSHelper

collaboration = Blueprint('collaboration', __name__,url_prefix="/api/events")



@collaboration.route("/<int:event_id>/share", methods=["POST"])
@jwt_required()
def share_event(event_id):
    """
    Share an Event with Another User
    ---
    tags:
      - Collaboration
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: ID of the event to share
      - in: body
        name: body
        required: true
        schema:
          id: ShareEvent
          required:
            - user_id
            - role
          properties:
            user_id:
              type: integer
            role:
              type: string
              description: Role to assign (e.g., viewer, editor)
    responses:
      200:
        description: Event shared
      400:
        description: Invalid input
    """
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
    """
    List User Permissions for an Event
    ---
    tags:
      - Collaboration
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: ID of the event
    responses:
      200:
        description: List of user permissions
      404:
        description: Event not found
    """
    db = RDSHelper()
    permissions = db.execute_query("SELECT * FROM event_permissions WHERE event_id = %s", (event_id,))
    return jsonify(permissions), 200


@collaboration.route("/<int:event_id>/permissions/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_permission(event_id, user_id):
    """
    Update a User's Permission for an Event
    ---
    tags:
      - Collaboration
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: ID of the event
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user whose role is to be updated
      - in: body
        name: body
        required: true
        schema:
          id: UpdatePermission
          required:
            - role
          properties:
            role:
              type: string
              description: New role for the user
    responses:
      200:
        description: Permission updated
      400:
        description: Invalid role or input
      404:
        description: Permission not found
    """
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
    """
    Remove a User's Permission from an Event
    ---
    tags:
      - Collaboration
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: ID of the event
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user whose permission is to be removed
    responses:
      200:
        description: Permission removed
      404:
        description: Permission not found
    """
    db = RDSHelper()
    db.execute_command(
        "DELETE FROM event_permissions WHERE event_id = %s AND user_id = %s", (event_id, user_id)
    )
    return jsonify({"message": "Permission removed"}), 200