from app.controlers import controller_tournament, controller_main, controller_user, controller_admin, controller_group,\
    controller_schedule

from app.config import db
from app.db_init import init_roles, create_super_admin_acc, init_mtg_sets, init_schedule_states_types, \
    init_tournament_states_types, init_group_roles, init_tournament_types


print("Inicializace")
db.create_all()
init_roles()
create_super_admin_acc()
#init_mtg_sets()
init_schedule_states_types()
init_tournament_states_types()
init_group_roles()
init_tournament_types()


