from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# Initializing Flask app and configuring PostgreSQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/Daily_expense_sharing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing SQLAlchemy
db = SQLAlchemy(app)


# Defining Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    split_method = db.Column(db.String(10), nullable=False)  # 'equal', 'exact', 'percentage'
    participants = db.Column(db.String(500), nullable=False)  # Store participant IDs
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Utility Functions
def validate_percentage_split(participants, percentages):
    total_percentage = sum(percentages)
    if total_percentage != 100:
        raise ValueError("Percentages must add up to 100%")


def calculate_expenses(expenses):
    balance_sheet = {}
    for expense in expenses:
        participants = expense.participants.split(',')
        amount_per_participant = expense.amount / len(participants) if expense.split_method == 'equal' else None
        if expense.split_method == 'exact':
            exact_splits = [float(participant) for participant in participants]
            for participant, split in zip(participants, exact_splits):
                balance_sheet[participant] = balance_sheet.get(participant, 0) + split
        elif expense.split_method == 'percentage':
            for participant, percentage in zip(participants, [float(part) for part in percentage]):
                balance_sheet[participant] = balance_sheet.get(participant, 0) + (expense.amount * (percentage / 100))
        elif expense.split_method == 'equal':
            for participant in participants:
                balance_sheet[participant] = balance_sheet.get(participant, 0) + amount_per_participant
    return balance_sheet


# Routes

# User Routes
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(email=data['email'], name=data['name'], mobile=data['mobile'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'email': user.email, 'name': user.name, 'mobile': user.mobile})


# Expense Routes
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    participants = data['participants']

    if data['split_method'] == 'percentage':
        validate_percentage_split(participants, data['percentages'])

    new_expense = Expense(
        amount=data['amount'],
        description=data.get('description', ''),
        split_method=data['split_method'],
        participants=','.join(participants),
        user_id=data['user_id']
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'message': 'Expense added'}), 201


@app.route('/expenses/<int:user_id>', methods=['GET'])
def get_user_expenses(user_id):
    expenses = Expense.query.filter_by(user_id=user_id).all()
    expenses_data = [{'id': expense.id, 'amount': expense.amount, 'description': expense.description} for expense in
                     expenses]
    return jsonify(expenses_data)


@app.route('/expenses', methods=['GET'])
def get_overall_expenses():
    expenses = Expense.query.all()
    balance_sheet = calculate_expenses(expenses)
    return jsonify(balance_sheet)


@app.route('/balance_sheet', methods=['GET'])
def download_balance_sheet():
    expenses = Expense.query.all()
    balance_sheet = calculate_expenses(expenses)

    # Converting balance sheet to DataFrame and exporting as CSV
    df = pd.DataFrame(list(balance_sheet.items()), columns=['User', 'Total Amount'])
    csv_path = 'balance_sheet.csv'
    df.to_csv(csv_path, index=False)

    return send_file(csv_path, as_attachment=True)


# Running the Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creating database tables
    app.run(debug=True)
