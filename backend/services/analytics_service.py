"""
Analytics service - Real data analytics from database
Provides real statistics for charts and dashboard
"""

from datetime import datetime, timedelta
from sqlalchemy import func, text
from backend.extensions import db
from backend.models.user import User
from backend.models.audit_log import AuditLog


class AnalyticsService:
    
    def get_daily_activity(self, days=7):
        """Get real daily activity (logins) for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query audit logs for login activities
        daily_logins = db.session.query(
            func.date(AuditLog.created_at).label('date'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= start_date,
            AuditLog.action.like('%login%')
        ).group_by(
            func.date(AuditLog.created_at)
        ).all()
        
        # Create a complete dataset for all days
        activity_data = []
        current_date = start_date.date()
        
        # Convert query results to dict for easy lookup
        login_dict = {result.date: result.count for result in daily_logins}
        
        day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        
        for i in range(days):
            date = current_date + timedelta(days=i)
            day_name = day_names[date.weekday()]
            count = login_dict.get(date, 0)
            
            activity_data.append({
                'label': day_name,
                'value': count,
                'date': date.isoformat()
            })
        
        return activity_data
    
    def get_monthly_registrations(self, months=6):
        """Get real monthly registrations for the last N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Query users created by month
        monthly_registrations = db.session.query(
            func.extract('year', User.created_at).label('year'),
            func.extract('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.extract('year', User.created_at),
            func.extract('month', User.created_at)
        ).order_by(
            func.extract('year', User.created_at),
            func.extract('month', User.created_at)
        ).all()
        
        # Create complete dataset
        registration_data = []
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                      'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        # Convert query results to dict
        reg_dict = {(int(r.year), int(r.month)): r.count for r in monthly_registrations}
        
        # Generate data for last N months
        current_date = end_date.replace(day=1)  # First day of current month
        
        for i in range(months):
            month_date = current_date - timedelta(days=i * 30)
            month_date = month_date.replace(day=1)  # Ensure first day of month
            
            year = month_date.year
            month = month_date.month
            count = reg_dict.get((year, month), 0)
            
            registration_data.insert(0, {
                'label': month_names[month - 1],
                'value': count,
                'year': year,
                'month': month
            })
        
        return registration_data
    
    def get_user_growth(self, days=30):
        """Get real user growth over the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get cumulative user count by day
        growth_data = []
        
        for i in range(days + 1):
            date = start_date + timedelta(days=i)
            
            # Count users created up to this date
            user_count = db.session.query(func.count(User.id)).filter(
                User.created_at <= date
            ).scalar()
            
            growth_data.append({
                'label': str(date.day),
                'value': user_count or 0,
                'date': date.isoformat()
            })
        
        return growth_data
    
    def get_user_status_distribution(self):
        """Get real user status distribution"""
        status_counts = db.session.query(
            User.statut,
            func.count(User.id).label('count')
        ).group_by(User.statut).all()
        
        status_labels = {
            'actif': 'Actifs',
            'desactive': 'Désactivés',
            'banni': 'Bannis',
            'en_attente': 'En attente'
        }
        
        distribution_data = []
        for status, count in status_counts:
            if count > 0:  # Only include statuses with users
                distribution_data.append({
                    'label': status_labels.get(status, status.title()),
                    'value': count
                })
        
        return distribution_data
    
    def get_recent_activity_stats(self):
        """Get recent activity statistics"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        this_week = today - timedelta(days=7)
        this_month = today - timedelta(days=30)
        
        stats = {}
        
        # Today's activity
        stats['today_logins'] = db.session.query(func.count(AuditLog.id)).filter(
            AuditLog.created_at >= today,
            AuditLog.action.like('%login%')
        ).scalar() or 0
        
        # This week's registrations
        stats['week_registrations'] = db.session.query(func.count(User.id)).filter(
            User.created_at >= this_week
        ).scalar() or 0
        
        # This month's registrations
        stats['month_registrations'] = db.session.query(func.count(User.id)).filter(
            User.created_at >= this_month
        ).scalar() or 0
        
        # Active users (logged in last 7 days)
        stats['active_users'] = db.session.query(func.count(func.distinct(AuditLog.target_id))).filter(
            AuditLog.created_at >= this_week,
            AuditLog.action.like('%login%')
        ).scalar() or 0
        
        return stats
    
    def get_all_analytics_data(self):
        """Get all analytics data for dashboard"""
        return {
            'daily_activity': self.get_daily_activity(),
            'monthly_registrations': self.get_monthly_registrations(),
            'user_growth': self.get_user_growth(),
            'status_distribution': self.get_user_status_distribution(),
            'recent_stats': self.get_recent_activity_stats()
        }


# Global instance
analytics_service = AnalyticsService()


def get_dashboard_analytics():
    """Get analytics data formatted for dashboard"""
    try:
        return analytics_service.get_all_analytics_data()
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        # Return empty data structure if there's an error
        return {
            'daily_activity': [],
            'monthly_registrations': [],
            'user_growth': [],
            'status_distribution': [],
            'recent_stats': {
                'today_logins': 0,
                'week_registrations': 0,
                'month_registrations': 0,
                'active_users': 0
            }
        }