# app.py
import os
from cs50 import SQL
from flask import Flask, render_template, request, flash, redirect, session, send_from_directory
from gradio_client import Client
from datetime import datetime
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, admin_required
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Define the home route


@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_ = request.form.get("confirmation")
        if username == "" or password == "" or password_ == "":
            return apology("All field must not be empty", 400)
        elif password != password_:
            return apology("Password doesn't match", 400)
        else:
            existing_username = db.execute(
                "SELECT username FROM users where username == ?", username
            )
            # print(f"existing user: {existing_username}")
            if existing_username:
                return apology("Username already exist", 400)
            else:
                hash = generate_password_hash(password)
                insert = db.execute(
                    "INSERT INTO users (username, hash) VALUES(?, ?)", username, hash
                )
                # print(f"insert: {insert}")

                # Remember which user has logged in
                session["user_id"] = insert

                # Redirect user to home page
                return redirect("/")

    return render_template("register.html")


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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


# Define the route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']

        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Generate a timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # Get the file extension
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        # Create a new filename with the timestamp
        new_filename = f"{timestamp}.{file_extension}"
        # Save the file to the uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)

        client = Client(
            "https://kvpratama-plant-disease.hf.space/--replicas/fflcf/")
        result = client.predict(filepath, api_name="/predict")
        print(result)

        transaction = db.execute(
            "INSERT INTO images (image_path, prediction, prediction_json, user_id, transacted) VALUES(?, ?, ?, ?, CURRENT_TIMESTAMP)",
            filepath,
            result["label"],
            json.dumps(result),
            session["user_id"],
        )

        # Extract labels and confidences from the result
        labels = [entry['label'] for entry in result['confidences']]
        confidences = [entry['confidence'] for entry in result['confidences']]
        print(confidences)

        # Render the result page with the chart
        return render_template('result.html', filepath=filepath, labels=labels, confidences=confidences)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    images = db.execute(
        "SELECT * FROM images where user_id == ?", session["user_id"])
    classes = db.execute("SELECT * FROM classes")
    return render_template("history.html", images=images, classes=classes)


@app.route("/details", methods=["GET", "POST"])
def details():
    if request.method == 'POST':
        # Check if the POST request has the file part
        image_id = request.form.get("image_id")

        images = db.execute(
            "SELECT * FROM images where image_id == ?", image_id)

        filepath = images[0]['image_path']
        labels = [entry['label'] for image in images for entry in json.loads(
            image['prediction_json'])['confidences']]
        confidences = [entry['confidence'] for image in images for entry in json.loads(
            image['prediction_json'])['confidences']]

        # # Render the result page with the chart
        return render_template('result.html', filepath=filepath, labels=labels, confidences=confidences)


@app.route("/suggest", methods=["GET", "POST"])
def suggest():
    if request.method == 'POST':
        # Check if the POST request has the file part
        image_id = request.form.get("image_id")
        suggested = request.form.get("suggestedPrediction")

        images = db.execute(
            "UPDATE images SET prediction_user = ? WHERE image_id = ?", suggested, image_id)
        return redirect("/feedback")


@app.route("/feedback")
@login_required
def feedback():
    """Show history of feedback"""
    images = db.execute(
        "SELECT * FROM images where prediction_user not null and user_id == ?", session["user_id"])
    return render_template("feedback.html", images=images)


@app.route("/feedback-users")
@admin_required
def feedbackUsers():
    """Show history of feedback"""
    images = db.execute(
        "SELECT images.image_path, images.prediction, images.prediction_user, users.username " +
        "FROM images AS images JOIN users AS users ON images.user_id = users.id " +
        "WHERE images.prediction_user NOT NULL;"
    )
    return render_template("feedback-users.html", images=images)

# Serve uploaded images


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
