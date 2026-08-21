import os
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from app.controllers.auth_helper import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.expense_service import ExpenseService
from app.dao.expense_dao import ExpenseClaimDAO, ExpenseItemDAO, ExpenseReceiptDAO
from app.dao.user_dao import EmployeeDAO
from app.dao.travel_dao import TravelDAO
from app.db import db

expense_bp = Blueprint('expense', __name__, url_prefix='/expense')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@expense_bp.route('/')
@login_required
def list_claims():
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not employee:
        flash('Employee profile not found.', 'danger')
        return redirect(url_for('auth.home'))
    
    if current_user.role == 'Employee':
        claims = ExpenseClaimDAO.get_by_employee_id(employee.id)
    else:

        claims = ExpenseClaimDAO.get_all()
        
    return render_template('expense/list.html', claims=claims)

@expense_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_claim():
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if not employee:
        flash('Employee profile not found.', 'danger')
        return redirect(url_for('auth.home'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        travel_request_id = request.form.get('travel_request_id')
        
        if not travel_request_id or travel_request_id == '':
            travel_request_id = None
        else:
            travel_request_id = int(travel_request_id)
            
        try:
            claim = ExpenseService.create_expense_claim(
                employee_id=employee.id,
                title=title,
                description=description,
                travel_request_id=travel_request_id
            )
            flash('Expense claim created successfully as a Draft. Add items below.', 'success')
            return redirect(url_for('expense.view_claim', claim_id=claim.id))
        except Exception as e:
            flash(str(e), 'danger')
            
    travel_requests = TravelDAO.get_by_employee_id(employee.id)
    return render_template('expense/new.html', travel_requests=travel_requests)

@expense_bp.route('/<int:claim_id>', methods=['GET'])
@login_required
def view_claim(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if current_user.role == 'Employee':
        if not employee or claim.employee_id != employee.id:
            abort(403)
            
    return render_template('expense/detail.html', claim=claim)

@expense_bp.route('/<int:claim_id>/item', methods=['POST'])
@login_required
def add_item(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if claim.employee_id != employee.id:
        abort(403)
        
    category = request.form.get('category')
    amount = float(request.form.get('amount', 0))
    expense_date = date.fromisoformat(request.form.get('expense_date'))
    description = request.form.get('description')
    
    try:
        ExpenseService.add_expense_item(
            claim_id=claim_id,
            category=category,
            amount=amount,
            expense_date=expense_date,
            description=description
        )
        flash('Line item added successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('expense.view_claim', claim_id=claim_id))

@expense_bp.route('/<int:claim_id>/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(claim_id, item_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if claim.employee_id != employee.id:
        abort(403)
        
    if claim.status != 'Draft':
        flash('Cannot delete items from a submitted or approved claim.', 'danger')
        return redirect(url_for('expense.view_claim', claim_id=claim_id))
        
    item = db.session.get(ExpenseItemDAO.model, item_id)
    if item and item.expense_claim_id == claim_id:
        db.session.delete(item)
        db.session.commit()
        claim.update_total_amount()
        flash('Line item deleted.', 'success')
    else:
        flash('Item not found.', 'danger')
        
    return redirect(url_for('expense.view_claim', claim_id=claim_id))

@expense_bp.route('/<int:claim_id>/receipt', methods=['POST'])
@login_required
def upload_receipt(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if claim.employee_id != employee.id:
        abort(403)
        
    if claim.status != 'Draft':
        flash('Cannot add receipts to a submitted or approved claim.', 'danger')
        return redirect(url_for('expense.view_claim', claim_id=claim_id))
        
    if 'receipt_file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('expense.view_claim', claim_id=claim_id))
        
    file = request.files['receipt_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('expense.view_claim', claim_id=claim_id))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        file_type = file.mimetype or 'application/octet-stream'
        
        try:
            ExpenseService.attach_receipt(
                claim_id=claim_id,
                filename=filename,
                filepath=filepath,
                file_type=file_type,
                file_size=file_size
            )
            flash('Receipt uploaded successfully.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
    else:
        flash('Invalid file type. Allowed formats: PDF, PNG, JPG, JPEG.', 'danger')
        
    return redirect(url_for('expense.view_claim', claim_id=claim_id))

@expense_bp.route('/<int:claim_id>/receipt/<int:receipt_id>/delete', methods=['POST'])
@login_required
def delete_receipt(claim_id, receipt_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if claim.employee_id != employee.id:
        abort(403)
        
    if claim.status != 'Draft':
        flash('Cannot delete receipts from a submitted or approved claim.', 'danger')
        return redirect(url_for('expense.view_claim', claim_id=claim_id))
        
    receipt = db.session.get(ExpenseReceiptDAO.model, receipt_id)
    if receipt and receipt.expense_claim_id == claim_id:
        try:
            if os.path.exists(receipt.filepath):
                os.remove(receipt.filepath)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete receipt file: {e}")
            
        db.session.delete(receipt)
        db.session.commit()
        flash('Receipt deleted.', 'success')
    else:
        flash('Receipt not found.', 'danger')
        
    return redirect(url_for('expense.view_claim', claim_id=claim_id))

@expense_bp.route('/<int:claim_id>/submit', methods=['POST'])
@login_required
def submit_claim(claim_id):
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)
        
    employee = EmployeeDAO.get_by_user_id(current_user.id)
    if claim.employee_id != employee.id:
        abort(403)
        
    try:
        ExpenseService.submit_claim(claim_id)
        flash('Expense claim submitted successfully for approval!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('expense.view_claim', claim_id=claim_id))
