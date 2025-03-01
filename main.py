from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from database import db
from models import User, bcrypt

app = Flask(__name__) #creates a Flask app
app.secret_key = "neo_from_the_matrix" 

#we have to configure the database

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db" #sets the database URI to the users.db file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #False so it does not track changes in the database

# initializing database
db.init_app(app) # inits the database based on Flask app name

#initialise bcrypt (password hasher)
bcrypt.init_app(app)

# routing (routes)

#home route
@app.route("/") # sets the route 
def home():
  if "username" in session: #checks if the user is logged in
    return  redirect(url_for("dashboard")) #redirects to the dashboard route of the logged in user
  return render_template("index.html") #returns the index.html template

# login route
@app.route("/login", methods=["POST"])
def login():
# collects info from form
  data = request.json
  # username = data["username"]
  email = data["email"]
  password = data["password"]
  
#checks database for if info exists
  existing_user = User.query.filter_by(email=email).first() 
  if existing_user and existing_user.check_password(password): 
    #redirects to dashboard if info exists
    session["email"] = email
    return jsonify({"success": "Login successful"}), 200
    # return redirect(url_for("dashboard")) #!!!
  else:
    #redirects to register page if info does not exist
    return render_template("register.html", error="Account does not exist")
    # return jsonify({"error": "Account does not exist"}), 400 #!!!


# register route
@app.route("/register", methods=["POST"])
def register():
#collects info from form
  data = request.json
  username = data["username"]
  email = data["email"]
  password = data["password"]
  
  # checks if user already exists
  existing_user = User.query.filter_by(email=email).first()
  if existing_user:
    return jsonify({"error": "Account already exists"}), 400
    # return render_template("index.html", error="Account already exists") #!!!
  else:
    #if user isnt already in db create new user
    new_user = User(email=email, username=username)
    #sets password
    new_user.set_password(password)
    
    #stores user in database
    db.session.add(new_user) 
    db.session.commit() #commits changes to database
    
    #opens a session and redirects to dashboard
    session["email"] = email 
    # return redirect(url_for("dashboard")) #!!!
    return jsonify({"success": "Account created"}), 200 


# dashboard route

# logout route

if __name__ == "__main__": #runs the app if this file is the main file
  with app.app_context(): #ensures that the database is created while knowing which app configuration to use
    db.create_all() #creates the database
  app.run(debug=True) 