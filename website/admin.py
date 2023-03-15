import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
import flask_login as login
from flask import Flask, url_for, redirect, render_template, request, abort

class AdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif not login.current_user.email == 'karim.echaouch@gmail.com':
            abort(401)
        return super(AdminIndexView, self).index()