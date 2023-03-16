import os
from flask import Flask, current_app, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, auth_required
from flask_mailman import Mail

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

app.config['SECURITY_TWO_FACTOR_ENABLED_METHODS'] = ['email',
  'authenticator']  # 'sms' also valid but requires an sms provider
app.config['SECURITY_TWO_FACTOR'] = True
app.config['SECURITY_TWO_FACTOR_RESCUE_MAIL'] = "put_your_mail@gmail.com"

app.config['SECURITY_TWO_FACTOR_ALWAYS_VALIDATE'] = False
app.config['SECURITY_TWO_FACTOR_LOGIN_VALIDITY'] = "1 week"

# Generate a good totp secret using: passlib.totp.generate_secret()
app.config['SECURITY_TOTP_SECRETS'] = {"1": "TjQ9Qa31VOrfEzuPy4VHQWPCTmRzCnFzMKLxXYiZu9B"}
app.config['SECURITY_TOTP_ISSUER'] = "put_your_app_name"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    # Make username unique but not required.
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    tf_phone_number = db.Column(db.String(128), nullable=True)
    tf_primary_method = db.Column(db.String(64), nullable=True)
    tf_totp_secret = db.Column(db.String(255), nullable=True)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

mail = Mail(app)

# Views
@app.route('/')
@auth_required()
def home():
    return render_template_string("Hello {{ current_user.email }}")

# one time setup
with app.app_context():
    # Create a user to test with
    db.create_all()
    if not app.security.datastore.find_user(email='test@me.com'):
        app.security.datastore.create_user(email='test@me.com', password='password')
    db.session.commit()

if __name__ == '__main__':
    app.run()