"""Fetching from Spoonacular API endpoints."""

import requests
from datetime import datetime
from crud import db, create_recipe, get_recipe_by_spoonacular_id, create_ingredient, create_recipe_nutrient, get_or_create_nutrient
import os 


API_KEY = os.environ['SPOONACULAR_KEY']
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

def get_and_cache_spoonacular_recipes(recipe_query, user_allergens=None, user_diet_restrictions=None, user_dislikes=None, protein_goal=None, limit=20):
    """Send search recipes request to Spoonacular API. Cache and return fetched recipes.
    protein_goal: "high" (>= 25g) or "low" (<= 10g)
    """

    headers = {'x-api-key': API_KEY} 

    spoonacular_params = {
        'query': recipe_query, # natural language recipe search query
        'number': limit, # how many recipes to return
        'instructionsRequired': True,
        'addRecipeInformation': True, 
        'addRecipeNutrition': True,
        'fillIngredients': True,
        'ignorePantry': True # assumes user has basics like salt/pepper
    }

    # user critical filters (allergies/diet)
    if user_allergens:
        spoonacular_params['intolerances'] = ','.join(user_allergens)
    
    if user_diet_restrictions:
        spoonacular_params['diet'] = ','.join(user_diet_restrictions)

    # parkinson's protein logic -- Levodopa management
    if protein_goal == "high":
        spoonacular_params['minProtein'] = 25 # grams
    elif protein_goal == "low":
        spoonacular_params['maxProtein'] = 15 # grams
    
    if user_dislikes:
        
        top_dislikes = user_dislikes[:5]
        spoonacular_params['excludeIngredients'] = ','.join(top_dislikes)
    
    try:
        response = requests.get(f'{SPOONACULAR_BASE_URL}/complexSearch', params=spoonacular_params)
        response.raise_for_status() # raise error if API fails
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Spoonacular API Error: {e}")
        return []

    spoonacular_recipes = data.get('results', [])
    cached_recipes_from_database = []

    new_ingredients_to_add = []
    new_recipe_nutrients_to_add = []

    for recipe in spoonacular_recipes:
        
        # check if a recipe is already in database
        existing_recipe = get_recipe_by_spoonacular_id(recipe['id'])

        if not existing_recipe: # if not in database
            # create new recipe
            new_recipe = create_recipe(
                spoonacular_id=recipe['id'],
                title=recipe.get('title', 'No title'),
                source=recipe.get('sourceName', 'N/A'),
                url=recipe.get('sourceUrl', 'N/A'),
                servings=recipe.get('servings', 1),
                instructions=recipe.get('instructions', 'No instructions provided'),
                diets=recipe.get('diets', []),
                texture=None
            )
            db.session.add(new_recipe)
            db.session.commit() # commit to get the ID
            

            # cache ingredients
            if 'extendedIngredients' in recipe:
                for ingredient in recipe['extendedIngredients']:
                    new_ingredient = create_ingredient(
                        recipe_id=new_recipe.recipe_id,
                        name=ingredient.get('name', 'N/A'),
                        quantity=ingredient.get('amount', 0.0),
                        unit=ingredient.get('unit', 'unit')
                    )
                    new_ingredients_to_add.append(new_ingredient) # add to list of ingredients to add/commit
            
            # cache nutrients
            # from setting 'addRecipeNutrition' param to True
            if 'nutrition' in recipe and 'nutrients' in recipe['nutrition']:
                for nutrient in recipe['nutrition']['nutrients']:
                    
                    # make sure nutrient exists
                    nutrient_in_recipe = get_or_create_nutrient(nutrient['name'], nutrient['unit'])

                    new_recipe_nutrient = create_recipe_nutrient(
                        recipe_id=new_recipe.recipe_id,
                        nutrient_id=nutrient_in_recipe.nutrient_id,
                        quantity=nutrient['amount'] # total amount per recipe, not per serving
                    )
                    new_recipe_nutrients_to_add.append(new_recipe_nutrient)

            cached_recipes_from_database.append(new_recipe) 

        else:
            cached_recipes_from_database.append(existing_recipe)
        
        # bulk add ingredients and nutrients
        db.session.add_all(new_ingredients_to_add)
        db.session.add_all(new_recipe_nutrients_to_add)
        db.session.commit()
    
    return cached_recipes_from_database
        





        
