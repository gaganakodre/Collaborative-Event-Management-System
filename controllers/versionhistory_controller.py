from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.rds_helper import RDSHelper



version_history = Blueprint('version_history', __name__,url_prefix="/api/events")


@version_history.route("/<int:event_id>/history/<int:version_number>", methods=["GET"])
@jwt_required()
def get_version(event_id, version_number):
    """
    Get Event Version
    ---
    tags:
      - Version History
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
      - name: version_number
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Specific version of the event
      404:
        description: Version not found
    """
    db = RDSHelper()
    version = db.execute_query(
        "SELECT * FROM event_versions WHERE event_id = %s AND version_number = %s",
        (event_id, version_number),
    )
    if not version:
        return jsonify({"error": "Version not found"}), 404
    return jsonify(version[0]), 200




@version_history.route("/<int:event_id>/rollback/<int:version_number>", methods=["POST"])
@jwt_required()
def rollback_version(event_id, version_number):
    """
    Rollback Event to Version
    ---
    tags:
      - Version History
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
      - name: version_number
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Event rolled back to the specified version
      400:
        description: Rollback failed
    """
    db = RDSHelper()
    db.execute_command("SELECT rollback_event_to_version(%s, %s)", (event_id, version_number))
    return jsonify({"message": "Rolled back to version"}), 200


# Changelog and Diff
@version_history.route("/<int:event_id>/changelog", methods=["GET"])
@jwt_required()
def get_changelog(event_id):
    """
    Get Event Changelog
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Changelog entries for the event
      404:
        description: Event or changelog not found
    """
    db = RDSHelper()
    log = db.execute_query("SELECT * FROM event_changelog WHERE event_id = %s ORDER BY created_at DESC", (event_id,))
    return jsonify(log), 200


@version_history.route("/<int:event_id>/diff/<int:v1>/<int:v2>", methods=["GET"])
@jwt_required()
def get_diff(event_id, v1, v2):
    """
    Get Differences Between Two Event Versions
    ---
    tags:
      - Version History
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: ID of the event
      - name: v1
        in: path
        type: integer
        required: true
        description: First version number
      - name: v2
        in: path
        type: integer
        required: true
        description: Second version number
    responses:
      200:
        description: Differences between the two event versions
      404:
        description: Diff not found
    """
    db = RDSHelper()
    diff = db.execute_query(
        "SELECT * FROM event_version_diffs WHERE event_id = %s AND version1 = %s AND version2 = %s",
        (event_id, v1, v2),
    )
    return jsonify(diff[0] if diff else {"error": "Diff not found"}), 200
