import bcrypt
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import db
from models import User
from users.forms import RegisterForm, LoginForm, ChangePasswordForm
import re
from datetime import datetime
from flask_login import login_user, logout_user
import pyotp
from flask_login import current_user

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_anonymous == False:
        flash('Cannot access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash('True')
            flash('Email not found in the system')
            return render_template('users/login.html', form=form)
        if form.password.data == user.password:
            # Successful login, reset password attempt count
            session.pop('password_attempts', None)
        else:
            # Incorrect password, update attempt count in session
            attempts = session.get('password_attempts', 0) + 1
            session['password_attempts'] = attempts

            if attempts >= 3:
                # send user to the homepage
                flash('You have exceeded 3 password attempts')
                session.pop('password_attempts', None)
                return redirect(url_for('index'))


            flash(f'Incorrect password. Attempt number {attempts}.')
            return render_template('users/login.html', form=form)

        if user.postcode != form.postcode.data:
            flash('Incorrect postcode')
            return render_template('users/login.html', form=form)
        pin_key = user.pin_key
        if len(form.pin.data) == 0:
            flash('Incorrect Pin Key')
            return render_template('users/login.html', form=form)
        if pyotp.TOTP(pin_key).verify(form.pin.data) == False:
            flash('Incorrect Pin Key')
            return render_template('users/login.html', form=form)
        login_user(user)
        current_user.last_login = current_user.current_login
        current_user.current_login = datetime.now()
        current_user.last_IP = current_user.current_IP
        current_user.current_IP = request.remote_addr
        current_user.total_logins = int(current_user.total_logins) + 1
        db.session.commit()
        if current_user.role == 'user':
            return render_template('lottery/lottery.html')
        else:
            return render_template('admin/admin.html')




    return render_template('users/login.html', form=form)

# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_anonymous == False:
        if current_user.role == 'user':
            flash('Cannot access that page')
            return redirect(url_for('index'))

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
        #checks to make sure Date of Birth is entered correctly.
        input_DOB = form.DOB.data
        try:
            # Attempt to parse the input date in the format DD/MM/YYYY
            parsed_date = datetime.strptime(input_DOB, '%d/%m/%Y')

            # Validate day, month, and year
            if 1 <= parsed_date.day <= 31 and 1 <= parsed_date.month <= 12:
                if parsed_date.year // 100 == 19 or parsed_date.year // 100 == 20:
                    # Convert the date to the desired format
                    input_DOB = parsed_date.date()
                else:
                    raise ValueError('Invalid year. Please use 19YY or 20YY.')
            else:
                raise ValueError('Invalid day or month.')

        except ValueError as e:
            flash(f'Invalid date format: {str(e)}')
            return render_template('users/register.html', form=form)


        #checks to make sure that postcode is entered correctly
        input_postcode = form.postcode.data
        valid_postcode_formats = [
            re.compile(r'^[A-Z]{2}\d{1,2}\s?\d[A-Z]{2}$'),
            re.compile(r'^[A-Z]{1}\d{2}\s?\d[A-Z]{2}$'),
            re.compile(r'^[A-Z]{2}\d{1,2}[A-Z]{3}$')
        ]

        if not any(pattern.match(input_postcode) for pattern in valid_postcode_formats):
            flash('Invalid postcode format. Please use a valid postcode.')
            return render_template('users/register.html', form=form)
        if current_user.is_anonymous == False:
            if current_user.role == 'admin':
                new_user = User(email=form.email.data,
                                firstname=form.firstname.data,
                                lastname=form.lastname.data,
                                phone=form.phone.data,
                                password=form.password.data,
                                role='admin',
                                DOB=form.DOB.data,
                                postcode=form.postcode.data
                                )
        else:
        # create a new user with the form data
            new_user = User(email=form.email.data,
                            firstname=form.firstname.data,
                            lastname=form.lastname.data,
                            phone=form.phone.data,
                            password=form.password.data,
                            role='user',
                            DOB=form.DOB.data,
                            postcode=form.postcode.data
                            )

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        # setting up 2 factor authentication
        session['email'] = new_user.email
        if current_user.is_anonymous == False:
            if current_user.role == 'admin':
                flash('New admin account has been created, pin key must be added manually.')
                user = User.query.filter_by(email=session['email']).first()

                flash(f'Secret Key:{user.pin_key}')
                return render_template('admin/admin.html')
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

    return render_template('users/setup_2fa.html', email=user.email, uri = user.get_2fa_uri()),\
           200, {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }


# view user account
@users_blueprint.route('/account')
def account():
    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    return render_template('users/account.html')


#Logout function
@users_blueprint.route('/logout')
def logout():
    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('index'))

@users_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))

    form = ChangePasswordForm()

    if form.validate_on_submit():
        #verifying old password correlates with password entered.
        if current_user.password != form.oldpassword.data:
            flash('Incorrect old password')
            return render_template('users/change_password.html', form=form)
        if form.newpassword.data == current_user.password:
            flash('New and Old passwords must not match')
            return render_template('users/change_password.html', form=form)
        #making sure new password is valid
        input_password = form.newpassword.data
        if not (len(input_password) > 6 and len(input_password) < 12) == True:
            flash('New password must be between 6 and 12 characters long')
            return render_template('users/change_password.html', form=form)
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        res = any(ele in input_password for ele in numbers)
        if res == False:
            flash('New password must contain at least 1 digit')
            return render_template('users/change_password.html', form=form)
        lower = False
        for i in input_password:
            if i.islower():
                lower = True
        if lower == False:
            flash('New password must contain at least one lower case letter')
            return render_template('users/change_password.html', form=form)
        upper = False
        for i in input_password:
            if i.isupper():
                upper = True
        if upper == False:
            flash('New password must contain at least one upper case letter')
            return render_template('users/change_password.html', form=form)
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if (regex.search(input_password) == None):
            flash('New password must contain at least 1 special character')
            return render_template('users/change_password.html', form=form)

        input_confirm_password = form.confirmpassword.data
        if input_confirm_password != input_password:
            flash('New passwords must match')
            return render_template('users/change_password.html', form=form)
        current_user.password = form.newpassword.data
        db.session.commit()
        flash('Password changed successfully')
        return redirect(url_for('users.account'))
    return render_template('users/change_password.html', form=form)