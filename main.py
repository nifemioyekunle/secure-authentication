from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from database import db
from models import User, bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt
from datetime import timedelta, datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__) #creates a Flask app

#CONFIGURATIONS

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db" #sets the database URI to the users.db file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #False so it does not track changes in the database

#key configurations
app.config["SECRET_KEY"] = "neo_from_the_matrix_secret_key" # this needs to be a secure random key
app.config["JWT_SECRET_KEY"] = "neo_from_the_matrix_JWT_key" # this needs to be a secure random key

#JWT configurations
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30) #sets the time for the access token to expire
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7) #sets the time for the refresh token to expire

# initializing database
db.init_app(app) # inits the database based on Flask app name

#initialise bcrypt (password hasher)
bcrypt.init_app(app)

#initialise JWT
jwt = JWTManager(app)

#initialise limiter
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"]) #limits the number of requests to 5 per minute

# ROUTING (routes)

#home route
@app.route("/") # sets the route 
def home():
  if "username" in session: #checks if the user is logged in
    return  redirect(url_for("dashboard")) #redirects to the dashboard route of the logged in user
  return render_template("index.html") #returns the index.html template


failed_login_attempts = {} #dictionary to store failed login attempts
# login route
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute") #limits the number of login attempts to 5 per minute
def login():
# collects info from form
  data = request.json
  # username = data["username"]
  email = data["email"]
  password = data["password"]
  
#checks if user has attempted to login more than 5 times (already in failed_login_attempts dictionary)
  if email in failed_login_attempts:
    failed_login_attempts[email] = attempts, lock_time  
    if attempts >= 5 and datetime.now() < lock_time:
      return jsonify({"error": "Too many failed login attempts. Please try again later."}), 400
    elif datetime.now() > lock_time:
      failed_login_attempts[email] = (0, datetime.now())
  
#checks database for if info exists
  existing_user = User.query.filter_by(email=email).first() 
  if existing_user and existing_user.check_password(password):
    
    failed_login_attempts[email] = (0, datetime.now()) #resets failed login attempts to 0 if user logs in successfully
    
    access_token = create_access_token(identity=existing_user.id) #creates access token for user if user exists
    refresh_token =create_access_token(identity=existing_user.id, fresh=False) #false because it is not a new token
    session["email"] = email
    
    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200
    # return redirect(url_for("dashboard")) #redirects to dashboard if info exists #!!!    
  else:
    attempts, lock_time = failed_login_attempts.get(email, (0, datetime.now()))
    failed_login_attempts[email] = (attempts + 1, datetime.now() + timedelta(minutes=5))
  
    return jsonify({"error": "Invalid email or password"}), 400
  #redirects to register page if info does not exist
    # return render_template("register.html", error="Account does not exist") #!!
  



# register route
@app.route("/register", methods=["POST"])
def register():
#collects info from form
  data = request.json
  username = data["username"]
  email = data["email"]
  password = data["password"]
  
  existing_user = User.query.filter_by(email=email).first()
  
  if existing_user: # checks if user already exists
    return jsonify({"error": "Account already exists"}), 400
    # return render_template("index.html", error="Account already exists") #!!!
  else:
    new_user = User(email=email, username=username) #if user isnt already in db create new user
    new_user.set_password(password) #sets password
  
    db.session.add(new_user) #stores user in database
    db.session.commit() #commits changes to database
    
    #opens a session and redirects to dashboard
    session["email"] = email 
    # return redirect(url_for("dashboard")) #!!!
    return jsonify({"success": "Account created"}), 200 
  
# protected route
@app.route("/protected")
def protected():
  
  user_id = get_jwt_identity() #gets user id of person trying to access protected route
  user = User.query.filter_by(id=user_id).first() #gets user from database
  
  if user:
    return jsonify({"email": user.email}), 200 #if user exists returns email
  else:
    return jsonify({"error: User does not exist"}), 400
  

# refresh route
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) #requires a refresh token to access this route
def refresh():
  existing_user_id = get_jwt_identity() #gets user id of person trying to access refresh route
  access_token = create_access_token(identity=existing_user_id) #creates a new access token for the user
  return jsonify({"access_token": access_token}), 200

# dashboard route

# logout route
@app.route("/logout")
@jwt_required() #requires a jwt token to access this route
def logout():
  jti = get_jwt()["jti"] #gets the jti from the jwt token
  token_blacklist.add(jti) #adds the jti to the token blacklist
  return jsonify({"message": "Successfully logged out"}), 200

#blacklist token code
token_blacklist = set()

@jwt.token_in_blacklist_loader # indicates that JWT library will load and check if token is blacklisted
def check_if_token_is_blacklisted(jwt_header, jwt_data):
  jti = jwt_data["jti"] #gets the jti(unique identifier) from the jwt data
  return jti in token_blacklist #checks if the jti is in the token blacklist


if __name__ == "__main__": #runs the app if this file is the main file
  with app.app_context(): #ensures that the database is created while knowing which app configuration to use
    db.create_all() #creates the database
  app.run(debug=True) 