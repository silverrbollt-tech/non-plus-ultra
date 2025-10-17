from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from myapp import db
from myapp.models import User
from . import main

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('servers.list_servers'))
    return redirect(url_for('auth.login'))

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title='Profile')

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/edit_profile.html', title='Edit Profile')