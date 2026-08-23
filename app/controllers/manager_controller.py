from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.controllers.auth_helper import login_required, current_user
from app.controllers.auth_decorator import role_required
from app.dao.user_dao import EmployeeDAO
from app.dao.travel_dao import TravelDAO
from app.dao.expense_dao import ExpenseClaimDAO
from app.services.travel_service import TravelService
from app.services.expense_service import ExpenseService
from app.db import db

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

def _page_number(name):
    return max(request.args.get(name, 1, type=int), 1)

@manager_bp.route('/')
@login_required
@role_required('Manager')
def dashboard():
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not employee:
        flash('Manager profile not found.', 'danger')
        return redirect(url_for('auth.home'))
        
    pending_travel = TravelDAO.get_pending_by_manager_id(employee.id, page=_page_number('travel_page'))
    pending_expenses = ExpenseClaimDAO.get_pending_by_manager_id(employee.id, page=_page_number('expense_page'))
    
    return render_template(
        'manager/dashboard.html',
        pending_travel=pending_travel,
        pending_expenses=pending_expenses
    )

@manager_bp.route('/travel/<int:request_id>')
@login_required
@role_required('Manager')
def view_travel(request_id):
    req = TravelDAO.get_by_id(request_id)
    if not req:
        abort(404)
        
    manager_employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not manager_employee or req.employee.manager_id != manager_employee.id:
        abort(403)
        
    return render_template('manager/view_travel.html', req=req)

@manager_bp.route('/travel/<int:request_id>/action', methods=['POST'])
@login_required
@role_required('Manager')
def approve_travel(request_id):
    req = TravelDAO.get_by_id(request_id)
    if not req:
        abort(404)
        
    manager_employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not manager_employee or req.employee.manager_id != manager_employee.id:
        abort(403)
        
    action = request.form.get('action') 
    comments = request.form.get('comments')
    
    if action not in ['Approved', 'Rejected']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('manager.view_travel', request_id=request_id))
        
    try:
        TravelService.approve_or_reject_travel_request(
            request_id=request_id,
            approver_user=current_user,
            action=action,
            comments=comments
        )
        flash(f'Travel request has been {action.lower()} successfully!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/expense/<int:claim_id>')
@login_required
@role_required('Manager')
def view_expense(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    manager_employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not manager_employee or claim.employee.manager_id != manager_employee.id:
        abort(403)
        
    return render_template('manager/view_expense.html', claim=claim)

@manager_bp.route('/expense/<int:claim_id>/action', methods=['POST'])
@login_required
@role_required('Manager')
def approve_expense(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    manager_employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not manager_employee or claim.employee.manager_id != manager_employee.id:
        abort(403)
        
    action = request.form.get('action') 
    comments = request.form.get('comments')
    
    if action not in ['Approved', 'Rejected']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('manager.view_expense', claim_id=claim_id))
        
    try:
        ExpenseService.approve_or_reject_claim(
            claim_id=claim_id,
            approver_user=current_user,
            action=action,
            comments=comments
        )
        flash(f'Expense claim has been {action.lower()} successfully!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('manager.dashboard'))
