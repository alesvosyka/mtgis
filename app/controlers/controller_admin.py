from flask import request, render_template
from flask_login import current_user

from app.models.model_exceptions import ErrorRecordExists
from app.models.model_user import User, TypeOfRole
from app.models.model_turnament import Tournament, Player
from app.models.model_mtg import MtgSet

from app.config import app, db

from datetime import datetime


@app.route('/management_user', methods=['POST', 'GET'])
def management_user():
    if request.method == 'GET':
        all_users = User.query.filter(User.nick_name != "superadmin").all()
        role_types = TypeOfRole.query.all()
        role_types_dict = dict([(r.name, r.id) for r in role_types])

        return render_template('contents/admin/users_management.html', all_users=all_users, role_types=role_types_dict)


@app.route('/edit_user_roles/<int:user_id>', methods=['POST', 'GET'])
def edit_user_roles(user_id):
    if request.method == 'POST':
        user = User.query.get(user_id)
        user.delete_roles()
        role_types = TypeOfRole.query.all()
        role_types_dict = dict([(r.name, r.id) for r in role_types])

        role_type_ids = request.form.getlist('role_type_id')
        for role_type_id in role_type_ids:
            user.add_role(role_type_id)

        all_users = User.query.filter(User.nick_name != "superadmin").all()
        return render_template('contents/admin/users_management.html', all_users=all_users, role_types=role_types_dict)
