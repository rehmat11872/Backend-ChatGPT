import requests
from django.conf import settings
from .models import Judge, Case
import logging

logger = logging.getLogger(__name__)

class CourtListenerService:
    BASE_URL = "https://www.courtlistener.com/api/rest/v3"
    
    def __init__(self):
        self.api_key = getattr(settings, 'COURTLISTENER_API_KEY', None)
        if not self.api_key:
            raise ValueError("CourtListener API key not configured")
        
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_judges(self, limit=100, offset=0):
        """Fetch judges from CourtListener API"""
        url = f"{self.BASE_URL}/people/"
        params = {
            'type': 'judge',
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching judges: {e}")
            return None
    
    def get_judge_by_id(self, judge_id):
        """Fetch specific judge by ID"""
        url = f"{self.BASE_URL}/people/{judge_id}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching judge {judge_id}: {e}")
            return None
    
    def get_opinions(self, judge_id=None, limit=100, offset=0):
        """Fetch court opinions, optionally filtered by judge"""
        url = f"{self.BASE_URL}/opinions/"
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if judge_id:
            params['author'] = judge_id
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching opinions: {e}")
            return None
    
    def get_dockets(self, judge_id=None, limit=100, offset=0):
        """Fetch docket data, optionally filtered by judge"""
        url = f"{self.BASE_URL}/dockets/"
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if judge_id:
            params['assigned_to'] = judge_id
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dockets: {e}")
            return None
    
    def ingest_judge_data(self, limit=50):
        """Ingest judge data and store in database"""
        judges_data = self.get_judges(limit=limit)
        if not judges_data:
            return 0
        
        created_count = 0
        for judge_info in judges_data.get('results', []):
            try:
                # Extract judge information
                judge_id = judge_info.get('id')
                name = f"{judge_info.get('name_first', '')} {judge_info.get('name_last', '')}".strip()
                
                # For now, use simple court info since positions are URLs
                court = "Unknown Court"
                jurisdiction = "Unknown Jurisdiction"
                
                # Create or update judge record
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
                    logger.info(f"Created judge: {name} ({court})")
                
            except Exception as e:
                logger.error(f"Error processing judge {judge_info.get('id')}: {e}")
                continue
        
        return created_count
    
    def ingest_all_judges(self):
        """Ingest ALL judge data with pagination"""
        created_count = 0
        offset = 0
        page_size = 20  # Smaller batches to avoid rate limits
        
        while True:
            judges_data = self.get_judges(limit=page_size, offset=offset)
            if not judges_data:
                break
            
            results = judges_data.get('results', [])
            if not results:
                break
            
            # Process this batch
            for judge_info in results:
                try:
                    judge_id = judge_info.get('id')
                    name = f"{judge_info.get('name_first', '')} {judge_info.get('name_last', '')}".strip()
                    
                    court = "Unknown Court"
                    jurisdiction = "Unknown Jurisdiction"
                    
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
                        logger.info(f"Created judge: {name} ({court})")
                    
                except Exception as e:
                    logger.error(f"Error processing judge {judge_info.get('id')}: {e}")
                    continue
            
            # Check if there are more pages
            if not judges_data.get('next'):
                break
            
            offset += page_size
            logger.info(f"Processed {offset} judges so far...")
            
            # Add delay to avoid rate limiting
            import time
            time.sleep(2)
        
        return created_count
    
    def link_cases_to_judges(self, limit=50):
        """Link cases to judges using docket and opinion data"""
        # Get dockets with assigned judges
        dockets_data = self.get_dockets(limit=limit)
        if not dockets_data:
            return 0
        
        linked_count = 0
        for docket in dockets_data.get('results', []):
            try:
                assigned_to = docket.get('assigned_to')
                if not assigned_to:
                    continue
                
                judge_id = assigned_to.get('id') if isinstance(assigned_to, dict) else assigned_to
                
                # Check if judge exists in our database
                try:
                    judge = Judge.objects.get(id=judge_id)
                except Judge.DoesNotExist:
                    continue
                
                # Create case record
                case_number = docket.get('docket_number', 'Unknown')
                case_title = docket.get('case_name', 'Unknown Case')
                
                case, created = Case.objects.get_or_create(
                    case_number=case_number,
                    defaults={
                        'title': case_title,
                        'judge': judge,
                        'organization': None  # Will be set when org system is implemented
                    }
                )
                
                if created:
                    linked_count += 1
                    logger.info(f"Linked case {case_number} to judge {judge.name}")
                
            except Exception as e:
                logger.error(f"Error linking case: {e}")
                continue
        
        return linked_count
    
    def link_all_cases_to_judges(self):
        """Link ALL cases to judges with pagination"""
        linked_count = 0
        offset = 0
        page_size = 20  # Smaller batches to avoid rate limits
        
        while True:
            dockets_data = self.get_dockets(limit=page_size, offset=offset)
            if not dockets_data:
                break
            
            results = dockets_data.get('results', [])
            if not results:
                break
            
            # Process this batch
            for docket in results:
                try:
                    assigned_to = docket.get('assigned_to')
                    if not assigned_to:
                        continue
                    
                    judge_id = assigned_to.get('id') if isinstance(assigned_to, dict) else assigned_to
                    
                    try:
                        judge = Judge.objects.get(id=judge_id)
                    except Judge.DoesNotExist:
                        continue
                    
                    case_number = docket.get('docket_number', 'Unknown')
                    case_title = docket.get('case_name', 'Unknown Case')
                    
                    case, created = Case.objects.get_or_create(
                        case_number=case_number,
                        defaults={
                            'title': case_title,
                            'judge': judge,
                            'organization': None
                        }
                    )
                    
                    if created:
                        linked_count += 1
                        logger.info(f"Linked case {case_number} to judge {judge.name}")
                    
                except Exception as e:
                    logger.error(f"Error linking case: {e}")
                    continue
            
            # Check if there are more pages
            if not dockets_data.get('next'):
                break
            
            offset += page_size
            logger.info(f"Processed {offset} dockets so far...")
            
            # Add delay to avoid rate limiting
            import time
            time.sleep(2)
        
        return linked_count