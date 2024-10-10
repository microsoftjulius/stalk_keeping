from datetime import datetime

from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, logout_user, login_user, login_required
from app import app, db, bcrypt
from forms.authentication import LoginForm
from forms.items import ItemForm
from models.stalk import StockRecord, Item
from models.user import User
from serializers.items import create_item, get_items


@app.route('/')
def index():
    user_form = LoginForm()
    return render_template('pages/login.html', form=user_form, title='Login')


@app.route('/sales')
def sales():
    records = StockRecord.query.order_by(StockRecord.date.desc()).all()
    items = Item.query.all()  # Retrieve all available items for selection
    return render_template('pages/stalk/sales.html', records=records, items=items, active_page='Sales')


@app.route('/add', methods=['POST'])
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
    cash = sales * item.price

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

    return redirect(url_for('index'))


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
    return render_template('pages/stalk/add_sales.html', active_page='Add Sales')


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
    dashboard_page = 'pages/dashboard.html'

    return render_template(dashboard_page, title='Dashboard', active_page='Dashboard')


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
