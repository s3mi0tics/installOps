# Process for testing the App
* clear the db
* open a terminal at the installOps directory path
* in the terminal enter the command sqlite3 installOps.db to fill the db with the schema and test values
* open a second terminal at the installOps directory path
* in the second terminal enter the command flask run
* hold command and click on the link
* sign in as an admin
* create new user
* in the sqlite3 terminal check to see that user was created
* log out
* log in as the recently created user
* click on the add a job and add a job
* click on the job added details and click on update
* click on schedule and fill in schedule details
* add new shades
* add complete note and incomplete note
