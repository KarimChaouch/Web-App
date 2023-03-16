from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, abort
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from . import app
import pyqrcode
from io import BytesIO


auth = Blueprint('auth', __name__)

# limiter configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("20/day;15/hour;10/minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        otp = request.form.get('otp')
        user = User.query.filter_by(email=email).first()
        check_otp = user.verify_totp(otp)
        if user and user.active and check_otp:
            if check_password_hash(user.password, password):
                # flash('Logged in successfully!', category='success')
                login_user(user, remember=False)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        elif user and not check_otp:
            flash('OTP incorrect', category='error')
        elif user and not user.active:
            flash('Account not active yet, please contact admin.', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
@limiter.limit("20/day;10/hour")
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('fullName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        admin = validate(email)
        active = validate(email)
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(full_name) < 2:
            flash('Full name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, full_name=full_name, password=generate_password_hash(
                password1, method='sha256'), admin=admin, active=active)
            db.session.add(new_user)
            db.session.commit()
            #login_user(new_user, remember=True)
            #flash('Account created. Contact admin to enable it!', category='success')
            #return redirect(url_for('auth.login'))
            session['email'] = email
            return redirect(url_for('auth.two_factor_setup'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/twofactor')
def two_factor_setup():
    if 'email' not in session:
        return redirect(url_for('auth.sign_up'))
    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return redirect(url_for('auth.sign_up'))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@auth.route('/qrcode')
def qrcode():
    if 'email' not in session:
        abort(404)
    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        abort(404)

    # for added security, remove username from session
    del session['email']

    # render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

def validate(user_email):
    if user_email == "karim.echaouch@gmail.com":
        return True
    return False


@auth.errorhandler(429)
def too_many_requests(e):
    return render_template('/errors/429.html', user=current_user), 429

@auth.errorhandler(404)
def page_not_found(e):
    return render_template('/errors/404.html', user=current_user), 404