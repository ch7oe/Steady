// get target date string 
        const targetDate = "{{ target_date.strftime('%Y-%m-%d') }}";
        
        // grab DOM elements 
        const recipeSearchInput = document.querySelector("#recipe-search-input");
        const recipeSearchBttn = document.querySelector("#recipe-search-button");
        const recipeSearchResultDiv = document.querySelector("#search-results");
        const filterLikesCheckbox = document.querySelector("#filter-likes")

        // fetch and display recipes
        const queryRecipeSearch = recipeSearchInput.value.trim();
        if (!queryRecipeSearch) {
            recipeSearchResultDiv.textContent = "<p>Please enter search term.</p>"
        }

recipeSearchBttn.addEventListener("click", (evt) => {
    
})