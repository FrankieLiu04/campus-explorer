import os
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union, List


def _get_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_csv(value: Optional[str]) -> Union[List[str], str]:
    if value is None:
        return ["http://localhost:3000"]
    cleaned = value.strip()
    if cleaned == "*":
        return "*"
    items = [v.strip() for v in cleaned.split(",")]
    return [v for v in items if v]


def load_config(*, instance_path: str) -> dict:
    env = os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    debug = _get_bool(os.getenv("FLASK_DEBUG"), default=(env == "development"))

    secret_key = os.getenv("SECRET_KEY")
    jwt_secret_key = os.getenv("JWT_SECRET_KEY") or secret_key

    if not secret_key:
        if debug:
            secret_key = os.urandom(32).hex()
        else:
            raise RuntimeError("SECRET_KEY is required in non-development environments")

    if not jwt_secret_key:
        if debug:
            jwt_secret_key = os.urandom(32).hex()
        else:
            raise RuntimeError("JWT_SECRET_KEY is required in non-development environments")

    instance_dir = Path(instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)
    db_path = instance_dir / "app.db"

    max_upload_mb = _get_int(os.getenv("MAX_UPLOAD_MB"), default=5)
    access_token_days = _get_int(os.getenv("JWT_ACCESS_TOKEN_DAYS"), default=7)

    return {
        "ENV": env,
        "DEBUG": debug,
        "SECRET_KEY": secret_key,
        "JWT_SECRET_KEY": jwt_secret_key,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path.as_posix()}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "MAX_CONTENT_LENGTH": max_upload_mb * 1024 * 1024,
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(days=access_token_days),
        "CORS_ORIGINS": _get_csv(os.getenv("CORS_ORIGINS")),
        "SOCKETIO_CORS_ORIGINS": _get_csv(os.getenv("SOCKETIO_CORS_ORIGINS") or os.getenv("CORS_ORIGINS")),
        "TRUST_PROXY_HEADERS": _get_bool(os.getenv("TRUST_PROXY_HEADERS"), default=False),
    }
