from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your mom"
app.permanent_session_lifetime = timedelta(minutes=15)

book_recs = ['Pride & Prejudice', 'The Hunger Games', 'The Trial']


@app.route('/')
def index():  # put application's code here
    return render_template("index.html", book_recs=book_recs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["user-email"]
        password = request.form["user-pass"]
        return redirect(url_for("success", email=email))
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["user-email"]
        session["email"] = email
        flash("Login Successful!")
        return redirect(url_for("success"))
    else:
        if "email" in session:
            flash("Already logged in!")
            return redirect(url_for("success"))
        return render_template("login.html")


@app.route("/success")
def success():
    if "email" in session:
        email = session["email"]
        return render_template("success.html", email=email)
    else:
        flash("You're not logged in.")
        return redirect(url_for("login"))


@app.route("/logout", methods=["GET"])
def logout():
    if "email" in session:
        email = session["email"]
        flash(f"You have been logged out, {email}.", "info")
    session.pop("email", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
