from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Session
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():

    failure = 'How do you expect to get by in life if you can\'t even remember your credentials...?'
    user = {}
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False


    # Search/query for any database entries within the user table that match the submitted email
    # [VULN - SQLi]
    result = db.engine.execute("SELECT * FROM user WHERE email='%s' AND password='%s'" % (email, password)).fetchone()
    # [Remediation - Avoid concatenating user-input directly into the query]:
    '''
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
      flash(failure)
      return redirect(url_for('auth.login'))
    '''

    # No results? Then no matches.
    if not result:
        flash(failure)
        return redirect(url_for('auth.login'))

    sesh = Session(email)
    sesh.start_session()
    print("Returning session id: %s" % (sesh.get_id()))

    resp = make_response(redirect(url_for('main.profile')))
    resp.set_cookie(sesh.cookey, sesh.get_id())
    resp.set_cookie('is_admin', 'False')

    return resp


@auth.route('/unauthorized')
def unauthorized():
    resp = make_response(render_template('unauthorized.html'), 401)
    return resp


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    # retrieve POST request parameters
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # check if this email is unique
    user = User.query.filter_by(email=email).first()

    # email is not unique. let user try to signup again.
    if user:
        flash('Oh how original... That email address already exists.')
        return redirect(url_for('auth.signup'))

    # create a new user instance with provided data. save plaintext password
    # [VULN - Insecure Password Storage]
    new_user = User(email=email, name=name, password=password)
    # [Remediation - Store hashes of the passwords, not the plaintext password]:
    # new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))


    # add and commit user data to database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    sesh = Session().authenticate(request)

    if not sesh:
        return redirect(url_for('auth.login'))

    resp = make_response(redirect(url_for('auth.login')))
    if not sesh.end_session(resp):
        print('[!] Fuck. Something went wrong removing the session from the db.')

    return resp





