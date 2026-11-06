from celery import shared_task
import requests
from .services import sync_all_matches, sync_team_by_id, sync_match_info_by_id, sync_all_leagues_team_standings, sync_all_competitions

@shared_task
def sync_league_matches_task():
    sync_all_matches()

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_team_task(self, team_id: int):
    try:
        sync_team_by_id(team_id)
    except Exception as exc:
        raise self.retry(exc=exc)
    
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_match_info_task(self, match_id: int):
    try:
        sync_match_info_by_id(match_id)
    except requests.exceptions.RequestException as exc:
        raise self.retry(exc=exc)

@shared_task(max_retries=3, 
             default_retry_delay=60,
             autoretry_for=(requests.exceptions),
             retry_backoff=10,
             retry_backoff_max=100,
             )
def sync_all_leagues_team_standings_task():
    sync_all_leagues_team_standings(['CL', 'PL', 'ELC', 'PD', 'SA', 'BL1', 'FL1', 'DED', 'PPL'])



@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def sync_tournaments_info_task(self):
    try:
        sync_all_competitions()
    except Exception as exc:
       raise self.retry(exc=exc)
