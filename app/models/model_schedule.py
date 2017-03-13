from app.config import db
from app.models.model_exceptions import ErrorRecordNotExists, ErrorRecordExists, ErrorNotSet
from app.models.model_matches import ResultMatch
from app.helpers.generators import generator_each_vs_each


class MatchesSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_type_id = db.Column(db.Integer, db.ForeignKey('type_of_schedule_state.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    rounds = db.relationship('ScheduleRound', order_by="ScheduleRound.order")

    def __init__(self, id=None, state_type_id=None, tournament_id=None):
        self.id = id
        self.state_type_id = state_type_id
        self.tournament_id = tournament_id

    def add(self):
        if MatchesSchedule.query.filter_by(tournament_id=self.tournament_id).first() is not None:
            raise ErrorRecordExists("")
        db.session.add(self)
        db.session.commit()
        return self

    def create_empty(self, count_players, count_rounds):
        max_count_rounds = count_players if count_players % 2 == 1 else count_players - 1
        count_matches_per_round = count_players // 2
        count_rounds = count_rounds if count_rounds <= max_count_rounds else max_count_rounds
        for round_index in range(count_rounds):
            new_round = ScheduleRound(schedule_id=self.id, order=round_index + 1)
            db.session.add(new_round)
            for _ in range(count_matches_per_round):
                new_result1 = ResultMatch()
                new_result2 = ResultMatch()
                db.session.add(new_result1)
                db.session.add(new_result2)
                db.session.commit()
                new_match = RoundMatch1vs1(round_id=new_round.id, result1_id=new_result1.id, result2_id=new_result2.id)
                db.session.add(new_match)
        db.session.commit()
        return None

    def create_each_vs_each(self, players=()):
        round_dict = generator_each_vs_each(player_list=players)
        for order_of_round in round_dict:
            new_round = ScheduleRound(schedule_id=self.id, order=order_of_round)
            new_round = new_round.add()
            new_round.create_1vs1(round_list=round_dict[order_of_round])

    @property
    def state_by_name(self):
        if self.state_type_id is None:
            raise ErrorNotSet("")
        state_type = TypeOfScheduleState.query.get(self.state_type_id)
        if state_type is None:
            raise ErrorRecordNotExists("")
        return state_type.name

    @state_by_name.setter
    def state_by_name(self, type_name=None):
        schedule_type = TypeOfScheduleState.query.filter_by(name=type_name).first()
        if schedule_type is None:
            raise ErrorRecordNotExists("")
        self.state_type_id = schedule_type.id
        db.session.commit()

    def delete(self):
        print("delete MatchesSchedule")
        for round in self.rounds:
            round.delete()
        db.session.delete(self)
        db.session.commit()


class ScheduleRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('matches_schedule.id'))
    order = db.Column(db.Integer)

    matches1vs1 = db.relationship('RoundMatch1vs1')

    def __init__(self, id=None, schedule_id=None, order=None):
        self.id = id
        self.schedule_id = schedule_id
        self.order = order

    def add(self):
        if ScheduleRound.query.filter_by(schedule_id=self.schedule_id, order=self.order).first() is not None:
            raise ErrorRecordExists("")
        db.session.add(self)
        db.session.commit()
        return self

    def create_1vs1_empty(self, count_matches=0):
        for i in range(count_matches):
            new_match = RoundMatch1vs1(round_id=self.id)
            new_match = new_match.add()
            new_match.add_empty()

    def create_1vs1(self, round_list=None):
        for match in round_list:
            new_match = RoundMatch1vs1(round_id=self.id)
            new_match = new_match.add()
            new_match.create(match=match)

    def delete(self):
        print("delete ScheduleRound")
        print(self.matches1vs1)
        for match in self.matches1vs1:
            match.delete()
        db.session.delete(self)
        db.session.commit()


class RoundMatch1vs1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('schedule_round.id'))
    result1_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))
    result2_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))

    @property
    def result1(self):
        return ResultMatch.query.get(self.result1_id)

    @property
    def result2(self):
        return ResultMatch.query.get(self.result2_id)

    def __init__(self, id=None, round_id=None, result1_id=None, result2_id=None):
        self.id = id
        self.round_id = round_id
        self.result1_id = result1_id
        self.result2_id = result2_id

    def add(self):
        if RoundMatch1vs1.query.filter_by(round_id=self.round_id,
                                          result1_id=self.result1_id,
                                          result2_id=self.result2_id).first() is not None:
            raise ErrorRecordExists("")
        db.session.add(self)
        db.session.commit()
        return RoundMatch1vs1.query.filter_by(round_id=self.round_id,
                                              result1_id=self.result1_id,
                                              result2_id=self.result2_id).first()

    def create(self, match=(None, None)):
        """
        create  2x new <app.models.model_matches.ResultMatch> record and save reference by id

        :param match:  Expects pair of <app.models.model_tournament.Player>.
        :return:  None
        """
        result1 = ResultMatch(user_id=match[0].user.id)
        result2 = ResultMatch(user_id=match[1].user.id)
        result1 = result1.add_result_match()
        result2 = result2.add_result_match()
        self.result1_id = result1.id
        self.result2_id = result2.id
        db.session.add(self)
        db.session.commit()
        return None

    def delete(self):
        print("delete  RoundMatch1vs1")
        try:
            db.session.delete(ResultMatch.query.get(self.result1_id))
            db.session.delete(ResultMatch.query.get(self.result2_id))
        except:
            pass
        db.session.delete(self)
        db.session.commit()


class TypeOfScheduleState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name