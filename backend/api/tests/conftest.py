import pytest
from api.models import Team, Tournament, TeamStats, Match
import pytest
from django.utils import timezone

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


@pytest.fixture 
def help_tournament():
    return Tournament.objects.create(
        external_id=1009,
        name='Ukrainian champ', 
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


