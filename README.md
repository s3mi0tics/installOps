#installOps

## Video Demo: [CS50 final project by Colby Kauk: ](https://youtu.be/C9PW849ps1E?si=_ZcZmNzClq3mtQwr)https://youtu.be/C9PW849ps1E?si=_ZcZmNzClq3mtQwr

## EXPLINATION
InstallOps is a Helpdesk web application designed to help a manager schedule the deliveries of products and services of a blind installation operation.

## UNDERSTANDING

InstallOps is a web application designed in python, using the Flask framework. It is stylized with bootstrap and uses modals for client input.

### app.py
Atop the file are numerous imports including some modules from the Flask web framework, the cs50 SQL module for using a SQLite database, and some security functions from werkzeug.security.

Next it configures Flask to store sessions on the local file system rather then Flask's default which stores them in digitally signed cookies. Code provided by CS50 distribution code from previous assignments.

The file then configures CS50's SQL module to use installOps.db.

Next the after_request function modifies the response after Flask processes each request. Code provided by CS50 distribution code from previous assignments.

#### After that the routes:
Each get route, besides login, begins by getting the user info inorder to display the info for (I would like to eventually create a helper function or global varibale so I dont have to declare it in each route).

I found that where possible when executing SQL queries it was easier to include as much information as possible and then creating a count to iterate through each table in order to display the information using JINJA in the templates by finding the info in the table.

##### index route:
For the index route I want to display two tables. One of all the unscheduled jobs and one of all the scheduled jobs. So I created a table of each and a count of how many of rows in each table.

##### complete_job route:
This route is a "post" only route that updates a job and sets it to be complete(sets the completed column to 1 for a given job).

##### complete_note route:
This route is a "post" only route that updates a note and sets it to be complete(sets the completed column to 1 for a given note).

##### delete_shades route:
This route is a "post" only route that deletes a shade and returns the user to the most recent page they visited.

##### job route:
This queries for all the information related to a particular job. It queries for the install details as well as all notes related to the job divided into completed and incomplete notes.

##### new_note route:
Post only route that creates a new record on the notes table.

##### new_shades route:
Post only route that creates a new record on the shades table.

##### update_shades route:
Post only route that updates a record on the shades table.

##### shades route:
If this route is accessed by a post method, it updates a shade other wise it queries for a table with information about all the shades related to a particular job.

##### update_job route:
A post only route that updates a job.

##### login route:
If accesed it will first clear sessions which will log out any users that may be logged in at the time. Then if the request method was reached via post it will first validate that the user inputed a username and an email.

Then it will query the db to make sure the username exists and if the username exists it will check the see if the hash of that user matches and stores the user_id in sessions.

##### logout route:
This route clears the session and redirects user to the login form.

##### register route:
This route first checks to see that the logged in users role is admin. Then renders a template with a form to register a new user.
When the form is submited via a post method the route first validates that all the fields are filled out. Then it checks to make sure the username is unique. Then it checks to make sure the passwords match. Then it hashes the password and add a new record to the user table.

### helpers.py
An implementation of apology, and login_required taken from distribution code previously provided in CS50 assignments.


### static/
Inside the static directory is a styles.css file where we define just one style for the navbar brand.

### templates/
In the templates directory are html files for the client.

* apology.html is a template for when a user doesn't provide the correct infomation. This template was also provided by the distribution code from a previoius CS50 assignment.

* index.html is a home page that displays a list of all the incomplete jobs and divides them into two categories, scheduled jobs, and unscheduled jobs.from the home page a user will be able to add a new job using a modal with a form. For each job there is a link to google maps for directions and a link to view the details of that particular job.

* job.html is a job detail where the client can view and edit the details of a given job. The user can schedule the install and add shades and shade details. The details will include information about the job, including the scheduled install time, and Installer, the shades and notes related to the job divided into completed and incomplete notes.

* layout.html includes a "fancy, mobile-friendly 'navbar'... it defines a block, main, inside of which templates (including apology.html and login.html) shall go. It also includes support for Flask’s message flashing so that you can relay messages from one route to another for the user to see." The aformentioned quote as well as the template for layout are also provided by disribution code from previous CS50 assignmnets.

* login.html displays a form for a user to log in. Code provided by distribution code from previous CS50 assignments.

* register.html, if a user is an admin a form allows the user to register new users into the database and select what type of user they are.

* shades.html will allow the user to view and edit all the shades for a given job.

### installOps.db should be an empty database file.

### schema.sql
This file defines a schema with 5 tables. Users, jobs, installs, shades and notes. Users that can have 1 of 3 roles: Admin, Manager, or Installer. Jobs that can many installs, shades and notes. The installs tabel can connect many users to many jobs and many jobs to many users thereby creating a many to many relationship. Aditionally the file provides some initial testing values for the application.

### test.md
This file provides a list of sequential operations for testing the application.

### TODOS.md
A file with a list of todo notes that I made along the way.

## Getting started
* create an account and log in to code50
* Open two terminals at the path /installOps
* in one terminal execute sqlite3 installOps.db
* copy the contents of schema.sql and paste into the commandline after the sqlite
* in the other terminal execute flask run
* this should open a local instance of the application.

### Get in touch

Question, comments, or input please contact me @ colby.kauk@gmail.com
