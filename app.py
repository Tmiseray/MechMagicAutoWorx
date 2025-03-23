
from app import create_app
from app.models import db


app = create_app('DevelopmentConfig')

with app.app_context():
    
    # db.drop_all()
    # print("Database dropped!")

    db.create_all()
    print("Database created!")


app.run()