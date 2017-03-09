from app.config import db
from app.models.model_user import TypeOfRole, User, Login, Role
from app.models.model_exceptions import ErrorRecordExists
from app.models.model_mtg import MtgSet
from app.models.model_turnament import TypeOfSchemeState, TypeOfTournamentState
from app.models.model_group import GroupRole, TypesOfGroupRole

from mtgsdk import Set
from mtgsdk.restclient import MtgException
from datetime import datetime

roles = ('super_admin', 'admin')
super_admin = ("superadmin", "superadmin123")
tournament_states = ("open", "closed")
scheme_states = ("lock_players", "no_schema", "complete")
group_roles = ("owner", "group_admin")


def init_roles():
    for name in roles:
        if TypeOfRole.query.filter_by(name=name).first() is None:
            role = TypeOfRole(name=name)
            db.session.add(role)
            db.session.commit()


def init_group_roles():
    for group_role in group_roles:
        if TypesOfGroupRole.query.filter_by(name=group_role).first() is None:
            role = TypesOfGroupRole(name=group_role)
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
        role = Role(user_id=user.id, type_of_role_id=TypeOfRole.query.filter_by(name="superadmin").first().id)
        print(role.user_id)
        try:
            role.add_role()
        except ErrorRecordExists:
            print("Error already exists")


def init_mtg_sets():
    try:
        sets = Set.all()
    except MtgException:

        return

    for card_set in sets:
        if not card_set.online_only:
            release_date = datetime.strptime(card_set.release_date, "%Y-%m-%d")
            mtg_set = MtgSet(name=card_set.name,
                             release_date=release_date,
                             block=card_set.block,
                             set_type=card_set.type)
            try:
                mtg_set.add_set()
            except ErrorRecordExists:
                print("Set is already in db.")


def init_tournament_states_types():
    for tournament_state in tournament_states:
        if TypeOfTournamentState.query.filter_by(name=tournament_state).first() is None:
            state = TypeOfTournamentState(name=tournament_state)
            try:
                db.session.add(state)
            except:
                pass
    db.session.commit()


def init_scheme_states_types():
    for scheme_state in scheme_states:
        if TypeOfSchemeState.query.filter_by(name=scheme_state).first() is None:
            state = TypeOfSchemeState(name=scheme_state)
            try:
                db.session.add(state)
            except:
                pass
    db.session.commit()
