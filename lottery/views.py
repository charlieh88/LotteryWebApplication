# IMPORTS
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from lottery.forms import DrawForm
from models import Draw
from flask_login import login_user, logout_user, current_user
from models import User

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
        submitted_numbers = (str(form.number1.data) + ' '
                          + str(form.number2.data) + ' '
                          + str(form.number3.data) + ' '
                          + str(form.number4.data) + ' '
                          + str(form.number5.data) + ' '
                          + str(form.number6.data))
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


