from __future__ import annotations

import os
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, session
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from werkzeug.utils import secure_filename

from backend.database import Database
from backend.services import AuthService, RoomService, RoomTypeService, BookingService, DashboardService


ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

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
    verification_code = str(payload.get("verification_code", "") or "").strip()
    if verification_code:
        ok, message = auth_service.register(payload.get("email", ""), verification_code)
    else:
        ok, message = auth_service.request_registration_code(
            payload.get("full_name", ""),
            payload.get("email", ""),
            payload.get("password", ""),
        )
    status_code = 201 if ok and verification_code else 200 if ok else 400
    return jsonify({"ok": ok, "message": message}), status_code


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


@app.post("/api/profile/password")
def update_password():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "") or "").strip().lower()

    if login_required():
        user_id = session["user"]["id"]
        ok, message = auth_service.change_password(
            user_id,
            str(payload.get("current_password", "") or ""),
            str(payload.get("new_password", "") or ""),
            str(payload.get("confirm_password", "") or ""),
            email=email or session["user"].get("email", ""),
        )
        return jsonify({"ok": ok, "message": message}), 200 if ok else 400

    ok, message = auth_service.change_password(
        None,
        str(payload.get("current_password", "") or ""),
        str(payload.get("new_password", "") or ""),
        str(payload.get("confirm_password", "") or ""),
        email=email,
    )
    return jsonify({"ok": ok, "message": message}), 200 if ok else 400


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


@app.get("/api/revenue-statistics")
def revenue_statistics():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    raw_year = request.args.get("year", "").strip()
    if raw_year:
        try:
            selected_year = int(raw_year)
        except ValueError:
            return jsonify({"ok": False, "message": "Năm thống kê không hợp lệ."}), 400
        return jsonify({"ok": True, **dashboard_service.get_monthly_revenue(selected_year)})

    return jsonify({"ok": True, **dashboard_service.get_monthly_revenue()})


def get_pdf_font_name() -> str:
    """Register a Unicode font so the revenue report renders Vietnamese correctly."""
    font_name = "LumiHotelUnicode"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    font_paths = (
        Path(os.environ.get("PDF_FONT_PATH", "")),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    )
    for font_path in font_paths:
        if font_path.is_file():
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            return font_name

    raise RuntimeError("Không tìm thấy font Unicode để tạo PDF tiếng Việt.")


def format_vnd(amount: float) -> str:
    """Match the Vietnamese whole-number currency presentation used by the UI."""
    return f"{round(float(amount or 0)):,}".replace(",", ".") + " đ"


def draw_pdf_footer(canvas, document) -> None:
    """Draw a restrained LumiHotel footer on every generated report page."""
    canvas.saveState()
    page_width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#C89B52"))
    canvas.setLineWidth(0.75)
    canvas.line(document.leftMargin, 1.28 * cm, page_width - document.rightMargin, 1.28 * cm)
    canvas.setFillColor(colors.HexColor("#6E4B2D"))
    canvas.setFont(get_pdf_font_name(), 8)
    canvas.drawString(document.leftMargin, 0.82 * cm, "LumiHotel • Hotel Management")
    canvas.drawRightString(
        page_width - document.rightMargin,
        0.82 * cm,
        f"Báo cáo thống kê thu nhập • Trang {document.page}",
    )
    canvas.restoreState()


@app.get("/api/revenue-statistics/export")
def export_revenue_statistics_pdf():
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    raw_year = request.args.get("year", "").strip()
    try:
        selected_year = int(raw_year) if raw_year else None
    except ValueError:
        return jsonify({"ok": False, "message": "Năm thống kê không hợp lệ."}), 400

    try:
        report = dashboard_service.get_monthly_revenue(selected_year)
        font_name = get_pdf_font_name()
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.8 * cm,
            leftMargin=1.8 * cm,
            topMargin=1.1 * cm,
            bottomMargin=1.45 * cm,
        )
        styles = getSampleStyleSheet()
        brand_style = styles["BodyText"].clone("PdfBrand")
        brand_style.fontName = font_name
        brand_style.fontSize = 18
        brand_style.leading = 21
        brand_style.textColor = colors.HexColor("#10263F")
        title_style = styles["Title"].clone("VietnameseTitle")
        title_style.fontName = font_name
        title_style.fontSize = 17
        title_style.leading = 22
        title_style.alignment = TA_CENTER
        title_style.textColor = colors.HexColor("#10263F")
        body_style = styles["BodyText"].clone("VietnameseBody")
        body_style.fontName = font_name
        body_style.fontSize = 9.2
        body_style.leading = 13
        body_style.textColor = colors.HexColor("#253746")
        center_style = body_style.clone("PdfCenter")
        center_style.alignment = TA_CENTER
        small_style = body_style.clone("PdfSmall")
        small_style.fontSize = 8
        small_style.leading = 11
        metric_label_style = body_style.clone("PdfMetricLabel")
        metric_label_style.fontSize = 7.4
        metric_label_style.leading = 10
        metric_label_style.textColor = colors.HexColor("#786B5B")
        metric_value_style = body_style.clone("PdfMetricValue")
        metric_value_style.fontSize = 12.5
        metric_value_style.leading = 16
        metric_value_style.textColor = colors.HexColor("#10263F")

        months = report["months"]
        month_totals = [float(item["total"] or 0) for item in months]
        revenue_month_count = sum(total > 0 for total in month_totals)
        has_revenue = revenue_month_count > 0
        highest_index = max(range(12), key=month_totals.__getitem__)
        lowest_index = min(range(12), key=month_totals.__getitem__)
        highest_detail = (
            f"{format_vnd(month_totals[highest_index])}<br/><font size=\"7.5\">Tháng {highest_index + 1}</font>"
            if has_revenue else "0 đ<br/><font size=\"7.5\">Chưa có doanh thu</font>"
        )
        lowest_detail = (
            f"{format_vnd(month_totals[lowest_index])}<br/><font size=\"7.5\">Tháng {lowest_index + 1}</font>"
            if has_revenue else "0 đ<br/><font size=\"7.5\">Chưa có doanh thu</font>"
        )

        def metric(label: str, value: str) -> Paragraph:
            return Paragraph(
                f'<font color="#786B5B" size="7.4">{label}</font><br/>{value}',
                metric_value_style,
            )

        brand = Table([
            [
                Paragraph("L", brand_style),
                Paragraph("LumiHotel<br/><font size=\"7.5\" color=\"#786B5B\">HOTEL MANAGEMENT</font>", brand_style),
                Paragraph(
                    f"<font size=\"8\" color=\"#786B5B\">NĂM THỐNG KÊ</font><br/><font size=\"13\">{report['year']}</font>",
                    body_style,
                ),
            ]
        ], colWidths=[1.05 * cm, 11.1 * cm, 3.8 * cm], rowHeights=[1.12 * cm])
        brand.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#C89B52")),
            ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#B6853E")),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("RIGHTPADDING", (2, 0), (2, 0), 2),
        ]))
        gold_rule = Table([[""]], colWidths=[15.95 * cm], rowHeights=[0.08 * cm])
        gold_rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#C89B52"))]))

        overview = Table([
            [
                metric("TỔNG THU NHẬP CẢ NĂM", format_vnd(report["total"])),
                metric("SỐ THÁNG CÓ DOANH THU", f"{revenue_month_count} / 12"),
            ],
            [
                metric("DOANH THU CAO NHẤT", highest_detail),
                metric("DOANH THU THẤP NHẤT", lowest_detail),
            ],
        ], colWidths=[7.975 * cm, 7.975 * cm], rowHeights=[1.42 * cm, 1.42 * cm])
        overview.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FCF8F0")),
            ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor("#E3D0A2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E3D0A2")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))

        rows = [["STT", "Tháng", "Tổng tiền của tháng"]]
        rows.extend([
            [str(index), f"Tháng {item['month']}", format_vnd(item["total"])]
            for index, item in enumerate(months, start=1)
        ])
        rows.append(["", "TỔNG THU NHẬP CẢ NĂM", format_vnd(report["total"])])
        table = Table(rows, colWidths=[1.3 * cm, 6.25 * cm, 8.4 * cm], repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C89B52")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#10263F")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 9), (-1, 9), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 11), (-1, 11), colors.HexColor("#FCF8F0")),
            ("BACKGROUND", (0, 13), (-1, 13), colors.HexColor("#F5E7C7")),
            ("TEXTCOLOR", (0, 13), (-1, 13), colors.HexColor("#10263F")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E1D6C5")),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (2, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ]))
        exported_at = datetime.now().strftime("%d/%m/%Y, %H:%M")
        report_preparer = str(session.get("user", {}).get("full_name", "")).strip()
        signature_name = report_preparer if report_preparer else " "
        signature = Table([
            [Paragraph(f"Ngày lập báo cáo: {exported_at}", small_style)],
            [Paragraph("Người lập báo cáo", center_style)],
            [Spacer(1, 0.72 * cm)],
            [Paragraph(signature_name, center_style)],
        ], colWidths=[6.3 * cm])
        signature.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        document.build([
            brand,
            Spacer(1, 0.1 * cm),
            gold_rule,
            Spacer(1, 0.22 * cm),
            Paragraph("BÁO CÁO THỐNG KÊ THU NHẬP", title_style),
            Paragraph("LUMIHOTEL – HOTEL MANAGEMENT", center_style),
            Spacer(1, 0.12 * cm),
            Paragraph(f"Báo cáo năm {report['year']} • Xuất lúc {exported_at}", center_style),
            Spacer(1, 0.22 * cm),
            overview,
            Spacer(1, 0.23 * cm),
            Paragraph("CHI TIẾT DOANH THU THEO THÁNG", body_style),
            Spacer(1, 0.08 * cm),
            table,
            Spacer(1, 0.18 * cm),
            Paragraph("GHI CHÚ", body_style),
            Paragraph(
                "• Doanh thu được tổng hợp từ dữ liệu hợp lệ của hệ thống.<br/>"
                "• Các tháng không có doanh thu được hiển thị 0 đ.<br/>"
                "• Tổng thu nhập năm bằng tổng doanh thu của 12 tháng.<br/>"
                "• Báo cáo được xuất từ hệ thống LumiHotel – Hotel Management.",
                small_style,
            ),
            Spacer(1, 0.08 * cm),
            Table([["", signature]], colWidths=[9.65 * cm, 6.3 * cm]),
        ], onFirstPage=draw_pdf_footer, onLaterPages=draw_pdf_footer)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"LumiHotel_ThongKeThuNhap_{report['year']}.pdf",
        )
    except Exception as exc:
        app.logger.exception("Không thể xuất báo cáo doanh thu PDF")
        return jsonify({"ok": False, "message": f"Không thể xuất PDF: {exc}"}), 500


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


@app.post("/api/rooms/<int:room_id>/checkout")
def checkout_room(room_id):
    if not login_required():
        return jsonify({"ok": False, "message": "Vui lòng đăng nhập."}), 401

    ok, message, room = room_service.checkout_room(room_id)
    if ok:
        return jsonify({"ok": True, "message": message, "room": room}), 200
    status_code = 404 if message == "Phòng không tồn tại." else 409
    return jsonify({"ok": False, "message": message}), status_code


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
