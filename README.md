# Stock-Taking System

## Overview

This is a Flask-based stock-taking system designed to manage inventory, track sales, and compute revenue for a bar or any other type of business that sells drinks. The system allows users to:
- Add new stock items (drinks) with predefined prices.
- Track daily stock levels by carrying over remaining stock from the previous day.
- Record sales and compute the revenue based on the sales quantity and item prices.
- Prevent adding duplicate items to the stock inventory.
- Carry forward the stock for the next day automatically.

## Features

1. **Item Management:**
   - Add new items to the stock list.
   - Prevent duplicate items from being added.
   - Predefined item prices for automatic cash computation based on sales.

2. **Stock Records:**
   - Track daily stock levels: Old Stock, Current Stock, and New Stock.
   - Automatically calculate sales based on stock usage.
   - Automatically calculate cash based on item prices and sales quantity.

3. **Daily Carry Forward:**
   - Automatically carry forward the remaining stock to the next day’s old stock.

4. **User Authentication:**
   - User login functionality using Flask-Login for authentication.
   - Passwords are securely hashed using Flask-Bcrypt.

## Technologies Used

- **Flask**: A lightweight Python web framework.
- **SQLAlchemy**: ORM for database operations.
- **Flask-Migrate**: Database migrations.
- **Flask-Bcrypt**: Password hashing for secure user authentication.
- **Flask-Login**: User session management.
- **Jinja2**: Templating engine for rendering HTML.
- **Postman**: API testing tool for interacting with routes.

## Requirements

To run this project, you'll need the following dependencies:

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-Login
- Environs

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/stock-taking-system.git
   cd stock-taking-system
   
2. Install dependencies:

    ```bash
     pip install -r requirements.txt

3. Create a .env file in the root directory with the following contents:
  
    ```bash
     SECRET_KEY=your_secret_key
     SQLALCHEMY_DATABASE_URI=your_database_uri
     SQLALCHEMY_TRACK_MODIFICATIONS=False

5. Run database migrations:
   
    ```bash
        flask db upgrade
7. Run the Flask app:

    ```bash
    python app.py
