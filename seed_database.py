"""Script to seed database."""

import os
from random import choice, randint
from datetime import datetime, time, date, timedelta

import crud 
from model import db, connect_to_db
from apis.api_spoonacular import get_and_cache_spoonacular_recipes
from server import app

# clean db
os.system("dropdb steady")
os.system("createdb steady")

connect_to_db(app)
app.app_context().push()
db.create_all()

print("Creating users...")

# ------- create sample users -------
user1 = crud.create_user("Chloe", "Nixon", "chloe@gmail.com", "password123", 150, False) # Vegetarian
user2 = crud.create_user("Court", "Yellow", "court@gmail.com", "password456", 175, False) # Gluten Free
user3 = crud.create_user("Jade", "Doe", "jade@gmail.com", "password789", 130, False)


db.session.add_all([user1, user2, user3])
db.session.commit()

# ------- seeding user-specific data -------
print("Seeding user preferences...")

# User 1 - vegetarian, peanut allergy 
user1_dr = crud.create_diet_restriction(user1.user_id, "vegetarian")
user1_allergy = crud.create_allergy(user1.user_id, "peanut")
user1_ng =  crud.create_nutrition_goal(user1.user_id, "high fiber")
user1_ld_1 = crud.create_like_dislike(user1.user_id, "broccoli", "like")
user1_ld_2 = crud.create_like_dislike(user1.user_id, "mayonnaise", "dislike")
# meds
user1_med_1 = crud.create_medication(user1.user_id, "levodopa", "100mg", "3 times daily", time(8,0))
user1_med_2 = crud.create_medication(user1.user_id, "levodopa", "100mg", "3 times daily", time(16,0))
user1_med_3 = crud.create_medication(user1.user_id, "levodopa", "100mg", "3 times daily", time(0,0))
user1_reminder = crud.create_reminder(user1.user_id, "medication", time(7, 55), "daily", "Take morning Levodopa!")

db.session.add_all(
    [user1_dr,
    user1_allergy, 
    user1_ng,
    user1_ld_1,
    user1_ld_2,
    user1_med_1,
    user1_med_2,
    user1_med_3,
    user1_reminder]
)
db.session.commit()

# User 2 - gluten free, dairy allergy
user2_dr = crud.create_diet_restriction(user2.user_id, "gluten free")
user2_allergy = crud.create_allergy(user2.user_id, "dairy")
user2_ng = crud.create_nutrition_goal(user2.user_id, "low protein")
user2_ld =crud.create_like_dislike(user2.user_id, "smoothies", "dislike")
user2_med_1 = crud.create_medication(user2.user_id, "levodopa", "50mg", "2 times daily", time(9, 0))
user2_med_2 = crud.create_medication(user2.user_id, "levodopa", "50mg", "2 times daily", time(17, 0))

db.session.add_all(
    [user2_dr,
    user2_allergy,
    user2_ng,
    user2_ld,
    user2_med_1,
    user2_med_2]
)
db.session.commit()

# User 3 - No diet restriction, no allergy 
user3_ng = crud.create_nutrition_goal(user3.user_id, "low sugar")
user3_ld_1 = crud.create_like_dislike(user3.user_id, "fish", "like")
user3_ld_2 = crud.create_like_dislike(user3.user_id, "olives", "dislike")

db.session.add_all([user3_ng, user3_ld_1, user3_ld_2])
db.session.commit()


# ------- nutrients definitions/to track -------
print("Seeding nutrients...")

nutrients = nutrients = ["Protein", "Fiber", "Sugar", "Sodium", "Calcium", "Vitamin D", "Omega-3 Fatty Acids", "Vitamin B6", "Folate", "Vitamin B12"]
units = ["g", "g", "g", "mg", "mg", "IU", "mg", "mg", "mcg", "mcg"]

for n, u in zip(nutrients, units):
    new_nutrient = crud.get_or_create_nutrient(n, u)

#  ------- recipe seeding using Spoonacular api and cached recipes -------
print("Seeding recipes (API + manual fallback)...")

# 1. Healthy
healthy_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="healthy",
    limit=5
)
if healthy_recipes: db.session.add_all(healthy_recipes)

# 2. Vegetarian stir fry (User 1)
user1_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="vegetarian stir fry",
    limit=5,
    user_diet_restrictions=["vegetarian"]
)
if user1_recipes: db.session.add_all(user1_recipes)

# 3. hicken Soup (User 2 - gluten free)
user2_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="chicken soup",
    limit=5,
    user_diet_restrictions=["gluten free"]
)

# 4. Fish (User 3)
user3_recipes = get_and_cache_spoonacular_recipes(recipe_query="fish", limit=5)
if user3_recipes: db.session.add_all(user3_recipes)

# 5. Vegetarian Soup
veg_soup_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="tomato soup",
    limit=3,
    user_diet_restrictions=["vegetarian"]
)
if veg_soup_recipes: db.session.add_all(veg_soup_recipes)

db.session.commit()

# ------- seeding user meal plans with recipes -------
print("Seeding meal plans...")

today = date.today()
tomorrow = today + timedelta(days=1)

# User 1 meal plan
mp_user1 = crud.create_meal_plan(user1.user_id, today)
db.session.add(mp_user1)
db.session.commit()

if user1_recipes:
    crud.add_recipe_to_meal_plan(mp_user1.meal_plan_id, user1_recipes[0].recipe_id, "dinner", 1.0)

# User 2 meal plan
mp_user2 = crud.create_meal_plan(user2.user_id, today)
db.session.add(mp_user2)
db.session.commit()

if user2_recipes:
    crud.add_recipe_to_meal_plan(mp_user2.meal_plan_id, user2_recipes[0].recipe_id, "lunch", 1.0)

# User 2 meal plan
mp_user3 = crud.create_meal_plan(user3.user_id, today)
db.session.add(mp_user3)
db.session.commit()

if user3_recipes:
    crud.add_recipe_to_meal_plan(mp_user3.meal_plan_id, user3_recipes[0].recipe_id, "breakfast", 1.0)


# ------- seeding user meal logs with recipes ------- 
print("Seeding meal logs...")

yesterday = today - timedelta(days=1)

# User 1 meal logs - breakfast & lunch 
log1 = crud.create_meal_log(user1.user_id, today, "breakfast")
db.session.add(log1)
db.session.commit()

if user1_recipes:
    # log one serving of first recipe today
    crud.add_recipe_to_meal_log(log1.meal_log_id, user1_recipes[0].recipe_id, 1.0)


log2 = crud.create_meal_log(user1.user_id, today, "lunch")
db.session.add(log2)
db.session.commit()

if user1_recipes and len(user1_recipes) > 1:
    # log one serving of second recipe
    crud.add_recipe_to_meal_log(log1.meal_log_id, user1_recipes[1].recipe_id, 1.0)

# User 2 meal log - lunch yesterday
log3 = crud.create_meal_log(user2.user_id, yesterday, "lunch")
db.session.add(log3)
db.session.commit()

if user2_recipes:
    crud.add_recipe_to_meal_log(log3.meal_log_id, user2_recipes[0].recipe_id, 1.0)


db.session.commit()

print("Database seeding complete! :)")