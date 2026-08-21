import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file
from app.controllers.auth_helper import login_required, current_user
from app.controllers.auth_decorator import role_required
from app.dao.expense_dao import ExpenseClaimDAO, ExpenseReceiptDAO
from app.services.expense_service import ExpenseService

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')


@finance_bp.route('/')
@login_required
@role_required('Finance')
def dashboard():
    
    status_filter = request.args.get('status', '').strip() or None
    if status_filter not in (None, 'Approved', 'Verified'):
        status_filter = None

    claims = ExpenseClaimDAO.get_all_for_finance(status_filter=status_filter)

    return render_template(
        'finance/dashboard.html',
        claims=claims,
        current_filter=status_filter or 'All'
    )


@finance_bp.route('/claim/<int:claim_id>')
@login_required
@role_required('Finance')
def view_claim(claim_id):
    
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)

    if claim.status not in ('Approved', 'Verified'):
        flash('This claim is not yet approved by the manager and cannot be reviewed by Finance.', 'danger')
        return redirect(url_for('finance.dashboard'))

    return render_template('finance/view_claim.html', claim=claim)


@finance_bp.route('/receipt/<int:receipt_id>/download')
@login_required
@role_required('Finance')
def download_receipt(receipt_id):
    
    receipt = ExpenseReceiptDAO.get_by_id(receipt_id)
    if not receipt:
        abort(404)

    if not os.path.exists(receipt.filepath):
        flash('Receipt file not found on server.', 'danger')
        return redirect(url_for('finance.dashboard'))

    return send_file(
        receipt.filepath,
        mimetype=receipt.file_type,
        as_attachment=True,
        download_name=receipt.filename
    )


@finance_bp.route('/claim/<int:claim_id>/reimburse', methods=['POST'])
@login_required
@role_required('Finance')
def reimburse_claim(claim_id):
   
    claim = ExpenseClaimDAO.get_by_id(claim_id)
    if not claim:
        abort(404)

    if claim.status != 'Approved':
        flash('Only manager-approved claims can be marked as reimbursed.', 'danger')
        return redirect(url_for('finance.view_claim', claim_id=claim_id))

    transaction_reference = request.form.get('transaction_reference', '').strip() or None

    try:
        ExpenseService.verify_and_reimburse(
            claim_id=claim_id,
            finance_user=current_user,
            transaction_reference=transaction_reference
        )
        flash(
            f'Expense claim "{claim.title}" has been verified and marked as reimbursed successfully!',
            'success'
        )
    except Exception as e:
        flash(str(e), 'danger')

    return redirect(url_for('finance.dashboard'))
