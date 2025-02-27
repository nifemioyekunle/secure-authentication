from main import db # imports the database from main.py
import bcrypt

#  creating database model
class User(db.Model): #inherits from db.Model
  
  # database columns
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True, nullable=False)
  email_address = db.Column(db.String(100), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
