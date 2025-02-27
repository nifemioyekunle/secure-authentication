from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import User

app = Flask(__name__) #creates a Flask app

#we have to configure the database

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db" #sets the database URI to the users.db file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #False so it does not track changes in the database

# initializing database
db = SQLAlchemy(app) #inits the database based on Flask app name

# routing (routes)
@app.route("/") #sets the route (home page)
def home():
  if "username" in session: #checks if the user is logged in
    return  redirect(url_for("dashboard")) #redirects to the dashboard of the logged in user
  return render_template("index.html")

if __name__ == "__main__": #runs the app if this file is the main file
  with app.app_context(): #ensures that the database is created while knowing which app configuration to use
    db.create_all() #creates the database
  app.run(debug=True) 