from app.config import db
from app.models.model_exceptions import ErrorRecordExists
from mtgsdk import Set
from datetime import datetime


class MtgSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    block = db.Column(db.String(40))
    type = db.Column(db.String(40))
    gatherer_code = db.Column(db.Integer)
    release_date = db.Column(db.DateTime)

    def __init__(self, name=None, release_date=None, block=None, set_type=None, gatherer_code=None):
        self.name = name
        self.release_date = release_date
        self.block = block
        self.type = set_type
        self.gatherer_code = gatherer_code

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

    @staticmethod
    def update():
        sets = Set.all()
        newest_set_in_db = MtgSet.query.order_by(MtgSet.release_date.desc()).first()
        for card_set in sets:
            if not card_set.online_only:
                release_date = datetime.strptime(card_set.release_date, "%Y-%m-%d")
                if newest_set_in_db is not None:
                    if release_date > newest_set_in_db.release_date:
                        mtg_set = MtgSet(name=card_set.name,
                                         release_date=release_date,
                                         block=card_set.block,
                                         set_type=card_set.type,
                                         gatherer_code=card_set.gatherer_code)
                        try:
                            mtg_set.add_set()
                        except ErrorRecordExists:
                            print("Set is already in db.")
                else:
                    mtg_set = MtgSet(name=card_set.name,
                                     release_date=release_date,
                                     block=card_set.block,
                                     set_type=card_set.type,
                                     gatherer_code=card_set.gatherer_code)
                    try:
                        mtg_set.add_set()
                    except ErrorRecordExists:
                        print("Set is already in db.")
        db.session.commit()
