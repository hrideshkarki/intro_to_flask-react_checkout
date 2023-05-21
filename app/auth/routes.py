from flask import Blueprint, flash, redirect, render_template, request, url_for
from .forms import LoginForm, SignUpForm
from ..models import User
from flask_login import  login_user, logout_user, login_required
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__, template_folder='auth_templates')

@auth.route('/signup', methods=["GET", "POST"])
def signupPage():
    form = SignUpForm()
    
    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(username = username).first()
            if user:
                flash('That username is taken.', 'danger')
                return render_template('signup.html', form = form, usernameError = True)
            user = User.query.filter_by(email = email).first()
            if user:
                flash('That email is already in use. Please use another email.', 'danger')
                return render_template('signup.html', form = form, emailError=True)
            user = User(username, email, password)
        
            user.saveToDB()
            flash('Successfully created your account.', 'success')
            return redirect(url_for('auth.loginPage'))
        else:
            flash('Invalid entry. Please try again', 'danger')

    return render_template('signup.html', form = form)

@auth.route('/login', methods=["GET", "POST"])
def loginPage():
    form = LoginForm()
    if request.method == "POST":
        if form.validate():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()            
            if user:
                # verify password
                if check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for('ig.homePage'))
                else:
                    print('invalid password')
            else:
                print('incorrect username or password')


    return render_template('login.html', form = form)

@auth.route('/logout')
@login_required
def logMeOut():
    logout_user()
    return redirect(url_for('auth.loginPage'))
