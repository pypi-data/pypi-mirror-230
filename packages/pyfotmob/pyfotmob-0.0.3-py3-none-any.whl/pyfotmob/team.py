from services.data import handle_league_match_player_team


class Team:
    BASE_URL = "https://www.fotmob.com/api/teams"

    def __init__(self, id_team: int):
        self.id = id_team

    def get(self, key: str = None) -> dict:
        return handle_league_match_player_team(
            entity='team',
            url=f"{Team.BASE_URL}?id={self.id}",
            id=self.id,
            key=key
        )
