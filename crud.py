"""CRUD operations"""

from model import db, User, DietaryRestriction, Medication, Allergy, NutritionGoal, LikeDislike, Reminder, Recipe, Ingredient, Nutrient, RecipeNutrient, MealLog, MealLogRecipe, MealPlan, MealPlanRecipe, connect_to_db
from datetime import datetime

# User functions

def create_user(fname, lname, email, password, weight, swallow_difficulty=False):
    """Create and return a new user."""

    user = User(
        fname = fname,
        lname = lname,
        email=email,
        password=password,
        weight=weight,
        signup_date=datetime.now(),
        swallow_difficulty=swallow_difficulty
    
    )

    return user
    

def get_users():
    """Return all users."""

    return db.session.query(User).all()


    














if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()



