from django.core.management.base import BaseCommand
from ai.models import Judge, Case
import random

class Command(BaseCommand):
    help = 'Create test cases for judges to demonstrate analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--judge-id',
            type=str,
            help='Judge ID to create cases for'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of test cases to create (default: 10)'
        )

    def handle(self, *args, **options):
        judge_id = options.get('judge_id')
        count = options['count']
        
        if judge_id:
            try:
                judge = Judge.objects.get(id=judge_id)
            except Judge.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Judge with ID {judge_id} not found'))
                return
        else:
            # Use first available judge
            judge = Judge.objects.first()
            if not judge:
                self.stdout.write(self.style.ERROR('No judges found'))
                return
        
        self.stdout.write(f'Creating {count} test cases for {judge.name}...')
        
        case_types = ['Civil Rights', 'Contract Dispute', 'Employment', 'Personal Injury', 'Criminal Defense']
        outcomes = ['Granted', 'Denied', 'Dismissed', 'Pending']
        
        created_count = 0
        for i in range(count):
            case_type = random.choice(case_types)
            outcome = random.choice(outcomes)
            
            case = Case.objects.create(
                title=f"{case_type} Case #{i+1}",
                case_number=f"CASE-{judge.id}-{i+1:03d}",
                judge=judge,
                outcome=outcome,
                organization=None
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test cases for {judge.name}'
            )
        )