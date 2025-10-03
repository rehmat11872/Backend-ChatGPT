from django.core.management.base import BaseCommand
import requests
from ai.models import Judge
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetch judges with rich court data from CourtListener'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Number of judges to fetch (default: all available)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fetch all available judges (ignores limit)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        fetch_all = options['all'] or limit is None
        
        api_key = getattr(settings, 'COURTLISTENER_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('CourtListener API key not configured'))
            return
        
        headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }
        
        if fetch_all:
            self.stdout.write('Fetching ALL judges with rich data...')
        else:
            self.stdout.write(f'Fetching {limit} judges with rich data...')
        
        # Fetch judges with pagination
        url = "https://www.courtlistener.com/api/rest/v3/people/"
        all_judges = []
        offset = 0
        page_size = 20  # Smaller batches to avoid rate limits
        
        while True:
            params = {
                'type': 'judge',
                'limit': page_size,
                'offset': offset
            }
        
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                judges_data = response.json()
                
                results = judges_data.get('results', [])
                if not results:
                    break
                
                all_judges.extend(results)
                self.stdout.write(f'Fetched {len(all_judges)} judges so far...')
                
                # Check if we should continue
                if not fetch_all and limit and len(all_judges) >= limit:
                    all_judges = all_judges[:limit]
                    break
                
                # Check if there are more pages
                if not judges_data.get('next'):
                    break
                
                offset += page_size
                
                # Add delay to avoid rate limiting
                import time
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching page at offset {offset}: {e}'))
                break
        
        self.stdout.write(f'Processing {len(all_judges)} judges...')
        
        try:
            created_count = 0
            updated_count = 0
            
            for judge_info in all_judges:
                judge_id = judge_info.get('id')
                name = f"{judge_info.get('name_first', '')} {judge_info.get('name_last', '')}".strip()
                
                # Get position data for court info
                court = "Unknown Court"
                jurisdiction = "Unknown Jurisdiction"
                
                positions = judge_info.get('positions', [])
                if positions:
                    # Fetch the first position URL to get court details
                    position_url = positions[0] if isinstance(positions[0], str) else None
                    if position_url:
                        try:
                            pos_response = requests.get(position_url, headers=headers)
                            if pos_response.status_code == 200:
                                pos_data = pos_response.json()
                                court_info = pos_data.get('court', {})
                                if court_info:
                                    # Fetch court details
                                    court_url = court_info if isinstance(court_info, str) else court_info.get('resource_uri')
                                    if court_url:
                                        court_response = requests.get(court_url, headers=headers)
                                        if court_response.status_code == 200:
                                            court_data = court_response.json()
                                            court = court_data.get('full_name', court_data.get('short_name', 'Unknown Court'))
                                            jurisdiction = court_data.get('jurisdiction', 'Unknown Jurisdiction')
                        except Exception as e:
                            self.stdout.write(f"Error fetching position data for {name}: {e}")
                
                # Create or update judge
                judge, created = Judge.objects.get_or_create(
                    id=judge_id,
                    defaults={
                        'name': name,
                        'court': court,
                        'jurisdiction': jurisdiction
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created: {name} - {court}")
                else:
                    # Update existing judge with rich data
                    judge.court = court
                    judge.jurisdiction = jurisdiction
                    judge.save()
                    updated_count += 1
                    self.stdout.write(f"Updated: {name} - {court}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {created_count} new judges and updated {updated_count} existing judges'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing judges: {e}'))