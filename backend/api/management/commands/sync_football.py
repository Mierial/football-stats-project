import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import TeamStats, Team, Tournament, Group, Country

leagues = ['BSA']

class Command(BaseCommand):
    help = "Synchronize a League teams standing from an external API"


    def handle(self, *args, **options):
        self.stdout.write('Start sync')
        for league in leagues:
            url = f"https://api.football-data.org/v4/competitions/{league}/standings?season=2026"
            headers = {
                'X-Auth-Token': settings.FOOTBALL_API_KEY
            }

            try:
                response = requests.get(url, headers=headers, timeout=5)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Error while connect to api: {e}"))
                return
            start_date = data.get('season').get('startDate')
            end_date = data.get('season').get('endDate')
            season_str=None
            if start_date:
                start_year = int(start_date[:4])
                season_str = f"{start_year}/{start_year+1}"
            country_obj, _ = Country.objects.update_or_create(
                external_id=data['area']['id'],
                defaults={
                        'name': data['area']['name'],
                        'flag': data['area']['flag']
                        })                                              
            tournament_obj, _ = Tournament.objects.update_or_create(
                external_id=data['competition']['id'],
                defaults={
                    'name': data['competition']['name'],
                    'image': data['competition']['emblem'],
                    'code': data['competition']['code'],
                    'country': country_obj,
                    'start_date': start_date,
                    'end_date': end_date,
                    'season': season_str,
                    'matchday':data.get('season').get('currentMatchday'),
                }
            )

            for standing in data['standings']:
                group_name = standing['group'] if standing['group'] else None
                group_obj, _ = Group.objects.update_or_create(
                    tournament=tournament_obj,
                    group_name=group_name,
                    defaults={}
                )

                for item in standing['table']:
                    team_obj, _ = Team.objects.update_or_create(
                        external_id=item['team']['id'],
                        defaults={
                            'name': item['team']['name'],
                            'image': item['team']['crest'],
                            'short_name': item['team']['shortName'],
                            'tla': item['team']['tla']
                        }
                    )
                    
                    TeamStats.objects.update_or_create(
                        team=team_obj,
                        group=group_obj,
                        defaults={
                            'place': item['position'],
                            'games_played': item['playedGames'],
                            'wins': item['won'],
                            'draws': item['draw'],
                            'losses': item['lost'],
                            'goals_for': item['goalsFor'],
                            'goals_against': item['goalsAgainst'],
                            'goal_difference': item['goalDifference'],
                            'points': item['points'],
                        }
                    )
        
        self.stdout.write(self.style.SUCCESS('Sync completed successfully!'))