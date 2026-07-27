from flask import Flask, render_template
from flask import request

app=Flask(__name__)

@app.route("/")
def home():
    title = "notes app"
    return render_template("index.html", title=title)
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/app", methods=["POST"])
def add():
    request.form["note"]