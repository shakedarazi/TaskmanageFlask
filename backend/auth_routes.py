from flask import Blueprint, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo
from logic.validators import validate_user_input
import logging
from limiter_config import limiter


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    valid, error = validate_user_input(data, ["username", "password"])
    if not valid:
        return {"error": error}, 400

    username = data["username"]
    password = data["password"]

    if mongo.db.users.find_one({"username": username}):
        return {"error": "User already exists"}, 400

    hashed = generate_password_hash(password)

    user_doc = {
        "username": username,
        "password": hashed
    }

    telegram_chat_id = data.get("telegram_chat_id")
    if telegram_chat_id:
        user_doc["telegram_chat_id"] = telegram_chat_id

    mongo.db.users.insert_one(user_doc)
    return {"message": "User registered"}, 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    valid, error = validate_user_input(data, ["username", "password"])
    if not valid:
        return {"error": error}, 400

    user = mongo.db.users.find_one({"username": data["username"]})
    logging.info(f"Login attempt for user: {data['username']}")
    if not user or not check_password_hash(user["password"], data["password"]):
        logging.warning(f"Failed login attempt for user: {data['username']}")
        return {"error": "Invalid credentials"}, 401

    session["username"] = data["username"]
    session.permanent = True  # Make it expire after timeout
    return {"message": "Login successful", "username": data["username"]}, 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return {"message": "Logged out"}, 200

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    username = session.get("username")
    if username:
        return {"username": username}, 200
    return {"error": "Unauthorized"}, 401