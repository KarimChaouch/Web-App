import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
import flask_login as login
from flask import Flask, url_for, redirect, render_template, request, abort

class AdminIndexView(admin.AdminIndexView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False
    
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif not login.current_user.admin:
            abort(401)
        return super(AdminIndexView, self).index()