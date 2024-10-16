from datetime import datetime, date

from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required
from sqlalchemy import extract
from app import app, db, bcrypt
from forms.authentication import LoginForm
from forms.deposits import DepositForm
from forms.items import ItemForm
from models.deposits import Deposit
from models.stalk import StockRecord, Item
from models.user import User
from serializers.deposits import create_deposit, get_deposits
from serializers.items import create_item, get_items
from sqlalchemy import func


@app.route('/')
def index():
    user_form = LoginForm()
    return render_template('pages/login.html', form=user_form, title='Login')


@app.route('/sales')
def sales():
    # Get the current date
    today = date.today()

    # Get the 'from' and 'to' date from the query parameters if they exist
    from_date = request.args.get('from_date', default=None)
    to_date = request.args.get('to_date', default=None)

    # Initialize the query
    query = StockRecord.query

    if from_date and to_date:
        # Parse the dates and filter records within the date range
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        query = query.filter(StockRecord.date.between(from_date_obj, to_date_obj))
    elif from_date:
        # Parse the single 'from' date and filter records for that day
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        query = query.filter(StockRecord.date == from_date_obj)
    else:
        # Default to showing today's records
        query = query.filter(StockRecord.date == today)

    # Order by the date descending
    records = query.order_by(StockRecord.date.desc()).all()

    # Retrieve all available items for selection
    items = Item.query.all()

    return render_template('pages/stalk/sales.html', records=records, items=items, active_page='Sales')


@app.route('/add-stock', methods=['POST'])
def add_stock():
    date = datetime.utcnow().date()
    item_id = request.form['item_id']
    old_stalk = request.form['old_stalk']
    current_stalk = request.form['current_stalk']
    new_stalk = request.form['new_stalk']

    # Find the selected item in the database
    item = Item.query.get(item_id)

    # Calculate sales and cash using the item's price
    sales = int(old_stalk) - int(current_stalk)
    cash = sales * item.selling_price

    if request.method == 'POST':
        new_record = StockRecord(
            date=date,
            item_id=item_id,
            old_stalk=old_stalk,
            current_stalk=current_stalk,
            new_stalk=new_stalk,
            sales=sales,
            cash=cash
        )

        db.session.add(new_record)
        db.session.commit()

    return redirect(url_for('new_stalk_page'))


# Carry forward stalk from previous day
@app.route('/create_new_sale')
def add_new_sale():
    last_day = StockRecord.query.order_by(StockRecord.date.desc()).first()
    if last_day:
        new_old_stalk = last_day.current_stalk + last_day.new_stalk

        # Add a new record for the next day with carried over old stock
        new_record = StockRecord(
            date=datetime.utcnow().date(),
            item_id=last_day.item_id,
            old_stalk=new_old_stalk,
            current_stalk=0,
            new_stalk=0
        )
        db.session.add(new_record)
        db.session.commit()

    return redirect(url_for('new_stalk_page'))


@app.route('/new_stalk_page')
def new_stalk_page():
    drinks = get_items()
    return render_template('pages/stalk/add_sales.html', active_page='Add Sales', drinks=drinks)


@app.route('/get_old_stalk/<drink_id>', methods=['GET'])
def get_old_stalk(drink_id):
    # Fetch the record for the drink_id from your database
    # Assuming you have a model called Stock that tracks this information
    stock = StockRecord.query.filter_by(item_id=drink_id).order_by(StockRecord.date.desc()).first()

    if stock:
        # Calculate old stalk as per your logic
        old_stalk = stock.new_stalk + stock.current_stalk
    else:
        old_stalk = 0  # Default value if no previous record exists

    return jsonify({'old_stalk': old_stalk})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Extract the fields from the request
    username = data.get('username')
    password = data.get('password')
    c_password = data.get('confirm_password')

    # Validate input fields
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if password != c_password:
        return jsonify({'error': 'Make sure the two passwords match'}), 400

    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user
    new_user = User(username=username, password=hashed_password)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/dashboard')
@login_required
def dashboard():
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    dashboard_page = 'pages/dashboard.html'
    this_month_deposits = db.session.query(func.sum(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year
    ).scalar()
    this_month_bar_deposits = db.session.query(func.sum(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).scalar()
    this_month_pool_table_deposits = db.session.query(func.sum(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'poolTable'
    ).scalar()
    this_month_chips_deposits = db.session.query(func.sum(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'chips'
    ).scalar()
    this_month_highest_sale = db.session.query(func.max(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).scalar()
    this_month_lowest_sale = db.session.query(func.min(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).scalar()

    # Highest Selling day
    max_amount_subquery = db.session.query(func.max(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).scalar_subquery()

    # Query to get the day of the week for the date_of_deposit of the maximum amount
    this_month_highest_selling_day_of_week = db.session.query(
        extract('dow', Deposit.date_of_deposit)  # Extract the day of the week (0=Sunday, 6=Saturday)
    ).filter(
        Deposit.amount == max_amount_subquery,
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).first()

    # Convert the result to a more human-readable format (if needed)
    if this_month_highest_selling_day_of_week:
        day_of_week_number = this_month_highest_selling_day_of_week[0]
        day_of_week_mapping = {
            0: 'Sunday',
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday'
        }
        day_of_week_name = day_of_week_mapping.get(day_of_week_number)
    else:
        day_of_week_name = None

    # Lowest Sales day
    min_amount_subquery = db.session.query(func.min(Deposit.amount)).filter(
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).scalar_subquery()

    # Query to get the day of the week for the date_of_deposit of the minimum amount
    this_month_lowest_selling_day_of_week = db.session.query(
        extract('dow', Deposit.date_of_deposit)  # Extract the day of the week (0=Sunday, 6=Saturday)
    ).filter(
        Deposit.amount == min_amount_subquery,
        extract('month', Deposit.date_of_deposit) == current_month,
        extract('year', Deposit.date_of_deposit) == current_year,
        Deposit.deposit_from == 'bar'
    ).first()

    # Convert the result to a more human-readable format (if needed)
    if this_month_lowest_selling_day_of_week:
        day_of_week_number = this_month_lowest_selling_day_of_week[0]

        day_of_week_mapping = {
            0: 'Sunday',
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday'
        }
        low_day_of_week_name = day_of_week_mapping.get(day_of_week_number)
    else:
        low_day_of_week_name = None

    stats = {
        'this_month_deposits': this_month_deposits,
        'this_month_bar_deposits': this_month_bar_deposits,
        'this_month_chips_deposits': this_month_chips_deposits,
        'highest_sale_made': this_month_highest_sale,
        'lowest_sale_made': this_month_lowest_sale,
        'highest_sale_day': day_of_week_name,
        'lowest_sale_day': low_day_of_week_name,
        'this_month_pool_table_deposits': this_month_pool_table_deposits,
    }
    return render_template(dashboard_page, title='Dashboard', active_page='Dashboard', statistics=stats)


@app.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    item_form = ItemForm()
    dashboard_page = 'pages/stalk/items.html'

    if request.method == 'POST':
        # Check if the item already exists in the database
        existing_item = Item.query.filter_by(name=item_form.name.data).first()
        if existing_item:
            # If item exists, flash a warning message and reload the page
            flash('Item already exists.', 'warning')
        else:
            # If item does not exist, create the item
            create_item(item_form.name.data, item_form.buying_price.data, item_form.selling_price.data,
                        item_form.category.data)
            flash('New item has been added successfully.', 'success')

    # Retrieve and display all items on the page
    bar_items = get_items()
    return render_template(dashboard_page, title='Dashboard', active_page='Items', form=item_form, items=bar_items)


@app.route('/mobile_deposits', methods=['GET', 'POST'])
@login_required
def mobile_deposits():
    page = 'pages/deposits.html'
    deposit_form = DepositForm()
    if request.method == 'POST':
        create_deposit(deposit_form.amount.data, deposit_form.date.data, deposit_form.deposit_from.data)
        flash('Deposit made successfully.', 'success')
    all_deposits = get_deposits()
    return render_template(page, title='Deposits', active_page='Deposits', form=deposit_form, deposits=all_deposits)
