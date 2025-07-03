"""Nutritional analysis"""

from datetime import date, timedelta

from model import connect_to_db
import crud


def calculate_daily_nutrient_intake(user_id, intake_date):
    """Calculates total nutrient intake for a user on a given date based on their logged meals.
    returns a dictionary (with keys as nutrient names), containing a dictionary (with quantity and unit as keys) 
    """

    daily_nutrient_intake = {} # will store daily nutrient intake info

    # get all meal logs for the user on given date - MealLog objects 
    meal_logs_for_day = crud.get_meal_log_by_user_id_and_date(user_id, intake_date)

    if not meal_logs_for_day: # if no meals logged for this day
        return daily_nutrient_intake
    
    for meallog in meal_logs_for_day:
        # get all MealLogRecipe entries associated with meal log's id
        meal_log_recipe_entries = crud.get_recipes_in_meal_log(meallog.meal_log_id)

        for logged_recipe_entry in meal_log_recipe_entries: # MealLogRecipe objects
            recipe_id = logged_recipe_entry.recipe_id 
            serving_size_eaten = logged_recipe_entry.serving_size

            # recipe_id from MealLogRecipe object to get full Recipe object
            full_recipe = crud.get_recipe_by_id(recipe_id)

            # total servings in recipe
            total_servings_in_recipe = full_recipe.servings
        
            # get all nutrients in recipe - RecipeNutrient objects 
            nutrients_in_recipe = crud.get_nutrients_by_recipe_id(recipe_id)
            
            for recipe_nutrient in nutrients_in_recipe: # RecipeNutrient objects
                nutrient_name = recipe_nutrient.nutrient.name
                nutrient_unit = recipe_nutrient.nutrient.unit
                nutrient_quantity = recipe_nutrient.quantity # total quantity of a nutrient for original recipe's servings

                # calculate actual quantity of nutrient consumed by the user 
                # based on logged serving size and recipe's original servings
                # (total nutrient quantity in original recipe / number of servings in original recipe ) * (actual servings eaten)

                if total_servings_in_recipe > 0: # avoid dividing by zero

                    actual_quantity_eaten = (nutrient_quantity / total_servings_in_recipe) * (serving_size_eaten)
                else:
                    actual_quantity_eaten = 0.0  # default to zero if original servings zero or not provided 

                if nutrient_name not in daily_nutrient_intake: 
                    # add nutrient quanity for the day with its quantity and unit to daily_nutrient_intake dictionary
                    daily_nutrient_intake[nutrient_name] = {"quantity": 0.0, "unit": nutrient_unit}
                    daily_nutrient_intake[nutrient_name]["quantity"] += actual_quantity_eaten

    return daily_nutrient_intake


# def get_nutrition_analysis_over_period(user_id, start_date, end_date):
#     """Calculates the average daily nutrient intake for a user over a given time period.
#     returns a dictionary of average daily nutrient intake (with keys as  
#     """

     
#     nutrient_intake_over_period = {}  # will store average daily nutrient intake over a time period
#     days_with_logs = 0  # to count number of days with logs to divide by to get average daily nutrient intake 


#     current_date = start_date # date time period starts 
#     while current_date <= end_date: 
#         daily_summary = calculate_daily_nutrient_intake(user_id, current_date)

#         if daily_summary: # only count days with recipe logs
#             days_with_logs += 1

#             for nutrient_name, 
            

def generate_simple_grocery_list_for_week(user_id, week_start_date, week_end_date):
    """generates a gorcery list for a user's meal plan within a given week
    
    returns list of ingredient dictionaries:

    Example: [
        {'name': 'Chicken', 'quantity': 500.0, 'unit': 'g'}, 
        {'name': 'Milk', 'quantity': 2.0, 'unit': 'cups'}
        ]
    """

    ingredient_dicts = {}
    
    current_date = week_start_date

    while current_date <= week_end_date:

        # get the meal plan for this specific day 
        meal_plan_for_day = crud.get_meal_plan_by_user_id_and_date(user_id, current_date)

        if meal_plan_for_day:

            # get MealPlanRecipe entries for this day 
            meal_plan_recipes = crud.get_recipes_in_meal_plan(meal_plan_for_day.meal_plan_id)

            for mp_recipe in meal_plan_recipes: # MealPlanRecipe Objects

                recipe = mp_recipe.recipe
                serving_size_planned = mp_recipe.serving_size

                if not recipe or not recipe.servings:
                    print("recipe not found of has not serving info. skipping ingredients.")
                    continue

                # get all ingredients for this recipe 
                ingredients_for_recipe = crud.get_ingredients_by_recipe_id(recipe.recipe_id)

                for ingredient in ingredients_for_recipe: # ingredient is an Ingredient object
                    ingredient_name = ingredient.name
                    ingredient_unit = ingredient.unit
                    quantity_per_recipe_original = ingredient.quantity # total for recipe's servings 

                    # calculate the quantity needed for the planned serving size 
                    if recipe.servings > 0: # avoid diving by zero

                        quantity_per_original_serving = quantity_per_recipe_original / recipe.servings
                        quantity_needed = quantity_per_original_serving * serving_size_planned
                    
                    else:
                        quantity_needed = 0.0

                    # using (name, unit) as key to correctly group unique items 
                    ingredient_key = (ingredient_name.lower(), ingredient_unit.lower())

                    if ingredient_key not in ingredient_dicts:
                        ingredient_dicts[ingredient_key] = {
                            "name": ingredient_name,
                            "quantity": 0.0,
                            "unit": ingredient_unit
                        }
                    
                    ingredient_dicts[ingredient_key]["quantity"] += quantity_needed

        current_date += timedelta(days=1)
    
    # convert ingredients dict to a list of its values 
    final_grocery_list = list(ingredient_dicts.values())

    return final_grocery_list







                    









if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()