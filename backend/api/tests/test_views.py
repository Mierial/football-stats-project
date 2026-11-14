import pytest
from rest_framework.test import APIClient
from api.tests.conftest import create_match

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_exist_tournament_stats(client, tournament):
    response = client.get('/tournaments/1000/stats')

    assert response.status_code == 200
    assert 'goals_by_matchday' in response.data

@pytest.mark.django_db
def test_unexist_tournament_stats(client):
    response = client.get('/tournaments/1001/stats')

    assert response.status_code == 404

@pytest.mark.django_db
def test_delete_match_by_anon(client, tournament, home_team, away_team):
    create_match(1, tournament, home_team, away_team, 2, 2, matchday=1, status='SCHEDULED')

    response = client.delete('/matches/1/')

    assert response.status_code == 401