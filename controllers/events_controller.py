from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.rds_helper import RDSHelper
from controllers.role_controller import role_required




events = Blueprint("events", __name__, url_prefix="/api/events")


@events.route("/", methods=["POST"])
@jwt_required()
@role_required(["Owner", "Editor"])
def create_event():
    data = request.get_json()
    required_fields = ["title", "start_time"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "Title and start_time are required"}), 400

    user_id = int(get_jwt_identity())
    db = RDSHelper()
    insert_sql = """
        INSERT INTO events (title, description, user_id, start_time, end_time, recurrence_rule)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """
    event_id = db.execute_command_returning_id(
        insert_sql,
        (
            data.get("title"),
            data.get("description"),
            user_id,
            data.get("start_time"),
            data.get("end_time"),
            data.get("recurrence_rule"),
        ),
    )
    db.execute_command(
        """
        INSERT INTO event_versions (
            event_id, version_number, title, description, start_time, end_time,
            recurrence_rule, updated_by, change_summary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            event_id, 1, data.get("title"), data.get("description"),
            data.get("start_time"), data.get("end_time"), data.get("recurrence_rule"),
            user_id, "Initial event creation"
        )
    )

    db.execute_command(
        """
        INSERT INTO event_changelog (event_id, action, user_id, description)
        VALUES (%s, %s, %s, %s)
        """,
        (event_id, "create", user_id, "Created event")
    )
    db.execute_command(
        """
        INSERT INTO event_version_diffs (event_id, version_number, diff_summary)
        VALUES (%s, %s, %s)
        """,
        (event_id, 1, "Initial version created")
    )

    return jsonify({"event_id": event_id, "message": "Event created"}), 201



@events.route("/", methods=["GET"])
@jwt_required()
def list_events():
    user_id = int(get_jwt_identity())
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))
    db = RDSHelper()
    events = db.execute_query(
        "SELECT * FROM events WHERE user_id = %s LIMIT %s OFFSET %s",
        (user_id, limit, offset),
    )
    return jsonify(events), 200


@events.route("/<int:event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id):
    db = RDSHelper()
    event = db.execute_query("SELECT * FROM events WHERE id = %s", (event_id,))
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event[0]), 200


@events.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
@role_required(["Owner", "Editor"])
def update_event(event_id):
    data = request.get_json()
    db = RDSHelper()
    user_id = int(get_jwt_identity())
    version_info = db.execute_query(
        "SELECT COALESCE(MAX(version_number), 0) AS version FROM event_versions WHERE event_id = %s",
        (event_id,)
    )
    new_version = version_info[0]["version"] + 1
   
    db.execute_command(
        """
        UPDATE events
        SET title=%s, description=%s, start_time=%s, end_time=%s, recurrence_rule=%s
        WHERE id=%s
        """,
        (
            data.get("title"),
            data.get("description"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("recurrence_rule"),
            event_id,
        ),
    )
    db.execute_command(
        """
        INSERT INTO event_versions (
            event_id, version_number, title, description, start_time, end_time,
            recurrence_rule, updated_by, change_summary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            event_id, new_version, data.get("title"), data.get("description"),
            data.get("start_time"), data.get("end_time"), data.get("recurrence_rule"),
            user_id, "Event updated"
        )
    )
    db.execute_command(
        """
        INSERT INTO event_changelog (event_id, action, user_id, description)
        VALUES (%s, %s, %s, %s)
        """,
        (event_id, "update", user_id, "Updated event")
    )

    db.execute_command(
        """
        INSERT INTO event_version_diffs (event_id, version_number, diff_summary)
        VALUES (%s, %s, %s)
        """,
        (event_id, new_version, "Updated title/description/start_time/etc.")
    )

    return jsonify({"message": "Event updated"}), 200



@events.route("/batch", methods=["POST"])
@jwt_required()
@role_required(["Owner", "Editor"])
def create_batch_events():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    db = RDSHelper()
    created_ids = []
    print(data,'ppp')
    for event in data['events']:
        print(event.values(),'event')
        event_id = db.execute_command_returning_id(
            """
            INSERT INTO events (title, description, user_id, start_time, end_time, recurrence_rule)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (
                event.get("title"),
                event.get("description"),
                user_id,
                event.get("start_time"),
                event.get("end_time"),
                event.get("recurrence_rule"),
            ),
        )
        created_ids.append(event_id)
    return jsonify({"created_event_ids": created_ids}), 201
