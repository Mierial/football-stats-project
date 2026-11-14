from django.utils import timezone
import pytest
from api.models import Team, Tournament, TeamStats, Match
from api.services import get_tournament_stats

@pytest.fixture
def home_team():
    return Team.objects.create(external_id=1, name='Dynamo')


@pytest.fixture
def away_team():
    return Team.objects.create(external_id=2, name='Shakhtar')

@pytest.fixture 
def tournament():
    return Tournament.objects.create(
        external_id=1000,
        name='Ukrainian champpions football', 
        season='2026/2027', 
        image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRSqT7bv126qhmsVIaT-AAz-iGgh5sQauwmxgQvsIVfiw&s',
        code='ucfl',
        )

def create_match(external_id, tournament, home_team, away_team, home_goals, away_goals, matchday, status='FINISHED'):
    return Match.objects.create(
        external_id=external_id,
        tournament=tournament,
        home_team=home_team,
        away_team=away_team,
        home_goals=home_goals,
        away_goals=away_goals,
        matchday=matchday,
        status=status,
        date=timezone.now(),
    )

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

