from flask import request, render_template
from app.config import app, db
from app.models.model_turnament import Tournament
from app.models.model_schedule import MatchesSchedule, PointSystem, RoundMatch1vs1
from app.models.model_matches import ResultMatch
from app.controlers.controller_decorators import privilege_required


@app.route('/save_schedule/<int:schedule_id>', methods=['POST', 'GET'])
def save_schedule_tournament(schedule_id):
    if request.method == 'POST':
        schedule = MatchesSchedule.query.get(schedule_id)
        tournament = schedule.tournament
        for key, value in request.form.items():
            if "player" in key:
                stamp, result_id = key.split()
                result = ResultMatch.query.get(int(result_id))
                result.user_id = int(value)
                match = RoundMatch1vs1.query.filter((RoundMatch1vs1.result1_id == result.id) |
                                                    (RoundMatch1vs1.result2_id == result.id)).first()
                match.update_player(user_id=int(value))
            if 'wins' in key:
                stamp, result_id = key.split()
                ResultMatch.query.get(int(result_id)).wins = int(value)
        if schedule.type_by_name == "manual" or schedule.type_by_name == "each_vs_each":
            point_system = PointSystem(schedule_id=schedule.id,
                                       pure_win=int(request.form['pure_win']),
                                       win=int(request.form['win']),
                                       draw=int(request.form['draw']),
                                       lose=int(request.form['lose']),
                                       pure_lose=int(request.form['pure_lose']))
            point_system.add_or_update()
        db.session.commit()
    return render_template('contents/tournaments/tournament_info.html',
                           tournament=tournament)


@app.route("/edit_schedule/<int:schedule_id>", methods=['POST', 'GET'])
def edit_schedule(schedule_id):
    if request.method == 'POST':
        schedule = MatchesSchedule.query.get(schedule_id)
        return render_template('contents/schedules/edit_schedule.html',
                               schedule=schedule)


@app.route('/delete_round_schedule/<int:schedule_id>', methods=['POST', 'GET'])
def delete_round_scheme(schedule_id):
    tournament = MatchesSchedule.query.get(schedule_id).tournament
    tournament.schedules[0].delete()
    tournament.state_by_name = "open"
    return render_template('contents/tournaments/tournament_info.html', tournament=tournament)


@app.route('/manual_setting_tournament_schedule/<int:tournament_id>', methods=['POST', 'GET'])
def manual_setting_tournament_scheme(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        schedule = MatchesSchedule(tournament_id=tournament_id)
        schedule = schedule.add()
        schedule.create_empty(len(tournament.players), int(request.form["count_of_round"]))
        schedule.type_by_name = "manual"
        schedule.state_by_name = "full"
        tournament.state_by_name = "with_schedule"
        return render_template('contents/schedules/edit_schedule.html',
                               schedule=schedule)


@app.route('/generateEachVsEach/<int:tournament_id>', methods=['POST', 'GET'])
def generate_each_vs_each(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        schedule = MatchesSchedule(tournament_id=tournament.id)
        schedule = schedule.add()
        schedule.create_each_vs_each(tournament.players)
        schedule.state_by_name = "full"
        schedule.type_by_name = "each_vs_each"
        tournament.state_by_name = "with_schedule"
        return render_template('contents/schedules/edit_schedule.html',
                               schedule=schedule)


# by_round-------------------------------------

@app.route('/generate_by_round/<int:tournament_id>', methods=['POST', 'GET'])
def generate_by_round(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        return render_template('contents/schedules/setting_round_generator.html',
                               tournament=tournament)


@app.route('/round_generator/<int:tournament_id>', methods=['POST', 'GET'])
def round_generator(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        if tournament.state_by_name == "open":
            schedule = MatchesSchedule(tournament_id=tournament_id)
            schedule.add()
            schedule.add_first_random_round()
            schedule.type_by_name = 'by_round'
            schedule.state_by_name = "not_full"
            point_system = PointSystem(schedule_id=schedule.id,
                                       pure_win=int(request.form['pure_win']),
                                       win=int(request.form['win']),
                                       draw=int(request.form['draw']),
                                       lose=int(request.form['lose']),
                                       pure_lose=int(request.form['pure_lose']))
            point_system.add_or_update()
            tournament.state_by_name = "with_schedule"
            return render_template('contents/schedules/round_generator.html',
                                   schedule=schedule)
        elif tournament.state_by_name == "with_schedule":
            schedule = tournament.schedules[0]
            if schedule.state_by_name == "not_full":
                for key, value in request.form.items():
                    print(request.form)
                    if "player" in key:
                        stamp, result_id = key.split()
                        ResultMatch.query.get(int(result_id)).user_id = int(value)
                    if 'wins' in key:
                        stamp, result_id = key.split()
                        ResultMatch.query.get(int(result_id)).wins = int(value)
                db.session.commit()
                schedule.next_round()
                count_players = len(tournament.players)
                max_rounds = count_players if count_players % 2 == 1 else count_players - 1
                if len(schedule.rounds) == max_rounds:
                    schedule.state_by_name = "full"
            return render_template('contents/schedules/round_generator.html',
                                   schedule=schedule)


@app.route("/edit_by_round/<int:schedule_id>", methods=['POST', 'GET'])
def edit_by_round(schedule_id):
    if request.method == 'POST':
        schedule = MatchesSchedule.query.get(schedule_id)
        return render_template('contents/schedules/round_generator.html',
                               schedule=schedule)

