"""Read-only Meta Graph API connector for Atlas.

This module validates Meta configuration and reads connection status only. It does
not publish posts, send messages, modify pages, spend money, or expose tokens.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping
from urllib import parse, request
from urllib.error import HTTPError, URLError

GRAPH_API_VERSION = "v20.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
DEFAULT_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
REQUIRED_META_KEYS = (
    "META_APP_ID",
    "META_APP_SECRET",
    "META_USER_ACCESS_TOKEN",
    "META_PAGE_ID",
    "META_PAGE_ACCESS_TOKEN",
)
OPTIONAL_META_KEYS = ("THREADS_APP_ID",)


class MetaConnectorError(RuntimeError):
    """Base Meta connector error."""


class MetaConfigError(MetaConnectorError):
    """Raised when required Meta configuration is missing."""


class MetaApiError(MetaConnectorError):
    """Raised when a Meta API read-only check fails."""


@dataclass(frozen=True)
class MetaConfig:
    app_id: str
    app_secret: str
    user_access_token: str
    page_id: str
    page_access_token: str
    threads_app_id: str = ""


def _strip_optional_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def read_dotenv(env_path: str | os.PathLike[str] | None = None) -> dict[str, str]:
    """Small .env reader so Meta status does not require python-dotenv."""
    path = Path(env_path or DEFAULT_ENV_PATH)
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        values[key] = _strip_optional_quotes(value)
    return values


def load_meta_config(env_path: str | os.PathLike[str] | None = None) -> MetaConfig:
    """Load Meta values from .env first, then process environment."""
    dotenv_values = read_dotenv(env_path)

    def value_for(key: str) -> str:
        return (dotenv_values.get(key) or os.getenv(key) or "").strip()

    missing = [key for key in REQUIRED_META_KEYS if not value_for(key)]
    if missing:
        raise MetaConfigError(f"Missing required Meta .env value(s): {', '.join(missing)}")

    return MetaConfig(
        app_id=value_for("META_APP_ID"),
        app_secret=value_for("META_APP_SECRET"),
        user_access_token=value_for("META_USER_ACCESS_TOKEN"),
        page_id=value_for("META_PAGE_ID"),
        page_access_token=value_for("META_PAGE_ACCESS_TOKEN"),
        threads_app_id=value_for("THREADS_APP_ID"),
    )


def missing_meta_config(env_path: str | os.PathLike[str] | None = None) -> list[str]:
    dotenv_values = read_dotenv(env_path)
    return [
        key
        for key in (*REQUIRED_META_KEYS, *OPTIONAL_META_KEYS)
        if not (dotenv_values.get(key) or os.getenv(key) or "").strip()
    ]


def mask_identifier(value: str) -> str:
    """Mask a non-secret identifier for dashboard display."""
    if not value:
        return "missing"
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * max(4, len(value) - 4) + value[-4:]


def _sanitize_detail(detail: str, config: MetaConfig | None = None) -> str:
    sanitized = detail
    if config:
        for secret in (config.app_secret, config.user_access_token, config.page_access_token):
            if secret:
                sanitized = sanitized.replace(secret, "[REDACTED]")
    return sanitized


def _graph_get_json(path: str, params: Mapping[str, str]) -> dict:
    query = parse.urlencode(params)
    url = f"{GRAPH_API_BASE_URL}{path}?{query}"
    req = request.Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise MetaApiError(f"Meta Graph API returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MetaApiError(f"Meta Graph API connection failed: {exc}") from exc


def _log_meta_status(lines: list[tuple[str, str]]) -> None:
    print("META CONNECT")
    for label, status in lines:
        print(f"{label} .... {status}")


def _base_status(status: str, last_check: str) -> dict:
    return {
        "status": status,
        "page": "Not configured",
        "page_id": "missing",
        "page_id_masked": "missing",
        "profile_picture": "",
        "instagram": "unknown",
        "threads": "not_configured",
        "last_check": last_check,
    }


def get_meta_status(
    env_path: str | os.PathLike[str] | None = None,
    get_json: Callable[[str, Mapping[str, str]], dict] | None = None,
) -> dict:
    """Return a safe Meta connection status payload for Atlas Mission Control."""
    last_check = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    getter = get_json or _graph_get_json

    try:
        config = load_meta_config(env_path)
    except MetaConfigError:
        missing = missing_meta_config(env_path)
        threads_status = "configured" if "THREADS_APP_ID" not in missing else "not_configured"
        _log_meta_status([
            ("App Config", "FAIL"),
            ("User Token", "SKIPPED"),
            ("Page", "SKIPPED"),
            ("Instagram", "UNKNOWN"),
            ("Threads", threads_status.upper()),
        ])
        status = _base_status("not_configured", last_check)
        status["threads"] = threads_status
        status["missing_config"] = missing
        return status

    try:
        user_response = getter("/me", {
            "fields": "id,name",
            "access_token": config.user_access_token,
        })
        if not user_response.get("id"):
            raise MetaApiError("User token validation did not return an id.")

        page_response = getter(f"/{config.page_id}", {
            "fields": "id,name,picture{url},instagram_business_account{id,username}",
            "access_token": config.page_access_token,
        })
        page_name = page_response.get("name") or "Configured Page"
        returned_page_id = str(page_response.get("id") or config.page_id)
        picture = page_response.get("picture") or {}
        picture_url = ""
        if isinstance(picture, dict):
            picture_data = picture.get("data") or {}
            if isinstance(picture_data, dict):
                picture_url = picture_data.get("url") or ""
        instagram_account = page_response.get("instagram_business_account")
        instagram_status = "connected" if instagram_account else "not_connected"
        threads_status = "configured" if config.threads_app_id else "not_configured"

        _log_meta_status([
            ("App Config", "PASS"),
            ("User Token", "VALID"),
            ("Page", "CONNECTED"),
            ("Instagram", "CONNECTED" if instagram_account else "NONE"),
            ("Threads", "CONFIGURED" if config.threads_app_id else "NOT CONFIGURED"),
        ])

        return {
            "status": "connected",
            "page": page_name,
            "page_id": "configured",
            "page_id_masked": mask_identifier(returned_page_id),
            "profile_picture": picture_url,
            "instagram": instagram_status,
            "threads": threads_status,
            "last_check": last_check,
        }
    except MetaConnectorError as exc:
        safe_error = _sanitize_detail(str(exc), config)
        _log_meta_status([
            ("App Config", "PASS"),
            ("User Token", "CHECK"),
            ("Page", "CHECK"),
            ("Instagram", "UNKNOWN"),
            ("Threads", "CONFIGURED" if config.threads_app_id else "NOT CONFIGURED"),
        ])
        status = _base_status("error", last_check)
        status.update({
            "page_id": "configured" if config.page_id else "missing",
            "page_id_masked": mask_identifier(config.page_id),
            "threads": "configured" if config.threads_app_id else "not_configured",
            "error": safe_error,
        })
        return status
