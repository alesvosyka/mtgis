from app.config import db
from app.models.model_exceptions import ErrorRecordExists
from app.models.model_user import User


class ResultMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    @property
    def user(self):
        return User.query.get(self.user_id)

    def __init__(self, id=None, user_id=None, wins=0, losses=0):
        self.user_id = user_id
        self.wins = wins
        self.losses = losses
        self.id = id

    def add_result_match(self):
        db.session.add(self)
        db.session.commit()
        return ResultMatch.query.order_by(ResultMatch.id.desc()).first()


