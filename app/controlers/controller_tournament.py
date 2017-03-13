from flask import request, render_template
from flask_login import current_user

from app.models.model_exceptions import ErrorRecordExists
from app.models.model_user import User
from app.models.model_turnament import Tournament, Player, TypeOfTournament, MtgSetsInTournament, GroupInTournament
from app.models.model_mtg import MtgSet
from app.models.model_group import Group
from app.config import app, db

from datetime import datetime


@app.route('/tournaments_list', methods=['POST', 'GET'])
def tournaments_list():
    if request.method == 'GET':
        tournaments = Tournament.query.all()
        return render_template('contents/tournaments/tournaments_list.html', tournaments=tournaments)


@app.route('/tournament_info/<int:tournament_id>', methods=['POST', 'GET'])
def tournament_info(tournament_id):
    if request.method == 'GET':
        tournament = Tournament.query.get(tournament_id)
        print(tournament.type_by_name, tournament.state_by_name)
        return render_template('contents/tournaments/tournament_info.html',
                               tournament=tournament,)


@app.route('/choice_tournament',  methods=['POST', 'GET'])
def choice_tournament():
    groups = Group.get_editable_groups(current_user.id)
    return render_template('contents/tournaments/choice_tournament.html', groups=groups)


@app.route('/create_tournament',  methods=['POST', 'GET'])
def create_tournament():
    if request.method == 'POST':
        if request.form['type'] == 'booster_draft':
            count_of_boosters = int(request.form['count_of_boosters'])
            sets_list = MtgSet.query.order_by(MtgSet.release_date.desc()).limit(30)
            group_ids = []
            if request.form['players'] == 'groups':
                group_ids = request.form.getlist('group')
                groups = []
                users = []
                for id in group_ids:
                    groups.append(Group.query.get(int(id)))
                for group in groups:
                    for member in group.get_all_members():
                        users.append(member.user)
            else:
                users = User.get_all_users()

            return render_template('contents/tournaments/create_tournament.html',
                                   type=request.form["type"],
                                   count_of_boosters=count_of_boosters,
                                   sets_list=sets_list,
                                   users=users,
                                   group_ids=group_ids)

    return render_template('contents/tournaments/create_tournament.html')


@app.route('/save_tournament', methods=['POST', 'GET'])
def save_tournament():
    if request.method == 'POST':
        print(request.form)
        tournament = Tournament(name=request.form['name'],
                                owner_id=current_user.id,
                                start_datetime=datetime.strptime(request.form['date'] + request.form['time'], "%Y-%m-%d%H:%M"),
                                type_id=TypeOfTournament.get_id_by_name(request.form['type']).id
                                )
        tournament.add()
        boosters_ids = request.form.getlist("booster")
        for id in boosters_ids:
            new_set = MtgSetsInTournament(set_id=id, tournament_id=tournament.id)
            db.session.add(new_set)
        db.session.commit()
        tournament.state_by_name = "open"
        unregistered_players = request.form['new_players'].split()
        registered_players = request.form.getlist('user')
        group_ids = request.form.getlist('group_id')
        for group_id in group_ids:
            group_in_tournament = GroupInTournament(group_id=group_id, tournament_id=tournament.id)
            db.session.add(group_in_tournament)
            db.session.commit()
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

        return render_template('contents/tournaments/tournament_info.html', tournament=tournament)


@app.route('/delete_tournament/<int:tournament_id>', methods=['POST', 'GET'])
def delete_tournament(tournament_id):
    if request.method == 'POST':
        tournament = Tournament.query.get(tournament_id)
        tournament.delete()
    tournaments = Tournament.query.all()
    return render_template('contents/tournaments/tournaments_list.html', tournaments=tournaments)
