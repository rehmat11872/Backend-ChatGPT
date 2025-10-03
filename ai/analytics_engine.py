from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Judge, Case
import random

class JudgeAnalyticsEngine:
    """Analytics engine for judge behavior analysis"""
    
    def calculate_ruling_tendencies(self, judge_id):
        """Calculate ruling tendencies for a judge"""
        judge = Judge.objects.get(id=judge_id)
        cases = Case.objects.filter(judge=judge)
        
        total_cases = cases.count()
        if total_cases == 0:
            return {
                'total_cases': 0,
                'granted_rate': 0,
                'denied_rate': 0,
                'dismissed_rate': 0,
                'pending_rate': 0
            }
        
        # Simulate outcomes for demo (in real implementation, use actual case outcomes)
        granted = random.randint(int(total_cases * 0.3), int(total_cases * 0.7))
        denied = random.randint(int(total_cases * 0.1), int(total_cases * 0.4))
        dismissed = random.randint(0, int(total_cases * 0.2))
        pending = total_cases - granted - denied - dismissed
        
        return {
            'total_cases': total_cases,
            'granted': granted,
            'denied': denied,
            'dismissed': dismissed,
            'pending': max(0, pending),
            'granted_rate': round((granted / total_cases) * 100, 2),
            'denied_rate': round((denied / total_cases) * 100, 2),
            'dismissed_rate': round((dismissed / total_cases) * 100, 2),
            'pending_rate': round((max(0, pending) / total_cases) * 100, 2)
        }
    
    def calculate_time_to_decision(self, judge_id):
        """Calculate average time to decision for a judge"""
        judge = Judge.objects.get(id=judge_id)
        cases = Case.objects.filter(judge=judge)
        
        # Simulate timing data for demo
        case_count = cases.count()
        if case_count == 0:
            return {
                'avg_days': 0,
                'fastest_decision': 0,
                'slowest_decision': 0,
                'median_days': 0
            }
        
        # Generate realistic timing data
        avg_days = random.randint(30, 180)
        fastest = random.randint(5, 30)
        slowest = random.randint(200, 500)
        median = random.randint(25, 150)
        
        return {
            'avg_days': avg_days,
            'fastest_decision': fastest,
            'slowest_decision': slowest,
            'median_days': median,
            'case_count': case_count
        }
    
    def calculate_party_win_rates(self, judge_id):
        """Calculate win rates by party type"""
        judge = Judge.objects.get(id=judge_id)
        cases = Case.objects.filter(judge=judge)
        
        total_cases = cases.count()
        if total_cases == 0:
            return {
                'government_wins': 0,
                'private_wins': 0,
                'civil_wins': 0,
                'criminal_wins': 0
            }
        
        # Simulate party win rates for demo
        return {
            'government_wins': random.randint(40, 70),
            'private_wins': random.randint(30, 60),
            'civil_plaintiff_wins': random.randint(35, 65),
            'civil_defendant_wins': random.randint(35, 65),
            'prosecution_wins': random.randint(60, 85),
            'defense_wins': random.randint(15, 40)
        }
    
    def get_recent_activity(self, judge_id, days=30):
        """Get recent case activity for a judge"""
        judge = Judge.objects.get(id=judge_id)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_cases = Case.objects.filter(
            judge=judge,
            created_at__gte=cutoff_date
        ).order_by('-created_at')
        
        return {
            'recent_cases_count': recent_cases.count(),
            'cases': [
                {
                    'id': str(case.id),
                    'title': case.title,
                    'case_number': case.case_number,
                    'outcome': case.outcome or 'Pending',
                    'created_at': case.created_at.isoformat()
                }
                for case in recent_cases[:10]
            ]
        }
    
    def get_case_type_distribution(self, judge_id):
        """Get distribution of case types for a judge"""
        judge = Judge.objects.get(id=judge_id)
        cases = Case.objects.filter(judge=judge)
        
        total_cases = cases.count()
        if total_cases == 0:
            return {}
        
        # Simulate case type distribution
        civil_count = random.randint(int(total_cases * 0.3), int(total_cases * 0.6))
        criminal_count = random.randint(int(total_cases * 0.2), int(total_cases * 0.5))
        motion_count = random.randint(int(total_cases * 0.1), int(total_cases * 0.3))
        other_count = max(0, total_cases - civil_count - criminal_count - motion_count)
        
        return {
            'civil': {
                'count': civil_count,
                'percentage': round((civil_count / total_cases) * 100, 2)
            },
            'criminal': {
                'count': criminal_count,
                'percentage': round((criminal_count / total_cases) * 100, 2)
            },
            'motion': {
                'count': motion_count,
                'percentage': round((motion_count / total_cases) * 100, 2)
            },
            'other': {
                'count': other_count,
                'percentage': round((other_count / total_cases) * 100, 2)
            }
        }
    
    def get_comprehensive_analytics(self, judge_id):
        """Get comprehensive analytics for a judge"""
        return {
            'ruling_tendencies': self.calculate_ruling_tendencies(judge_id),
            'timing_analysis': self.calculate_time_to_decision(judge_id),
            'party_win_rates': self.calculate_party_win_rates(judge_id),
            'recent_activity': self.get_recent_activity(judge_id),
            'case_type_distribution': self.get_case_type_distribution(judge_id)
        }
    
    def get_court_comparison(self, court_name):
        """Get comparison analytics for judges in the same court"""
        judges_in_court = Judge.objects.filter(court=court_name)
        
        comparison_data = []
        for judge in judges_in_court:
            case_count = Case.objects.filter(judge=judge).count()
            ruling_data = self.calculate_ruling_tendencies(judge.id)
            
            comparison_data.append({
                'judge_id': str(judge.id),
                'judge_name': judge.name,
                'total_cases': case_count,
                'granted_rate': ruling_data['granted_rate'],
                'avg_decision_time': self.calculate_time_to_decision(judge.id)['avg_days']
            })
        
        return {
            'court_name': court_name,
            'judges_count': len(comparison_data),
            'judges': comparison_data
        }