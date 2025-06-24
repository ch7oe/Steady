"""Models for Parkinson's App."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    hashed_password = db.Column(db.String, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    signup_date = db.Column(db.DateTime, nullable=False)
    swallow_difficulty = db.Column(db.Boolean)

    diet_restrictions = db.relationship("DietaryRestriction", back_populates="user")
    nutrition_goals = db.relationship("NutritionGoal", back_populates="user")
    likes_dislikes = db.relationship("LikeDislike", back_populates="user")
    allergies = db.relationship("Allergy", back_populates="user")
    meds = db.relationship("Medication", back_populates="user")
    reminders = db.relationship("Reminder", back_populates="user")
    meal_plans = db.relationship("MealPlan", back_populates="user")
    meal_logs = db.relationship("MealLog", back_populates="user")

    def __repr__(self):
        return f"<User user_id={self.user_id} fname={self.fname} lname={self.lname}>"
    

class DietaryRestriction(db.Model):
    """A user's dietary restriction."""

    __tablename__ = "dietary_restrictions"

    diet_restriction_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    restriction = db.Column(db.String, nullable=False)

    user = db.relationship("User", back_populates="diet_restrictions")

    def __repr__(self):
        return f"<DietaryRestriction diet_restriction_id={self.diet_restriction_id}>"


class Medication(db.Model):
    """Medication a user is taking."""

    __tablename__ = "medications"

    medication_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)  # ex. "100mg"
    frequency = db.Column(db.String, nullable=False) # ex. "daily"
    timing = db.Column(db.Time, nullable=False)  # ex. "8:00 AM"

    user = db.relationship("User", back_populates="meds")

    def __repr__(self):
        return f"<Medication medication_id={self.medication_id} name={self.name}>"


class Allergy(db.Model):
    """A user's allergen."""

    __tablename__ = "allergies"

    allergy_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    allergen = db.Column(db.String, nullable=False)

    user = db.relationship("User", back_populates="allergies")

    def __repr__(self):
        return f"<Allergy allergy_id={self.allergy_id} allergen={self.allergen}>"
    

class NutritionGoal(db.Model):
    """A user's nutrition goal."""

    __tablename__ = "nutrition_goals" 

    nutrition_goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    goal = db.Column(db.String, nullable=False) # ex. "low protein"

    user = db.relationship("User", back_populates="nutrition_goals")

    def __repr__(self):
        return f"<NutritionGoal nutrition_goal_id={self.nutrition_goal_id} goal={self.goal}>"
    

class LikeDislike(db.Model):
    """A user's like/dislike."""

    __tablename__ = "likesdislikes"

    like_dislike_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    preference = db.Column(db.String, nullable=False) # ex. "like" or "dislike"

    user = db.relationship("User", back_populates="likes_dislikes")

    def __repr__(self):
        return f"<LikeDislike like_dislike_id={self.likes_dislikes_id} name={self.name} preference={self.preference}>"


class Reminder(db.Model):
    """A user's reminder."""

    __tablename__ = "reminders"

    reminder_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    reminder_type = db.Column(db.String, nullable=False) # ex. "medication" "meal" "hydration"
    reminder_time = db.Column(db.Time, nullable=False)
    frequency = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)

    user = db.relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder reminder_id={self.reminder_id} type={self.reminder_type}>"


class Recipe(db.Model):
    """A recipe."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    spoonacular_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    source = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    servings = db.Column(db.Float, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    texture = db.Column(db.String)
    diets = db.Column(JSONB) 
    date_added = db.Column(db.DateTime, nullable=False)

    meal_plan_recipes = db.relationship("MealPlanRecipe", back_populates="recipe")
    meal_log_recipes = db.relationship("MealLogRecipe", back_populates="recipe")
    ingredients = db.relationship("Ingredient", back_populates="recipe")
    recipe_nutrients = db.relationship("RecipeNutrient", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe recipe_id={self.recipe_id} title={self.title}>"
    

class Ingredient(db.Model):
    """An ingredient in a recipe."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String, nullable=False)

    recipe = db.relationship("Recipe", back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient ingredient_id={self.ingredient_id} name={self.name}>"


class Nutrient(db.Model):
    """A nutrient the app tracks."""

    __tablename__ = "nutrients"

    nutrient_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    unit = db.Column(db.String, nullable=False)

    recipe_nutrients = db.relationship("RecipeNutrient", back_populates="nutrient")

    def __repr__(self):
        return f"<Nutrient nutrient_id={self.nutrient_id} name={self.name}>"
    

class RecipeNutrient(db.Model): 
    """A nutrient in a recipe."""

    __tablename__ = "recipe_nutrients"

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), primary_key=True, nullable=False)
    nutrient_id = db.Column(db.Integer, db.ForeignKey("nutrients.nutrient_id"), primary_key=True, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    recipe = db.relationship("Recipe", back_populates="recipe_nutrients")
    nutrient = db.relationship("Nutrient", back_populates="recipe_nutrients")

    def __repr__(self):
        return f"<RecipeNutrient recipe_id={self.recipe_id} nutrient_id={self.nutrient_id}>"


class MealLog(db.Model):
    """An instance a user eats a meal."""

    __tablename__ = "meal_logs"

    meal_log_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String, nullable=False) # ex. ex. "breakfast" "lunch" "dinner" "snack"
    date_added = db.Column(db.Date, nullable=False)

    user = db.relationship("User", back_populates="meal_logs")
    meal_log_recipes = db.relationship("MealLogRecipe", back_populates="meal_log")

    def __repr__(self):
        return f"<MealLog meal_log_id={self.meal_log_id} meal_type={self.meal_type}>"
    

class MealLogRecipe(db.Model):
    """A recipe a user ate in a meal."""

    __tablename__ = "meal_log_recipes"

    meal_log_id = db.Column(db.Integer, db.ForeignKey("meal_logs.meal_log_id"), primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), primary_key=True, nullable=False)
    serving_size = db.Column(db.Float, nullable=False)

    recipe = db.relationship("Recipe", back_populates="meal_log_recipes")
    meal_log = db.relationship("MealLog", back_populates="meal_log_recipes")

    def __repr__(self):
        return f"<MealLogRecipe meal_log_id={self.meal_log_id} recipe_id={self.recipe_id}>"
    

class MealPlan(db.Model):
    """A user's meal plan."""

    __tablename__ = "meal_plans"

    meal_plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    meal_plan_date = db.Column(db.Date, nullable=False)
    date_added = db.Column(db.Date, nullable=False)

    user = db.relationship("User", back_populates="meal_plans")
    meal_plan_recipes = db.relationship("MealPlanRecipe", back_populates="meal_plan")

    def __repr__(self):
        return f"<MealPlan meal_plan_id={self.meal_plan_id} meal_plan_date={self.meal_plan_date}>"
    

class MealPlanRecipe(db.Model):
    """A recipe in a meal plan."""

    __tablename__ = "meal_plan_recipes"

    meal_plan_id = db.Column(db.Integer, db.ForeignKey("meal_plans.meal_plan_id"), primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"), primary_key=True, nullable=False)
    meal_type = db.Column(db.String, primary_key=True, nullable=False) # ex. ex. "breakfast" "lunch" "dinner" "snack"
    serving_size = db.Column(db.Float, nullable=False)

    recipe = db.relationship("Recipe", back_populates="meal_plan_recipes")
    meal_plan = db.relationship("MealPlan", back_populates="meal_plan_recipes")

    def __repr__(self):
        return f"<MealPlanRecipe meal_plan_id={self.meal_plan_id} recipe_id={self.recipe_id} meal_type={self.meal_type}>"
    


def connect_to_db(flask_app, db_uri="postgresql:///steady", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected! :)")


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()
