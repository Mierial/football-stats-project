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
@pytest.mark.django_db
def test_request_count_in_mathces(client, home_team, away_team, tournament, django_assert_num_queries):
    create_match(1, tournament, home_team, away_team, 2, 2, matchday=1, status='SCHEDULED')
    create_match(2, tournament, home_team, away_team, 2, 2, matchday=1, status='SCHEDULED')
    create_match(3, tournament, home_team, away_team, 2, 2, matchday=1, status='SCHEDULED')

    with django_assert_num_queries(4):
        response = client.get(f'/matches/')
    assert response.status_code == 200
    