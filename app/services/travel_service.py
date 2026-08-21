from app.dao.travel_dao import TravelDAO
from app.models.travel import TravelRequest
from app.models.history import ApprovalHistory
from app.db import db
from datetime import datetime

class TravelService:
    @staticmethod
    def create_travel_request(employee_id, destination, start_date, end_date, purpose, estimated_budget):
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
            
        request = TravelRequest(
            employee_id=employee_id,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            purpose=purpose,
            estimated_budget=estimated_budget,
            status='Pending'
        )
        return TravelDAO.save(request)

    @staticmethod
    def approve_or_reject_travel_request(request_id, approver_user, action, comments=None):
        if action not in ['Approved', 'Rejected']:
            raise ValueError("Invalid action")
            
        request = TravelDAO.get_by_id(request_id)
        if not request:
            raise ValueError("Travel request not found")
            
        request.status = action
        
        
        history = ApprovalHistory(
            request_type='Travel',
            request_id=request_id,
            approver_id=approver_user.id,
            action=action,
            comments=comments
        )
        
        db.session.add(history)
        db.session.commit()
        return request
