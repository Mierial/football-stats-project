from django.core.management.base import BaseCommand
from api.services import sync_all_countries

class Command(BaseCommand):
    help = 'Синхронізація всіх країн (areas) з Football-Data API'

    def handle(self, *args, **options):
        self.stdout.write('Починаємо синхронізацію країн...')
        
        try:
            count = sync_all_countries()
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Успішно! Синхронізовано країн: {count}.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('API не повернуло країн або сталася помилка з отриманням даних.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Помилка під час синхронізації: {str(e)}')
            )