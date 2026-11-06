from django.core.management.base import BaseCommand

from ...services import sync_all_matches

leagues = ['PD', 'PL', 'FL1', 'CL', 'BL1']

class Command(BaseCommand):
    help = "Synchronize a matches schedule from an external API"
    def handle(self, *args, **options):
        self.stdout.write('Sync start')

        for league in leagues:
            self.stdout.write(f"Syncing league: {league}...")
            sync_all_matches(league)
        self.stdout.write('all mathces was synced')
