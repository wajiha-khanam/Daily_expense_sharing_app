# Daily Expenses Sharing Application
A backend service for managing daily expenses among a group of users. Users can add expenses and split them using three methods: equal split, exact amounts, and percentage split. This application also provides an option to download a balance sheet that shows all expenses in a CSV format.

## Features
* User Management: Add users with email, name, and mobile number.
* Expense Management:
   * Add expenses and split using:
     * Equal split (shared equally)
     * Exact amounts (user-specified amounts)
     * Percentage (user-specified percentage)
   * Retrieve expenses for a specific user or for all users.
* Balance Sheet: Download a CSV file summarizing all expenses.
## Technologies Used
* Flask (Web Framework)
* PostgreSQL (Database)
* SQLAlchemy (ORM for Flask)
* Pandas (For generating balance sheets)
## Setup
1. Install Dependencies
2. Set up PostgreSQL Database
3. Run the Application
## API Endpoints
### 1. Create a New User
* URL: /users
* Method: POST
* Request Body (JSON):
   {
  "email": "user@example.com",
  "name": "John Doe",
  "mobile": "1234567890"
}
### 2. Get User Details
* URL: /users/<user_id>
* Method: GET
### 3. Add an Expense
* URL: /expenses
* Method: POST
* Request Body (JSON example for percentage split):
 {
  "amount": 4000,
  "description": "Party expenses",
  "split_method": "percentage",
  "participants": ["1", "2", "3"],  
  "percentages": [50, 25, 25],      // Percentages (must add to 100)
  "user_id": 1                   
}
### 4. Get User Expenses
* URL: /expenses/<user_id>
* Method: GET
### 5. Get Overall Expenses
* URL: /expenses
* Method: GET
### 6. Download Balance Sheet
* URL: /balance_sheet
* Method: GET

