from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.controllers.auth_helper import login_required, current_user
from app.services.travel_service import TravelService
from app.dao.travel_dao import TravelDAO
from app.dao.user_dao import EmployeeDAO
from datetime import date

travel_bp = Blueprint('travel', __name__, url_prefix='/travel')

def _page_number():
    return max(request.args.get('page', 1, type=int), 1)

@travel_bp.route('/')
@login_required
def list_requests():
    if current_user.role not in ('Employee', 'Manager', 'Finance', 'Admin'):
        abort(403)
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not employee:
        flash('Employee profile not found. Contact admin.', 'danger')
        return redirect(url_for('auth.home'))
    requests = TravelDAO.get_by_employee_id(employee.id, page=_page_number())
    return render_template('travel/list.html', requests=requests)

@travel_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    if current_user.role != 'Employee':
        abort(403)

    if request.method == 'POST':
        destination = request.form.get('destination')
        start_date  = date.fromisoformat(request.form.get('start_date'))
        end_date    = date.fromisoformat(request.form.get('end_date'))
        purpose     = request.form.get('purpose')
        budget      = float(request.form.get('estimated_budget', 0))

        employee = EmployeeDAO.get_by_user_id(current_user.id)
        if not employee:
            flash('Employee profile not found.', 'danger')
            return redirect(url_for('auth.home'))

        try:
            TravelService.create_travel_request(
                employee_id=employee.id,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                purpose=purpose,
                estimated_budget=budget
            )
            flash('Travel request submitted successfully!', 'success')
            return redirect(url_for('travel.list_requests'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('travel/new.html')

@travel_bp.route('/<int:request_id>')
@login_required
def view_request(request_id):
    travel_req = TravelDAO.get_by_id(request_id)
    if not travel_req:
        abort(404)

    employee = EmployeeDAO.get_by_user_id(current_user.id)
   
    if current_user.role not in ('Finance', 'Admin', 'Manager'):
        if not employee or travel_req.employee_id != employee.id:
            abort(403)

    return render_template('travel/detail.html', travel_req=travel_req)
