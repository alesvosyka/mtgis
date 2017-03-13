from app.config import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.model_exceptions import ErrorRecordExists, ErrorIncorrectPassword, ErrorRecordNotExists


class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    password = None

    def __init__(self, login_name='', password='', user_id=None):
        self.password = password
        self.login_name = login_name
        self.user_id = user_id

    def exists(self):
        if Login.query.filter_by(login_name=self.login_name).first() is None:
            return False
        else:
            return True

    def add_login(self, user_id):
        if self.exists():
            raise ErrorRecordExists(self.login_name)

        self.password_hash = generate_password_hash(self.password)
        self.user_id = user_id
        db.session.add(self)
        db.session.commit()
        return Login.query.filter_by(login_name=self.login_name).first()

    def authentication(self):
        login = Login.query.filter_by(login_name=self.login_name).first()
        if login is None:
            raise ErrorRecordNotExists(self.login_name)
        if not check_password_hash(login.password_hash, self.password):
            raise ErrorIncorrectPassword()
        return login

    def __repr__(self):
        return "Login: {}, id: {}, psw: {}, hash: {} ".format(self.login_name, self.id, self.password, self.password_hash)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    type_of_role_id = db.Column(db.Integer, db.ForeignKey("type_of_role.id"))

    type_of_role = db.relationship('TypeOfRole')

    def __init__(self, user_id=None, type_of_role_id=None):
        self.user_id = user_id
        self.type_of_role_id = type_of_role_id

    @property
    def role_name(self):
        return TypeOfRole.query.filter_by(id=self.type_of_role_id).first()

    def add_role(self):
        if Role.query.filter_by(user_id=self.user_id,
                                type_of_role_id=self.type_of_role_id).first() is None:
            db.session.add(self)
            db.session.commit()
        else:
            raise ErrorRecordExists(self.id)
        return Role.query.filter_by(user_id=self.user_id, type_of_role_id=self.type_of_role_id).first()


class TypeOfRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __init__(self, name=None, role_id=None):
        self.id = role_id
        self.name = name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(80), unique=True)

    list_of_roles = db.relationship('Role', backref="user", lazy='dynamic')
    login = db.relationship('Login', backref="user",  uselist=False)

    def __init__(self,  nick_name=None, user_id=None):
        self.nick_name = nick_name
        self.id = user_id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_all_users(filter_id_list=[]):
        condition = "(User.id != 1)"
        for id in filter_id_list:
            condition += "& (User.id != {})".format(id)
        return User.query.filter(condition).all()

    def __repr__(self):
        return "Nick: {}, id: {} ".format(self.nick_name, self.id)

    def delete_roles(self):
        for role in self.list_of_roles:
            db.session.delete(role)
            db.session.commit()

    def add_role(self, role_type_id):
        role = Role(user_id=self.id, type_of_role_id=role_type_id)
        try:
            role.add_role()
        except ErrorRecordExists:
            pass

    def exists(self):
        if User.query.filter_by(nick_name=self.nick_name).first() is None:
            return False
        else:
            return True

    def add_user(self):
        if self.exists():
            raise ErrorRecordExists(self.nick_name)
        db.session.add(self)
        db.session.commit()
        return User.query.filter_by(nick_name=self.nick_name).first()



