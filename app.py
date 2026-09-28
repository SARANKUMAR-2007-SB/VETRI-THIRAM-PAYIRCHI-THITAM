import os
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from services.db import (
    add_activity, add_quiz_result, create_user, get_activity,
    get_quiz_results, get_user_by_email, get_user_by_id, init_db
)
from services.gemini_service import GeminiService
from services.pdf_service import extract_pdf_text

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-in-production")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

init_db()
gemini = GeminiService()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter a name, valid email, and password of at least 6 characters.")
            return render_template("register.html")
        if get_user_by_email(email):
            flash("An account with this email already exists.")
            return render_template("register.html")
        user_id = create_user(name, email, generate_password_hash(password))
        session["user_id"] = user_id
        session["user_name"] = name
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    return render_template(
        "dashboard.html",
        user=get_user_by_id(user_id),
        activities=get_activity(user_id, 8),
        quiz_results=get_quiz_results(user_id, 8)
    )

@app.post("/api/qna")
@login_required
def qna():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify(error="Please enter a question."), 400
    try:
        answer = gemini.qna(question)
        add_activity(session["user_id"], "QnA", question[:100], answer)
        return jsonify(answer=answer)
    except Exception as exc:
        return jsonify(error=str(exc)), 500

@app.post("/api/summary")
@login_required
def summary():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(error="Please enter text to summarize."), 400
    try:
        result = gemini.summary(text)
        add_activity(session["user_id"], "Summary", "Study material", result)
        return jsonify(summary=result)
    except Exception as exc:
        return jsonify(error=str(exc)), 500

@app.post("/api/quiz")
@login_required
def quiz():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(error="Please enter a passage."), 400
    try:
        result = gemini.quiz(text)
        add_activity(session["user_id"], "Quiz", "Generated 3 MCQs", str(result))
        return jsonify(quiz=result)
    except Exception as exc:
        return jsonify(error=str(exc)), 500

@app.post("/api/quiz/result")
@login_required
def quiz_result():
    data = request.get_json() or {}
    add_quiz_result(session["user_id"], int(data.get("score", 0)), int(data.get("total", 3)))
    return jsonify(ok=True)

@app.post("/api/learning-path")
@login_required
def learning_path():
    data = request.get_json() or {}
    topic = (data.get("topic") or "").strip()
    level = (data.get("level") or "Beginner").strip()
    if not topic:
        return jsonify(error="Please enter a topic."), 400
    try:
        result = gemini.learning_path(topic, level)
        add_activity(session["user_id"], "Learning Path", f"{topic} ({level})", result)
        return jsonify(path=result)
    except Exception as exc:
        return jsonify(error=str(exc)), 500

@app.post("/api/pdf")
@login_required
def pdf_upload():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify(error="Please upload a PDF file."), 400
    safe_name = secure_filename(file.filename)
    path = UPLOAD_DIR / safe_name
    file.save(path)
    try:
        text = extract_pdf_text(path)
        if not text.strip():
            return jsonify(error="No readable text was found in the PDF."), 400
        return jsonify(text=text[:50000], filename=safe_name)
    finally:
        try:
            path.unlink()
        except OSError:
            pass

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
