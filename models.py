from database import db # imports the database from database.py
import bcrypt

#  creating database model
class User(db.Model): #inherits from db.Model
  
  # database columns
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True, nullable=False)
  email_address = db.Column(db.String(100), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  
  #Hash passwrod before its stored in the database
  # def set_password(self, password):
    
  #   # Salt is the random data used in the hashing function.
  #   salt = bcrypt.gensalt() #generates salt. 
    
  #   bytes = password.encode("utf-8") #converts password to bytes
  #   hashed_password = bcrypt.hashpw(bytes, salt) #hashes password using salt.
  #   decoded_hashed_password = hashed_password.decode("utf-8") #converts hashed password to string
  #   self.password = decoded_hashed_password #stores hashed password in database
    
  #OR

  #Hash passwrod before its stored in the database
  def set_password(self, password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"),  bcrypt.gensalt())
    self.password = hashed_password.decode("utf-8")
    
  #checks if password in login input is correct
  def check_password(self, password):
    return bcrypt.checkpw(password.encode("utf-8"), self.password.encode)