from app.config import db
from app.models.model_user import TypeOfRole, User, Login, Role
from app.models.model_exceptions import ErrorRecordExists
from app.models.model_mtg import MtgSet
from app.models.model_turnament import TypeOfState

from mtgsdk import Set
from mtgsdk.restclient import MtgException
from datetime import datetime

privileges = {1: 'super_admin', 2: 'admin'}
super_admin = ("superadmin", "superadmin123")
tournament_states = ("open_with_scheme", "open", "closed")


def init_roles():
    for role_id, name in privileges.items():
        if TypeOfRole.query.filter_by(name=name, id=role_id).first() is None:
            privilege = TypeOfRole(name=name, role_id=role_id)
            db.session.add(privilege)
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
        role = Role(user_id=user.id, type_of_role_id=1)
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


def init_tournament_states():
    for tournament_state in tournament_states:
        state = TypeOfState(tournament_state)
        try:
            db.session.add(state)
        except:
            pass
    db.session.commit()
