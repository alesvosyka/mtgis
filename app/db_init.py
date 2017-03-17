from app.config import db
from app.models.model_user import TypeOfRole, User, Login, Role
from app.models.model_exceptions import ErrorRecordExists
from app.models.model_mtg import MtgSet
from app.models.model_turnament import TypeOfTournamentState, TypeOfTournament
from app.models.model_group import TypeOfGroupRole
from app.models.model_schedule import TypeOfScheduleState, TypeOfSchedule


from mtgsdk import Set
from mtgsdk.restclient import MtgException
from datetime import datetime

roles = ('super_admin', 'admin')
super_admin = ("superadmin", "superadmin123")
tournament_states = ("open", "closed", "with_schedule")
schedule_states = ("empty", "full", "not_full")
schedule_types = ("manual", "each_vs_each", "by_round")
group_roles = ("owner", "group_admin")
tournament_types = ("booster_draft", "classic")


def init_tournament_types():
    for name in tournament_types:
        if TypeOfTournament.query.filter_by(name=name).first() is None:
            role = TypeOfTournament(name=name)
            db.session.add(role)
    db.session.commit()


def init_roles():
    for name in roles:
        if TypeOfRole.query.filter_by(name=name).first() is None:
            role = TypeOfRole(name=name)
            db.session.add(role)
    db.session.commit()


def init_group_roles():
    for group_role in group_roles:
        if TypeOfGroupRole.query.filter_by(name=group_role).first() is None:
            role = TypeOfGroupRole(name=group_role)
            try:
                db.session.add(role)
            except:
                pass
    db.session.commit()


def create_super_admin_acc():
        user = User(nick_name=super_admin[0])
        try:
            user = user.add_user()
        except ErrorRecordExists:
            print("User already exists.")
            return
        login = Login(login_name=super_admin[0], password=super_admin[1])
        try:
            login.add_login(user.id)
        except ErrorRecordExists:
            print("Login already exists.")
            return
        role = Role(user_id=user.id, type_of_role_id=TypeOfRole.query.filter_by(name="super_admin").first().id)
        print(role.user_id)
        try:
            role.add_role()
        except ErrorRecordExists:
            print("Error already exists")


def init_mtg_sets():
    MtgSet.update()


def init_tournament_states_types():
    for tournament_state in tournament_states:
        if TypeOfTournamentState.query.filter_by(name=tournament_state).first() is None:
            state = TypeOfTournamentState(name=tournament_state)
            try:
                db.session.add(state)
            except:
                pass
    db.session.commit()


def init_schedule_states_types():
    for schedule_state in schedule_states:
        if TypeOfScheduleState.query.filter_by(name=schedule_state).first() is None:
            state = TypeOfScheduleState(name=schedule_state)
            try:
                db.session.add(state)
            except:
                pass
    db.session.commit()


def init_schedule_types():
    for schedule_type in schedule_types:
        if TypeOfSchedule.query.filter_by(name=schedule_type).first() is None:
            type = TypeOfSchedule(name=schedule_type)
            try:
                db.session.add(type)
            except:
                pass
    db.session.commit()
