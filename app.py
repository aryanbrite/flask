from flask import Flask, render_template, redirect, url_for
from flask import request

app=Flask(__name__)

notes = []


@app.route("/")
def home():
    title = "Notes"
    return render_template("index.html", title=title, notes=notes)

@app.route("/add", methods=["POST"])
def add():
    ho = request.form["note"]
    notes.append(ho)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

