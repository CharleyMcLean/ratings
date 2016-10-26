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
    # Pass sessions to determine whether to show login or logout
    return render_template("homepage.html", session=session)

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)



@app.route("/register", methods=["GET"])
def register_form():
    """Registration Form"""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Register as a user"""

    # Grab form inputs
    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    # Check if email already associated with a user
    if User.query.filter(User.email == email).first():
        flash("Email already in use.")
    # If not create user instance, add to db and commit
    else:
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        flash("You are registered! Please login")

    return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():
    """Login Form"""

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_process():
    """Login process"""

    # Get email and password from input fields in form
    email = request.form.get('email')
    password = request.form.get('password')


    # If email is in database, grab password from database
    if User.query.filter(User.email == email).first():
        # Grab user OBJECT
        user = User.query.filter(User.email==email).first()

        db_password = user.password

        # Check if provided pw matches db pw
        if password == db_password:

            # Set session cookie to user_id from user OBJECT
            session['current_user'] = user.user_id 
            flash("Logged in as %s" % user.email)
            return redirect("/")

        # If wrong password, flash message, redirect to login
        else:
            flash("Wrong password!")
            return redirect("/login")

    # If email is not in database, flash message, redirect to /login
    else:
        flash("Email is not in use.  Please register.")
        return redirect("/login")


@app.route("/logout")
def logout():
    """"Logout User"""

    # delete specific session for user from session dictionary
    del session['current_user']
    flash("You've been logged out")

    return redirect("/")
    

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    # Prevent redirects
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    
    app.run(port=5000)
