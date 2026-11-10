import logging

import requests

logger = logging.getLogger(__name__)


class FootballApiClient:
    BASE_URL = 'http://api.football-data.org/v4'

    def __init__(self, api_key):
        self.headers = {
            'X-Auth-Token': api_key
        }

    def _base_request(self, endpoint: str) -> dict | list[dict] | None:
        response = requests.get(
            url=f'{self.BASE_URL}/{endpoint}', 
            headers=self.headers, 
            timeout=5
            )
        if not response.ok:
            logger.warning("Football API %s: status %s", endpoint, response.status_code)
            response.raise_for_status()
        return response.json()

    def get_team(self, team_id: int) -> dict | None:
        return self._base_request(f"teams/{team_id}")

    def get_teams(self, league_code: str) -> dict | None:
         return self._base_request(f"competitions/{league_code}/teams")

    def get_match(self, match_id: int) -> dict | None:
            return self._base_request(f"matches/{match_id}")
    
    def get_matches(self, league_code: str) -> dict | None:
            return self._base_request(f"competitions/{league_code}/matches")
    
    def get_live_matches(self) -> dict | None:
         return self._base_request(f"matches")
    def get_areas(self) -> dict | None:
             return self._base_request(f"areas")

    def get_team_standings(self, tournament_id) -> list[dict] | None:
         return self._base_request(f"competitions/{tournament_id}/standings")

    def get_all_competitions(self) ->list[dict] | None:
         return self._base_request(f"competitions")
    