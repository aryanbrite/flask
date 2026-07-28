from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SECRET_KEY"] = "change-this-secret"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------------
# MODELS
# ------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(100),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------------
# HOME
# ------------------------

@app.route("/")
@login_required
def home():

    notes = Note.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Note.created_at.desc()
    ).all()

    return render_template(
        "index.html",
        notes=notes
    )


# ------------------------
# REGISTER
# ------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        existing = User.query.filter_by(
            username=username
        ).first()

        if existing:
            return "Username already exists."

        user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------------
# LOGIN
# ------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(url_for("home"))

    return render_template("login.html")


# ------------------------
# LOGOUT
# ------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# ------------------------
# ADD NOTE
# ------------------------

@app.route("/add", methods=["POST"])
@login_required
def add():

    title = request.form["title"]
    content = request.form["note"]

    note = Note(
        title=title,
        content=content,
        user_id=current_user.id
    )

    db.session.add(note)
    db.session.commit()

    return redirect(url_for("home"))


# ------------------------
# DELETE
# ------------------------

@app.route("/delete/<int:id>")
@login_required
def delete(id):

    note = Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("home"))


# ------------------------
# EDIT
# ------------------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    note = Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))

    if request.method == "POST":

        note.title = request.form["title"]
        note.content = request.form["note"]

        db.session.commit()

        return redirect(url_for("view_note", id=note.id))

    return render_template(
        "edit.html",
        note=note
    )

@app.route("/note/<int:id>")
@login_required
def view_note(id):

    note = Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))

    return render_template(
        "view.html",
        note=note
    )


# ------------------------
# SETTINGS
# ------------------------

@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html"
    )


with app.app_context():
    db.create_all()

@app.route("/new")
@login_required
def new():
    return render_template("new.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        old = request.form["old_password"]
        new = request.form["new_password"]

        if check_password_hash(current_user.password, old):

            current_user.password = generate_password_hash(new)

            db.session.commit()

            return redirect(url_for("settings"))

    return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True)