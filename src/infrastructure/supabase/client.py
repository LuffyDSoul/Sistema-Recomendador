"""
Cliente HTTP Nativo de Supabase (Infraestructura)
Permite interactuar con la API PostgREST sin dependencias de terceros.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = f"{base_url}/rest/v1"
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def select(self, table: str, query_params: str = "select=*") -> List[Dict[str, Any]]:
        url = f"{self.base_url}/{table}?{query_params}"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Error HTTP en SELECT a '{table}': {e.code} - {err_body}")
            raise

    def insert(self, table: str, data: List[Dict[str, Any]], upsert: bool = False) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/{table}"
        headers = self.headers.copy()
        if upsert:
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Error HTTP en INSERT a '{table}': {e.code} - {err_body}")
            raise

    def delete(self, table: str, query_params: str) -> None:
        url = f"{self.base_url}/{table}?{query_params}"
        req = urllib.request.Request(url, headers=self.headers, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Error HTTP en DELETE a '{table}': {e.code} - {err_body}")
            raise
