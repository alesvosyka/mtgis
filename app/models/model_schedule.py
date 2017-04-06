from app.config import db
from app.models.model_exceptions import ErrorRecordNotExists, ErrorRecordExists, ErrorNotSet
from app.models.model_matches import ResultMatch
from app.helpers.generators import generator_each_vs_each, shuffle_list, compute_round
from app.models.model_turnament import Tournament, Player
from app.helpers.point_systems import get_sorted_players, SchedulePlayer


class MatchesSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_type_id = db.Column(db.Integer, db.ForeignKey('type_of_schedule_state.id'))
    schedule_type_id = db.Column(db.Integer, db.ForeignKey('type_of_schedule.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    rounds = db.relationship('ScheduleRound', order_by="ScheduleRound.order")
    players_order = db.relationship('PlayerOrder', order_by="PlayerOrder.order")

    @property
    def tournament(self):
        return Tournament.query.get(self.tournament_id)

    @property
    def point_system(self):
        return PointSystem.query.filter_by(schedule_id=self.id).first()

    @property
    def sum_points(self):
        tournament = Tournament.query.get(self.tournament_id)
        matches = []
        point_table = {player: SchedulePlayer(player=player,
                                              reverse_order=len(tournament.players) -
                                              PlayerOrder.query.filter_by(player_id=player.id).first().order)
                       for player in tournament.players}
        for round in self.rounds:
            matches.extend(round.matches1vs1)
        sorted_players = get_sorted_players(matches=matches,
                                            point_table=point_table,
                                            point_system=self.point_system,
                                            return_list_of_schedule_players=True)
        return sorted_players

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

    @property
    def type_by_name(self):
        if self.schedule_type_id is None:
            raise ErrorNotSet("")
        schedule_type = TypeOfSchedule.query.get(self.schedule_type_id)
        if schedule_type is None:
            raise ErrorRecordNotExists("")
        return schedule_type.name

    @type_by_name.setter
    def type_by_name(self, type_name=None):
        schedule_type = TypeOfSchedule.query.filter_by(name=type_name).first()
        if schedule_type is None:
            raise ErrorRecordNotExists("")
        self.schedule_type_id = schedule_type.id
        db.session.commit()

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
                new_result1 = ResultMatch(user_id=self.tournament.players[0].user_id)
                new_result2 = ResultMatch(user_id=self.tournament.players[0].user_id)
                db.session.add(new_result1)
                db.session.add(new_result2)
                db.session.commit()
                new_match = RoundMatch1vs1(round_id=new_round.id,
                                           result1_id=new_result1.id,
                                           result2_id=new_result2.id,
                                           player1_id=self.tournament.players[0].id,
                                           player2_id=self.tournament.players[0].id)
                db.session.add(new_match)
        db.session.commit()
        return None

    def add_first_random_round(self):
        tournament = Tournament.query.get(self.tournament_id)
        players = tournament.players[:]
        shuffle_list(players)
        new_round = ScheduleRound(schedule_id=self.id, order=1)
        new_round.add()
        while len(players) > 1:
            player1 = players.pop()
            player2 = players.pop()
            result1 = ResultMatch(user_id=player1.user_id)
            result2 = ResultMatch(user_id=player2.user_id)
            db.session.add(result1)
            db.session.add(result2)
            db.session.commit()

            new_match = RoundMatch1vs1(round_id=new_round.id,
                                       result1_id=result1.id,
                                       result2_id=result2.id,
                                       player1_id=player1.id,
                                       player2_id=player2.id)
            db.session.add(new_match)
            db.session.commit()

    def add_first_round_by_order(self):
        players_orders = PlayerOrder.query.filter_by(schedule_id=self.id).order_by(PlayerOrder.order).all()
        new_round = ScheduleRound(schedule_id=self.id, order=1)
        new_round.add()
        for index in range(0, len(players_orders) if len(players_orders) % 2 == 0 else len(players_orders) - 1, 2):
            result1 = ResultMatch(user_id=players_orders[index].player.user_id)
            result2 = ResultMatch(user_id=players_orders[index + 1].player.user_id)
            db.session.add(result1)
            db.session.add(result2)
            db.session.commit()
            new_match = RoundMatch1vs1(round_id=new_round.id,
                                       result1_id=result1.id,
                                       result2_id=result2.id,
                                       player1_id=players_orders[index].player.id,
                                       player2_id=players_orders[index + 1].player.id)
            db.session.add(new_match)
            db.session.commit()

    def next_round(self):
        matches = []

        all_players = {player for player in Tournament.query.get(self.tournament_id).players}
        empty_pairs = []
        for round in self.rounds:
            players_in_round = set()
            for match in round.matches1vs1:
                players_in_round.add(match.player1)
                players_in_round.add(match.player2)
                matches.append(match)
            alone_player = all_players - players_in_round
            if len(alone_player) > 0:
                for player in alone_player:
                    empty_pairs.append((None, player))

        tournament = Tournament.query.get(self.tournament_id)
        new_round = ScheduleRound(schedule_id=self.id, order=len(self.rounds) + 1)
        new_round.add()

        point_table = {player: SchedulePlayer(player=player,
                                              reverse_order=len(tournament.players) -
                                                            PlayerOrder.query.filter_by(
                                                                player_id=player.id).first().order)
                       for player in tournament.players}

        sorted_players = get_sorted_players(matches=matches,
                                            point_table=point_table,
                                            point_system=self.point_system,
                                            with_score=False)
        if len(all_players) % 2 == 1:
            sorted_players.append(None)

        played_players_pairs = [(match.player1, match.player2) for match in matches]
        played_players_pairs.extend(empty_pairs)
        new_player_pairs = compute_round(played_pairs=played_players_pairs, desc_list=sorted_players)

        for pair in new_player_pairs:
            if None in pair:
                continue
            result1 = ResultMatch(user_id=pair[0].user_id)
            result2 = ResultMatch(user_id=pair[1].user_id)
            db.session.add(result1)
            db.session.add(result2)
            db.session.commit()
            new_match = RoundMatch1vs1(round_id=new_round.id,
                                       result1_id=result1.id,
                                       result2_id=result2.id,
                                       player1_id=pair[0].id,
                                       player2_id=pair[1].id)
            db.session.add(new_match)
            db.session.commit()

    def create_each_vs_each(self, players=()):
        round_dict = generator_each_vs_each(player_list=players)
        for order_of_round in round_dict:
            new_round = ScheduleRound(schedule_id=self.id, order=order_of_round)
            new_round = new_round.add()
            new_round.create_1vs1(round_list=round_dict[order_of_round])

    def delete(self):
        tournament = self.tournament
        for round in self.rounds:
            round.delete()

        players_orders = PlayerOrder.query.filter_by(schedule_id=self.id)
        if players_orders is not None:
            for player_order in players_orders:
                player_order.delete()
        db.session.delete(self)
        tournament.state_by_name = "open"
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
            new_match = RoundMatch1vs1(round_id=self.id,
                                       player1_id=match[0].id,
                                       player2_id=match[1].id)
            new_match = new_match.add()
            new_match.create(match=match)

    def delete(self):
        for match in self.matches1vs1:
            match.delete()
        db.session.delete(self)
        db.session.commit()


class RoundMatch1vs1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('schedule_round.id'))
    result1_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))
    result2_id = db.Column(db.Integer, db.ForeignKey('result_match.id'))
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    @property
    def result1(self):
        return ResultMatch.query.get(self.result1_id)

    @property
    def result2(self):
        return ResultMatch.query.get(self.result2_id)

    @property
    def player1(self):
        return Player.query.get(self.player1_id)

    @property
    def player2(self):
        return Player.query.get(self.player2_id)

    def update_player(self, user_id):
        round = ScheduleRound.query.get(self.round_id)
        schedule = MatchesSchedule.query.get(round.schedule_id)
        player = Player.query.filter_by(user_id=user_id, tournament_id=schedule.id).first()

        if self.result1.user_id == user_id:
            self.player1_id = player.id
        else:
            self.player2_id = player.id

    def __init__(self, id=None, round_id=None, result1_id=None, result2_id=None, player1_id=None, player2_id=None):
        self.id = id
        self.round_id = round_id
        self.result1_id = result1_id
        self.result2_id = result2_id
        self.player1_id = player1_id
        self.player2_id = player2_id

    def add(self):
        if RoundMatch1vs1.query.filter_by(round_id=self.round_id,
                                          result1_id=self.result1_id,
                                          result2_id=self.result2_id).first() is not None:
            raise ErrorRecordExists("")
        db.session.add(self)
        db.session.commit()
        return self

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


class TypeOfSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class PointSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('matches_schedule.id'))
    pure_win = db.Column(db.Integer)
    win = db.Column(db.Integer)
    lose = db.Column(db.Integer)
    pure_lose = db.Column(db.Integer)
    draw = db.Column(db.Integer)

    def __init__(self, id=None, schedule_id=None, pure_win=0, win=0, lose=0, pure_lose=0, draw=0):
        self.pure_win = pure_win
        self.win = win
        self.lose = lose
        self.pure_lose = pure_lose
        self.draw = draw
        self.schedule_id = schedule_id
        self.id = id

    def add_or_update(self):
        point_system = PointSystem.query.filter_by(schedule_id=self.schedule_id).first()
        if point_system is None:
            db.session.add(self)
            db.session.commit()
            return self
        else:
            point_system.win = self.win
            point_system.pure_win = self.pure_win
            point_system.pure_lose = self.pure_lose
            point_system.lose = self.lose
            point_system.draw = self.draw
            db.session.commit()
            return point_system


class PlayerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('matches_schedule.id'))
    order = db.Column(db.Integer)

    @property
    def player(self):
        return Player.query.get(self.player_id)

    def __init__(self, id=None, schedule_id=None, player_id=None, order=None):
        self.id = id
        self.schedule_id = schedule_id
        self.order = order
        self.player_id = player_id

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
