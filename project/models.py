from . import db
from flask import request, make_response
from datetime import datetime
import uuid
import json


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))
	session = db.Column(db.String(100), unique=True)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(1000))
	author = db.Column(db.String(1000))
	timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)


class UserHandler:
	def __init__(self, user=None):
		self.user = user

	def updatePassword(self, new_pass):
		if not self.user or not new_pass:
			return None

		self.user.password = new_pass
		db.session.commit()
		return self.user

	def updateName(self, new_name):
		if not self.user or not new_name:
			return None

		self.user.name = new_name
		db.session.commit()
		return self.user


class CommentHandler:
	def getAll(self):
		payload = {}
		comments = Comment.query.order_by(Comment.timestamp.asc())
		if not comments:
			payload['1'] = {
					"name": "Error",
					"content": "Looks like there was an error retrieving the comments."
				}

			return payload

		for c in comments:
			payload[str(c.id)] = {"name": c.author, "content": c.text}

		return payload

	def createNew(self, text, author):
		c = Comment(text=text, author=author)
		db.session.add(c)
		db.session.commit()
		return 0

	def reset(self):
		if Comment.query.order_by(Comment.timestamp.asc()).count() > 0:
			self.deleteAll()
		self.createNew(" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean efficitur sit amet massa fringilla egestas. Nullam condimentum luctus turpis.", "JohnSmith")
		self.createNew("Sooo cool! Dave Mathews for like! #blessed #emotionallyFragile", "KateDoe")
		return 0

	def deleteAll(self):
		Comment.query.delete()
		db.session.commit()
		return 0
		

class Session:
	# Queries and inits associated User object if email is provided. -> call start_session()
	# Otherwise, everything is init to None. -> call authenticate(token)
	def __init__(self, email=None):
		self.session_id = None
		if email is None:
			self.user = None
		else:
			self.user = User.query.filter_by(email=email).first()
		self.cookey = 'sessionID'

	# Generate and store a hex encoded UUIDv4 string in the DB for the associated User
	# Called after successful login
	def start_session(self):
		self.session_id = uuid.uuid4().hex
		if not self.session_id or not self.user:
			return None

		self.user.session = self.session_id
		db.session.commit()
		print("Created session with id: %s" % (self.session_id))
		return (self.session_id)

	# Remove the session_id from the DB for the associated User.
	# Updates response to expire cookie for client
	def end_session(self, resp):
		if not self.session_id or not self.user or not resp:
			return None

		self.session_id = None
		self.user.session = None
		db.session.commit()
		print("Ended session for user: %s" % (self.user.name))

		resp.set_cookie(self.cookey, '', expires=0)
		resp.set_cookie('is_admin', '', expires=0)
		return (resp)

	# Pull the session_id from the cookie and return this Session object
	def authenticate(self, req):
		if not req:
			return None

		if self.cookey not in req.cookies:
			return None

		token = req.cookies.get(self.cookey)
		return (self.load_session(token))

	# Same as 'authenticate' except we check for the admin cookie as well.
	# [VULN - Authorization Bypass]
	# [Remediation - Never trust user-data. Ever. User DB table should store whether 
	#	or not a user is an admin. We can retrieve this info when we load the user
	#	associated with the session cookie. Or we implement a strong JSON Web Token
	#	(JWT) auth system (https://auth0.com/docs/secure/tokens/json-web-tokens)]
	def authenticate_admin(self, req):
		if not req:
			return None

		if 'is_admin' not in req.cookies:
			return None

		is_admin = req.cookies.get('is_admin')
		if is_admin != 'True':
			return None
			
		if self.cookey not in req.cookies:
			return None

		token = req.cookies.get(self.cookey)
		return (self.load_session(token))

	# Load the session from the DB and init User, session ID
	def load_session(self, token):
		if not token:
			return None

		user = User.query.filter_by(session=token).first()
		if not user:
			return None

		session_id = user.session
		if not session_id:
			return None

		self.user = user
		self.session_id = session_id

		return self

	# Returns associated User object
	def get_user(self):
		return self.user

	# Returns associated session ID
	def get_id(self):
		return self.session_id

