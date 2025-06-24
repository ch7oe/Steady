"""CRUD operations"""

from model import db, User, DietaryRestriction, Medication, Allergy, NutritionGoal, LikeDislike, Reminder, Recipe, Ingredient, Nutrient, RecipeNutrient, MealLog, MealLogRecipe, MealPlan, MealPlanRecipe, connect_to_db
from sqlalchemy import or_, and_
from datetime import datetime
from passlib.hash import argon2


# ------- User CRUD functions -------

def create_user(fname, lname, email, raw_password, weight, swallow_difficulty=False):
    """Create and return a new user."""

    # hash password before storing
    hashed_password = argon2.hash(raw_password)

    user = User(
        fname=fname,
        lname=lname,
        email=email,
        hashed_password=hashed_password,
        weight=weight,
        signup_date=datetime.now(),
        swallow_difficulty=swallow_difficulty
    
    )

    return user


def verify_password(raw_password, hashed_password):
    """Verify raw password against hashed password in database."""

    return argon2.verify(raw_password, hashed_password) # boolean value
    

def get_users():
    """Return all users."""

    return db.session.query(User).all()


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return db.session.query(User).get(user_id)


def get_user_by_email(email):
    """Return a user by email."""

    return db.session.query(User).filter(User.email==email).first()


def update_user_profile(user_id, fname=None, lname=None, email=None, password=None, weight=None, swallow_difficulty=None):
    """Update and return a user's profile info."""

    user = db.session.query(User).get(user_id)

    if not user:
        return None # user not found 
    
    if fname:
        user.fname = fname
    if lname:
        user.lname = lname
    if email:
        user.email = email 
    if password:
        user.password = password
    if weight:
        user.weight = weight
    if swallow_difficulty:
        user.swallow_diffculty = swallow_difficulty

    return user


def delete_user(user_id):
    """Delete a user and their associated data."""

    user = db.session.query(User).get(user_id)

    if user:

        db.session.delete(user)
        

        return True # user will be deleted after db.commit()

    return False # if user not found 


# ------- DietRestriction CRUD functions -------

def create_diet_restriction(user_id, restriction):
    """Create and return a new dietary restriction for a user."""

    diet_restriction = DietaryRestriction(user_id=user_id, restriction=restriction.lower())

    return diet_restriction


def get_diet_restriction_by_user_id(user_id):
    """Return diet restrictions for a given user."""

    return db.session.query(DietaryRestriction).filter(User.user_id==user_id).all()


# ------- Medication CRUD functions -------

def create_medication(user_id, name, dosage, frequency, timing):
    """Create and return a new medication entry for a user."""

    med = Medication(
        user_id=user_id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        timing=timing
    )

    return med


def get_medications_by_user_id(user_id):
    """Return all medications for a given user."""

    return db.session.query(Medication).filter(User.user_id==user_id).all()


def update_medication(medication_id, name=None, dosage=None, frequency=None, timing=None):
    """Update and return a user's medication info."""

    med = db.session.query(Medication).get(medication_id)

    if not med:
        return None  # med not found
    
    if name:
        med.name = name
    if dosage:
        med.dosage = dosage
    if frequency:
        med.frequency = frequency
    if timing:
        med.timing = timing

    return med 
    

# ------- Allergy CRUD functions -------

def create_allergy(user_id, allergen):
    """Create and return a new allergy entry for a user."""

    allergy = Allergy(user_id=user_id, allergen=allergen)
    
    return allergy


def get_allergies_by_user_id(user_id):
    """Return all allergy by user id."""

    return db.session.query(Allergy).filter(User.user_id==user_id).all()


# ------- NutritionGoal CRUD functions -------

def create_nutrition_goal(user_id, goal):
    """Create and return a nutrition goal for a user."""

    ng = NutritionGoal(user_id=user_id, goal=goal)

    return ng


def get_nutrition_goals_by_user_id(user_id):
    """Return all nutrition goals for a given user."""

    return db.session.query(NutritionGoal).filter(User.user_id==user_id).all()


# ------- LikeDislike CRUD functions -------

def create_like_dislike(user_id, name, preference):
    """Create and return a new like/dislike entry for a user."""

    likedislike = LikeDislike(
        user_id=user_id,
        name=name,
        preference=preference
    )

    return likedislike


def get_likes_and_dislikes_by_user_id(user_id):
    """Return all likes/dislikes for a given user."""
    
    return db.session.query(LikeDislike).filter(User.user_id==user_id).all()


def get_likes_or_dislikes_by_user_id(user_id, preference):
    """Return all likes or dislikes for a given user."""

    if preference == "like":

        return db.session.query(LikeDislike).filter(User.user_id==user_id,
                                                    LikeDislike.preference=="like")
    
    elif preference == "dislike":

        return db.session.query(LikeDislike).filter(User.user_id==user_id,
                                                    LikeDislike.preference=="dislike")
    

def update_like_dislike(like_dislike_id, name=None, preference=None):
    """Update and return a user's like or dislike."""

    like_dislike = db.session.query(LikeDislike).filter(LikeDislike.like_dislike_id==like_dislike_id)

    if not like_dislike:
        return None # like or dislike not found
    
    if name:
        like_dislike.name = name
    if preference:
        like_dislike.preference = preference
    
    return like_dislike


# ------- Reminder CRUD functions -------

def create_reminder(user_id, reminder_type, reminder_time, frequency, message):
    """Create and return a new reminder for a user."""

    reminder = Reminder(
        user_id=user_id,
        reminder_type=reminder_type,
        reminder_time=reminder_time,
        frequency=frequency,
        message=message
    )

    return reminder


def get_reminders_by_user_id(user_id):
    """Return all reminders for a given user."""

    return db.session.query(Reminder).filter(User.user_id==user_id).all()


def update_reminder(reminder_id, reminder_type=None, reminder_time=None, frequency=None, message=None):
    """Update and return a reminder for a user."""

    reminder = db.session.query(Reminder).filter(Reminder.reminder_id==reminder_id)

    if not reminder:
        return None # reminder not found
    
    if reminder_type:
        reminder.reminder_type = reminder_type
    if reminder_time:
        reminder.reminder_time = reminder_time
    if frequency:
        reminder.frequency = frequency
    if message:
        reminder.message = message
    
    return reminder


# ------- Recipe CRUD functions -------

# caching from recipes Spoonacular API
def create_recipe(spoonacular_id, title, source, url, servings, instructions, texture, diets):
    """Create and return a new recipe."""

    recipe = Recipe(
        spoonacular_id=spoonacular_id,
        title=title,
        source=source,
        url=url,
        servings=servings,
        instructions=instructions,
        texture=texture,
        diets=diets,
        date_added=datetime.now()
    )

    return recipe


def get_recipe_by_id(recipe_id):
    """Return a recipe by primary key."""

    return db.session.query(Recipe).get(recipe_id)


def get_recipe_by_spoonacular_id(spoonacular_id):
    """Return a recipe by Spoonacular id."""

    return db.session.query(Recipe).filter(Recipe.spoonacular_id==spoonacular_id).first()


def get_recipes_by_search(user_id, search_term, likes=None, limit=50):
    """Filters recipes based on search term and user's personal info/settings."""

    # get user
    user = db.session.query(User).get(user_id)

    if not user:
        print("User not found.")
        return 
    
    # user specific data 
    user_allergens = {a.allergen for a in user.allergies} # user allergies 
    user_diet_restrictions = {dr.restriction for dr in user.diet_restrictions} # user diet restrictions
    user_nutrition_goals = {ng.goal for ng in user.nutrition_goals} # user nutrtion goals
    user_likes = {like.name for like in user.likes_dislikes if like.preference == "like"} # user likes -- for extra filtering
    user_dislikes = {dislike.name for dislike in user.likes_dislikes if dislike.preference == "dislike"} # user dislikes 

    # initial query --> where search term is included in a recipe's title OR ingredients
    initial_query = db.session.query(Recipe).outerjoin(Ingredient, Recipe.recipe_id == Ingredient.recipe_id).filter(
        ((Recipe.title.ilike(f"%{search_term}%")) | (Ingredient.name.ilike(f"%{search_term}%")))
    ).distinct()

    current_filtered_recipes = initial_query

    # exclude user allergens
    for allergen in user_allergens:
        current_filtered_recipes = current_filtered_recipes.filter(~Recipe.ingredients.any(Ingredient.name.ilike(f"%{allergen}%")))
    
    # exclude user dislikes 
    # for dislike in user_dislikes:
    #     current_filtered_recipes = current_filtered_recipes.filter(~Recipe.ingredients.any(Ingredient.name.ilike(f"{dislike}")))

    # # include likes if True
    # if likes and user_likes:
    #         # list comprehension to hold all individual likes for OR condition
    #         user_like_conditions = [
    #             Recipe.ingredients.any(Ingredient.name.ilike(f"%{liked_ingredient}%")) 
    #             for liked_ingredient in user_likes                   
    #         ]

    #         current_filtered_recipes = current_filtered_recipes.filter(
    #             or_(*user_like_conditions)
    #         )

    # #nutritional goal filters
    # for goal in user_nutrition_goals:
    #     if goal == "low sugar":
    #         # exclude recipes where sugar quantity > 10g per serving
    #         current_filtered_recipes = current_filtered_recipes.filter(
    #             ~Recipe.recipe_nutrients.any(
    #                 and_(
    #                     RecipeNutrient.nutrient_id == Nutrient.nutrient_id,
    #                     Nutrient.name.ilike("%sugar%"),
    #                     RecipeNutrient.quantity > 10
    #                 )
    #             )
    #         )

    #     elif goal == "high protein":
    #         # include recipes where protein quantity >= 20g per serving 
    #         current_filtered_recipes = current_filtered_recipes.filter(
    #             Recipe.recipe_nutrients.any(
    #                 and_(
    #                     RecipeNutrient.nutrient_id == Nutrient.nutrient_id,
    #                     Nutrient.name.ilike("%protein%"),
    #                     RecipeNutrient.quantity >= 20
    #                 )
    #             )
    #         )
        
    #     elif goal == "high fiber":
    #         # include recipes where fiber quantity>=< 5g per serving 
    #         current_filtered_recipes = current_filtered_recipes.filter(
    #             Recipe.recipe_nutrients.any(
    #                 and_(
    #                     RecipeNutrient.nutrient_id == Nutrient.nutrient_id,
    #                     Nutrient.name.ilike("%fiber%"),
    #                     RecipeNutrient.quantity >= 5 
    #                 )
    #             )
    #         )
        
    #     elif goal == "low sodium":
    #         # exclude recipes where sodium quantity > 300mg
    #         current_filtered_recipes = current_filtered_recipes.filter(
    #             ~Recipe.recipe_nutrients.any(
    #                 and_(
    #                     RecipeNutrient.nutrient_id == Nutrient.nutrient_id,
    #                     Nutrient.name.ilike("%sodium%"),
    #                     RecipeNutrient.quantity <= 300
    #                 )
    #             )
    #         )
    
    # diet restirction filters
    # for restriction in user_diet_restrictions:

    #     current_filtered_recipes = current_filtered_recipes.filter(
    #         Recipe.diets.contains([restriction])
    #     )

    current_filtered_recipes = current_filtered_recipes.order_by(Recipe.title)

    return current_filtered_recipes.limit(limit).all()


# ------- Ingredient CRUD functions -------

def create_ingredient(recipe_id, name, quantity, unit):
    """Create and return a new ingredient for a recipe."""

    ingredient = Ingredient(
        recipe_id=recipe_id,
        name=name,
        quantity=quantity,
        unit=unit
    )

    return ingredient


def get_ingredients_by_recipe_id(recipe_id):
    """Return all ingredients for a given recipe."""

    return db.session.query(Ingredient).filter(Recipe.recipe_id==recipe_id).all()


# ------- Nutrient CRUD functions (tracked nutrients defined)-------

def create_nutrient(name, unit):
    """Create and return a new nutrient."""

    nutrient = Nutrient(name=name, unit=unit)

    return nutrient


def get_nutrient_by_name(name):
    """Return a nutrient by its name."""

    return db.session.query(Nutrient).filter(Nutrient.name==name).first()


def get_or_create_nutrient(name, unit):
    """Get or create nutreint, then return nutrient."""

    nutrient = get_nutrient_by_name(name)

    if not nutrient:
        nutrient = create_nutrient(name, unit)
        db.session.add(nutrient)
        db.session.commit()
    
    return nutrient


# ------- RecipeNutrient CRUD functions -------

def create_recipe_nutrient(recipe_id, nutrient_id, quantity):
    """Create and return a new recipe-nutrient link."""

    recipe_nutrient = RecipeNutrient(
        recipe_id=recipe_id,
        nutrient_id=nutrient_id,
        quantity=quantity
    )

    return recipe_nutrient


def get_nutrients_by_recipe_id(recipe_id):
    """Return all nutrients and their quantities."""

    return db.session.query(RecipeNutrient).filter(Recipe.recipe_id==recipe_id).all()


# ------- MealLog CRUD functions -------

def create_meal_log(user_id, log_date, meal_type):
    """Create and return a new meal log entry."""

    meal_log = MealLog(
        user_id=user_id,
        log_date=log_date,
        meal_type=meal_type,
        date_added=datetime.now()
    )

    return meal_log


def get_meal_log_by_user_id_and_date(user_id, log_date):
    """Return all meal logs for a user on a specific date."""

    return db.session.query(MealLog).filter(User.user_id==user_id, MealLog.log_date==log_date).all()


def get_meal_log_by_id(meal_log_id):
    """Return a meal log by its primary key."""

    return db.session.query(MealLog).get(meal_log_id)


# ------- MealLogRecipe CRUD functions -------

def add_recipe_to_meal_log(meal_log_id, recipe_id, serving_size):
    """Add and return a recipe to a meal log."""

    ml_recipe = MealLogRecipe(
        meal_log_id=meal_log_id,
        recipe_id=recipe_id,
        serving_size=serving_size
    )

    return ml_recipe


def get_recipes_in_meal_log(meal_log_id):
    """Return all recipes for a specific meal log entry."""

    return db.session.query(MealLogRecipe).filter(
        MealLogRecipe.meal_log_id==meal_log_id).all()


# ------- MealPlan CRUD functions -------

def create_meal_plan(user_id, meal_plan_date):
    """Create and return a new meal plan."""

    meal_plan = MealPlan(
        user_id=user_id,
        meal_plan_date=meal_plan_date,
        date_added = datetime.now()
    )

    return meal_plan


def get_meal_plan_by_user_id_and_date(user_id, meal_plan_date):
    """Return a meal plan for a user on a specific date."""

    return db.session.query(MealPlan).filter(
        User.user_id==user_id, MealPlan.meal_plan_date==meal_plan_date).first()


# ------- MealPlanRecipe CRUD functions -------

def add_recipe_to_meal_plan(meal_plan_id, recipe_id, meal_type, serving_size):
    """Add and return a recipe to a meal plan."""

    mp_recipe = MealPlanRecipe(
        meal_plan_id=meal_plan_id,
        recipe_id=recipe_id,
        meal_type=meal_type,
        serving_size=serving_size
    )

    return mp_recipe


def get_recipes_in_meal_plan(meal_plan_id):
    """Return all recipes in a meal plan."""

    return db.session.query(MealPlanRecipe).filter(MealPlanRecipe.meal_plan_id==meal_plan_id).all()




if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()



