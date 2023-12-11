from flask import Blueprint, render_template, flash, redirect, url_for
from app import db
from models import User
from users.forms import RegisterForm
import re
# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        #checks to make sure there was a valid email address inputted, if not, sends user back to registration page
        input_email = form.email.data
        if re.match(r"[^@]+@[^@]+\.[^@]+", input_email):
            imputEmail = True
        else:
            flash('Invalid email address')
            return render_template('users/register.html', form=form)

        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('True')
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        #Checks to make sure firstname and lastname do not contain characters that are not allowed. return to registration page if true.
        input_firstname = form.firstname.data
        input_lastname = form.lastname.data
        characters = ['*', '?', '!', '^', '+', '%', '&', '/', '(', ')', '=', '}', ']', '[', '{', '$', '#', '@', '<', '>']
        res = any(ele in input_firstname for ele in characters)
        if res == True:
            flash('Error with firstname, included disallowed characters.')
            return render_template('users/register.html', form=form)

        res = any(ele in input_lastname for ele in characters)
        if res == True:
            flash('Error with lastname, included disallowed characters.')
            return render_template('users/register.html', form=form)

        #Checks to make sure phone number is written in form XXXX-XXX-XXXX, if not returns to register page with error message.
        input_phone = form.phone.data
        if len(input_phone) != 13:
            flash('Phone number entered incorrectly')
            return render_template('users/register.html', form=form)
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        c = 0
        for i in input_phone:
            if c == 4 or c == 8:
                if i != '-':
                    flash('Phone number entered incorrectly')
                    return render_template('users/register.html', form=form)
            else:
                res = any(ele in i for ele in numbers)
                if res == False:
                    flash('Phone number entered incorrectly')
                    return render_template('users/register.html', form=form)
            c += 1
        #Checks if password is valid. if not, returns appropriate error message, and returns to registration page
        input_password = form.password.data
        if not( len(input_password) > 6 and len(input_password) < 12) == True:
            flash('Password must be between 6 and 12 characters long')
            return render_template('users/register.html', form=form)
        res = any(ele in input_password for ele in numbers)
        if res == False:
            flash('Password must contain at least 1 digit')
            return render_template('users/register.html', form=form)
        lower = False
        for i in input_password:
            if i.islower():
                lower = True
        if lower == False:
            flash('Password must contain at least one lower case letter')
            return render_template('users/register.html', form=form)
        upper = False
        for i in input_password:
            if i.isupper():
                upper = True
        if upper == False:
            flash('Password must contain at least one upper case letter')
            return render_template('users/register.html', form=form)
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if (regex.search(input_password) == None):
            flash('Password must contain at least 1 special character')
            return render_template('users/register.html', form=form)

        input_confirm_password = form.confirm_password.data
        if input_confirm_password != input_password:
            flash('Passwords must match')
            return render_template('users/register.html', form=form)


        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        # setting up 2 factor authentication
        session['email'] = new_user.email
        return redirect(url_for('users.setup_2fa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)

# view 2fa
@users_blueprint.route('/setup_2fa')
def setup_2fa():
    if 'email' not in session:
        return redirect(url_for('register.html'))
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return redirect(url_for('login.html'))
    del session['email']

    return render_template('users/setup2fa.html', email=user.email, uri = user.get_2fa_uri()),\
           200, {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }



# view user login
@users_blueprint.route('/login')
def login():
    return render_template('users/login.html')


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")
