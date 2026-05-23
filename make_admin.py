from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='akshaye214@gmail.com').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print('Admin role assigned!')
    else:
        print('User not found!')