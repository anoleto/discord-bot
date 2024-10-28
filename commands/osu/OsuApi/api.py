from __future__ import annotations

from typing import Optional
import requests
import config

class ApiClient:
    def __init__(self, server: str = config.Bancho):
        """API client for Bancho.py based osu! server."""
        self.server = server
        self.key = config.BanchoApiKey  # api key
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict) -> dict:
        response = self.session.get(f"https://api.{self.server}/v1/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def get_player_scores(self, scope: str, user_id: Optional[int] = None,
                          username: Optional[str] = None, mods_arg: Optional[str] = None,
                          mode_arg: Optional[int] = None) -> dict:
        params = {
            "name": username,
            "id": user_id,
            "mods": mods_arg,
            "mode": mode_arg,
            "scope": scope
        }
        
        return self._get("get_player_scores", {k: v for k, v in params.items() if v is not None})

    def get_map_info(self, map_id: Optional[int] = None, md5: Optional[str] = None) -> dict:
        params = {
            "id": map_id,
            "md5": md5
        }

        return self._get("get_map_info", {k: v for k, v in params.items() if v is not None})

    def get_player_info(self, scope: str, user_id: Optional[int] = None,
                        username: Optional[str] = None) -> dict:
        params = {
            "id": user_id,
            "name": username,
            "scope": scope,
        }

        return self._get("get_player_info", {k: v for k, v in params.items() if v is not None})