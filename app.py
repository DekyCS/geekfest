from flask import Flask, redirect, render_template, request
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='/static', static_folder='static')
db = SQL("sqlite:///geekfest.db")

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect("/login")
        
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login5.html")
        
    else:
        
        username = request.form.get("username")
        password = request.form.get("password")
        userid = db.execute("SELECT userid FROM users WHERE username = %s", username)
        

        if not userid:
            print("did not found accout")
            return redirect('/login')
            
            
        else:
            print("made connections")
            correctPassword = db.execute("SELECT password FROM users where username = ?", username)
            if password == correctPassword:
                print("connected")
                return redirect("/")
            else:
                return redirect("/login")
        


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "GET":
        return render_template("register5.html")
        print("wow")

    else:
        print("made a request to the /register page")
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password2")

        

        users = db.execute("SELECT * FROM users WHERE username = %s", (username,))

        if not users: # no users with the same username
            if password != password_confirm:
                return redirect("/register")
            else:
                db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, password)


                print("we have made a new user")
                return redirect("/login")
        else:
            return redirect("/register") # their existe alr a user with that username

@app.route("/bellx", methods=["GET", "POST"])
def bellx():
    return render_template("/")



if __name__ == '__main__':
    app.run(debug=True)


             
