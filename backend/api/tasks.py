from celery import shared_task
from django.utils import timezone
import requests

from api.models import Match
from core import settings
from .services import sync_team_by_id, sync_match_info_by_id, sync_team_standings, sync_all_competitions, sync_live_matches, sync_league_data

@shared_task(
        bind=True,
        max_retries=3,
        default_retry_delay=60,
        autoretry_for=(
            requests.exceptions.Timeout, 
            requests.exceptions.ConnectionError),
        retry_backoff=60,
)
def sync_league_data_task(self, league):
    try:
        sync_league_data(league)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code in (429, 500, 502, 503, 504):
            raise self.retry(exc=exc)
        raise
    
@shared_task
def sync_all_leagues_data_task():
    for league in settings.API_TOURNAMENTS:
        sync_league_data_task.delay(league)

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

@shared_task(
        bind=True,
        max_retries=3, 
        default_retry_delay=60,
        autoretry_for=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        retry_backoff=60,
)
def sync_team_standings_task(self, code):
    try:
        sync_team_standings(code)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code in (429, 500, 502, 503, 504):
            raise self.retry(exc=exc)
        raise 

@shared_task
def sync_all_leagues_team_standings_task():
    for code in settings.API_TOURNAMENTS:
        sync_team_standings_task.delay(code)


@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def sync_tournaments_info_task(self):
    try:
        sync_all_competitions()
    except Exception as exc:
       raise self.retry(exc=exc)


@shared_task(
        ignore_result=True, 
        soft_time_limit=30, 
        time_limit=40,
        autoretry_for=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_retries=1,
        default_retry_delay=30,
)        
def sync_live_matches_task():
    has_live_matches = Match.objects.filter(
        status__in=['IN_PLAY', 'PAUSED'],
    ).exists() or Match.objects.filter(
        status__in=['SCHEDULED', 'TIMED'],
        date__lte=timezone.now(),
    ).exists()

    if not has_live_matches:
        return
    
    sync_live_matches()