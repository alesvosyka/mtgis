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


class Privilege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    type_of_privilege_id = db.Column(db.Integer, db.ForeignKey("type_of_privilege.id"))
    type_of_privilege = db.relationship('TypeOfPrivilege')

    def __init__(self, user_id=None, type_of_privilege_id=None):
        self.user_id = user_id
        self.type_of_privilege_id = type_of_privilege_id

    def add_privileges(self):
        if Privilege.query.filter_by(user_id=self.user_id,
                                     type_of_privilege_id=self.type_of_privilege_id).first() is None:
            db.session.add(self)
            db.session.commit()
        else:
            raise ErrorRecordExists(self.id)
        return Privilege.query.filter_by(user_id=self.user_id, type_of_privilege_id=self.type_of_privilege_id).first()


class TypeOfPrivilege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __init__(self, name, privilege_id=None):
        self.id = privilege_id
        self.name = name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(80), unique=True)
    list_of_privileges = db.relationship('Privilege', backref="user", lazy='dynamic')

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

    def __repr__(self):
        return "Nick: {}, id: {} ".format(self.nick_name, self.id)

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


class ResultMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    def __init__(self, user_id, wins=0, losses=0):
        self.user_id = user_id
        self.wins = wins
        self.losses = losses
