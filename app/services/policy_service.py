from app.dao.policy_dao import ExpensePolicyDAO
from app.models.policy import ExpensePolicy
from app.db import db

class PolicyService:
    @staticmethod
    def create_policy(category, max_limit, role_restriction=None):
        policy = ExpensePolicyDAO.get_by_category(category)
        if policy:
            policy.max_limit_per_expense = max_limit
            policy.role_restriction = role_restriction
        else:
            policy = ExpensePolicy(
                category=category,
                max_limit_per_expense=max_limit,
                role_restriction=role_restriction
            )
            db.session.add(policy)
        db.session.commit()
        return policy

    @staticmethod
    def is_compliant(category, amount, role=None):
        policy = ExpensePolicyDAO.get_by_category(category)
        if not policy:
            return True, None
            
        if amount > policy.max_limit_per_expense:
            return False, f"Exceeds policy limit of {policy.max_limit_per_expense} for category {category}."
        return True, None
