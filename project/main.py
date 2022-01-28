from flask import Blueprint, render_template, redirect, url_for, request
from . import db
from .models import User, Session, CommentHandler, UserHandler

main = Blueprint('main', __name__)

@main.route('/')
def index():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	return render_template('index.html')


@main.route('/profile')
def profile():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	return render_template('profile.html', name=user.name)


@main.route('/blog')
def blog():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	return render_template('blog.html')


@main.route('/account')
def account():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	return render_template('account.html')


@main.route('/account', methods=['POST'])
def account_post():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	userhandle = UserHandler(user)
	new_pass = request.form.get('password')
	new_name = request.form.get('name')
	if new_pass:
		userhandle.updatePassword(new_pass)
	if new_name:
		userhandle.updateName(new_name)

	return render_template('profile.html', name=new_name, status="Successful update!")


@main.route('/comment')
def comment():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	comments = CommentHandler().getAll()
	return comments


@main.route('/comment', methods=['POST'])
def comment_post():
	sesh = Session().authenticate(request)
	if not sesh:
		return redirect(url_for('auth.login'))
	user = sesh.get_user()

	comment = request.form.get('comment')
	if not comment:
		redirect(url_for('main.blog'))

	c = CommentHandler()
	c.createNew(comment, user.name)

	return redirect(url_for('main.blog'))