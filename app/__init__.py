from app.controlers import controler_tournament, controller_main, controller_user, controler_admin
from app.config import db
from app.db_init import init_roles, create_super_admin_acc, init_mtg_sets


print("Inicializace")
db.create_all()
init_roles()
create_super_admin_acc()
#init_mtg_sets()
