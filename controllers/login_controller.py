from flask import Blueprint, request, jsonify
# from flask_jwt_extended import create_access_token
from utils.rds_helper import RDSHelper
import hashlib
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,  create_access_token,
)
from flask_jwt_extended import  unset_jwt_cookies


auth = Blueprint("auth", __name__, url_prefix="/api/auth")


def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


@auth.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Register
          required:
            - username
            - email
            - password
            - role_id
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            role_id:
              type: integer
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing fields
      409:
        description: User already exists
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role_id = data.get("role_id")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    db = RDSHelper()
    
    # Check if user already exists by email or username
    existing_user = db.execute_query(
        "SELECT id FROM users WHERE email = %s OR username = %s",
        (email, username)
    )
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = hash_password(password)
    insert_sql = """
        INSERT INTO users (username, email, password_hash, role_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    user_id = db.execute_command_returning_id(
        insert_sql, (username, email, hashed_password, role_id)
    )

    token = create_access_token(identity=str(user_id))
    return jsonify({"user_id": user_id, "token": token}), 201


@auth.route("/login", methods=["POST"])
def login():
    """
    Login a user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Login
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      400:
        description: Missing login fields
      401:
        description: Wrong password
      404:
        description: User not found
    """
    data = request.get_json()
    identifier = data.get("username") or data.get("email")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "Missing login fields"}), 400

    db = RDSHelper()
    
    # Retrieve user by username or email
    user = db.execute_query(
        "SELECT * FROM users WHERE username = %s OR email = %s",
        (identifier, identifier)
    )

    if not user:
        return jsonify({"error": "User not found"}), 404

    user = user[0]
    if hash_password(password) != user["password_hash"]:
        return jsonify({"error": "Wrong password"}), 401

    token = create_access_token(identity=str(user["id"]))
    return jsonify({"user_id": user["id"], "token": token}), 200


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the access token using a valid refresh token
    ---
    tags:
      - Auth
    responses:
      200:
        description: New access token created
      401:
        description: Invalid refresh token
    """
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout the current user by clearing JWT token cookies
    ---
    tags:
      - Auth
    responses:
      200:
        description: Logout successful
    """
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
