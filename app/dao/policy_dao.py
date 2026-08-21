from app.dao.base_dao import BaseDAO
from app.models.policy import ExpensePolicy

class ExpensePolicyDAO(BaseDAO):
    model = ExpensePolicy

    @classmethod
    def get_by_category(cls, category):
        return cls.model.query.filter_by(category=category).first()
