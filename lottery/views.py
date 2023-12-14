# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for
from app import db
from lottery.forms import DrawForm
from models import Draw
from flask_login import current_user
from cryptography.fernet import Fernet
# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
def lottery():
    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME")


# view all draws that have not been played
@lottery_blueprint.route('/create_draw', methods=['POST'])
def create_draw():

    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    form = DrawForm()

    if form.validate_on_submit():
        #checking to make sure all inputs are between 1 and 60
        if int(form.number1.data) < 1 or int(form.number1.data) > 60:
            flash('Number 1 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        if int(form.number2.data) < 1 or int(form.number2.data) > 60:
            flash('Number 2 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        if int(form.number3.data) < 1 or int(form.number3.data) > 60:
            flash('Number 3 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        if int(form.number4.data) < 1 or int(form.number4.data) > 60:
            flash('Number 4 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        if int(form.number5.data) < 1 or int(form.number5.data) > 60:
            flash('Number 5 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        if int(form.number6.data) < 1 or int(form.number6.data) > 60:
            flash('Number 6 must be between 1 and 60')
            return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)
        submitted_numbers = (str(form.number1.data) + ' '
                          + str(form.number2.data) + ' '
                          + str(form.number3.data) + ' '
                          + str(form.number4.data) + ' '
                          + str(form.number5.data) + ' '
                          + str(form.number6.data))

        ##secret_key = Fernet.generate_key()
        ##encnumbers = Fernet(secret_key).encrypt(bytes(submitted_numbers, 'utf-8'))
        # create a new draw with the form data.

        new_draw = Draw(user_id=current_user.id, numbers=submitted_numbers, master_draw=False, lottery_round=0)
        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html', name="PLACEHOLDER FOR FIRSTNAME", form=form)


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
def view_draws():

    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(user_id=current_user.id).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        for i in playable_draws:
            a = Fernet
        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():

    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    # get played draws
    played_draws = Draw.query.filter_by(been_played=True).all()
    user_played_draws = [draw for draw in played_draws if draw.user_id == current_user.id]

    # if played draws exist
    if len(user_played_draws) != 0:
        return render_template('lottery/lottery.html', results=user_played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
def play_again():
    #making sure only verified users access this page
    if current_user.is_anonymous == True:
        flash('Must be signed in to access that page')
        return redirect(url_for('index'))
    if current_user.is_anonymous == False:
        if current_user.role == 'admin':
            flash('Admin cannot access this page')
            return redirect(url_for('admin'))
    Draw.query.filter_by(been_played=True, master_draw=False, user_id=current_user.id).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


