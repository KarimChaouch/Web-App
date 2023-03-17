from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Message
from . import db
import json
import logging
from . import app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(
    get_remote_address,
    app=app,
    # default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
logger = logging.getLogger('web-app')

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    logger.info(f'User {current_user.full_name} accessed home page.')
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})



@views.route('/contact',methods=['GET','POST'])
@limiter.limit("20/day0/hour")
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        new_message = Message(name=name, email=email, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()
        flash('Thank you for your message! We will come back to you soon.', category='success')
    return render_template("contact.html", user=current_user)


@views.errorhandler(429)
def too_many_requests(e):
    return render_template('/errors/429.html', user=current_user), 429

@views.errorhandler(404)
def page_not_found(e):
    return render_template('/errors/404.html', user=current_user), 404