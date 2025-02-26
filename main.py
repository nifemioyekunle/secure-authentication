from flask import Flask, render_template

app = Flask(__name__) #creates a Flask app

@app.route("/") #sets the route (home page)
def index():
  return render_template("index.html")

if __name__ == "__main__": #runs the app if this file is the main file
  app.run(debug=True) #run app debug mode when page is reloaded