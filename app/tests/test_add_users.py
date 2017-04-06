
from app.models.model_user import User

user1 = User('User1', 'User1', 'user1@domain.com', 'heslo123')
user2 = User('User2', 'Fanda', 'user2@domain.com', '123')
user3 = User('User3', 'Karel', 'user3@domain.com', '54981')
user4 = User('User4', 'Nekdo', 'user4@domain.com', 'prd')
user5 = User('User5', 'Nikdo', 'user5@domain.com', 'heslo123')

users = [user1, user2, user3, user4, user5]


def test_correct_adding():
    for user in users:
        if user.check_collisions() is None:
            user.register()
    assert user1.nick == User.query.filter_by(nick='User1').first()
