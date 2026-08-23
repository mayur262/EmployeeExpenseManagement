from app.db import db

class ExpensePolicy(db.Model):
    __tablename__ = 'expense_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True, nullable=False) 
    max_limit_per_expense = db.Column(db.Numeric(10, 2), nullable=False)
    role_restriction = db.Column(db.String(50), nullable=True) 

    def __repr__(self):
        return f"<ExpensePolicy Category: {self.category}, Limit: {self.max_limit_per_expense}>"
