from django.core.management.base import BaseCommand
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Count total judges available in CourtListener API'

    def handle(self, *args, **options):
        api_key = getattr(settings, 'COURTLISTENER_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('CourtListener API key not configured'))
            return
        
        headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }
        
        url = "https://www.courtlistener.com/api/rest/v3/people/"
        params = {
            'type': 'judge',
            'limit': 1,  # Just get 1 result to see total count
            'offset': 0
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            total_count = data.get('count', 0)
            self.stdout.write(f'Total judges available: {total_count:,}')
            
            if total_count > 0:
                pages_needed = (total_count + 19) // 20  # 20 per batch
                estimated_time = pages_needed * 2 / 60  # 2 seconds per batch
                self.stdout.write(f'Pages needed (20 per batch): {pages_needed:,}')
                self.stdout.write(f'Estimated time: {estimated_time:.1f} minutes')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))