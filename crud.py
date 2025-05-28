"""CRUD operations"""

from model import db, User, DietaryRestriction, Medication, Allergy, NutritionGoal, LikeDislike, Reminder, Recipe, Ingredient, Nutrient, RecipeNutrient, MealLog, MealLogRecipe, MealPlan, MealPlanRecipe, connect_to_db
from datetime import datetime

# User functions

def create_user(fname, lname, email, password, weight, swallow_difficulty=False):
    """Create and return a new user."""

    # test: 
    # user = create_user("chloe", "nixon", "cnixon@gmail.com", "pass1234", 150)
    # user_2 = create_user("coffee", "brew", "cnixonnixon@gmail.com", "fun", 122)
    # db.session.add(user)
    # db.session.add(user_2)
    # db.session.commit()

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


def get_user_by_id(user_id):
    """Return a user by primary key."""

    return db.session.query(User).get(user_id)


def get_user_by_email(email):

    return db.session.query(User).filter(User.email == email).first()

    














if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()



