import requests

class FootballApiClient:
    BASE_URL = 'http://api.football-data.org/v4'

    def __init__(self, api_key):
        self.headers = {
            'X-Auth-Token': api_key
        }

    def _base_request(self, endpoint: str) -> dict | list[dict] | None:
        try:
            response = requests.get(
                url=f'{self.BASE_URL}/{endpoint}', 
                headers=self.headers, 
                timeout=5
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print("Час очікування вичерпано (більше 5 секунд)")
            return None       
        except requests.exceptions.RequestException as e:
            print(f'Error while connect to api: {e}')
            return None

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
    