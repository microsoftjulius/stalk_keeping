from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from environs import Env

# Load environment variables
env = Env()
Env.read_env()

# Initialize the Flask app
app = Flask(__name__)

# App configuration
app.config['SECRET_KEY'] = env.str('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = env.str('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = env.bool("SQLALCHEMY_TRACK_MODIFICATIONS")

app.config['UPLOAD_FOLDER'] = 'stalk_taking/static/uploads/'
app.config['STAFF_PHOTOS_FOLDER'] = 'stalk_taking/static/staff_photos/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Configuration for Flask-Mail
# app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'smtp@mailtrap.io'
# app.config['MAIL_PASSWORD'] = '212cb2e364e87c7699dc912c38991eb5'
# app.config['MAIL_DEFAULT_SENDER'] = ('Bar Travel', 'support@bar-travel.com')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


# Load the User model inside the function to avoid circular import
@login_manager.user_loader
def load_user(user_id):
    from models.user import User  # Import here to avoid circular import
    user = User.query.get(user_id)
    return user


# Import routes after app is created to avoid circular imports
from controllers.back_end import *
from controllers.authentication import *

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
