from app.config import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    nick = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    password = None

    def __init__(self, login='', nick='', email='', password=''):
        self.email = email
        self.nick = nick
        self.login = login
        self.password = password

    flags = ("incorrect_login_name", "incorrect_password", "success")
    necessary_attributes = ('login', 'nick', 'email', 'password')
    unique_attributes = ('login', 'nick', 'email', 'password')

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
        return "Nick: {}, email: {}, password: {}, login: {}".format(self.nick, self.email, self.password, self.login)

    def check_collisions(self):
        collisions = list()
        for item in self.unique_attributes:
            if User.query.filter(getattr(User, item) == getattr(self, item)).first() is not None:
                collisions.append(item)
        if len(collisions) == 0:
            return None
        return collisions

    def check_empties(self):
        empties = list()
        for item in self.necessary_attributes:
            if getattr(self, item) == "":
                empties.append(item)
        if len(empties) == 0:
            return None
        return empties

    def register(self):
        collision = self.check_collisions()
        if collision is None:
            self.password_hash = generate_password_hash(self.password)
            db.session.add(self)
            db.session.commit()
        else:
            return collision
        return None

    def authentication(self):
        user = User.query.filter_by(login=self.login).first()
        if user is None:
            return None, 0
        if check_password_hash(user.password_hash, self.password):
            return user, 2
        return None, 1
