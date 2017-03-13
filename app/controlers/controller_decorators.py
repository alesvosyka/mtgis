from flask import abort
from flask_login import current_user
from app.models.model_turnament import Tournament


def privilege_required(view_function):
    def check_user_wrapper(tournament_id):
        if not current_user.is_authenticated:
            abort(401)
        tournament = Tournament.query.get(tournament_id)
        print(tournament.id, current_user.id)
        if tournament.owner.id == current_user.id:
            return view_function(tournament_id)
        else:
            abort(401)
    return check_user_wrapper

