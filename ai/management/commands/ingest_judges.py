from django.core.management.base import BaseCommand
# from ai.courtlistener_service import CourtListenerService  # Disabled

class Command(BaseCommand):
    help = 'Ingest judge data from CourtListener API'

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
        
        if fetch_all:
            self.stdout.write('Starting judge data ingestion (fetching ALL judges)...')
        else:
            self.stdout.write(f'Starting judge data ingestion (limit: {limit})...')
        
        try:
            service = CourtListenerService()
            
            # Ingest judges
            self.stdout.write('Fetching judges from CourtListener API...')
            if fetch_all:
                judges_created = service.ingest_all_judges()
            else:
                judges_created = service.ingest_judge_data(limit=limit)
            
            # Link cases to judges
            self.stdout.write('Linking cases to judges...')
            if fetch_all:
                cases_linked = service.link_all_cases_to_judges()
            else:
                cases_linked = service.link_cases_to_judges(limit=limit)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully ingested {judges_created} judges and linked {cases_linked} cases'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during ingestion: {str(e)}')
            )