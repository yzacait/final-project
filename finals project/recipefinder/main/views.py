# main/views.py
import re
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

from django import forms
from .forms import IngredientsForm, FiltersForm

from django.core.paginator import Paginator

def home(request):
    return render(request, 'main/home.html')

def checklist(request):
    if request.method == 'POST':

        ingredients_form = IngredientsForm(request.POST)
        filters_form = FiltersForm(request.POST)
        if ingredients_form.is_valid() and filters_form.is_valid():
            ingredients = ingredients_form.cleaned_data
            filters = filters_form.cleaned_data
            request.session['ingredients'] = ingredients
            request.session['filters'] = filters
            return redirect('results')
    else:
        ingredients_form = IngredientsForm()
        filters_form = FiltersForm()

    return render(request, 'main/checklist.html', {'ingredients_form': ingredients_form, 'filters_form': filters_form})


def results(request):
    ingredients = request.session.get('ingredients', {})
    filters = request.session.get('filters', {})

    df = pd.read_csv('main/data/recipes.csv')

    df['Vegetarian'] = df['Vegetarian?'].map({'Yes': True, 'No': False})
    
    # Initialize filtered_df with all recipes
    filtered_df = df.copy()

    # Apply ingredient filters if any ingredients are selected
    if any(ingredients.values()):
        mask = pd.Series([False] * len(df), dtype=bool)
        for category, selected_ingredients in ingredients.items():
            if selected_ingredients:
                ingredient_masks = [filtered_df['Ingredients'].str.contains(ingredient, case=False) for ingredient in selected_ingredients]
                category_mask = pd.concat(ingredient_masks, axis=1).any(axis=1)
                mask |= category_mask
        filtered_df = filtered_df[mask]

    # Apply cuisine filter
    if filters.get('cuisine'):
        cuisines = [cuisine.lower() for cuisine in filters['cuisine']]
        filtered_df = filtered_df[filtered_df['Cuisine'].str.lower().isin(cuisines)]

    # Apply vegetarian filter
    vegetarian = filters.get('vegetarian')
    if vegetarian is not None:
        filtered_df = filtered_df[filtered_df['Vegetarian'] == vegetarian]

    # Apply difficulty filter
    if filters.get('difficulty'):
        difficulties = [difficulty.lower() for difficulty in filters['difficulty']]
        filtered_df = filtered_df[filtered_df['Level'].str.lower().isin(difficulties)]

    # Count matched ingredients
    filtered_df['Matched Ingredients'] = 0
    for category, selected_ingredients in ingredients.items():
        if selected_ingredients:
            for ingredient in selected_ingredients:
                filtered_df.loc[filtered_df['Ingredients'].str.contains(ingredient, case=False), 'Matched Ingredients'] += 1

    # Sort recipes by number of matched ingredients in descending order
    filtered_df = filtered_df.sort_values(by='Matched Ingredients', ascending=False)

    # Convert filtered DataFrame to dictionary records
    recipes = filtered_df.to_dict('records')

    # Add a new key to each recipe dictionary with the count of matched ingredients
    for recipe in recipes:
        recipe['num_matched_ingredients'] = recipe['Matched Ingredients']

    if not recipes:
        messages.info(request, 'No recipes found matching your criteria.')

    # Pagination
    paginator = Paginator(recipes, 30)  # Show 30 recipes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/results.html', {'page_obj': page_obj})


def replace_single_quotes(text):
    # This regular expression matches single quotes within double quotes
    return re.sub(r'(?<=")[^"]*(?=")', lambda x: x.group(0).replace("'", ""), text)

def recipe_detail(request, recipe_id):
    df = pd.read_csv('main/data/recipes.csv')
    recipe = df.loc[df['ID'] == recipe_id].to_dict('records')[0]
    
    # Replace single quotes inside double quotes with blanks in Ingredients
    recipe['Ingredients'] = replace_single_quotes(recipe['Ingredients'])
    
    # Split ingredients into a list and strip extra characters
    ingredients_list = [ingredient.strip("[],") for ingredient in re.split(r"[\"']", recipe['Ingredients'])]
    recipe['Ingredients'] = ingredients_list

    # Replace single quotes inside double quotes with blanks in Directions
    recipe['Directions'] = replace_single_quotes(recipe['Directions'])
    
    # Split instructions into a list and strip extra characters
    instructions_list = [instruction.strip("[],") for instruction in re.split(r"[\"']", recipe['Directions'])]
    recipe['Directions'] = instructions_list
    
    return render(request, 'main/recipe_detail.html', {'recipe': recipe})
