from app.config import db, app
from app.models.model_user import User, ResultMatch
from datetime import datetime

from app.models.model_exceptions import ErrorRecordExists


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    owner_id = db.Column(db.Integer)
    start_datetime = db.Column(db.DateTime)

    round_scheme = db.relationship('TournamentRound')
    players = db.relationship('Player')

    def __init__(self, name='Tournament', owner_id=None, start_datetime=None):
        self.name = name
        self.owner_id = owner_id
        self.start_datetime = start_datetime

    @property
    def owner(self):
        return User.query.get(self.owner_id)

    @property
    def tournament_state(self):
        return TournamentState.query.filter_by(tournament_id=self.id).first()

    @property
    def scheme_state(self):
        return SchemeState.query.filter_by(tournament_id=self.id).first()

    def add_tournament(self):
        db.session.add(self)
        db.session.commit()
        return Tournament.query.order_by(Tournament.id.desc()).first()

    def get_tournament_players(self):
        players = Player.query.filter_by(tournament_id=self.id).all()
        users = []
        for player in players:
            user = User.query.get(player.user_id)
            users.append(user)
        return users

    def get_count_of_players(self):
        return len(self.get_tournament_players())

    def has_round_scheme(self):
        if TournamentRound.query.filter_by(tournament_id=self.id).first() is None:
            return False
        return True

    def get_round_scheme(self):
        return TournamentRound.query.filter_by(tournament_id=self.id).all()


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def user(self):
        return User.query.get(self.user_id)

    def __init__(self, tournament_id=None, user_id=None):
        self.tournament_id = tournament_id
        self.user_id = user_id

    def add_player(self):
        if self.exists():
            raise ErrorRecordExists("")
        else:
            db.session.add(self)
            db.session.commit()
            return Player.query.filter_by(tournament_id=self.tournament_id, user_id=self.user_id).first()

    def exists(self):
        if Player.query.filter_by(tournament_id=self.tournament_id, user_id=self.user_id).first() is None:
            return False
        return True


class TournamentRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    order = db.Column(db.Integer)

    match_scheme = db.relationship('Match1vs1')

    def __init__(self, tournament_id=None, order=None):
        self.tournament_id = tournament_id
        self.order = order

    def exists(self):
        if TournamentRound.query.filter_by(tournament_id=self.tournament_id, order=self.order).first() is None:
            return False
        return True

    def add_tournament_round(self):
        if not self.exists():
            db.session.add(self)
            db.session.commit()
            return TournamentRound.query.filter_by(tournament_id=self.tournament_id, order=self.order).first()
        else:
            raise ErrorRecordExists("")


class SchemeState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    state_type_id = db.Column(db.Integer, db.ForeignKey('type_of_scheme_state.id'))

    @property
    def state_name(self):
        return TypeOfSchemeState.query.get(self.state_type_id).name

    def __init__(self, id=None, tournament_id=None, state_type_id=None):
        self.state_type_id = state_type_id
        self.id = id
        self.tournament_id = tournament_id

    def add_or_update_scheme_state(self):
        record = SchemeState.query.filter_by(tournament_id=self.tournament_id).first()
        if record is not None:
            record.state_type_id = self.state_type_id
            db.session.commit()
        else:
            db.session.add(self)
            db.session.commit()
            record = SchemeState.query.filter_by(tournament_id=self.tournament_id).first()
        return record


class TypeOfSchemeState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class TournamentState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    state_type_id = db.Column(db.Integer, db.ForeignKey('type_of_tournament_state.id'))

    def __init__(self, id=None, tournament_id=None, state_type_id=None):
        self.id = id
        self.tournament_id = tournament_id
        self.state_type_id = state_type_id


class TypeOfTournamentState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class Match1vs1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_round_id = db.Column(db.Integer, db.ForeignKey('tournament_round.id'))
    result_match1_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))
    result_match2_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))

    @property
    def result_match1(self):
        return ResultMatch.query.get(self.result_match1_id)

    @property
    def result_match2(self):
        return ResultMatch.query.get(self.result_match2_id)

    def __init__(self, id=None, tournament_round_id=None, result_match1_id=None, result_match2_id=None):
        self.id = id
        self.result_match1_id = result_match1_id
        self.result_match2_id = result_match2_id
        self.tournament_round_id = tournament_round_id

    def exists(self):
        result = Match1vs1.query.filter_by(result_match1_id=self.result_match1_id,
                                           result_match2_id=self.result_match2_id,
                                           tournament_round_id=self.tournament_round_id).first()
        if result is None:
            return False
        return True

    def add_match1vs1(self):
        if self.exists():
            raise ErrorRecordExists
        else:
            db.session.add(self)
            db.session.commit()
            return Match1vs1.query.filter_by(result_match1_id=self.result_match1_id,
                                             result_match2_id=self.result_match1_id,
                                             tournament_round_id=self.tournament_round_id).first()



