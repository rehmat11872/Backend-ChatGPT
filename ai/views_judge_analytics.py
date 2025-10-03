from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Judge, Case
from .courtlistener_service import CourtListenerService
from .analytics_engine import JudgeAnalyticsEngine
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
@require_http_methods(["POST"])
def ingest_judge_data(request):
    """Ingest judge data from CourtListener API"""
    try:
        data = json.loads(request.body)
        limit = data.get('limit', 50)
        
        service = CourtListenerService()
        
        # Ingest judges
        judges_created = service.ingest_judge_data(limit=limit)
        
        # Link cases to judges
        cases_linked = service.link_cases_to_judges(limit=limit)
        
        return JsonResponse({
            'success': True,
            'judges_created': judges_created,
            'cases_linked': cases_linked,
            'message': f'Successfully ingested {judges_created} judges and linked {cases_linked} cases'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_judges_list(request):
    """Get list of judges with basic info"""
    try:
        judges = Judge.objects.all().order_by('name')
        
        judges_data = []
        for judge in judges:
            case_count = Case.objects.filter(judge=judge).count()
            judges_data.append({
                'id': str(judge.id),
                'name': judge.name,
                'court': judge.court,
                'jurisdiction': judge.jurisdiction,
                'case_count': case_count,
                'created_at': judge.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'judges': judges_data,
            'total_count': len(judges_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_judge_analytics(request, judge_id):
    """Get detailed analytics for a specific judge"""
    try:
        judge = Judge.objects.get(id=judge_id)
        analytics_engine = JudgeAnalyticsEngine()
        
        # Get comprehensive analytics
        analytics_data = analytics_engine.get_comprehensive_analytics(judge_id)
        
        return JsonResponse({
            'success': True,
            'judge': {
                'id': str(judge.id),
                'name': judge.name,
                'court': judge.court,
                'jurisdiction': judge.jurisdiction
            },
            'analytics': analytics_data
        })
        
    except Judge.DoesNotExist:
        return JsonResponse({'error': 'Judge not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_judges(request):
    """Search judges by name, court, or jurisdiction"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'error': 'Search query required'}, status=400)
        
        # Search across name, court, and jurisdiction
        judges = Judge.objects.filter(
            Q(name__icontains=query) |
            Q(court__icontains=query) |
            Q(jurisdiction__icontains=query)
        ).order_by('name')
        
        results = []
        for judge in judges:
            case_count = Case.objects.filter(judge=judge).count()
            results.append({
                'id': str(judge.id),
                'name': judge.name,
                'court': judge.court,
                'jurisdiction': judge.jurisdiction,
                'case_count': case_count
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_court_statistics(request):
    """Get statistics by court"""
    try:
        # Group judges by court
        court_stats = {}
        judges = Judge.objects.all()
        
        for judge in judges:
            court = judge.court
            if court not in court_stats:
                court_stats[court] = {
                    'judge_count': 0,
                    'total_cases': 0,
                    'judges': []
                }
            
            case_count = Case.objects.filter(judge=judge).count()
            court_stats[court]['judge_count'] += 1
            court_stats[court]['total_cases'] += case_count
            court_stats[court]['judges'].append({
                'id': str(judge.id),
                'name': judge.name,
                'case_count': case_count
            })
        
        # Convert to list format
        courts_list = []
        for court_name, stats in court_stats.items():
            courts_list.append({
                'court_name': court_name,
                'judge_count': stats['judge_count'],
                'total_cases': stats['total_cases'],
                'avg_cases_per_judge': round(stats['total_cases'] / stats['judge_count'], 2) if stats['judge_count'] > 0 else 0,
                'judges': stats['judges']
            })
        
        # Sort by total cases
        courts_list.sort(key=lambda x: x['total_cases'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'courts': courts_list,
            'total_courts': len(courts_list)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_court_comparison(request, court_name):
    """Get comparison analytics for judges in a specific court"""
    try:
        analytics_engine = JudgeAnalyticsEngine()
        comparison_data = analytics_engine.get_court_comparison(court_name)
        
        return JsonResponse({
            'success': True,
            'comparison': comparison_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)