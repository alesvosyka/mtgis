from app.config import db
from app.models.model_user import User
from app.models.model_exceptions import ErrorRecordExists, ErrorRecordNotExists, ErrorNotSet
from app.models.model_mtg import MtgSet
from app.models.model_group import Group


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    owner_id = db.Column(db.Integer)
    start_datetime = db.Column(db.DateTime)
    type_id = db.Column(db.Integer, db.ForeignKey("type_of_tournament.id"))
    state_type_id = db.Column(db.Integer, db.ForeignKey("type_of_tournament_state.id"))

    players = db.relationship('Player')
    schedules = db.relationship("MatchesSchedule")
    playing_sets = db.relationship("MtgSetsInTournament")

    def __init__(self, name=None, owner_id=None, start_datetime=None, type_id=None):
        self.name = name
        self.owner_id = owner_id
        self.start_datetime = start_datetime
        self.type_id = type_id

    @property
    def owner(self):
        return User.query.get(self.owner_id)

    @property
    def players_by_user_id(self):
        return [player.user_id for player in self.players]

    @property
    def groups(self):
        groups_in_tournament = GroupInTournament.query.filter_by(tournament_id=self.id).all()
        groups = []
        for group_in_tournament in groups_in_tournament:
            try:
                groups.append(Group.query.get(group_in_tournament .group_id))
            except:
                pass
        return groups

    @property
    def type_by_name(self):
        if self.type_id is None:
            raise ErrorNotSet("")
        tournament_type = TypeOfTournament.query.get(self.type_id)
        if tournament_type is None:
            raise ErrorRecordNotExists("")
        return tournament_type.name

    @type_by_name.setter
    def type_by_name(self, type_name=None):
        tournament_type = TypeOfTournament.query.filter_by(name=type_name).first()
        if tournament_type is None:
            raise ErrorRecordNotExists("")
        self.type_id = tournament_type.id
        db.session.commit()

    @property
    def state_by_name(self):
        if self.state_type_id is None:
            raise ErrorNotSet("")
        state_type = TypeOfTournamentState.query.filter_by(id=self.state_type_id).first()
        if state_type is None:
            raise ErrorRecordNotExists("")
        return state_type.name

    @state_by_name.setter
    def state_by_name(self, state_name=None):
        state_type = TypeOfTournamentState.query.filter_by(name=state_name).first()
        if state_type is None:
            raise ErrorRecordNotExists("")
        self.state_type_id = state_type.id
        db.session.commit()

    def add_groups(self, group_ids=()):
        for group_id in group_ids:
            db.session.add(GroupInTournament(group_id=group_id, tournament_id=self.id))
            db.session.commit()

    def add(self):
        db.session.add(self)
        db.session.commit()
        return Tournament.query.order_by(Tournament.id.desc()).first()

    def delete_schedule(self):
        print(self.schedules)
        for schedule in self.schedules:
            schedule.delete()

    def delete(self):
        try:
            self.delete_schedule()
        except:
            pass
        for player in self.players:
            db.session.delete(player)
        db.session.delete(self)
        db.session.commit()


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


class TypeOfTournamentState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class GroupInTournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    def __init__(self, id=None, group_id=None, tournament_id=None):
        self.id =id
        self.group_id = group_id
        self.tournament_id = tournament_id


class MtgSetsInTournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    set_id = db.Column(db.Integer, db.ForeignKey('mtg_set.id'))

    @property
    def set_by_name(self):
        mtg_set = MtgSet.query.get(self.set_id)
        if mtg_set is None:
            raise ErrorRecordNotExists("")
        return mtg_set.name


    def __init__(self, id=None, tournament_id=None, set_id=None):
        self.id = id
        self.tournament_id = tournament_id
        self.set_id = set_id


class TypeOfTournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __init__(self, id=None, name=None):
        self.name = name
        self.id = id

    @staticmethod
    def get_id_by_name(name):
        return TypeOfTournament.query.filter_by(name=name).first()





