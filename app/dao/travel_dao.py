from app.dao.base_dao import BaseDAO
from app.models.travel import TravelRequest
from app.models.user import Employee

class TravelDAO(BaseDAO):
    model = TravelRequest

    @classmethod
    def get_by_employee_id(cls, employee_id, page=None, per_page=10):
        query = cls.model.query.filter_by(employee_id=employee_id).order_by(TravelRequest.created_at.desc())
        return query.all() if page is None else query.paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def get_pending_by_manager_id(cls, manager_id, page=None, per_page=10):
        query = cls.model.query.join(Employee).filter(
            Employee.manager_id == manager_id,
            TravelRequest.status == 'Pending'
        ).order_by(TravelRequest.created_at.desc())
        return query.all() if page is None else query.paginate(page=page, per_page=per_page, error_out=False)
