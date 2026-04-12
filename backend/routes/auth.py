from flask import Blueprint, request, jsonify
from utils.helpers import is_valid_email, is_strong_password

auth_bp = Blueprint("auth", __name__)

# Temporary database
users = []


# ------------------------
# Signup
# ------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Required fields
    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    # Email validation
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email"}), 400

    # Password validation
    if not is_strong_password(password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check duplicate email
    for user in users:
        if user["email"] == email:
            return jsonify({"error": "Email already exists"}), 400

    # Add user
    users.append({
        "username": username,
        "email": email,
        "password": password
    })

    return jsonify({"message": "Signup success"}), 201


# ------------------------
# Login
# ------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify({
                "message": "Login success",
                "username": user["username"]
            }), 200

    return jsonify({"error": "Invalid credentials"}), 401


# ------------------------
# Get all users
# ------------------------
@auth_bp.route("/users", methods=["GET"])
def get_users():
    return jsonify(users), 200


# ------------------------
# Delete user
# ------------------------
@auth_bp.route("/delete/<email>", methods=["DELETE"])
def delete_user(email):
    global users

    users = [u for u in users if u["email"] != email]

    return jsonify({"message": "User deleted"}), 200