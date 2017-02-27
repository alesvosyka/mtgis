import app.controller
from app.config import db
from app.db_init import init_privileges, create_super_admin_acc



print("Inicializace")
db.create_all()
init_privileges()
create_super_admin_acc()

