from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy here
db = SQLAlchemy()

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = 'hopeNobodyDisclosesThisKey'
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	db.init_app(app)

	# blueprint for auth routes within the app
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	# blueprint for non-auth routes
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	# blueprint for admin routes
	from .admin import admin as admin_blueprint
	app.register_blueprint(admin_blueprint)

	return app