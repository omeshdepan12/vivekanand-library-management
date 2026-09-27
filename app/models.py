from datetime import datetime, timedelta
import random

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.models import Admin, Student, Payment, AutoPay, AuditLog

main_bp = Blueprint("main", __name__)


def generate_otp():
    return str(random.randint(100000, 999999))


def login_required(user_type=None):
    def decorator(view_func):
        def wrapped(*args, **kwargs):
            if "user_id" not in session or "user_type" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("main.login"))

            if user_type and session.get("user_type") != user_type:
                flash("You do not have access to this page.", "danger")
                return redirect(url_for("main.home"))
            return view_func(*args, **kwargs)

        wrapped.__name__ = view_func.__name__
        return wrapped

    return decorator


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        student_id = request.form.get("student_id", "").strip()
        joining_date = request.form.get("joining_date", "").strip()
        batch = request.form.get("batch", "").strip()
        monthly_fee = float(request.form.get("monthly_fee", 0) or 0)
        emergency_contact = request.form.get("emergency_contact", "").strip()

        if not all([name, mobile, student_id, joining_date, batch, emergency_contact]):
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("main.register"))

        if Student.query.filter((Student.mobile == mobile) | (Student.student_id == student_id)).first():
            flash("Mobile number or Student ID already exists.", "danger")
            return redirect(url_for("main.register"))

        student = Student(
            name=name,
            mobile=mobile,
            student_id=student_id,
            joining_date=joining_date,
            batch=batch,
            monthly_fee=monthly_fee,
            emergency_contact=emergency_contact,
            status="active"
        )
        db.session.add(student)
        db.session.commit()
        AuditLog.log("student", "registered", f"Student {name} registered.")

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form.get("user_type")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if user_type == "student":
            student = Student.query.filter_by(mobile=username).first()
            if student and student.student_id == password:
                otp = generate_otp()
                session["otp_pending"] = {
                    "user_type": "student",
                    "user_id": student.id,
                    "user_name": student.name,
                    "identifier": student.mobile,
                    "otp_code": otp,
                    "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                }
                flash(f"OTP sent to {student.mobile}. Demo OTP: {otp}", "info")
                return redirect(url_for("main.verify_otp"))

            flash("Invalid student login details.", "danger")
            return redirect(url_for("main.login"))

        if user_type == "admin":
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.password == password:
                otp = generate_otp()
                session["otp_pending"] = {
                    "user_type": "admin",
                    "user_id": admin.id,
                    "user_name": admin.name,
                    "identifier": admin.username,
                    "otp_code": otp,
                    "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                }
                flash(f"Admin OTP generated. Demo OTP: {otp}", "info")
                return redirect(url_for("main.verify_otp"))

            flash("Invalid admin credentials.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")


@main_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    pending = session.get("otp_pending")

    if not pending:
        flash("No pending OTP session found.", "warning")
        return redirect(url_for("main.login"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        stored_otp = pending.get("otp_code")

        if stored_otp and stored_otp == entered_otp:
            session["user_id"] = pending["user_id"]
            session["user_type"] = pending["user_type"]
            session["name"] = pending["user_name"]
            session.pop("otp_pending", None)
            flash("OTP verified successfully.", "success")

            if pending["user_type"] == "student":
                return redirect(url_for("main.student_dashboard"))
            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid OTP. Please try again.", "danger")

    return render_template("otp_verify.html", otp_value=pending.get("otp_code"), target=pending.get("identifier"))


@main_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@main_bp.route("/student/dashboard")
@login_required("student")
def student_dashboard():
    student = Student.query.get_or_404(session["user_id"])
    payments = Payment.query.filter_by(student_id=student.id).all()
    auto_pay = AutoPay.query.filter_by(student_id=student.id).first()
    return render_template("student/dashboard.html", student=student, payments=payments, auto_pay=auto_pay)


@main_bp.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    students = Student.query.order_by(Student.id.desc()).all()
    total_students = Student.query.count()
    active_students = Student.query.filter_by(status="active").count()
    inactive_students = Student.query.filter_by(status="inactive").count()
    pending_fees = Payment.query.filter_by(status="pending").count()
    collections = sum(payment.amount for payment in Payment.query.filter_by(status="paid").all())

    return render_template(
        "admin/dashboard.html",
        students=students,
        total_students=total_students,
        active_students=active_students,
        inactive_students=inactive_students,
        pending_fees=pending_fees,
        collections=collections,
    )


@main_bp.route("/student/fees")
@login_required("student")
def student_fees():
    student = Student.query.get_or_404(session["user_id"])
    payments = Payment.query.filter_by(student_id=student.id).all()
    return render_template("student/fees.html", student=student, payments=payments)


@main_bp.route("/admin/students")
@login_required("admin")
def admin_students():
    students = Student.query.all()
    return render_template("admin/students.html", students=students)


@main_bp.route("/student/payments")
@login_required("student")
def student_payments():
    student = Student.query.get_or_404(session["user_id"])
    payments = Payment.query.filter_by(student_id=student.id).all()
    return render_template("student/payments.html", student=student, payments=payments)


@main_bp.route("/admin/payments")
@login_required("admin")
def admin_payments():
    payments = Payment.query.all()
    return render_template("admin/payments.html", payments=payments)


@main_bp.route("/admin/audit")
@login_required("admin")
def admin_audit():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return render_template("admin/audit.html", logs=logs)
