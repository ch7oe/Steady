"""Server for Parkinson's app."""

from flask import Flask, render_template, request, flash, session, redirect, jsonify 
from model import connect_to_db, db, MealPlanRecipe, MealLog, MealLogRecipe
from datetime import date, timedelta, datetime
import crud
from nutritional_analysis import calculate_daily_nutrient_intake
from apis.api_spoonacular import get_and_cache_spoonacular_recipes


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
        # swallow_difficulty = request.form.get("swallow-diff")
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
                swallow_difficulty=None,
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
        if user:
            verify_password = crud.verify_password(raw_password, user.hashed_password)

        if not user or not verify_password: # if no user found with email and raw password
            flash("Account not found.")
            return redirect("/login")
        
        if verify_password: # if correct password
            session["user_id"] = user.user_id # login user
            flash(f"You're logged in! 🌻")
            return redirect("/dashboard")
    
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

    return render_template(
        "meal_plan_view.html",
        week_start=week_start,
        week_end=week_end,
        weekly_meal_plan_info=weekly_meal_plan_info
    )


@app.route("/meal-plan/edit/<date_string>", methods=["GET", "POST"])
def meal_plan_add_edit(date_string):
    """Display page to add/edit meals for a specific date.
    <date_string> in YYYY-MM-DD format.
    """

    if request.method == "POST":
        chosen_date_str = request.form.get("date-string")

        if chosen_date_str:
            return redirect(f"/meal-plan/edit/{chosen_date_str}")
        
        else:
            flash("No date was chosen. Select a date to change date.")
            return redirect(f"/meal-plan/edit/{date_string}")
        

    user_id = session.get("user_id") # verify user logged in 
    if not user_id:
        flash("Login to manage meal plans.")
        return redirect("/login")
    
    user = crud.get_user_by_id(user_id)
    
    # convert date string to datetime object and then discard time info
    target_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    
    # MealPlan object for target date
    meal_plan = crud.get_meal_plan_by_user_id_and_date(user_id, target_date)

    if not meal_plan: # create new meal plan, if no meal plan for target date exists
        meal_plan = crud.create_meal_plan(user_id, target_date)
        db.session.add(meal_plan)
        db.session.commit()
    
    current_planned_meals_for_day = {
        "breakfast": [], "lunch": [], "dinner": [], "snack": [],
    }

    # MealPlanRecipe objects from meal plan
    meal_plan_recipes = crud.get_recipes_in_meal_plan(meal_plan.meal_plan_id)

    # add each recipe in meal plan to current_planned_meals_for_day dictionary 
    for meal_plan_recipe in meal_plan_recipes: 
        if meal_plan_recipe.meal_type in current_planned_meals_for_day:
            current_planned_meals_for_day[meal_plan_recipe.meal_type].append(meal_plan_recipe)
    
    return render_template(
        "meal_plan_add_edit.html",
        user=user,
        target_date=target_date,
        current_planned_meals_for_day=current_planned_meals_for_day    
    )

    
@app.route("/recipes/search")
def get_recipe_search_page():
    """Display standalone recipe search page."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Login to search recipes.")
        return redirect("/login")
    
    user = crud.get_user_by_id(user_id)

    return render_template("recipe_search.html", user=user)


# api endpoint for recipe search (AJAX)
@app.route("/api/recipes/search", methods=["GET"])
def api_search_recipes():
    """api endpoint to search for recipes.
    Returns JSON list of recipes.
    """

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Login to search for recipes."})
    
    user = crud.get_user_by_id(user_id)

    # get search term and filters
    search_term = request.args.get("query", "").strip()  
    likes_filter = request.args.get("likes") # true or false
    

    if not search_term:
        return jsonify([]) # return empty list if no search term 
    
    user_allergens = [a.allergen for a in user.allergies]
    user_diet_restrictions = [dr.restriction for dr in user.diet_restrictions]
    user_dislikes = [dislike.name.lower() for dislike in user.likes_dislikes]

    cached_recipes_from_api = get_and_cache_spoonacular_recipes(
        recipe_query=search_term,
        user_allergens=user_allergens,
        user_diet_restrictions=user_diet_restrictions,
        user_dislikes=user_dislikes,
    )

    # filtered_recipes_from_db = crud.get_recipes_by_search(
    #     user_id=user_id,
    #     search_term=search_term,
    #     likes=likes_filter
    # )

    if not cached_recipes_from_api:
        return jsonify({"message": "No recipes found matching criteria."})

    # list of dictionaries with recipe data to send as JSON to frontend
    recipes_data_for_frontend = []
    
    for recipe_object in cached_recipes_from_api:
        recipes_data_for_frontend.append({
            "id": recipe_object.recipe_id,
            "spoonacular_id": recipe_object.spoonacular_id,
            "title": recipe_object.title,
            "source": recipe_object.source,
            "url": recipe_object.url,
            "servings": recipe_object.servings,
            "instructions": recipe_object.instructions
        })

    
    # return JSON response
    return jsonify(recipes_data_for_frontend)


# api for adding recipe to meal plan (AJAX POST) 
@app.route("/api/meal-plan/add", methods=["POST"])
def add_recipe_to_meal_plan():
    """Add recipe to meal plan."""

    user_id = session.get("user_id")
    if not user_id:
        flash("Login to view and edit meal plan.")
        return redirect("/login")
    
    meal_plan_date_str = request.json.get("meal_plan_date") # string YYYY-MM-DD
    recipe_id = request.json.get("recipe_id")
    meal_type = request.json.get("meal_type")
    serving_size = request.json.get("serving_size")

    meal_plan_date = datetime.strptime(meal_plan_date_str, "%Y-%m-%d").date()

    meal_plan_object = crud.get_meal_plan_by_user_id_and_date(user_id, meal_plan_date)

    if not meal_plan_object:
        meal_plan_object = crud.create_meal_plan(user_id, meal_plan_date)
    
    if not all([meal_plan_date_str, recipe_id, meal_type, serving_size]):
        return jsonify({"message": "Missing required data"})
    
    # check if recipe for meal type already exists in the plan
    existing_recipe = db.session.query(MealPlanRecipe).filter(
        MealPlanRecipe.meal_plan_id == meal_plan_object.meal_plan_id,
        MealPlanRecipe.meal_type == meal_type,
        MealPlanRecipe.recipe_id == recipe_id 
    ).first()

    if existing_recipe:
        return jsonify({"message": "Recipe already exist for this meal type on this day"})
    else:
        # if recipe doesnt alrady exist for meal type on this day
        new_recipe_entry = crud.add_recipe_to_meal_plan(
            meal_plan_object.meal_plan_id,
            recipe_id,
            meal_type,
            serving_size
        )
        db.session.add(new_recipe_entry)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Recipe added to {meal_type} plan!"})


# api for removing recipe from meal plan (AJAX POST)
@app.route("/api/meal-plan/remove", methods=["POST"])
def remove_recipe_from_meal_plan():
    """remove recipe from meal plan."""

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "message": "Login to edit your meal plan."
        })

    meal_plan_data_str = request.json.get("meal_plan_date")
    recipe_id = request.json.get("recipe_id")
    meal_type = request.json.get("meal_type")

    if not all([meal_plan_data_str, recipe_id, meal_type]):
        return jsonify({"message": "Missing required data"})
    
    meal_plan_date = datetime.strptime(meal_plan_data_str, "%Y-%m-%d").date()

    meal_plan_obj = crud.get_meal_plan_by_user_id_and_date(user_id, meal_plan_date)

    entry_to_delete = db.session.query(MealPlanRecipe).filter(
        MealPlanRecipe.meal_plan_id==meal_plan_obj.meal_plan_id,
        MealPlanRecipe.recipe_id==recipe_id,
        MealPlanRecipe.meal_type==meal_type
    ).first()

    if entry_to_delete:
        db.session.delete(entry_to_delete)
        db.session.commit()

        return jsonify({"message": "Recipe removed from plan."})
    else:
        return jsonify({"message": "Failed to remove recipe from plan"})
    

@app.route("/log-meal")
def meal_log():
    """Display meal log page."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Login to log your meals.")
        return redirect("/login")
    
    today_str = date.today().strftime('%Y-%m-%d')

    return render_template("log_meal.html", today_str=today_str)


# api for getting logged meals (AJAX)
@app.route("/api/meal-log/get", methods=["GET"])
def api_get_logged_meals():
    """get logged meals for a specific user and date.
    """

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Login to view logged meals"})
    
    # get date string from query params
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"message": "date is required"})
    
    # convert to datetime object
    log_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # get meal logs for user on log date chosen - MealLog objects
    meal_logs = crud.get_meal_log_by_user_id_and_date(user_id, log_date)

    logged_meals_data = [] # store logged meals to send to frontend
    for meal_log in meal_logs:
        #loop through MealLogRecipe entries associated with this MealLog
        for meal_recipe_entry in meal_log.meal_log_recipes:
            logged_meals_data.append({
                "meal_log_id": meal_log.meal_log_id,
                "recipe_id": meal_recipe_entry.recipe_id,
                "recipe_title": meal_recipe_entry.recipe.title,
                "meal_type": meal_log.meal_type,
                "serving_size": meal_recipe_entry.serving_size
            })

    return jsonify(logged_meals_data)


# api for adding a logged meal (AJAX POST)
@app.route("/api/meal-log/add", methods=["POST"])
def api_add_logged_meal():
    """Log a new meal for a user.
    creates meallog and meallog recipe entries.
    """

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"message": "Login to log a meal"})
    
    #  json from frontend 
    log_date_str = request.json.get("log_date")
    meal_type = request.json.get("meal_type")
    recipe_id = request.json.get("recipe_id")
    serving_size = request.json.get("serving_size")

    if not all([log_date_str, meal_type, recipe_id, serving_size]):
        return jsonify({"message": "missing required data."})    
    
    log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()

    meal_log_obj = db.session.query(MealLog).filter(
        MealLog.user_id == user_id,
        MealLog.log_date == log_date,
        MealLog.meal_type == meal_type
    ).first()

    if not meal_log_obj:
        # create a meal log for a user
        meal_log_obj = crud.create_meal_log(user_id, log_date, meal_type)
        db.session.add(meal_log_obj)
        db.session.commit()

    existing_ml_recipe = db.session.query(MealLogRecipe).filter(
        MealLogRecipe.meal_log_id == meal_log_obj.meal_log_id,
        MealLogRecipe.recipe_id == recipe_id
    ).first()

    if existing_ml_recipe:
        # if entry exists, update its serving size 
        existing_ml_recipe.serving_size = serving_size
        db.session.add(existing_ml_recipe)
        db.session.commit()

        return jsonify({"message": "logged meal serving size updated!"})
    
    else:
        new_ml_recipe = crud.add_recipe_to_meal_log(
            meal_log_obj.meal_log_id,
            recipe_id,
            serving_size
        )
        db.session.add(new_ml_recipe)
        db.session.commit()

        return jsonify({"message": "Meal logged successfully!"})
    

# api for removing a logged meal (AJAX POST)
@app.route("/api/meal-log-remove", methods=["POST"])
def api_remove_logged_meal():
    """remove a logged meal for a user."""

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Login to remove a logged meal."})
    
    meal_log_id = request.json.get("meal_log_id")
    recipe_id = request.json.get("recipe_id")
    meal_type = request.json.get("meal_type")

    if not all([meal_log_id, recipe_id, meal_type]):
        return jsonify({"message": "Missing required data."})
    
    ml_to_delete = db.session.query(MealLogRecipe).filter(
        MealLogRecipe.meal_log_id == meal_log_id,
        MealLogRecipe.recipe_id == recipe_id,
        MealLogRecipe.meal_log.meal_type == meal_type
    ).first()

    if ml_to_delete:
        db.session.delete(ml_to_delete)
        db.session.commit()

        return jsonify({"message": "Logged meal removed."})
    
    else:
        return jsonify({"message": "Logged meal not found for this meal type."})
    

@app.route("/grocery-list")
def grocery_list():
    """Display the user's grocery list for the current week."""

    user_id = session.get("user_id")

    if not user_id:

        flash("Login to view your grocery list")
        return redirect("/login")
    
    # calculate for the current week (Monday to Sunday)
    today = date.today()
    week_start_date = today - timedelta(days=today.weekday())
    week_end_date = week_start_date + timedelta(days=6)

    # generate grocery list using helper function from nutritional_analysis.py
    grocery_list_data = 

    













    






# @app.route("/logout", methods=[])









if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True, port=6060)




