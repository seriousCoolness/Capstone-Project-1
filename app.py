from flask import Flask, request, abort, redirect, render_template, flash, session, get_flashed_messages
from sqlalchemy.exc import IntegrityError
import random
import requests

from models import db, connect_db, Users, Highscores, EnemyHistories
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///catgame_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
app.app_context().push()
db.create_all()

app.config['SECRET_KEY'] = 'OSnfovanodjiFOSIFH'

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


@app.route('/highscores')
def highscores_page():
    user_id = request.args.get('user',type=int)

    highscores = None
    if user_id:
        highscores = Highscores.query.filter_by(user_id=user_id).order_by(Highscores.score.desc()).all()
    else:
        highscores = Highscores.query.order_by(Highscores.score.desc()).all()

    scores_list = []
    for highscore in highscores:
        history = EnemyHistories.query.filter_by(score_id=highscore.id).order_by(EnemyHistories.run_order.desc()).first()
        scores_list.append({ 
                            'id': highscore.id,
                            'user':Users.query.get_or_404(highscore.user_id),
                            'score':highscore.score,
                            'image_url':history.image_url
        })
    
    return render_template('highscores.html', scores=scores_list)


@app.route('/history/<int:highscore_id>')
def history_page(highscore_id):
    histories = EnemyHistories.query.filter_by(score_id=highscore_id).order_by(EnemyHistories.run_order.asc()).all()

    return render_template('histories.html', histories=histories)

@app.route('/game')
def game_page():
    """Page where game logic is run."""

    if not session.get('user'):
        return redirect('/login')

    #If enemy hasn't been created yet, create one.
    if not session.get('enemy_image'):
        generate_enemy()

    if session.get('current_score') == None:
        user = Users.query.get_or_404(session['user'].get('id'))
        user.times_played += 1
        db.session.commit()

        session['current_score'] = 0
        session['player_max_hp'] = 50
        session['player_cur_hp'] = session['player_max_hp']

    if session.get('player_cur_hp') > 0:
        return render_template('game.html')
    


@app.route('/game/restart', methods=["POST"])
def restart_game():

    if not session.get('user'):
        return redirect('/login')
    
    session['enemy_image'] = None
    session['current_score'] = None

    return redirect('/game')



@app.route('/game/attack', methods=["POST"])
def attack_enemy():

    if not session.get('user'):
        return redirect('/login')
    
    if session.get('current_score') == None or not session.get('enemy_image'):
        return redirect('/game')
    
    #damage enemy
    session['enemy_cur_hp'] -= random.randrange(1,6)

    #enemy retaliates against player
    session['player_cur_hp'] -= random.randrange(0,6)

    #logic if player dies
    if session.get('player_cur_hp') <= 0:
        user = Users.query.get_or_404(session['user'].get('id'))
        user.battles_lost += 1
        db.session.commit()

        session['player_cur_hp'] = 0
        game_over()
        flash(f'Game over! Your score was: {session["current_score"]}', 'success')
        session['current_score'] = None
        session['enemy_image'] = None
        return redirect('/highscores')

    #logic if player won battle
    if session.get('enemy_cur_hp') <= 0:
        add_history()

        user = Users.query.get_or_404(session['user'].get('id'))
        user.battles_won += 1
        db.session.commit()

        session['current_score'] += 1
        session['enemy_image'] = None

    return redirect('/game')

def generate_enemy():
    rand_x = random.randint(50,300)
    rand_y = random.randint(50,300)

    session['enemy_image'] = f"http://placekitten.com/{rand_x}/{rand_y}/"
    session['enemy_max_hp'] = 10
    if session.get('current_score'):
        session['enemy_max_hp'] = session['enemy_max_hp'] + session['current_score']
    
    session['enemy_cur_hp'] = session['enemy_max_hp']

def game_over():
    """End run and submit score"""
    add_history()
    
    highscore = Highscores(user_id=session['user'].get('id'), score=session['current_score'])
    db.session.add(highscore)
    db.session.commit()

    for i, history in enumerate(session.get('run_history')):
        score_history = EnemyHistories(run_order=i, 
                                       score_id=highscore.id, 
                                       image_url=history.get('image_url'), 
                                       player_health=history.get('player_health'), 
                                       enemy_health=history.get('enemy_health'))
        db.session.add(score_history)
        db.session.commit()
    
    session['run_history'] = None

def add_history():
    
    if session.get('run_history') == None:
        session['run_history'] = []

    session.get('run_history').append({ 
        'image_url': session['enemy_image'],
        'enemy_health': session['enemy_max_hp'],
        'player_health': session['player_cur_hp']
        })