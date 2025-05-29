"""CRUD operations"""

from model import db, User, DietaryRestriction, Medication, Allergy, NutritionGoal, LikeDislike, Reminder, Recipe, Ingredient, Nutrient, RecipeNutrient, MealLog, MealLogRecipe, MealPlan, MealPlanRecipe, connect_to_db
from datetime import datetime

# ------- User CRUD functions -------

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
    """Return a user by email."""

    return db.session.query(User).filter(User.email == email).first()


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

    diet_restriction = DietaryRestriction(user_id=user_id, restriction=restriction)

    return diet_restriction


def get_diet_restriction_by_user_id(user_id):
    """Return diet restrictions for a given user."""

    return db.session.query(DietaryRestriction).filter(user_id=user_id).all()


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

    return db.session.query(Medication).filter(user_id=user_id).all()


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

    return db.session.query(Allergy).filter(user_id=user_id).all()


# ------- NutritionGoal CRUD functions -------

def create_nutrition_goal(user_id, goal):
    """Create and return a nutrition goal for a user"""

    ng = NutritionGoal(user_id=user_id, goal=goal)

    return ng


def get_nutrition_goals_by_user_id(user_id):
    """Return all nutrition goals for a given user."""

    return db.session.query(NutritionGoal).filter(user_id=user_id).all()


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
    
    return db.session.query(LikeDislike).filter(user_id=user_id).all()


def get_likes_or_dislikes_by_user_id(user_id, preference):
    """Return all likes or dislikes for a given user."""

    if preference == "like":

        return db.session.query(LikeDislike).filter(user_id=user_id,
                                                    preference="like")
    
    elif preference == "dislike":

        return db.session.query(LikeDislike).filter(user_id=user_id,
                                                    preference="dislike")
    

def update_like_dislike(like_dislike_id, name=None, preference=None):
    """Update and return a user's like or dislike"""

    like_dislike = db.session.query(LikeDislike).filter(like_dislike_id=like_dislike_id)

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

    return db.session.query(Reminder).filter(user_id=user_id).all()


def update_reminder(reminder_id, reminder_type=None, reminder_time=None, frequency=None, message=None):
    """Update and return a reminder for a user."""

    reminder = db.session.query(Reminder).filter(reminder_id=reminder_id)

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









if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()



