"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime

import crud 
from model import db, User, DietaryRestriction, Medication, Allergy, NutritionGoal, LikeDislike, Reminder, Recipe, Ingredient, Nutrient, RecipeNutrient, MealLog, MealLogRecipe, MealPlan, MealPlanRecipe, connect_to_db
from server import app

os.system("dropdb steady")
os.system("createdb steady")

connect_to_db(app)
app.app_context().push()
db.create_all()

