from django.utils import timezone
from api.services import get_tournament_stats
from api.models import Match
import pytest
from api.tests.conftest import create_match


@pytest.mark.django_db
def test_stats_for_tournament_with_matches(tournament, home_team, away_team):
    create_match(1, tournament, home_team, away_team, 2, 1, matchday=1)
    create_match(2, tournament, home_team, away_team, 2, 2, matchday=2)
    create_match(3, tournament, away_team, home_team, 2, 1, matchday=3)

    stats = get_tournament_stats(tournament)

    assert stats['matches'] == 3
    assert stats['home_wins_count'] == 2
    assert stats['total_goals'] == 10
    assert stats['draws_count'] == 1 
    assert stats['max_goals_in_match'] == 4


@pytest.mark.django_db
def test_stats_ignore_not_finished_matches(tournament, home_team, away_team):
    create_match(1, tournament, home_team, away_team, 2, 2, matchday=1, status='SCHEDULED')
    create_match(2, tournament, home_team, away_team, 5, 0, matchday=2, status='FINISHED')

    stats = get_tournament_stats(tournament)
    assert stats['matches'] == 1
    assert stats['total_goals'] == 5

@pytest.mark.django_db

def test_top_teams_sum_home_and_away_goals(tournament, home_team, away_team):
    create_match(1, tournament, home_team, away_team, 6, 2, matchday=1, status='FINISHED')
    create_match(2, tournament, away_team, home_team, 2, 3, matchday=2, status='FINISHED')

    stats = get_tournament_stats(tournament)

    assert stats['top_teams_by_goals'][0]['goals'] == 9 and stats['top_teams_by_goals'][0]['team'] == 'Dynamo'
    assert stats['top_teams_by_goals'][1]['goals'] == 4 and stats['top_teams_by_goals'][1]['team'] == 'Shakhtar'
    
@pytest.mark.django_db
def test_stats_in_different_leagues(tournament, help_tournament, home_team, away_team):
    create_match(1, tournament, home_team, away_team, 3, 2, matchday=1, status='FINISHED')
    create_match(2, help_tournament, home_team, away_team, 4, 3, matchday=2, status='FINISHED')
    stats = get_tournament_stats(tournament)


    assert stats['matches'] == 1
    assert stats['total_goals'] == 5
    assert stats['max_goals_in_match'] == 5
