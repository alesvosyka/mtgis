from app.config import db
from app.models.model_exceptions import ErrorRecordExists


class MtgSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    block = db.Column(db.String(40))
    type = db.Column(db.String(40))
    release_date = db.Column(db.DateTime)

    def __init__(self, name=None, release_date=None, block=None, set_type=None):
        self.name = name
        self.release_date = release_date
        self.block = block
        self.type = set_type

    def exists(self):
        if MtgSet.query.filter_by(name=self.name).first() is not None:
            return True
        return False

    def add_set(self):
        if not self.exists():
            db.session.add(self)
            db.session.commit()
        else:
            raise ErrorRecordExists("")
