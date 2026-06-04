"""
API Notification Resources
REST API endpoints for real-time notifications
"""

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from backend.models.notification import Notification
from backend.extensions import db
from datetime import datetime

class NotificationResource(Resource):
    """Resource for notifications management"""
    
    @jwt_required()
    def get(self):
        """
        Get user notifications
        ---
        tags:
          - Notifications
        security:
          - JWT: []
        parameters:
          - in: query
            name: unread_only
            type: boolean
            default: false
          - in: query
            name: limit
            type: integer
            default: 50
        responses:
          200:
            description: Notifications retrieved successfully
        """
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = request.args.get('limit', type=int, default=50)
        
        # Build query
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Get notifications
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        # Get unread count
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return {
            'success': True,
            'notifications': [notif.to_dict() for notif in notifications],
            'unread_count': unread_count,
            'total': len(notifications)
        }, 200
    
    @jwt_required()
    def patch(self):
        """
        Mark notifications as read
        ---
        tags:
          - Notifications
        security:
          - JWT: []
        parameters:
          - in: body
            name: notification_ids
            schema:
              type: object
              properties:
                notification_ids:
                  type: array
                  items:
                    type: integer
                mark_all:
                  type: boolean
        responses:
          200:
            description: Notifications marked as read
        """
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        mark_all = data.get('mark_all', False)
        notification_ids = data.get('notification_ids', [])
        
        if mark_all:
            # Mark all user's notifications as read
            Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Toutes les notifications ont été marquées comme lues'
            }, 200
        
        if not notification_ids:
            return {
                'success': False,
                'message': 'Aucun ID de notification fourni'
            }, 400
        
        # Mark specific notifications as read
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).all()
        
        for notif in notifications:
            notif.mark_as_read()
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'{len(notifications)} notification(s) marquée(s) comme lue(s)'
        }, 200
    
    @jwt_required()
    def delete(self):
        """
        Delete notifications
        ---
        tags:
          - Notifications
        security:
          - JWT: []
        parameters:
          - in: body
            name: notification_ids
            schema:
              type: object
              properties:
                notification_ids:
                  type: array
                  items:
                    type: integer
        responses:
          200:
            description: Notifications deleted
        """
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return {
                'success': False,
                'message': 'Aucun ID de notification fourni'
            }, 400
        
        # Delete specific notifications
        deleted = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'{deleted} notification(s) supprimée(s)'
        }, 200
