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



@app.route("/users/<user_id>")
def user_details(user_id):
    """User details, shows all movies rated by user."""

    # Get user OBJECT
    user = User.query.get(user_id)

    # All movies rated by user.
    movie_ratings = (db.session.query(Movie, Rating)
                               .join(Rating).filter(Rating.user_id == user_id)
                               .order_by(Movie.title).all())

    return render_template("user_details.html", user=user
                                              , movie_ratings=movie_ratings
                                              , session=session)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<int:movie_id>")
def movie_details(movie_id):
    """Show movie detail page with all ratings for that movie."""

    movie = Movie.query.get(movie_id)

    ratings = movie.ratings

    # If logged in, allow to rate the movie.
    if session['current_user']:
        user_rating = (db.session.query(Rating.score)
                         .filter(Rating.user_id == session['current_user']
                         , Rating.movie_id == movie_id).first())

    # If user has not rated the movie, show no user rating.
    else:
        user_rating = None

    return render_template("movie_details.html", movie=movie
                                               , ratings=ratings
                                               , session=session
                                               , user_rating=user_rating)


@app.route("/rate_movie", methods=["POST"])
def rate_movie():
    """Adds or updates rating in database."""

    # Grab parameters from HTML form.
    score = int(request.form.get('rating'))
    movie_id = request.form.get('movie_id')
    user_id = request.form.get('user_id')

    # If there is a rating from that user for that movie, update to new rating.
    if (Rating.query.filter(Rating.movie_id == movie_id
                                  , Rating.user_id == user_id).first()):

        #  Grab rating object for specific movie and user.
        rating = (Rating.query.filter(Rating.movie_id == movie_id
                              , Rating.user_id == user_id).one())

        # Update score attribute to new score.
        rating.score = score
        db.session.commit()

    #  If there is no rating, add rating to database.
    else:
        # Create a rating object. Add and commit to database.
        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(rating)
        db.session.commit()

    redirect_path = '/movies/%s' % movie_id
    return redirect(redirect_path)



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

            # Tried to put path as argument, but had to make variable first
            redirect_path = '/users/%s' % str(user.user_id)
            return redirect(redirect_path) 

        # If wrong password, flash message, redirect to login
        else:
            flash("Wrong password!")
            return redirect("/login")

    # If email is not in database, flash message, redirect to /login
    else:
        flash("Email is not in use.  Please register.")
        return redirect("/login")



@app.route("/logout", methods=["POST"])
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
