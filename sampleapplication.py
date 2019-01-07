import os
import datetime
from PyAstronomy import pyasl
from collections import Counter

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///DiscoverU.db")


@app.route("/")
@login_required
def homepage():
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Runs if the request method is POST
    if request.method == "POST":
        # Gets items from the register form
        username = request.form.get("username")
        password = request.form.get("password")
        password_conf = request.form.get("confirmation")
# https://docs.python.org/2/library/constants.html
    # Error checks for missing fields
        if not username:
            return apology("Missing username!", 400)
        if not password:
            return apology("Missing password!", 400)
        if not password_conf:
            return apology("Missing password confirmation!", 400)
    # Error checks for a password confirmation that doesn't match the password
        if password != password_conf:
            return apology("Passwords do not match!", 400)
    # My personal touch. Makes sure that there are exactly 5 letters and 2 numbers in the password(As suggested on CS50 discourse)
        letter_counter = 0
        digit_counter = 0
        for letter in password:
            if letter.isalpha():
                letter_counter = letter_counter+1
            if letter.isdigit():
                digit_counter = digit_counter+1
        if letter_counter < 5:
            return apology("Please enter a password with 5 letters and 2 numbers")
        if digit_counter < 2:
            return apology("Please enter a password with 5 letters and 2 numbers")
        # Hashes the password for security purposes.
        hash = generate_password_hash(password)
        # Inserts the registered user into to the users table
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                            username=request.form.get("username"), hash=hash)
        # Ensures that the username was not already taken
        if not result:
            return apology("Sorry! That one's taken already!", 400)
        # Keeps the user logged in
        session["user_id"] = result
        # Redirects the user to index
        return redirect("/")
    # Renders the register.html template if the request method is GET.
    else:
        return render_template("register.html")


datetime_now = datetime.datetime.now()


@app.route("/Daily", methods=["GET", "POST"])
def Daily():
    # Runs if the request method is POST
    if request.method == "POST":
        # Gets the rating from the user's form
        rating = request.form.get("rating")
# Makes sure the user provided a rating
        if not rating:
            return apology("Please enter a rating", 400)
# Gets the notes the user provided
        notes = request.form.get("notes")
# Makes sure the user provided notes
        if not notes:
            return apology("Enter all fields", 400)
# Gets the emotional rating the user provided on the form
        emotions = request.form.get("emotional")
# Makes sure the user provided an emotional rating
        if not emotions:
            return apology("Please enter an emotional rating", 400)
# Gets the mental rating the user provided
        mental = request.form.get("mental")
# Makes sure the user provided a value for mental rating
        if not mental:
            return apology("Please enter a mental rating", 400)
# Gets the physical rating the user provided
        physical = request.form.get("physical")
# Makes sure the user provided a physical rating
        if not physical:
            return apology("Please enter a physical rating", 400)
# Stores the current user_id
        user_id = db.execute("SELECT id FROM users WHERE id=:idd", idd=session["user_id"])[0]["id"]
# Inserts the values into the database
        insertion = db.execute("INSERT INTO Info (rating, emotions, mental, physical, notes, user_id) VALUES(:rating, :emotions, :mental, :physical, :notes, :user_id)",
                               rating=rating, emotions=emotions, mental=mental, physical=physical, notes=notes, user_id=user_id)
        return redirect("/")
    else:
        return render_template("Daily.html")


@app.route("/visual", methods=["GET", "POST"])
@login_required
def visual():
    # Runs if the request method is post
    if request.method == "POST":
        return render_template("visual.html")
    # Runs if the request method is get
    else:
        # Stores the current user id
        user_id = db.execute("SELECT id FROM users WHERE id=:idd", idd=session["user_id"])[0]["id"]
        # Selects the overall rating from the database
        selection = db.execute("SELECT rating FROM info WHERE user_id=:user_id", user_id=user_id)
        # Selects the physical rating from the database
        physical_selection = db.execute("SELECT physical FROM info WHERE user_id=:user_id", user_id=user_id)
        # Selects the mental rating from the database
        mental_selection = db.execute("SELECT mental FROM info WHERE user_id=:user_id", user_id=user_id)
        # Selects the emotional rating from the database
        emotions_selection = db.execute("SELECT emotions FROM info WHERE user_id=:user_id", user_id=user_id)
        # Selects the id from the database
        ids = db.execute("SELECT id FROM info WHERE user_id=:user_id", user_id=user_id)
        # Creates the arrays for individual ratings to be stored in
        rating = []
        physical = []
        mental = []
        emotions = []
        id_collection = []
        # Iterates over the items in overall rating
        for i in selection:
            rating.append(i["rating"])
        # Iterates over the items in physical rating
        for i in physical_selection:
            physical.append(i["physical"])
        # Iterates over the items in mental rating
        for i in mental_selection:
            mental.append(i["mental"])
        # iterates over the items in ids
        for i in ids:
            id_collection.append(i["id"])
        # iterates over the items in emotions_selection
        for i in emotions_selection:
            emotions.append(i["emotions"])
        return render_template("visual.html", rating=rating, id_collection=id_collection, physical=physical, mental=mental, emotions=emotions)


@app.route("/frequency", methods=["GET"])
@login_required
def frequency():
    if request.method == "GET":
        user_id = db.execute("SELECT id FROM users WHERE id=:idd", idd=session["user_id"])[0]["id"]
        note_selection = db.execute("SELECT notes FROM Info WHERE user_id=:user_id", user_id=user_id)
        words_lists = []
# https://pymotw.com/2/collections/counter.html
        for i in note_selection:
            words_lists.append(i["notes"].split(" "))
        words = []
        for i in words_lists:
            for j in i:
                words.append(j)
        print(words)
        counts = Counter((words))
# https://www.tutorialspoint.com/python/dictionary_keys.html
        print(counts)
        mentions = []
        for word in words:
            mentions.append("You mentioned %s the following number of times:%s" % (word, counts[word]))
        mentions = set(mentions)
        print(mentions)
        return render_template("frequency.html", mentions=mentions)
    else:
        return render_template("frequency.html", mentions=mentions)


@app.route("/mental_health", methods=["GET"])
@login_required
def mental_health():
    # Renders the template for mental health
    return render_template("mental_health.html")


@app.route("/faq", methods=["GET"])
@login_required
def faq():
    return render_template("faq.html")


@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    # Runs if the request method is post
    if request.method == "POST":
        # Gets the form submission value
        submitted = request.form.get("feeling")
# Declares the variables for the if-blocks so they can be passed into the template
        happy = ""
        hwording = ""
        angry = ""
        awording = ""
        frustrated = ""
        fwording = ""
        nervous = ""
        nerwording = ""
        sad = ""
        swording = ""
        # If the user submitted happy, then it sets variables to the GIF to be displayed and the wording to be displayed
        if submitted == "happy":
            happy = "https://thumbor.thedailymeal.com/RsVwTGdS-m9GT7Nkz04NR9aVTqU=/774x516/https://www.theactivetimes.com/sites/default/files/uploads/r/rsz_front_shutterstock_163379924.jpg"
            hwording = "You're already happy! While exercise is always a good thing, you can do whatever you'd like at the gym as long as you're channeling your energy in a positive way."
        #  If the user submitted angry, then it sets variables to the GIF to be displayed and the wording to be displayed
        if submitted == "angry":
            angry = "https://media.giphy.com/media/J99LWJ61hkOVq/giphy.gif"
            awording = "We recommend a nice hard run! Feel free to use either a treadmill or to run outdoors. Studies show that a run is the best way to relieve anger."
        #  If the user submitted frustrated, then it sets variables to the GIF to be displayed and the wording to be displayed
        if submitted == "frustrated":
            frustrated = "https://gifyu.com/images/conor1.gif"
            fwording = "The best type of workout for frustration is some form of martial arts. Whether it be boxing, wrestling, kickboxing or jiu-jitsu."
        #  If the user submitted nervous, then it sets variables to the GIF to be displayed and the wording to be displayed
        if submitted == "nervous":
            nervous = "https://media.giphy.com/media/3oKIPavRPgJYaNI97W/source.gif"
            nerwording = "If you are stressed out or anxious then yoga is your best option. It is a wonderful option to clear the mind."
        #  If the user submitted sad, then it sets variables to the GIF to be displayed and the wording to be displayed
        if submitted == "sad":
            sad = "https://media.giphy.com/media/mJU6hvRgjJkha/giphy.gif"
            swording = "Believe it or not, it has been proven that going for a swim is the best way to get out of a particularly sad state of mind. Find a pool to go for a swim and have fun!"
        return render_template("exercise.html", happy=happy, hwording=hwording, angry=angry, awording=awording, frustrated=frustrated, fwording=fwording, nervous=nervous, nerwording=nerwording, sad=sad, swording=swording)

    else:
        return render_template("exercise.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
