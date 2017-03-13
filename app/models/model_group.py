from app.config import db
from app.models.model_exceptions import ErrorRecordExists, ErrorRecordNotExists
from app.models.model_user import User


class TypeOfGroupRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class GroupRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_of_group_role_id = db.Column(db.Integer, db.ForeignKey("type_of_group_role.id"))
    member_id = db.Column(db.Integer, db.ForeignKey("group_member.id"))

    def __init__(self, id=None, type_of_group_role_id=None, member_id=None):
        self.id = id
        self.type_of_group_role_id = type_of_group_role_id
        self.member_id = member_id



    @property
    def role_name(self):
        role = TypeOfGroupRole.query.filter_by(id=self.type_of_group_role_id).first()
        if role is None:
            return None
        else:
            return role.name


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    member_group_roles = db.relationship('GroupRole')


    @property
    def user(self):
        return User.query.get(self.user_id)

    def __init__(self, id=None, user_id=None, group_id=None):
        self.id = id
        self.group_id = group_id
        self.user_id = user_id

    def add_role_by_name(self, name=None):
        type_role = TypeOfGroupRole.query.filter_by(name=name).first()
        if type_role is None:
            raise ErrorRecordNotExists('')
        role = GroupRole(type_of_group_role_id=type_role.id, member_id=self.id)
        try:
            db.session.add(role)
            db.session.commit()
        except:
            return None
        return GroupRole.query.filter_by(member_id=self.id).first()

    def add_group_member(self):
        if GroupMember.query.filter_by(user_id=self.user_id, group_id=self.group_id).first() is None:
            db.session.add(self)
            db.session.commit()
            return GroupMember.query.filter_by(user_id=self.user_id, group_id=self.group_id).first()
        else:
            raise ErrorRecordExists("")

    def delete_member(self):
        db.session.delete(self)
        db.session.commit()


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    group_members = db.relationship('GroupMember', backref="group")

    def __init__(self, id=None, name=None, owner_id=None):
        self.name = name
        self.id = id
        self.owner_id = owner_id

    @property
    def owner(self):
        return User.query.get(self.owner_id)

    def get_members_without_owner(self):
        return GroupMember.query.filter(GroupMember.user_id != self.owner_id, GroupMember.group_id == self.id).all()

    def get_all_members(self):
        return GroupMember.query.filter(GroupMember.group_id == self.id).all()


    @staticmethod
    def get_editable_groups(user_id=None):
        members = GroupMember.query.filter_by(user_id=user_id).all()
        groups = []
        for member in members:
            print(member.user.nick_name)
            for role in member.member_group_roles:
                print(role.role_name)
                if role.role_name == 'owner' or role.role_name == 'group_admin':
                    groups.append(Group.query.get(member.group.id))
        return groups

    def add_group(self):
        if Group.query.filter_by(name=self.name).first() is None:
            db.session.add(self)
            db.session.commit()
            return Group.query.filter_by(name=self.name).first()
        else:
            raise ErrorRecordExists("")
