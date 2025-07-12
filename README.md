# Steady
---

## Table of Contents

1.  [Project Description](#project-description)
2.  [Features](#features)
3.  [Demo & Screenshots](#demo--screenshots)
4.  [Tech Stack](#tech-stack)
5.  [Installation & Setup](#installation--setup)
6.  [Usage](#usage)
7.  [Challenges & Learning](#challenges--learning)
8.  [Future Features](#future-features)
9.  [Author](#author)
10. [License](#license)

---

## Project Description

SteadyPlate is a personalized web application designed to empower Parkinson's patients and their caregivers in managing daily dietary needs. Inspired by the challenges faced with meal planning and nutrition management, SteadyPlate aims to reduce decision fatigue and support healthier routines by providing intuitive tools for custom meal planning, nutrition tracking, and grocery list generation. It brings ease and comfort back to the kitchen, one plate at a time.

---

## Features

* **Secure User Authentication:**
    * Seamless user registration and login.
    * Password hashing with `argon2` for enhanced security.
* **Dynamic Meal Planning:**
    * **Weekly Calendar View:** Visualize meal plans for the entire week.
    * **Daily Add/Edit Interface:** Easily add or remove recipes for specific meal types (breakfast, lunch, dinner, snack) on any given day.
* **Recipe Search & Caching:**
    * **AJAX-powered search** allows users to discover recipes without page reloads.
    * **Smart Filtering:** Recipes are filtered based on a combination of user preferences (allergies, dislikes, diet restrictions, nutritional goals) and search terms.
    * **Spoonacular API Integration:** Fetches and caches new recipes from Spoonacular, ensuring a rich and growing local database while managing API rate limits.
* **Meal Logging:**
    * Log consumed meals by selecting recipes and specifying serving sizes for any date.
* **Nutritional Tracking & Analysis:**
    * View daily nutrient summaries (Protein, Fiber, Calcium, Vitamins, etc.) based on logged meals.
    * Interactive **Chart.js** bar chart visualizes daily intake against predefined goals.
* **Automated Grocery List Generation:**
    * Consolidates all ingredients from planned weekly meals into a single, aggregated, and alphabetically sorted grocery list.

---

## Demo & Screenshots

https://youtu.be/MmirFVgMLqI?si=c_5cC41HpoREQBUW

**Homepage:**
<img width="1280" height="800" alt="homepage screenshot" src="https://github.com/user-attachments/assets/2821b617-2f61-483a-a1b9-ec5455d30551" />

**Dashboard:**
<img width="1275" height="718" alt="dashboard screenshot" src="https://github.com/user-attachments/assets/eb9370a1-265c-4fc4-98cb-7676034271f2" />

**Meal Plan Add/Edit:**
<img width="1280" height="671" alt="meal plan page screenshot" src="https://github.com/user-attachments/assets/c5ab087e-e0c3-4dd0-bbe4-faf6b36c181f" />

<img width="1278" height="675" alt="your weekly meal Plan page screenshot" src="https://github.com/user-attachments/assets/7d5e9aa9-26f7-47b0-9671-68e8e77a5e51" />

**Meal Logging:**
<img width="1280" height="674" alt="log meal page 1 screenshot" src="https://github.com/user-attachments/assets/fbf9f2d7-fdc5-4b5d-bb5c-ec82cfbdf51f" />

<img width="1280" height="675" alt="log meal page 2 screenshot" src="https://github.com/user-attachments/assets/1411433d-5f9f-47ad-9a5d-8d79561bcc08" />

**Grocery List:**
<img width="1280" height="718" alt="grocery list" src="https://github.com/user-attachments/assets/4ef635fd-0fca-461f-9c06-9cec99aa9f26" />

---

## Tech Stack

**Backend:**
* **Python 3.9+**
* **Flask:** Web framework for routing and server logic.
* **SQLAlchemy:** ORM for interacting with the database.
* **PostgreSQL:** Relational database for persistent data storage (recipes, users, logs).

**Frontend:**
* **HTML5**
* **CSS3** Custom styling to complement the cozy theme
* **JavaScript:** For dynamic content, AJAX requests, and DOM manipulation.
* **Bootstrap 5:** Responsive CSS framework for UI components and layout.
* **Jinja2:** Templating engine for dynamic HTML generation.

**APIs & Libraries:**
* **Spoonacular API:** For comprehensive recipe data (ingredients, instructions, nutrition).
* **Chart.js:** For interactive data visualization on the dashboard.
* **Passlib (Argon2):** For secure password hashing.
* **Requests:** For making HTTP requests to external APIs.
* **(Planned): Twilio API:** For future medication text reminders.

---

## Author

**Chloe Nixon**
Github Profile - https://github.com/ch7oe
LinkedIn Profile - https://www.linkedin.com/in/ch10e/






