from app.dao.user_dao import UserDAO, EmployeeDAO
from app.models.user import User, Employee
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    @staticmethod
    def register_user(email, password, role, first_name, last_name, department, designation, phone=None, manager_id=None):
        existing_user = UserDAO.get_by_email(email)
        if existing_user:
            raise ValueError("Email already exists")
            
        password_hash = generate_password_hash(password)
        new_user = User(email=email, password_hash=password_hash, role=role)
        

        db.session.add(new_user)
        db.session.flush() # populated user.id
        
        new_employee = Employee(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            department=department,
            designation=designation,
            phone=phone,
            manager_id=manager_id
        )
        
        db.session.add(new_employee)
        db.session.commit()
        return new_user

    @staticmethod
    def authenticate_user(email, password):
        user = UserDAO.get_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
