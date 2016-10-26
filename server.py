"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify
from flask_debugtoolbar import DebugToolbarExtension

# from model import connect_to_db, db

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    # print User.query.filter(User.email == email).first()

    if User.query.filter(User.email == email).first():
        flash("Email already in use.")
    else:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        flash("You are registered! Please login")

    # store some sort of session that indicates logged in

    return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_process():
    

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter(User.email == email).first():
        user = User.query.filter(User.email==email).first()

        db_password = user.password

        if password == db_password:
            session['current_user'] = user.user_id
            flash("Logged in as %s" % user.email)
            return redirect("/")

        else:
            flash("Wrong password!")
            return redirect("/login")

    else:
        flash("Email is not in use.  Please register.")
    return redirect("/login")

    



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000)
