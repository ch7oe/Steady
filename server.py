"""Server for Parkinson's app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
from datetime import date, timedelta
import crud
from nutritional_analysis import calculate_daily_nutrient_intake

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
        raw_password = request.form.get("password")
        swallow_difficulty = request.form.get("swallow-diff")
        weight = request.form.get("weight")

        existing_user = crud.get_user_by_email(email)
        
        if existing_user: # check is user already exists
            flash("An account with this email already exists. Please login.")
            return redirect("/login")
        else:
            new_user = crud.create_user( # create user in database with hashed password
                fname=fname,
                lname=lname,
                email=email,
                raw_password=raw_password,
                swallow_difficulty=swallow_difficulty,
                weight=weight
            )
            db.session.add(new_user)
            db.session.commit()

            # login user automatically after sign up
            session["user_id"] = new_user.user_id

            flash(f"Welcome, {new_user.fname}! Account created successfully.")
            return redirect("/dashboard")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Login a user."""

    if request.method == "POST":
        email = request.form.get("email")
        raw_password = request.form.get("password") 

        user = crud.get_user_by_email(email) # verify a user with given email

        # verify raw password against user's stored hashed password
        verify_password = crud.verify_password(raw_password, user.hashed_password)

        if not user: # if no user with given email exists
            flash("Account not found.")
            redirect("/login")
        
        if verify_password: # if correct password
            session["user_id"] = user.user_id # login user
            flash(f"Hello, {user.fname}! 🌻")
            redirect("/dashboard")
    
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """Display a user's dashboard."""

    user_id = session.get("user_id") # check if user logged in 

    if not user_id: # if user not logged in
        flash("Log in to view dashboard")
        return redirect("/login")
    
    user = crud.get_user_by_id(user_id)

    # today's meal plan
    meal_plan_today = crud.get_meal_plan_by_user_id_and_date(user.user_id, date.today())
    planned_recipes_today = []

    if meal_plan_today: # if user has a meal plan today
        # get recipes in meal plan
        planned_recipes_today = crud.get_recipes_in_meal_plan(meal_plan_today.meal_plan_id)

    # today's nutrition analysis
    today_nutrition = calculate_daily_nutrient_intake(user.user_id, date.today())

    # recent/today's meal logs
    today_meal_logs = crud.get_meal_log_by_user_id_and_date(user.user_id, date.today())

    return render_template(
        "dashboard.html",
        user=user,
        meal_plan_today=meal_plan_today,
        planned_recipes_today=planned_recipes_today,
        today_nutrition=today_nutrition,
        today_meal_logs=today_meal_logs
    )


@app.route("/meal-plan")
def view_meal_plan():
    """Display a user's weekly meal plan."""
    
    user_id = session.get("user_id")

    if not user_id:
        flash("Log in to view meal plans.")
        return redirect("/login")
    # implement "previous/next week" from request.args and adjust week start

    # calculate start and end of the week
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)

    # get meal plans for the week
    weekly_meal_plan_info = {} # dictionary of dates, each containing a dict of meal types
    
    current_day_in_week = week_start # used to increment to end while loop 
    
    while current_day_in_week <= week_end:
        weekly_meal_plan_info[current_day_in_week] = {
            "breakfast": [], "lunch": [], "dinner": [], "snack": [],
        }

        # get meal plan for this specific day 
        meal_plan_today = crud.get_meal_plan_by_user_id_and_date(user_id, current_day_in_week)

        if meal_plan_today:
            # get MealPlanRecipes for this specific day - has .recipe relationship
            meal_plan_recipes = crud.get_recipes_in_meal_plan(meal_plan_today.meal_plan_id)

            for planned_recipe in meal_plan_recipes: # for each recipe in in meal plan for today
                if planned_recipe.meal_type in weekly_meal_plan_info[current_day_in_week]: 
                    # add each recipe from meal plan to week meal plan info dict according to its meal type 
                    weekly_meal_plan_info[current_day_in_week][planned_recipe.meal_type].append(planned_recipe)

        current_day_in_week += timedelta(days=1) # counter to stop while loop when current day is after end date 

    render_template(
        "meal_plan_view.html",
        week_start=week_start,
        week_end=week_end,
        weekly_meal_plan_info=weekly_meal_plan_info
    )            
    






# @app.route("/logout", methods=[])









if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True, port=6060)




