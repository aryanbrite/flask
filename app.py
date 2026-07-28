from flask import Flask, render_template, redirect, url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///notes.db"

db = SQLAlchemy(app)

class Note (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)



@app.route("/")
def home():
    title = "Notes"
    return render_template("index.html", title=title, notes=Note.query.all())

@app.route("/add", methods=["POST"])
def add():
    ho = request.form["note"]
    new_note =Note(content=ho)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()
@app.route("/delete/<int:id>")
def delete(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

