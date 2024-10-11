from flask import redirect, url_for, session
from flask import render_template, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from flask import request, redirect, url_for, flash
from flask_bcrypt import Bcrypt

from app import app, bcrypt, db
from forms.authentication import LoginForm
from models.user import User


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_form = LoginForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):  # Use bcrypt for password checking
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('pages/login.html', form=user_form, title="Login", active_page="Login")


@app.route('/protected')
@login_required
def protected():
    return f'Hello, {current_user.username}!'


@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['POST'])
def change_password():
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')

    user = User.query.get(user_id)
    if user:
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password for user {user.username} has been updated successfully.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('staff'))

