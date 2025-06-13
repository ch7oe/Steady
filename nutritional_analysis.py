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
            


    




                    









if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    app.app_context().push()