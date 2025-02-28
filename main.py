from flask import Flask, render_template, session, request, redirect, url_for
from database import db
from models import User

app = Flask(__name__) #creates a Flask app

#we have to configure the database

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db" #sets the database URI to the users.db file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #False so it does not track changes in the database

# initializing database
db.init_app(app) # inits the database based on Flask app name

# routing (routes)

#home route
@app.route("/") # sets the route 
def home():
  if "username" in session: #checks if the user is logged in
    return  redirect(url_for("dashboard")) #redirects to the dashboard of the logged in user
  return render_template("index.html") 

# login route
@app.route("/login", methods=["POST"])
def login():
# collects info from form
  data = request.json
  # username = data["username"]
  email= data["email"]
  password = data["password"]
  
#checks database for if info exists
  existing_user = User.query.filter_by(email=email).first() 
  if existing_user and existing_user.check_password(password): #!CHANGE WAS HERE 
    #redirects to dashboard if info exists
    session["email"] = email
    return redirect(url_for("dashboard"))
  else:
    #redirects to register if info does not exist
    return render_template("register", error="Account does not exist")


# register route
@app.route("/register", methods=["POST"])
def register():
#collects info from form
  data = request.json
  username = data["username"]
  email= data["email"]
  password = data["password"]
  
  # checks if user already exists
  existing_user = User.query.filter_by(email=email).first()
  if existing_user:
    return render_template("index", error="Account already exists")
  else:
    #if user isnt already in db create new user
    new_user = User(email=email, username=username) #!CHANGE WAS HERE
    
    #sets password
    new_user.set_password(password) #!CHANGE WAS HERE
    
    #stores user in database
    db.session.add(new_user) 
    db.session.commit() #commits changes to database
    
    #opens a session and redirects to dashboard
    session["email"] = email 
    return redirect(url_for("dashboard"))


# dashboard route

# logout route

if __name__ == "__main__": #runs the app if this file is the main file
  with app.app_context(): #ensures that the database is created while knowing which app configuration to use
    db.create_all() #creates the database
  app.run(debug=True) 