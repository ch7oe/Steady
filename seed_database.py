"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime, time, date, timedelta

import crud 
from model import db, connect_to_db
from apis.api_spoonacular import get_and_cache_spoonacular_recipes
from server import app

os.system("dropdb steady")
os.system("createdb steady")

connect_to_db(app)
app.app_context().push()
db.create_all()


# ------- create sample users -------

user1 = crud.create_user(
    fname="Chloe",
    lname="Nixon", 
    email="chloe@gmail.com", 
    raw_password="password123", 
    swallow_difficulty=False,
    weight=150 
)

user2 = crud.create_user(
    fname="Court",
    lname="Yellow", 
    email="court@gmail.com", 
    raw_password="password456", 
    swallow_difficulty=False,
    weight=175
)

user3 = crud.create_user(
    fname="Jade",
    lname="Doe", 
    email="jade@gmail.com", 
    raw_password="password789", 
    swallow_difficulty=False,
    weight=130 
)

db.session.add_all([user1, user2, user3])
db.session.commit()


# ------- seeding user-specific data -------

# user1 data - Chloe
user1_dr = crud.create_diet_restriction(user1.user_id, "Vegetarian")
user1_allergy = crud.create_allergy(user1.user_id, "Peanut")
user1_ng =  crud.create_nutrition_goal(user1.user_id, "High Fiber")
user1_ld_1 = crud.create_like_dislike(user1.user_id, "Broccoli", "like")
user1_ld_2 = crud.create_like_dislike(user1.user_id, "mayonnaise", "dislike")
user1_med_1 = crud.create_medication(user1.user_id, "Levodopa", "100mg", "3 times daily", time(8,0))
user1_med_2 = crud.create_medication(user1.user_id, "Levodopa", "100mg", "3 times daily", time(16,0))
user1_med_3 = crud.create_medication(user1.user_id, "Levodopa", "100mg", "3 times daily", time(0,0))
user1_reminder = crud.create_reminder(user1.user_id, "Medication", time(7, 55), "daily", "A reminder to take your morning Levodopa! :)")

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

# user2 data - Court
user2_dr = crud.create_diet_restriction(user2.user_id, "Gluten Free")
user2_allergy = crud.create_allergy(user2.user_id, "Dairy")
user2_ng = crud.create_nutrition_goal(user2.user_id, "Low Protein")
user2_ld =crud.create_like_dislike(user2.user_id, "Smoothies", "dislike")
user2_med_1 = crud.create_medication(user2.user_id, "Levodopa", "50mg", "2 times daily", time(9, 0))
user2_med_2 = crud.create_medication(user2.user_id, "Levodopa", "50mg", "2 times daily", time(17, 0))

db.session.add_all(
    [user2_dr,
    user2_allergy,
    user2_ng,
    user2_ld,
    user2_med_1,
    user2_med_2]
)
db.session.commit()

# user3 data - Jade
user3_ng = crud.create_nutrition_goal(user3.user_id, "Low Sugar")
user3_ld_1 = crud.create_like_dislike(user3.user_id, "Fish", "like")
user3_ld_2 = crud.create_like_dislike(user3.user_id, "Olives", "dislike")

db.session.add_all([user3_ng, user3_ld_1, user3_ld_2])
db.session.commit()


# ------- nutrients definitions/to track -------

protein = crud.get_or_create_nutrient("Protin", "g")
fiber = crud.get_or_create_nutrient("Fiber", "g")
sugar = crud.get_or_create_nutrient("Sugar", "g")
sodium = crud.get_or_create_nutrient("Sodium", "mg")
calcium = crud.get_or_create_nutrient("Calcium", "mg")
vitamin_d = crud.get_or_create_nutrient("Vitamin D", "IU")
omega3 = crud.get_or_create_nutrient("Omega-3 Fatty Acids", "mg")
b6 = crud.get_or_create_nutrient("Vitamin B6", "mg")
b9 = crud.get_or_create_nutrient("Folate", "mcg")
b12 = crud.get_or_create_nutrient("Vitamin B12", "mcg")

db.session.add_all(
    [protein,
    fiber,
    sugar,
    sodium,
    calcium,
    vitamin_d,
    omega3,
    b6,
    b9,
    b12]
)
db.session.commit()


#  ------- recipe seeding using Spoonacular api and cached recipes -------

# general healthy recipes
healthy_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="healthy recipes", limit=10
)

db.session.add_all(healthy_recipes)
db.session.commit()

# user1 recipes - Chloe - Vegetarian
chloe_diet_restrictions = [dr.restriction for dr in user1.diet_restrictions]
chloe_allergens = [allergy.allergen for allergy in user1.allergies]

chloe_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="vegetarian stir fry",
    limit=7,
    user_diet_restrictions=chloe_diet_restrictions,
    user_allergens=chloe_allergens
)
db.session.add_all(chloe_recipes)
db.session.commit()

# user2 recipes - Court - Gluten Free
court_diet_restrictions = [dr.restriction for dr in user2.diet_restrictions]
court_allergen = [allergy.allergen for allergy in user1.allergies]

court_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="chicken soup",
    limit=5,
    user_diet_restrictions=court_diet_restrictions,
    user_allergens=court_allergen
)
db.session.add_all(court_recipes)
db.session.commit()

# user3 recipes - Jade - 
jade_dislikes = [dislike.name for dislike in user3.likes_dislikes if dislike.preference == "dislike"]

jade_recipes = get_and_cache_spoonacular_recipes(
    recipe_query="fish",
    limit=5,
    user_dislikes=jade_dislikes
)
db.session.add_all(jade_recipes)
db.session.commit()


# ------- seeding user meal plans with recipes -------

today = date.today()
tomorrow = today + timedelta(days=1)
day_after_tomorrow = today + timedelta(days=2)

# user1 meal plan for today 
meal_plan_today_user1 = crud.create_meal_plan(user1.user_id, today)
db.session.add(meal_plan_today_user1)
db.session.commit()

if chloe_recipes: # breakfast
    user1_mp_recipe_1 = crud.add_recipe_to_meal_plan(
        meal_plan_today_user1.meal_plan_id,
        chloe_recipes[0].recipe_id,
        "breakfast",
        1.0
    )
    
if chloe_recipes: # lunch
    user1_mp_recipe_2 = crud.add_recipe_to_meal_plan(
        meal_plan_today_user1.meal_plan_id,
        chloe_recipes[1].recipe_id, 
        "lunch",
        1.0                  
    )

if chloe_recipes: # dinner
    user1_mp_recipe_3 = crud.add_recipe_to_meal_plan(
        meal_plan_today_user1.meal_plan_id,
        chloe_recipes[1].recipe_id,
        "dinner",
        1.5
    )

db.session.add_all(
    [user1_mp_recipe_1,
    user1_mp_recipe_2,
    user1_mp_recipe_3]
)
db.session.commit()


# user2 meal plan for today and tomorrow
# today
meal_plan_today_user2 = crud.create_meal_plan(user2.user_id, today)
db.session.add(meal_plan_today_user2)
db.session.commit()

if court_recipes: # lunch
    user2_mp_recipe_1 = crud.add_recipe_to_meal_plan(
        meal_plan_today_user2.meal_plan_id,
        court_recipes[0].recipe_id,
        "lunch",
        1.0
    )

# tomorrow
meal_plan_tomorrow_user2 = crud.create_meal_plan(user2.user_id, tomorrow)
db.session.add(meal_plan_tomorrow_user2)
db.session.commit()

if court_recipes: # lunch
    user2_mp_recipe_2 = crud.add_recipe_to_meal_plan(
        meal_plan_tomorrow_user2.meal_plan_id,
        court_recipes[1].recipe_id,
        "lunch",
        1.5
    )

db.session.add_all(
    [user2_mp_recipe_1,
    user2_mp_recipe_2]
)
db.session.commit()


# user3 meal plan for today, tomorrow, and day after tomorrow  
# today
meal_plan_today_user3 = crud.create_meal_plan(user3.user_id, today)
db.session.add(meal_plan_today_user3)
db.session.commit()

if jade_recipes:
    user3_mp_recipe_1 = crud.add_recipe_to_meal_plan(
        meal_plan_today_user3.meal_plan_id,
        jade_recipes[0].recipe_id,
        "dinner",
        1.0
    )

# tomorrow
meal_plan_tomorrow_user3 = crud.create_meal_plan(user3.user_id, tomorrow)
db.session.add(meal_plan_tomorrow_user3)
db.session.commit()

if jade_recipes:
    user3_mp_recipe_2 = crud.add_recipe_to_meal_plan(
        meal_plan_tomorrow_user3.meal_plan_id,
        jade_recipes[1].recipe_id,
        "dinner",
        1.0
    )

# day after tomorrow 
meal_plan_after_tom_user3 = crud.create_meal_plan(user3.user_id, day_after_tomorrow)
db.session.add(meal_plan_after_tom_user3)
db.session.commit()

if jade_recipes:
    user3_mp_recipe_3 = crud.add_recipe_to_meal_plan(
        meal_plan_after_tom_user3.meal_plan_id,
        jade_recipes[2].recipe_id,
        "dinner",
        1.0
    )

db.session.add_all(
    [user3_mp_recipe_1,
    user3_mp_recipe_2,
    user3_mp_recipe_3]
)
db.session.commit()


# ------- seeding user meal logs with recipes ------- 

yesterday = today - timedelta(days=1)

# user1 meal logs today 
user1_meal_log_1 = crud.create_meal_log(user1.user_id, today, "breakfast")
db.session.add(user1_meal_log_1)
db.session.commit()

if chloe_recipes:
    user1_recipe_ml_1 = crud.add_recipe_to_meal_log(
        user1_meal_log_1.meal_log_id,
        chloe_recipes[0].recipe_id,
        1.0
    )

user1_meal_log_2 = crud.create_meal_log(user1.user_id, today, "lunch")
db.session.add(user1_meal_log_2)
db.session.commit()

if chloe_recipes:
    user1_recipe_ml_2 = crud.add_recipe_to_meal_log(
        user1_meal_log_2.meal_log_id,
        chloe_recipes[1].recipe_id,
        0.75
    )
db.session.add_all([user1_recipe_ml_1, user1_recipe_ml_2])
db.session.commit()


# user2 meal log yesterday
user2_meal_log_1 = crud.create_meal_log(user2.user_id, yesterday, "lunch")
db.session.add(user2_meal_log_1)
db.session.commit()

if court_recipes:
    user2_recipe_ml_1 = crud.add_recipe_to_meal_log(
        user2_meal_log_1.meal_log_id,
        court_recipes[1].recipe_id,
        1.0
    )
db.session.add(user2_recipe_ml_1)
db.session.commit()


# user3 meal log yesterday 
user3_meal_log_1 = crud.create_meal_log(user3.user_id, yesterday, "dinner")
db.session.add(user3_meal_log_1)
db.session.commit()

if court_recipes:
    user3_recipe_ml_1 = crud.add_recipe_to_meal_log(
        user3_meal_log_1.meal_log_id,
        jade_recipes[0].recipe_id,
        1.0
    )
db.session.add(user3_recipe_ml_1)
db.session.commit()

print("Database seeding complete! :)")