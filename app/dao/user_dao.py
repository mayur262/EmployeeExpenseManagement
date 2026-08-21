from app.dao.base_dao import BaseDAO
from app.models.user import User, Employee

class UserDAO(BaseDAO):
    model = User

    @classmethod
    def get_by_email(cls, email):
        return cls.model.query.filter_by(email=email).first()

class EmployeeDAO(BaseDAO):
    model = Employee

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.model.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_by_manager_id(cls, manager_id):
        return cls.model.query.filter_by(manager_id=manager_id).all()
