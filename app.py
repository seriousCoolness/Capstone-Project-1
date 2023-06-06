from flask import Flask, redirect, render_template, session

from models import db, connect_db, Users, Highscores, EnemyHistories

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///catgame_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
app.app_context().push()
db.create_all()

app.config['SECRET_KEY'] = 'STOP HacKIgN ME!!!!1!1!!'

