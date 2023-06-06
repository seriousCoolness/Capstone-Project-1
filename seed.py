from models import Users, db
from app import app

app.app_context().push()
db.drop_all()
db.create_all()

Users.query.delete()

test_user = Users.signup('caldw3ll', 'caldw3ll')

db.session.commit()