from flask import Blueprint, render_template, redirect, url_for, request, make_response
from . import db
from .models import User, Session, CommentHandler, UserHandler

admin = Blueprint('admin', __name__)


@admin.route('/admin')
def adminpage():
	sesh = Session().authenticate_admin(request)
	if not sesh:
		return redirect(url_for('auth.unauthorized'))

	return render_template('admin.html')


@admin.route('/admin/resetcomments')
def resetcomments():
	sesh = Session().authenticate_admin(request)
	if not sesh:
		return redirect(url_for('auth.unauthorized'))

	c = CommentHandler()
	c.reset()

	return render_template('blog.html')


@admin.route('/admin/resetusers')
def resetusers():
	sesh = Session().authenticate_admin(request)
	if not sesh:
		return redirect(url_for('auth.unauthorized'))

	# TKTK
	return redirect(url_for('index.html'))