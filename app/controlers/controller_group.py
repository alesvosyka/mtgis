from flask import request, render_template
from flask_login import current_user

from app.models.model_exceptions import ErrorRecordExists
from app.models.model_user import User

from app.models.model_group import Group, GroupMember

from app.config import app, db


@app.route('/create_group', methods=['POST', 'GET'])
def create_group():
    filter_ids = [current_user.id]
    users = User.get_all_users(filter_ids)
    return render_template('contents/groups/create_group.html', users=users)


@app.route('/edit_group/<int:group_id>', methods=['POST', 'GET'])
def edit_group(group_id):
    if request.method == 'POST':
        group = Group.query.get(group_id)
        if current_user.id == group.owner_id:
            group_members = group.get_members_without_owner()
            filter_ids = [current_user.id]
            for member in group_members:
                filter_ids.append(member.user.id)
            free_users = User.get_all_users(filter_ids)
            return render_template('contents/groups/edit_group.html',
                                   group=group,
                                   group_members=group_members,
                                   free_users=free_users)
    return render_template('contents/groups/group_info.html', group=group)


@app.route('/save_edited_group/<int:group_id>', methods=['POST', 'GET'])
def save_edited_group(group_id):
    group = Group.query.get(group_id)
    if request.method == 'POST':
        group.name = request.form['group_name']
        old_members = group.get_members_without_owner()
        member_ids = request.form.getlist('member')
        for member in old_members:
            if str(member.id) not in member_ids:
                member.delete_member()
        new_members_ids = request.form.getlist('user')
        for id in new_members_ids:
            membership = GroupMember(user_id=int(id), group_id=group.id)
            membership.add_group_member()
        db.session.commit()
    return render_template('contents/groups/group_info.html', group=group)


@app.route('/list_of_groups', methods=['POST', 'GET'])
def list_of_groups():
    groups = Group.query.all()
    return render_template('contents/groups/list_of_groups.html', groups=groups)


@app.route('/save_group', methods=['POST', 'GET'])
def save_group():
    if request.method == 'POST':
        group = Group(name=request.form['group_name'], owner_id=current_user.id)
        try:
            group = group.add_group()
        except ErrorRecordExists:
            users = User.get_all_users()
            return render_template('contents/groups/create_group.html', users=users, message="Jméno skupiny se již používá! Zadejte jiné.")

        group_members_ids = request.form.getlist('user')
        owner = GroupMember(user_id=current_user.id, group_id=group.id)
        try:
            owner = owner.add_group_member()
        except ErrorRecordExists:
            users = User.get_all_users()
            return render_template('contents/groups/create_group.html', users=users, message="Chyba přidání - vlastník této skupiny už existuje")

        owner.add_role_by_name(name="owner")

        for member_id in group_members_ids:
            new_member = GroupMember(user_id=member_id, group_id=group.id)
            try:
                new_member.add_group_member()
            except:
                pass
        return render_template('contents/groups/group_info.html', group=group)


@app.route('/group_info/<int:group_id>', methods=['POST', 'GET'])
def group_info(group_id):
    group = Group.query.get(group_id)
    return render_template('contents/groups/group_info.html', group=group)
