from models import User
from extensions import db

def get_users():
    """Fetch all users from the database using SQLAlchemy ORM"""
    users = User.query.all()
    
    return [
        {
            "id": user.id,
            "profile_picture": user.profile_picture,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "created_on": user.created_at.strftime("%d-%m-%Y %H:%M")  # Formatting datetime
        }
        for user in users
    ]
