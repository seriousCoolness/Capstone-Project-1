from flask import Flask, request, abort, redirect, render_template, flash, session, get_flashed_messages
from sqlalchemy.exc import IntegrityError
import random
import requests

from models import db, connect_db, Users, Highscores, EnemyHistories
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://:5433/catgame_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
app.app_context().push()
db.create_all()

app.config['SECRET_KEY'] = 'STOP HacKIgN ME!!!!1!1!!'

@app.route('/')
def home_page():
    """Displays the "start new game" screen if logged in. Redirects to login if not logged in."""

    if(not session.get('user')):
        return redirect('/login')
    
    return render_template('home.html')
    


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """Page for the register form."""

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = Users.signup(form.username.data,form.password.data)

            db.session.commit()
        except IntegrityError:
            flash('Username already used! Choose another.', 'danger')
            return render_template('register.html', form=form)
    
        session['user'] = user.serialize()
        flash(f'Successfully registered as {form.username.data}!', 'success')
        
        return redirect('/')
    else:

        return render_template('register.html', form=form)
        


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Page for the login form."""

    form = LoginForm()

    if form.validate_on_submit():

        user = Users.authenticate(form.username.data,form.password.data)

        if(user):
            session['user'] = user.serialize()
            flash(f'Logged in! Welcome {user.username}!', 'success')
            
            return redirect('/')
        else:
            flash('Username or password is not valid!', 'danger')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)

@app.route('/logout')
def do_logout():
    """Logs out user."""

    session['user'] = None
    return redirect('/')


@app.route('/profile')
def my_profile():

    if not session.get('user'):
        return redirect('/login')
    else:
        return redirect(f'/profile/{session.get("user").get("id")}')

@app.route('/profile/<user_id>')
def user_profile(user_id):

    user = Users.query.get_or_404(user_id)
    highest_score = Highscores.query.filter_by(user_id=user_id).order_by(Highscores.score.desc()).first()

    if not highest_score:
        highest_score = '0'
    
    return render_template('profile.html', user=user, highest_score=highest_score)
        

@app.route('/game')
def game_page():
    """Page where game logic is run."""

    #If enemy hasn't been created yet, create one.
    if not session.get('enemy_image'):
        generate_enemy()

    if session.get('current_score') == None:
        session['current_score'] = 0
        session['player_max_hp'] = 50
        session['player_cur_hp'] = session['player_max_hp']
        
    if session.get('player_cur_hp') > 0:
        return render_template('game.html')
        

def generate_enemy():
    rand_x = random.randrange(100,200)
    rand_y = random.randrange(100,200)

    session['enemy_image'] = f"http://placekitten.com/{rand_x}/{rand_y}/"
    session['enemy_max_hp'] = 10
    if session.get('current_score'):
        session['enemy_max_hp'] = session['enemy_max_hp'] + session['current_score']
    
    session['enemy_cur_hp'] = session['enemy_max_hp']

