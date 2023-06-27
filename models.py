"""Models for storing game-data in the long-term.\n\nTemporary persistent storage should be stored in the session, until the end of a battle, where any relevant data will be sent to the database.\n\nRelevant data includes:\n* User info\n* Highscores\n* Run History\n\nTL;DR: This is for stuff that should stay even when the browser closes."""
from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


# DO NOT MODIFY THIS FUNCTION SERIOUSLY IT WILL BREAK THINGS
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Users(db.Model):
    """Basic username and password stuff. Includes functions for hashing passwords."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Text, unique=True, nullable=False)

    password_hash = db.Column(db.Text, nullable=False)

    date_of_creation = db.Column(db.DateTime, nullable=False, default=datetime.now())

    times_played = db.Column(db.Integer, nullable=False, default=0)

    battles_won = db.Column(db.Integer, nullable=False, default=0)

    battles_lost = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.date_of_creation}>"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "date_of_creation": self.date_of_creation,
        }

    @classmethod
    def signup(cls, username, password):
        """Encrypts password hash and adds user to table."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = Users(
            username=username,
            password_hash=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Searches for a user whose password_hash is the password and returns the user if it can find one.\n\nIf theres no user or pass is wrong, returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password_hash, password)
            if is_auth:
                return user

        return False
    

class Highscores(db.Model):
    """Model for highscores and archived scores.\n\nContains a reference to the user who owns the score and the battle history of this score's run."""

    __tablename__ = 'highscores'

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    score = db.Column(db.Integer, nullable=False, default=0)

    date_of_creation = db.Column(db.DateTime, default=datetime.now())


    user = db.relationship('Users', backref='highscores')


    def __repr__(self):
        return f"<Highscore #{self.id}: {self.user.username} - {self.score} ({self.date_of_creation})>"


class EnemyHistories(db.Model):
    """A model representing a list of the end-results of a given run's battles, in the order which they were fought during said run.\n\nEach entry contains:\n* The order number of fight, counting up from zero at the start of the run.\n* The associated highscore entry.\n* The fight's cat picture.\n* The enemy's health at the end. (Will be zero if the user won.)\n* The user's health at the end. (Will be zero if they lost.)\n\n(Note: A "run" refers to a single playthrough of the game, from when the user begins a game, to when they inevitably lose)"""

    __tablename__ = 'enemy_histories'


    id = db.Column(db.Integer, primary_key=True)

    run_order = db.Column(db.Integer, nullable=False, default=0)
    
    score_id = db.Column(db.Integer, db.ForeignKey('highscores.id', ondelete='cascade'))
    
    image_url = db.Column(db.Text, nullable=False)

    enemy_health = db.Column(db.Integer, nullable=False)

    player_health = db.Column(db.Integer, nullable=False)


    score = db.relationship('Highscores', backref='enemies')


    def __repr__(self):
        return f"<Enemy #{self.run_order}: Enemy:{self.enemy_health} - {self.score.user.username}: {self.player_health}>"



