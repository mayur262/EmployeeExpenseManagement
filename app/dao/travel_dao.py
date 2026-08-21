from app.dao.base_dao import BaseDAO
from app.models.travel import TravelRequest
from app.models.user import Employee

class TravelDAO(BaseDAO):
    model = TravelRequest

    @classmethod
    def get_by_employee_id(cls, employee_id):
        return cls.model.query.filter_by(employee_id=employee_id).order_by(TravelRequest.created_at.desc()).all()

    @classmethod
    def get_pending_by_manager_id(cls, manager_id):
        return cls.model.query.join(Employee).filter(
            Employee.manager_id == manager_id,
            TravelRequest.status == 'Pending'
        ).order_by(TravelRequest.created_at.desc()).all()
