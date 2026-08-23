from app.dao.user_dao import UserDAO, EmployeeDAO
from app.dao.policy_dao import ExpensePolicyDAO
from app.models.policy import ExpensePolicy
from app.models.user import User, Employee
from app.db import db

class AdminService:



    @staticmethod
    def get_all_users(page=None, per_page=10):
        return UserDAO.get_all(page=page, per_page=per_page)

    @staticmethod
    def get_user_by_id(user_id):
        return UserDAO.get_by_id(user_id)

    @staticmethod
    def update_user_role(user_id, new_role):
        allowed_roles = ("Employee", "Manager", "Finance", "Admin")
        if new_role not in allowed_roles:
            raise ValueError(f"Invalid role. Allowed: {', '.join(allowed_roles)}")
        user = UserDAO.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.role = new_role
        db.session.commit()
        return user

    @staticmethod
    def toggle_user_active(user_id):
        user = UserDAO.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.is_active = not user.is_active
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserDAO.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        UserDAO.delete(user)



    @staticmethod
    def get_all_policies(page=None, per_page=10):
        return ExpensePolicyDAO.get_all(page=page, per_page=per_page)

    @staticmethod
    def get_policy_by_id(policy_id):
        return ExpensePolicyDAO.get_by_id(policy_id)

    @staticmethod
    def create_or_update_policy(category, max_limit, role_restriction=None, policy_id=None):
        if not category or not category.strip():
            raise ValueError("Category cannot be empty.")
        try:
            max_limit = float(max_limit)
            if max_limit <= 0:
                raise ValueError("Limit must be positive.")
        except (TypeError, ValueError):
            raise ValueError("Max limit must be a positive number.")

        if policy_id:
            policy = ExpensePolicyDAO.get_by_id(policy_id)
            if not policy:
                raise ValueError("Policy not found.")
            policy.category = category.strip()
            policy.max_limit_per_expense = max_limit
            policy.role_restriction = role_restriction if role_restriction else None
        else:
            existing = ExpensePolicyDAO.get_by_category(category.strip())
            if existing:
                existing.max_limit_per_expense = max_limit
                existing.role_restriction = role_restriction if role_restriction else None
                db.session.commit()
                return existing
            policy = ExpensePolicy(
                category=category.strip(),
                max_limit_per_expense=max_limit,
                role_restriction=role_restriction if role_restriction else None
            )
            db.session.add(policy)

        db.session.commit()
        return policy

    @staticmethod
    def delete_policy(policy_id):
        policy = ExpensePolicyDAO.get_by_id(policy_id)
        if not policy:
            raise ValueError("Policy not found.")
        ExpensePolicyDAO.delete(policy)
