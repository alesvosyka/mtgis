from flask import request, render_template
from flask_login import current_user

from app.models.model_exceptions import ErrorRecordExists
from app.models.model_user import User, ResultMatch
from app.models.model_turnament import Tournament, Player, TournamentRound, Match1vs1, TournamentState, SchemeState, TypeOfSchemeState
from app.models.model_mtg import MtgSet
from app.models.model_group import Group, GroupMember, GroupRole

from app.config import app, db

from app.helpers.generators import generator_each_vs_each

from datetime import datetime


@app.route('/tournaments_list', methods=['POST', 'GET'])
def tournaments_list():
    if request.method == 'GET':
        result = db.session.query(Tournament, User).join(User, Tournament.owner_id == User.id).all()
        return render_template('contents/tournaments/tournaments_list.html', result=result)


@app.route('/tournament_info/<int:tournament_id>', methods=['POST', 'GET'])
def tournament_info(tournament_id):
    if request.method == 'GET':
        tournament = Tournament.query.get(tournament_id)
        return render_template('contents/tournaments/tournament_info.html',
                               tournament=tournament,)


@app.route('/manual_setting_tournament_scheme/<int:tournament_id>', methods=['POST', 'GET'])
def manual_setting_tournament_scheme(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        players_count = tournament.get_count_of_players()
        rounds_count = players_count if players_count % 2 == 1 else players_count - 1
        matches_in_round_count = players_count // 2
        #print("{} player: {} macthes per {} round".format(players_count, matches_in_round_count, rounds_count))
        for round_order in range(rounds_count):
            new_round = TournamentRound(tournament_id=tournament.id, order=round_order+1)
            new_round = new_round.add_tournament_round()
            for match in range(matches_in_round_count):
                result_match1 = ResultMatch()
                result_match1 = result_match1.add_result_match()
                result_match2 = ResultMatch()
                result_match2 = result_match2.add_result_match()
                new_match1vs1 = Match1vs1(tournament_round_id=new_round.id,
                                          result_match1_id=result_match1.id,
                                          result_match2_id=result_match2.id)
                new_match1vs1.add_match1vs1()

        return render_template('contents/tournaments/edit_schema_tournament.html',
                               tournament=tournament)


@app.route('/generateEachVsEach/<int:tournament_id>', methods=['POST', 'GET'])
def generate_each_vs_each(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        scheme_state = SchemeState(state_type_id=TypeOfSchemeState.query.filter_by(name='lock_players').first().id,
                                   tournament_id=tournament.id)
        scheme_state.add_or_update_scheme_state()
        player_ids = [player.user.id for player in tournament.players]
        print(player_ids)
        pair_dict = generator_each_vs_each(player_ids)
        print(pair_dict)
        players_count = tournament.get_count_of_players()
        rounds_count = players_count if players_count % 2 == 1 else players_count - 1
        matches_in_round_count = players_count // 2
        # print("{} player: {} matches per {} round".format(players_count, matches_in_round_count, rounds_count))
        for round_order in range(rounds_count):
            new_round = TournamentRound(tournament_id=tournament.id, order=round_order + 1)
            new_round = new_round.add_tournament_round()
            for match in range(matches_in_round_count):
                print('id1 {} id2 {}'.format(pair_dict[round_order+1][match][0], pair_dict[round_order+1][match][1]))
                result_match1 = ResultMatch(user_id=pair_dict[round_order+1][match][0])
                result_match1 = result_match1.add_result_match()
                result_match2 = ResultMatch(user_id=pair_dict[round_order+1][match][1])
                result_match2 = result_match2.add_result_match()
                new_match1vs1 = Match1vs1(tournament_round_id=new_round.id,
                                          result_match1_id=result_match1.id,
                                          result_match2_id=result_match2.id)
                new_match1vs1.add_match1vs1()
        print(tournament.scheme_state.state_name)
        return render_template('contents/tournaments/edit_schema_tournament.html',
                               tournament=tournament)


@app.route('/save_schedule_tournament', methods=['POST', 'GET'])
def save_schedule_tournament():
    if request.method == 'POST':
        tournament = Tournament.query.get(int(request.form['tournament_id']))
        print(request.form)
        for key, value in request.form.items():
            if "player" in key:
                stamp, result_id = key.split()
                ResultMatch.query.get(int(result_id)).user_id = int(value)
            if 'wins' in key:
                stamp, result_id = key.split()
                ResultMatch.query.get(int(result_id)).wins = int(value)
        db.session.commit()
    return render_template('contents/tournaments/tournament_info.html',
                           tournament=tournament)


@app.route("/edit_schedule_tournament", methods=['POST', 'GET'])
def edit_schedule_tournament():
    if request.method == 'POST':
        tournament = Tournament.query.get(request.form['tournament_id'])
        return render_template('contents/tournaments/edit_schema_tournament.html',
                               tournament=tournament)


@app.route('/delete_round_scheme/<int:tournament_id>', methods=['POST', 'GET'] )
def delete_round_scheme(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    for tournament_round in tournament.round_scheme:
        for match1vs1 in tournament_round.match_scheme:
            result_match1 = ResultMatch.query.get(match1vs1.result_match1_id)
            result_match2 = ResultMatch.query.get(match1vs1.result_match2_id)
            db.session.delete(result_match1)
            db.session.delete(result_match2)
            db.session.delete(match1vs1)
        db.session.delete(tournament_round)
    db.session.commit()
    return render_template('contents/tournaments/tournament_info.html', tournament=tournament)


@app.route('/save_tournament', methods=['POST', 'GET'])
def save_tournament():
    if request.method == 'POST':
        tournament = Tournament(name=request.form['name'],
                                owner_id=current_user.id,
                                start_datetime=datetime.strptime(request.form['date'] + request.form['time'], "%Y-%m-%d%H:%M"))
        tournament = tournament.add_tournament()
        owner = User.query.get(tournament.owner_id)
        unregistered_players = request.form['new_players'].split()
        registered_players = request.form.getlist('user')
        for player in unregistered_players:
            user = User(nick_name=player)
            try:
                user = user.add_user()
                registered_players.append(user.id)
            except ErrorRecordExists:
                pass
        for player_id in registered_players:
            player = Player(tournament_id=tournament.id, user_id=player_id)
            try:
                player.add_player()
            except ErrorRecordExists:
                pass
        users = tournament.get_tournament_players()

        return render_template('contents/tournaments/tournament_info.html', tournament=tournament, owner=owner, users=users)


@app.route('/create_tournament',  methods=['POST', 'GET'])
def create_tournament():
    if request.method == 'POST':
        if request.form['type'] == 'booster_draft':
            count_of_boosters = int(request.form['count_of_boosters'])
            sets_list = MtgSet.query.order_by(MtgSet.release_date.desc()).limit(30)
            users = User.query.filter(User.nick_name != 'superadmin').all()
            return render_template('create_tournament.html',
                                   count_of_boosters=count_of_boosters,
                                   sets_list=sets_list,
                                   users=users)
        return render_template('contents/tournaments/create_tournament.html')
    else:
        return render_template('contents/tournaments/create_tournament.html')


@app.route('/choice_tournament',  methods=['POST', 'GET'])
def choice_tournament():
    if request.method == 'POST':
        return render_template('contents/tournaments/choice_tournament.html')
    else:
        return render_template('contents/tournaments/choice_tournament.html')