from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.rds_helper import RDSHelper

events = Blueprint("events", __name__, url_prefix="/api/events")


@events.route("/", methods=["POST"])
@jwt_required()
def create_event():
    """
    Create a new event
    ---
    tags:
      - Events
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: CreateEvent
          required:
            - title
            - start_time
          properties:
            title:
              type: string
            description:
              type: string
            start_time:
              type: string
            end_time:
              type: string
    responses:
      201:
        description: Event created
      400:
        description: Missing required fields
    """
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if not title or not start_time:
        return jsonify({"error": "Title and start_time are required"}), 400

    user = get_jwt_identity()
    user_id = int(get_jwt_identity())
    
    db = RDSHelper()
    insert_sql = """
        INSERT INTO events (title, description, user_id, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """
    event_id = db.execute_command_returning_id(
        insert_sql, (title, description, user_id, start_time, end_time)
    )
    return jsonify({"event_id": event_id, "message": "Event created"}), 201


@events.route("/<int:event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id):
    """
    Get an event by ID
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: event_id
        required: true
        type: integer
    responses:
      200:
        description: Event found
      404:
        description: Event not found
    """
    db = RDSHelper()
    event = db.execute_query("SELECT * FROM events WHERE id = %s", (event_id,))
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event[0]), 200


@events.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id):
    """
    Update an existing event
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: event_id
        required: true
        type: integer
      - in: body
        name: body
        schema:
          id: UpdateEvent
          properties:
            title:
              type: string
            description:
              type: string
            start_time:
              type: string
            end_time:
              type: string
    responses:
      200:
        description: Event updated
    """
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    db = RDSHelper()
    update_sql = """
        UPDATE events
        SET title=%s, description=%s, start_time=%s, end_time=%s
        WHERE id=%s
    """
    db.execute_command(update_sql, (title, description, start_time, end_time, event_id))
    return jsonify({"message": "Event updated"}), 200


@events.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    """
    Delete an event
    ---
    tags:
      - Events
    parameters:
      - in: path
        name: event_id
        required: true
        type: integer
    responses:
      200:
        description: Event deleted
    """    
    db = RDSHelper()
    db.execute_command("DELETE FROM events WHERE id = %s", (event_id,))
    return jsonify({"message": "Event deleted"}), 200
