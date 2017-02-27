from app.config import db
from mtgsdk import set


class MtgSets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    owner_id = db.Column(db.Integer)