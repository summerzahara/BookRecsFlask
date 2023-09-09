from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "your mom"
app.permanent_session_lifetime = timedelta(minutes=15)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///book_recs.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

book_recs = [
    ['Pride & Prejudice', 'Jane Austen'],
    ['The Hunger Games', 'Suzzanne Collins'],
    ['The Trial', 'Franz Kafka']
]


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.Date, default=datetime.utcnow)
    books = db.relationship("BookRec", backref="recommender")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class BookRec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(300), unique=True, nullable=False)
    book_author = db.Column(db.String(300), nullable=False)
    created_date = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __int__(self, book_tile, book_author):
        self.book_title = book_tile
        self.book_author = book_author


with app.app_context():
    db.create_all()


@app.route('/')
def index():  # put application's code here
    return render_template("index.html", book_recs=book_recs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["user-name"]
        user_email = request.form["user-email"]
        user_password = request.form["user-pass"]
        session["email"] = user_email

        # Add New user
        new_user = Users(user_name, user_email, user_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect(url_for("login", name=user_name, email=user_email))
        except Exception as e:
            db.session.rollback()
            return f"Commit failed. Error: {e}"
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        user_email = request.form["user-email"]
        session["email"] = user_email
        flash("Login Successful!")
        return redirect(url_for("success"))
    else:
        if "email" in session:
            flash("Already logged in!")
            return redirect(url_for("success"))
        return render_template("login.html")


@app.route("/success", methods=["POST", "GET"])
def success():
    new_rec = None
    if "email" in session:
        user_email = session["email"]
        current_user = Users.query.filter_by(email=user_email).first()
        user_name = current_user.name
        user_id = current_user.id

        if request.method == "POST":
            new_rec_title = request.form["new_rec_title"]
            new_rec_author = request.form["new_rec_author"]
            book_recs.append([new_rec_title, new_rec_author])

            new_rec = BookRec(book_title=new_rec_title, book_author=new_rec_author, user_id=user_id)
            db.session.add(new_rec)
            try:
                db.session.commit()
                flash("Book Recommendation Added!")
                render_template("success.html", name=user_name, book_recs=book_recs,new_rec_title=new_rec_title,
                                new_rec_author=new_rec_author)
            except Exception as e:
                db.session.rollback()
                return f"Commit failed. Error: {e}"

        return render_template("success.html", name=user_name, book_recs=book_recs)
    else:
        flash("You're not logged in.")
        return redirect(url_for("login"))


@app.route("/logout", methods=["GET"])
def logout():
    if "email" in session:
        email = session["email"]
        flash(f"You have been logged out, {email}.", "info")
    session.pop("email", None)
    session.pop("new_rec", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    db.drop_all()
    app.run()
