from flask import request, render_template
from app.config import app, db
from app.models.model_turnament import Tournament
from app.models.model_schedule import MatchesSchedule
from app.models.model_matches import ResultMatch
from app.controlers.controller_decorators import privilege_required


@app.route('/save_schedule_tournament', methods=['POST', 'GET'])
def save_schedule_tournament():
    if request.method == 'POST':
        tournament = Tournament.query.get(int(request.form['tournament_id']))
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


@app.route('/delete_round_schedule/<int:tournament_id>', methods=['POST', 'GET'])
@privilege_required
def delete_round_scheme(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    tournament.schedules[0].delete()
    tournament.state_by_name = "open"
    return render_template('contents/tournaments/tournament_info.html', tournament=tournament)


@app.route('/manual_setting_tournament_scheme/<int:tournament_id>', methods=['POST', 'GET'])
def manual_setting_tournament_scheme(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        schedule = MatchesSchedule(tournament_id=tournament_id)
        schedule = schedule.add()
        schedule.create_empty(len(tournament.players), len(tournament.players))
        schedule.state_by_name = "unlock_players"
        tournament.state_by_name = "with_schedule"
        return render_template('contents/tournaments/edit_schema_tournament.html',
                               tournament=tournament)


@app.route('/generateEachVsEach/<int:tournament_id>', methods=['POST', 'GET'])
def generate_each_vs_each(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        schedule = MatchesSchedule(tournament_id=tournament.id)
        schedule = schedule.add()
        schedule.create_each_vs_each(tournament.players)
        schedule.state_by_name = "lock_players"
        tournament.state_by_name = "with_schedule"
        return render_template('contents/tournaments/edit_schema_tournament.html',
                               tournament=tournament)

