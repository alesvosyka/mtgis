from app.config import db, app
from app.models.model_user import TypeOfPrivilege, User, Login, Privilege
from app.models.model_exceptions import ErrorRecordExists

privileges = {1: 'super_admin', 2: 'admin'}
super_admin = ("superadmin", "superadmin123")


def init_privileges():
    for privilege_id, name in privileges.items():
        if TypeOfPrivilege.query.filter_by(name=name, id=privilege_id).first() is None:
            privilege = TypeOfPrivilege(name=name, privilege_id=privilege_id)
            db.session.add(privilege)
            db.session.commit()


def create_super_admin_acc():
        user = User(nick_name=super_admin[0])
        try:
            user = user.add_user()
        except ErrorRecordExists:
            return
            print("User already exists.")
        login = Login(login_name=super_admin[0], password=super_admin[1])
        try:
            login = login.add_login(user.id)
        except ErrorRecordExists:
            print("Login already exists.")
            return
        privilege = Privilege(user_id=user.id, type_of_privilege_id=1)
        try:
            privilege.add_privileges()
        except ErrorRecordExists:
            print("Error already exists")


def init_mtg_sets():
    pass
