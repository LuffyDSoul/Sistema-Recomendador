"""
Configuración de Infraestructura
Carga variables de entorno para Supabase de forma nativa o con python-dotenv.
"""

import os
from dataclasses import dataclass


def _load_env_natively(filepath: str = ".env") -> None:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val


@dataclass(frozen=True)
class AppConfig:
    supabase_url: str
    supabase_key: str

    @classmethod
    def load(cls) -> "AppConfig":
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            _load_env_natively()

        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        key = os.getenv("SUPABASE_KEY", "")

        if not url or not key:
            raise ValueError(
                "Configuración incompleta: SUPABASE_URL y SUPABASE_KEY son requeridos en el archivo .env."
            )

        return cls(supabase_url=url, supabase_key=key)
