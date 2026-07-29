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
import re


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SECRET_KEY"] = "change-this-secret"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# PASSWORD CHECK

def strong_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True



class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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



@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        if not strong_password(password):

            return """
            Password must contain:
            <br>• Minimum 8 characters
            <br>• One uppercase letter
            <br>• One lowercase letter
            <br>• One number
            <br>• One special character
            """



        existing = User.query.filter_by(
            username=username
        ).first()


        if existing:
            return "Username already exists"



        user = User(
            username=username,
            password=generate_password_hash(password)
        )


        db.session.add(user)
        db.session.commit()


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )



@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]


        user=User.query.filter_by(
            username=username
        ).first()


        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("home")
            )


    return render_template(
        "login.html"
    )



@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )



@app.route("/add", methods=["POST"])
@login_required
def add():

    note=Note(
        title=request.form["title"],
        content=request.form["note"],
        user_id=current_user.id
    )

    db.session.add(note)
    db.session.commit()

    return redirect(
        url_for("home")
    )



@app.route("/delete/<int:id>")
@login_required
def delete(id):

    note=Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))


    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("home"))



@app.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit(id):

    note=Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))


    if request.method=="POST":

        note.title=request.form["title"]
        note.content=request.form["note"]

        db.session.commit()

        return redirect(
            url_for("view_note",id=id)
        )


    return render_template(
        "edit.html",
        note=note
    )



@app.route("/note/<int:id>")
@login_required
def view_note(id):

    note=Note.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(url_for("home"))


    return render_template(
        "view.html",
        note=note
    )



@app.route("/settings")
@login_required
def settings():

    return render_template(
        "settings.html"
    )



@app.route("/new")
@login_required
def new():

    return render_template(
        "new.html"
    )



@app.route("/change-password", methods=["GET","POST"])
@login_required
def change_password():

    if request.method=="POST":

        old=request.form["old_password"]
        new=request.form["new_password"]


        if not check_password_hash(
            current_user.password,
            old
        ):
            return "Old password incorrect"


        if not strong_password(new):

            return """
            New password is weak.
            <br>Password needs:
            <br>8+ characters,
            uppercase,
            lowercase,
            number,
            special character
            """



        current_user.password = generate_password_hash(
            new
        )

        db.session.commit()


        return redirect(
            url_for("settings")
        )


    return render_template(
        "change_password.html"
    )



with app.app_context():
    db.create_all()



if __name__=="__main__":
    app.run(debug=True)