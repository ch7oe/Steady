"""Fetching from Spoonacular API endpoints."""
import requests
from datetime import datetime
from crud import db, create_recipe, get_recipe_by_spoonacular_id, create_ingredient, create_recipe_nutrient, get_or_create_nutrient
import os 


API_KEY = os.environ['SPOONACULAR_KEY']
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

def get_and_cache_spoonacular_recipes(recipe_query, user_allergens=None, user_diet_restrictions=None, user_likes=None, user_dislikes=None, limit=10):
    """Send search recipes request to Spoonacular API. Cache and return fetched recipes."""

    headers = {'x-api-key': API_KEY} # can put api key for spoonacular in header or query string 

    spoonacular_params = {
        'query': recipe_query, # natural language recipe search query
        'number': limit, # how many recipes to return
        'instructionsRequired': True,
        'addRecipeInformation': True, 
        'addRecipeNutrition': True,
    }

    # user specific filters 
    if user_allergens:
        spoonacular_params['intolerances'] = ', '.join(user_allergens)
    
    if user_diet_restrictions:
        spoonacular_params['diet'] = ', '.join(user_diet_restrictions)

    if user_likes:
        spoonacular_params['includeIngredients'] = ', '.join(user_likes)
    
    if user_dislikes:
        spoonacular_params['excludeIngredients'] = ', '.join(user_dislikes)
    
    # try and except????
    response = requests.get(f'{SPOONACULAR_BASE_URL}/complexSearch', headers=headers, params=spoonacular_params)
    response = response.json()

    spoonacular_recipes = response.get('results', [])
    cached_recipes_from_database = []

    for recipe in spoonacular_recipes:
        
        # check if a recipe is already in database
        existing_recipe = get_recipe_by_spoonacular_id(recipe['id'])

        if not existing_recipe: # if not in database
            # create new recipe in database
            new_recipe = create_recipe(
                spoonacular_id=recipe['id'],
                title=recipe.get('title', 'No title'),
                source=recipe.get('sourceName', 'N/A'),
                url=recipe.get('sourceUrl', 'N/A'),
                servings=recipe.get('servings', 1),
                instructions=recipe.get('instructions', 'No instructions provided'),
                diets=recipe.get('diets', 'N/A'),
                texture=None
            )

            db.session.add(new_recipe)
            cached_recipes_from_database.append(new_recipe) # append to list of recipes cached during this fetch

            # cache ingredients
            if 'extendedIngredients' in recipe:
                for ingredient in recipe['extendedIngredients']:
                    create_ingredient(
                        recipe_id=new_recipe.recipe_id,
                        name=ingredient.get('name', 'N/A'),
                        quantity=ingredient.get('amount', 0.0),
                        unit=ingredient.get('unit', 'unit')
                    )
            
            # cache nutrients
            # from setting 'addRecipeNutrition' param to True
            if 'nutrition' in recipe and 'nutrients' in recipe['nutrition']:
                for nutrient in recipe['nutrition']['nutrients']:

                    nutrient_in_recipe = get_or_create_nutrient(nutrient['name'], nutrient['unit'])

                    if nutrient_in_recipe: # check if nutrient exists before linking to recipe
                        create_recipe_nutrient(
                            recipe_id=new_recipe.recipe_id,
                            nutrient_id=nutrient_in_recipe.nutrient_id,
                            quantity=nutrient['amount'] # total amount per recipe, not per serving
                        )

        else:
            # if recipe is already cached, add to list of recipes to return 
            cached_recipes_from_database.append(existing_recipe)
    
    return cached_recipes_from_database
        





        
