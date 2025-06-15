"""Server for Parkinson's app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = 'devtech' # for flask and session
app.jinja_env.undefined = StrictUndefined # throw errors for undefined variables 


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new user."""

    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        swallow_difficulty = request.form.get("swallow-diff")
        weight = request.form.get("weight")

        existing_user = crud.get_user_by_email(email)
        if existing_user: # check is user already exists
            flash("An account with this email already exists. Please login.")
            return redirect("/login")
        else:
            new_user = crud.create_user(
                fname=fname,
                lname=lname,
                email=email,
                password=password,
                swallow_difficulty=swallow_difficulty,
                weight=weight
            )



    return render_template("register.html")






if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True, port=6060)




