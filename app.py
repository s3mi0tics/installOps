import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///installOps.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


""" INDEX READ/View jobs that are not completed """
@app.route("/")
@login_required
def index():
    """ Two tables showing scheduled and unscheduled jobs that are not complete"""
    # Get user info for layout
    user_id = session.get("user_id")
    user_table = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_table[0]["username"]
    first_name = user_table[0]["first_name"]
    last_name = user_table[0]["last_name"]
    role = user_table[0]["role"]

    # Get count of scheduled and unscheduled jobs:
    unscdCount_table = db.execute("SELECT COUNT(*) AS count FROM jobs LEFT JOIN installs ON jobs.id = installs.job_id WHERE installs.user_id is ? and completed = ?", None, 0)
    unscdCount = unscdCount_table[0]["count"]
    scdCount_table = db.execute("SELECT COUNT(*) AS count FROM jobs INNER JOIN installs ON jobs.id = installs.job_id WHERE completed = ?", 0)
    scdCount = scdCount_table[0]["count"]

    # Get tables of scheduled and unscheduled jobs
    unscd = db.execute("SELECT * FROM jobs LEFT JOIN installs ON jobs.id = installs.job_id WHERE installs.user_id is ? and completed = ?", None, 0)
    scd = db.execute("SELECT jobs.id AS id, jobs.first_name AS job_first_name, jobs.last_name AS job_last_name, jobs.address, jobs.recieved, jobs.timeframe_hour, jobs.timeframe_min, installs.user_id, installs.date, installs.time, users.first_name AS installer_first_name, users.last_name AS installer_last_name FROM jobs INNER JOIN installs ON jobs.id = installs.job_id JOIN users on users.id = installs.user_id WHERE completed = ?", 0)

    return render_template("index.html",
                               username=username,
                               first_name=first_name,
                               last_name=last_name,
                               role=role,
                               unscd=unscd,
                               scd=scd,
                               unscdCount=unscdCount,
                               scdCount=scdCount
                               )


""" UPDATE job as completed """
@app.route("/complete_job/<job_id>", methods=["POST"])
@login_required
def complete_job(job_id):
    if request.method == "POST":
        db.execute("UPDATE jobs SET completed = ? WHERE id = ?", 1, job_id)
        return redirect("/")
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" UPDATE note as completed """
@app.route("/complete_note", methods=["POST"])
@login_required
def complete_note():
    if request.method == "POST":
        user_id = session.get("user_id")
        note_id = int(request.form.get("note_id"))
        job_id = int(request.form.get("job_id"))
        db.execute("UPDATE notes SET completed = ?, completed_by = ?, completed_on = date('now') WHERE job_id = ? and id = ?", 1, user_id, job_id, note_id)
        #redirect to the most recent page
        last_page = request.referrer
        if last_page:
            return redirect(url_for('job', job_id=job_id))
        else:
            return redirect("/")
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" DELETE shades """
@app.route("/delete_shades/<shades_id>", methods=["POST"])
@login_required
def delete_shades(shades_id):
    if request.method == "POST":
        job_id_table = db.execute("SELECT job_id FROM shades WHERE shades.id = ?", shades_id)
        job_id = job_id_table[0]["job_id"]
        db.execute("DELETE FROM shades WHERE shades.id = ?", shades_id)
        last_page = request.referrer
        if last_page:
            return redirect(last_page)
        else:
            return redirect(url_for('job', job_id=job_id))
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" READ/View Job """
@app.route("/job/<job_id>")
@login_required
def job(job_id):
    # Get user info for layout
    user_id = session.get("user_id")
    user_table = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_table[0]["username"]
    first_name = user_table[0]["first_name"]
    last_name = user_table[0]["last_name"]
    role = user_table[0]["role"]

    # Get job info
    job = db.execute("SELECT jobs.last_name AS job_last_name, jobs.first_name AS job_first_name, contact, phone, recieved, address, timeframe_hour, timeframe_min, total_cost, paid_in_full, installs.date AS install_date, installs.time AS install_time, users.username AS installer_username, users.first_name AS installer_first_name, users.last_name AS installer_last_name FROM jobs JOIN installs ON jobs.id = installs.job_id JOIN users ON users.id = installs.user_id WHERE jobs.id = ?", job_id)
    if len(job) == 0:
        job = db.execute("SELECT jobs.last_name AS job_last_name, jobs.first_name AS job_first_name, contact, phone, recieved, address, timeframe_hour, timeframe_min, total_cost, paid_in_full FROM jobs WHERE jobs.id = ?", job_id)
        scheduled = 0

    # Get incomplete notes info and count
    incomplete_notes = db.execute("SELECT notes.id, notes.job_id, notes.created_on, notes.note, notes.completed_on, created_by.username AS cr_username, created_by.first_name AS cr_first, created_by.last_name AS cr_last FROM notes JOIN users AS created_by ON notes.created_by = created_by.id LEFT JOIN users AS completed_by ON notes.completed_by = completed_by.id WHERE notes.job_id = ? AND notes.completed = ?", job_id, 0)
    incomplete_note_count_table = db.execute("SELECT COUNT(*) AS count FROM notes JOIN jobs on notes.job_id = jobs.id WHERE jobs.id = ? and notes.completed = ?", job_id, 0)
    incomplete_note_count = incomplete_note_count_table[0]["count"]

    # Get complete notes info and count
    # Note table rows for completed_by are co_username... and rows for created_by are cr_username...
    complete_notes = db.execute("SELECT notes.job_id, notes.created_on, notes.note, notes.completed_on, created_by.username AS cr_username, created_by.first_name AS cr_first, created_by.last_name AS cr_last, completed_by.username AS co_username, completed_by.first_name AS co_first, completed_by.last_name AS co_last FROM notes JOIN users AS created_by ON notes.created_by = created_by.id LEFT JOIN users AS completed_by ON notes.completed_by = completed_by.id WHERE notes.job_id = ? AND notes.completed = ?", job_id, 1)
    complete_note_count_table = db.execute("SELECT COUNT(*) AS count FROM notes JOIN jobs on notes.job_id = jobs.id WHERE jobs.id = ? AND notes.completed = ?", job_id, 1)
    complete_note_count = complete_note_count_table[0]["count"]

    # Get installers and count
    installers = db.execute("SELECT users.first_name, users.last_name FROM users JOIN installs ON users.id = installs.user_id WHERE installs.job_id = ?", job_id)
    installer_count_table = db.execute("SELECT COUNT(*) AS count FROM users JOIN installs on users.id = installs.user_id WHERE installs.job_id = ?", job_id)
    installer_count = installer_count_table[0]["count"]

    #Get all installers for updating
    all_installers = db.execute("SELECT * FROM users WHERE role = ?", 'installer')
    all_installers_count_table = db.execute("SELECT COUNT (*) AS count FROM users WHERE role = ?", 'installer')
    all_installers_count = all_installers_count_table[0]['count']


    # Get shades, count, and total shades
    shades = db.execute("SELECT id, type, quantity, location FROM shades WHERE job_id = ?", job_id)
    shade_count_table = db.execute("SELECT COUNT(*) AS count FROM shades WHERE job_id = ?", job_id)
    shade_count = shade_count_table[0]["count"]
    total_shades_table = db.execute("SELECT SUM(quantity) AS total_shades FROM shades WHERE job_id = ?", job_id)
    total_shades = total_shades_table[0]["total_shades"]


    return render_template("job.html",
                            job_id=job_id,
                            job=job,
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            role=role,
                            incomplete_notes=incomplete_notes,
                            incomplete_note_count=incomplete_note_count,
                            complete_notes=complete_notes,
                            complete_note_count=complete_note_count,
                            installers=installers,
                            installer_count=installer_count,
                            shades=shades,
                            shade_count=shade_count,
                            total_shades=total_shades,
                            all_installers=all_installers,
                            all_installers_count=all_installers_count
                        )


""" CREATE new job """
@app.route("/new_job", methods=["POST"])
@login_required
def new_job():
    # Get user info for layout
    user_id = session.get("user_id")
    user_table = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_table[0]["username"]
    first_name = user_table[0]["first_name"]
    last_name = user_table[0]["last_name"]
    role = user_table[0]["role"]

    if request.method == "POST":
        last_name = request.form.get("last_name")
        first_name = request.form.get("first_name")
        contact = request.form.get("contact")
        phone = request.form.get("phone")
        address = request.form.get("address")
        timeframe_hour = request.form.get("timeframe_hour")
        timeframe_min = request.form.get("timeframe_min")
        recieved = request.form.get("recieved")
        cost = request.form.get("cost")

        # Validations
        if not last_name:
            return apology("Must provide Last Name")
        elif not first_name:
            return apology("Must provide First Name")
        elif not phone:
            return apology("Must provide phone")
        elif not address:
            return apology("Must provide Address")
        elif not timeframe_hour:
            return apology("Must provide estimated hours")
        elif not timeframe_min:
            return apology("Must provide estimated minutes")
        elif not cost:
            return apology("Must provide Job Cost")
        else:
            db.execute ("INSERT INTO jobs (last_name, first_name, contact, phone, address, timeframe_hour, timeframe_min, recieved, total_cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        last_name,
                        first_name,
                        contact,
                        phone,
                        address,
                        timeframe_hour,
                        timeframe_min,
                        recieved,
                        cost)
            job_id_table = db.execute("SELECT id FROM jobs ORDER BY id DESC LIMIT ?", 1)
            job_id = job_id_table[0]["id"]

            return redirect(url_for('job', job_id=job_id))
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" CREATE new note for job"""
@app.route("/new_note/<job_id>", methods=["POST"])
@login_required
def new_note(job_id):
    if request.method == "POST":
        note = request.form.get("note")
        completed = request.form.get("completed")
        user_id = session.get("user_id")
        current_date_table = db.execute("SELECT CURRENT_DATE")
        current_date = current_date_table[0]["CURRENT_DATE"]

        if not completed:
            db.execute("INSERT INTO notes (job_id, created_by, note) VALUES (?, ?, ?)", job_id, user_id, note)
        else:
            db.execute("INSERT INTO notes (job_id, created_by, note, completed, completed_on, completed_by) VALUES (?, ?, ?, ?, ?, ?)", job_id, user_id, note, completed, current_date, user_id)
        return redirect(url_for('job', job_id=job_id))

    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" Create new shades for job """
@app.route("/new_shades/<job_id>", methods=["POST"])
@login_required
def new_shades(job_id):
    if request.method == "POST":
        type = request.form.get("type")
        quantity = request.form.get("quantity")
        location = request.form.get("location")

        db.execute("INSERT INTO shades (job_id, type, quantity, location) VALUES (?, ?, ?, ?)", job_id, type, quantity, location)
        return redirect(url_for('job', job_id=job_id))
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)

""" UPDATE shades """
@app.route("/update_shades/<job_id>", methods=["POST"])
@login_required
def update_shades(job_id):
    if request.method == "POST":
        type = request.form.get("type")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        shades_id = request.form.get("shades_id")
        db.execute("UPDATE shades SET type = ?, quantity = ?, location = ? WHERE shades.id = ?", type, quantity, location, shades_id)
        #redirect to the most recent page
        last_page = request.referrer
        print(last_page)
        if last_page:
            return redirect(last_page)
        else:
            return redirect("/")
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" READ/view Shades for job """
@app.route("/shades/<job_id>", methods=["GET", "POST"])
@login_required
def shades(job_id):
    # Get user info for layout
    user_id = session.get("user_id")
    user_table = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_table[0]["username"]
    first_name = user_table[0]["first_name"]
    last_name = user_table[0]["last_name"]
    role = user_table[0]["role"]
    if request.method == "POST":
        type = request.form.get("type")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        shades_id = request.form.get("shades_id")
        job_id = request.form.get("job_id")
        db.execute("UPDATE shades SET type = ?, quantity = ?, location = ? WHERE shades.id = ?", type, quantity, location, shades_id)
        return redirect(url_for('shades', job_id=job_id))
    else:
        job = db.execute("SELECT * FROM jobs WHERE jobs.id = ?", job_id)
        shades = db.execute("SELECT * FROM shades WHERE shades.job_id = ?", job_id)
        shades_count_table= db.execute("SELECT COUNT(*) AS count FROM shades JOIN jobs ON shades.job_id = jobs.id WHERE jobs.id = ?", job_id)
        shades_count = shades_count_table[0]["count"]
        return render_template("shades.html", job_id=job_id, job=job, shades_count=shades_count, shades=shades)


""" UPDATE job """
@app.route("/update_job/<job_id>", methods=["POST"])
@login_required
def update_job(job_id):
    if request.method == "POST":
        date = request.form.get("date")
        time = request.form.get("time")
        installer_id = request.form.get("installer_id")
        last_name = request.form.get("last_name")
        first_name = request.form.get("first_name")
        contact = request.form.get("contact")
        phone = request.form.get("phone")
        address = request.form.get("address")
        timeframe_hour = request.form.get("timeframe_hour")
        timeframe_min = request.form.get("timeframe_min")
        recieved = request.form.get("recieved")
        cost = request.form.get("cost")

        # Validations
        if date or time or installer_id:
            if not (date and time and installer_id):
                return apology("Must provide all 3 date time and installer to properly schedule a job")
        if not last_name:
            return apology("Musts provide Last Name")
        elif not first_name:
            return apology("Musts provide First Name")
        elif not address:
            return apology("Must provide Address")
        elif not recieved:
            return apology("Musts provide the date the Job was recieved")
        elif not cost:
            return apology("Musts provide Job Cost")
        else:
            db.execute ("INSERT INTO jobs (last_name, first_name, contact, phone, address, timeframe_hour, timeframe_min, recieved, total_cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        last_name,
                        first_name,
                        contact,
                        phone,
                        address,
                        timeframe_hour,
                        timeframe_min,
                        recieved,
                        cost)
            db.execute("INSERT INTO installs (date, time, user_id, job_id) VALUES (?, ?, ?, ?)", date, time, installer_id, job_id)
        #redirect to the most recent page,
        last_page = request.referrer
        if last_page:
            return redirect(last_page)
        else:
            return redirect("/")
    else:
        # If method not "POST"
        return apology("Method not allowed", 405)


""" Login and Register """
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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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
    """Register user"""

    # Get user info for layout
    user_id = session.get("user_id")
    user_table = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    username = user_table[0]["username"]
    first_name = user_table[0]["first_name"]
    last_name = user_table[0]["last_name"]
    role = user_table[0]["role"]

    if role != 'admin':
        return redirect("/")

    else:
        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            username = request.form.get("username")
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            role = request.form.get("role")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            # Ensure all fields are completed
            if not username:
                return apology("must provide username", 400)
            elif not first_name:
                return apology("must provide First Name", 400)
            elif not last_name:
                return apology("must provide last Name", 400)
            elif not password:
                return apology("must provide password", 400)
            elif not confirmation:
                return apology("must confirm password", 400)
            elif not role:
                return apology("must select Role", 400)

            # Return apology if username already exists
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
            if rows:
                return apology("username already exists")

        # Ensure password and confirmation match else return an apology
            if password != confirmation:
                return apology("password and confirmation do not match")
            else:
            # Add user to database
                hash = generate_password_hash(password)
                db.execute("INSERT INTO users (username, first_name, last_name, role, hash) VALUES (?, ?, ?, ?, ?)", username, first_name, last_name, role, hash)

            # Redirect admin to register
            return redirect("/register")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("register.html", username=username, first_name=first_name, last_name=last_name, role=role)

