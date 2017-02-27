from app.config import db
from app.models.model_user import User
from datetime import datetime

playing_type_names = ['EachVsEach']


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    owner_id = db.Column(db.Integer)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, tournament_id, user_id):
        self.tournament_id = tournament_id
        self.user_id = user_id

    def create_player(self):
        db.session.add(self)
        db.session.commit()


class PlayingType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self, name):
        self.name = name


class Round1vs1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id1 = db.Column(db.Integer, db.ForeignKey('result_match.id'))
    match_id2 = db.Column(db.Integer, db.ForeignKey('result_match.id'))


