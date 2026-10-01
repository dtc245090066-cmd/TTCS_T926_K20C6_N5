from __future__ import annotations

import os
import uuid

from flask import Flask, jsonify, render_template, request, session
from werkzeug.utils import secure_filename

from backend.database import Database
from backend.services import AuthService, RoomService, RoomTypeService, BookingService, DashboardService


ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "lumi-hotel-local-development-key",
)
app.config["DATABASE_PATH"] = os.environ.get(
    "DATABASE_PATH",
    os.path.join(ROOT, "hotel_management.db"),
)
app.config["UPLOAD_FOLDER"] = os.path.join(ROOT, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

database = Database(app.config["DATABASE_PATH"])

auth_service = AuthService(database)
room_service = RoomService(database)
room_type_service = RoomTypeService(database)
booking_service = BookingService(database)
dashboard_service = DashboardService(database)


def login_required():
    return session.get("user")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "") or "").strip()
    password = str(payload.get("password", "") or "")

    if not email or not password:
        return jsonify({
            "ok": False,
            "message": "Vui lòng nhập email và mật khẩu.",
        }), 400

    user = auth_service.login(email, password)

    if not user:
        return jsonify({
            "ok": False,
            "message": "Email hoặc mật khẩu không chính xác."
        }), 401

    session.clear()
    session["user"] = user
    return jsonify({
        "ok": True,
        "message": "Đăng nhập thành công.",
        "user": user,
    })


@app.post("/api/register")
def register():
    payload = request.get_json(silent=True) or {}
    ok, message = auth_service.register(
        payload.get("full_name", ""),
        payload.get("email", ""),
        payload.get("password", ""),
    )
    return jsonify({"ok": ok, "message": message}), 201 if ok else 400


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True, "message": "Bạn đã đăng xuất."})


@app.get("/api/session")
def current_session():
    return jsonify({"user": session.get("user")})


@app.get("/api/profile")
def get_profile():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    profile = auth_service.get_profile(session["user"]["id"])
    if profile is None:
        return jsonify({"ok": False, "message": "Không tìm thấy hồ sơ."}), 404

    return jsonify({"ok": True, "user": profile})


@app.put("/api/profile")
def update_profile():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    payload = request.get_json(silent=True) or {}
    ok, message, profile = auth_service.update_profile(session["user"]["id"], payload)
    if ok and profile is not None:
        session["user"] = profile
        session["user"]["full_name"] = profile["full_name"]
        session["user"]["email"] = profile["email"]
        session["user"]["role"] = profile["role"]

    return jsonify({"ok": ok, "message": message, "user": profile}), 200 if ok else 400


@app.post("/api/profile/avatar")
def upload_profile_avatar():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    image = request.files.get("avatar")
    allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp"}
    extension = os.path.splitext(image.filename or "")[1].lower().lstrip(".") if image else ""

    if image is None or not image.filename:
        return jsonify({"ok": False, "message": "Vui lòng chọn một ảnh."}), 400
    if extension not in allowed_extensions or not (image.mimetype or "").startswith("image/"):
        return jsonify({"ok": False, "message": "Chỉ chấp nhận ảnh JPG, PNG, GIF hoặc WEBP."}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = f"avatar_{session['user']['id']}_{uuid.uuid4().hex}.{secure_filename(extension)}"
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return jsonify({"ok": True, "avatar_url": f"/static/uploads/{filename}"})


@app.get("/api/dashboard")
def dashboard():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    return jsonify({"ok": True, **dashboard_service.get_summary()})


@app.get("/api/rooms")
def get_rooms():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    return jsonify({"ok": True, "rooms": room_service.list_rooms()})


@app.get("/api/room-types")
def get_room_types():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    active_only = request.args.get("active_only", "0") == "1"
    return jsonify({"ok": True, "room_types": room_type_service.list_room_types(active_only)})


@app.post("/api/room-types")
def create_room_type():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    payload = request.get_json(silent=True) or {}
    ok, message, room_type = room_type_service.create_room_type(payload)
    return jsonify({"ok": ok, "message": message, "room_type": room_type}), 201 if ok else 400


@app.put("/api/room-types/<int:room_type_id>")
def update_room_type(room_type_id):
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    payload = request.get_json(silent=True) or {}
    ok, message, room_type = room_type_service.update_room_type(room_type_id, payload)
    return jsonify({"ok": ok, "message": message, "room_type": room_type}), 200 if ok else 400


@app.delete("/api/room-types/<int:room_type_id>")
def delete_room_type(room_type_id):
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    ok, message = room_type_service.delete_room_type(room_type_id)
    return jsonify({"ok": ok, "message": message}), 200 if ok else 400


@app.post("/api/rooms")
def create_room():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    payload = request.get_json(silent=True) or {}
    ok, message, room = room_service.create_room(payload)
    return jsonify({"ok": ok, "message": message, "room": room}), 201 if ok else 400


@app.post("/api/rooms/image")
def upload_room_image():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    image = request.files.get("image")
    allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp"}
    extension = os.path.splitext(image.filename or "")[1].lower().lstrip(".") if image else ""

    if image is None or not image.filename:
        return jsonify({"ok": False, "message": "Vui lòng chọn ảnh phòng."}), 400
    if extension not in allowed_extensions or not (image.mimetype or "").startswith("image/"):
        return jsonify({"ok": False, "message": "Chỉ chấp nhận ảnh JPG, PNG, GIF hoặc WEBP."}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    filename = f"room_{uuid.uuid4().hex}.{secure_filename(extension)}"
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return jsonify({"ok": True, "image_url": f"/static/uploads/{filename}"})


@app.put("/api/rooms/<int:room_id>")
def update_room(room_id):
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    payload = request.get_json(silent=True) or {}
    ok, message, room = room_service.update_room(room_id, payload)
    return jsonify({"ok": ok, "message": message, "room": room}), 200 if ok else 400


@app.delete("/api/rooms/<int:room_id>")
def delete_room(room_id):
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    ok, message = room_service.delete_room(room_id)
    return jsonify({"ok": ok, "message": message}), 200 if ok else 400


@app.get("/api/bookings")
def get_bookings():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401
    return jsonify({"ok": True, "bookings": booking_service.list_bookings()})


@app.post("/api/bookings")
def create_booking():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    payload = request.get_json(silent=True) or {}
    ok, message, booking = booking_service.create_booking(payload)

    return jsonify({
        "ok": ok,
        "message": message,
        "booking": booking,
    }), 201 if ok else 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
