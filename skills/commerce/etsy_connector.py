"""Read-only Etsy OAuth 2.0 PKCE connector for RAMFAM Kingdom.

This module intentionally requests only shops_r and listings_r scopes. It does not
publish listings, edit shops/listings, message customers, delete data, or spend money.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, MutableMapping
from urllib import parse, request
from urllib.error import HTTPError, URLError

AUTHORIZATION_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
API_BASE_URL = "https://api.etsy.com/v3/application"
READ_ONLY_SCOPES = ("shops_r", "listings_r")
DEFAULT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class EtsyConnectorError(RuntimeError):
    """Base Etsy connector error."""


class EtsyConfigError(EtsyConnectorError):
    """Raised when required Etsy configuration is missing."""


class EtsyOAuthError(EtsyConnectorError):
    """Raised when Etsy OAuth/token/API calls fail."""


@dataclass(frozen=True)
class EtsyConfig:
    keystring: str
    shared_secret: str
    access_token: str | None = None
    refresh_token: str | None = None
    shop_id: str | None = None


def _strip_optional_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def read_dotenv(env_path: str | os.PathLike[str] | None = None) -> dict[str, str]:
    """Small .env reader so this connector does not require python-dotenv."""
    path = Path(env_path or DEFAULT_ENV_PATH)
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        values[key] = _strip_optional_quotes(value)
    return values


def load_etsy_config(env_path: str | os.PathLike[str] | None = None) -> EtsyConfig:
    """Load required Etsy OAuth values from environment and .env."""
    dotenv_values = read_dotenv(env_path)
    prefer_dotenv = env_path is not None
    if prefer_dotenv:
        keystring = dotenv_values.get("ETSY_KEYSTRING") or os.getenv("ETSY_KEYSTRING")
        shared_secret = dotenv_values.get("ETSY_SHARED_SECRET") or os.getenv("ETSY_SHARED_SECRET")
        access_token = dotenv_values.get("ETSY_ACCESS_TOKEN") or os.getenv("ETSY_ACCESS_TOKEN")
        refresh_token = dotenv_values.get("ETSY_REFRESH_TOKEN") or os.getenv("ETSY_REFRESH_TOKEN")
        shop_id = dotenv_values.get("ETSY_SHOP_ID") or os.getenv("ETSY_SHOP_ID")
    else:
        keystring = os.getenv("ETSY_KEYSTRING") or dotenv_values.get("ETSY_KEYSTRING")
        shared_secret = os.getenv("ETSY_SHARED_SECRET") or dotenv_values.get("ETSY_SHARED_SECRET")
        access_token = os.getenv("ETSY_ACCESS_TOKEN") or dotenv_values.get("ETSY_ACCESS_TOKEN")
        refresh_token = os.getenv("ETSY_REFRESH_TOKEN") or dotenv_values.get("ETSY_REFRESH_TOKEN")
        shop_id = os.getenv("ETSY_SHOP_ID") or dotenv_values.get("ETSY_SHOP_ID")

    missing = []
    if not keystring:
        missing.append("ETSY_KEYSTRING")
    if not shared_secret:
        missing.append("ETSY_SHARED_SECRET")
    if missing:
        raise EtsyConfigError(f"Missing required Etsy .env value(s): {', '.join(missing)}")

    return EtsyConfig(
        keystring=keystring,
        shared_secret=shared_secret,
        access_token=access_token,
        refresh_token=refresh_token,
        shop_id=shop_id,
    )


def pkce_s256_challenge(code_verifier: str) -> str:
    """Return RFC 7636 S256 code_challenge: base64url(sha256(verifier)) without padding."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def generate_code_verifier() -> str:
    """Generate a high-entropy PKCE code_verifier in the required 43-128 char range."""
    return secrets.token_urlsafe(64)[:128].rstrip("=")


def generate_pkce_pair() -> tuple[str, str]:
    verifier = generate_code_verifier()
    return verifier, pkce_s256_challenge(verifier)


def build_authorization_url(
    *,
    keystring: str,
    redirect_uri: str,
    code_verifier: str | None = None,
    state: str | None = None,
    scopes: tuple[str, ...] = READ_ONLY_SCOPES,
) -> tuple[str, str, str]:
    """Build Etsy's OAuth authorization URL and return (url, state, verifier)."""
    verifier = code_verifier or generate_code_verifier()
    oauth_state = state or secrets.token_urlsafe(32)
    query = {
        "response_type": "code",
        "client_id": keystring,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": oauth_state,
        "code_challenge": pkce_s256_challenge(verifier),
        "code_challenge_method": "S256",
    }
    return f"{AUTHORIZATION_URL}?{parse.urlencode(query)}", oauth_state, verifier


def _post_form(url: str, form: Mapping[str, str], headers: Mapping[str, str]) -> dict:
    data = parse.urlencode(form).encode("utf-8")
    req = request.Request(url, data=data, headers=dict(headers), method="POST")
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise EtsyOAuthError(f"Etsy token request failed with HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EtsyOAuthError(f"Etsy token request failed: {exc}") from exc


def _get_json(url: str, headers: Mapping[str, str]) -> dict:
    req = request.Request(url, headers=dict(headers), method="GET")
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise EtsyOAuthError(f"Etsy API read-only check failed with HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EtsyOAuthError(f"Etsy API read-only check failed: {exc}") from exc


def exchange_code_for_tokens(
    *,
    code: str,
    redirect_uri: str,
    code_verifier: str,
    keystring: str,
    post_form: Callable[[str, Mapping[str, str], Mapping[str, str]], dict] | None = None,
) -> dict:
    """Exchange an Etsy OAuth authorization code for tokens using PKCE."""
    if not code:
        raise EtsyOAuthError("Missing Etsy authorization code.")
    if not code_verifier:
        raise EtsyOAuthError("Missing Etsy PKCE code_verifier.")

    form = {
        "grant_type": "authorization_code",
        "client_id": keystring,
        "redirect_uri": redirect_uri,
        "code": code,
        "code_verifier": code_verifier,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    tokens = (post_form or _post_form)(TOKEN_URL, form, headers)
    if not tokens.get("access_token") or not tokens.get("refresh_token"):
        raise EtsyOAuthError("Etsy token response did not include both access_token and refresh_token.")
    return tokens


def refresh_access_token(
    *,
    refresh_token: str,
    keystring: str,
    post_form: Callable[[str, Mapping[str, str], Mapping[str, str]], dict] | None = None,
) -> dict:
    """Refresh Etsy OAuth tokens using the saved refresh token."""
    if not refresh_token:
        raise EtsyOAuthError("Missing Etsy refresh token. Visit /etsy/connect first.")

    form = {
        "grant_type": "refresh_token",
        "client_id": keystring,
        "refresh_token": refresh_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    tokens = (post_form or _post_form)(TOKEN_URL, form, headers)
    if not tokens.get("access_token") or not tokens.get("refresh_token"):
        raise EtsyOAuthError("Etsy refresh response did not include both access_token and refresh_token.")
    return tokens


def _quote_env_value(value: str) -> str:
    if value == "" or any(char.isspace() or char in {'"', "'", "#"} for char in value):
        return json.dumps(value)
    return value


def _set_env_lines(existing_text: str, updates: Mapping[str, str]) -> str:
    seen: set[str] = set()
    output: list[str] = []
    for raw_line in existing_text.splitlines():
        stripped = raw_line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                output.append(f"{key}={_quote_env_value(updates[key])}")
                seen.add(key)
                continue
        output.append(raw_line)

    for key, value in updates.items():
        if key not in seen:
            output.append(f"{key}={_quote_env_value(value)}")
    return "\n".join(output).rstrip() + "\n"


def save_tokens_safely(
    tokens: Mapping[str, str],
    *,
    env_path: str | os.PathLike[str] | None = None,
) -> dict[str, object]:
    """Atomically save Etsy tokens to .env and create a timestamped .env backup first."""
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if not access_token or not refresh_token:
        raise EtsyOAuthError("Cannot save Etsy tokens because access_token or refresh_token is missing.")

    path = Path(env_path or DEFAULT_ENV_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_text = path.read_text(encoding="utf-8") if path.exists() else ""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(f"{path.name}.backup_etsy_{timestamp}")
    backup_path.write_text(existing_text, encoding="utf-8")

    updated_text = _set_env_lines(
        existing_text,
        {
            "ETSY_ACCESS_TOKEN": access_token,
            "ETSY_REFRESH_TOKEN": refresh_token,
        },
    )

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temp_file:
        temp_file.write(updated_text)
        temp_name = temp_file.name

    os.replace(temp_name, path)
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    return {
        "saved": ["ETSY_ACCESS_TOKEN", "ETSY_REFRESH_TOKEN"],
        "env_path": str(path),
        "backup_path": str(backup_path),
    }


def _etsy_user_id_from_access_token(access_token: str) -> str:
    if "." not in access_token:
        raise EtsyOAuthError("Cannot determine Etsy user ID from access token prefix.")
    user_id = access_token.split(".", 1)[0]
    if not user_id:
        raise EtsyOAuthError("Cannot determine Etsy user ID from access token prefix.")
    return user_id


def verify_read_only_connection(
    *,
    keystring: str,
    shared_secret: str,
    access_token: str,
    shop_id: str | None = None,
    get_json: Callable[[str, Mapping[str, str]], dict] | None = None,
) -> dict:
    """Verify OAuth by reading the configured Etsy shop. Read-only only."""
    headers = {
        "x-api-key": f"{keystring}:{shared_secret}",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "User-Agent": "RAMFAM-KINGDOM-ATLAS",
    }

    if shop_id:
        url = f"{API_BASE_URL}/shops/{parse.quote(str(shop_id))}"
        shop = (get_json or _get_json)(url, headers)
        return {
            "connected": True,
            "scope": " ".join(READ_ONLY_SCOPES),
            "shop_count": 1,
            "shops": [shop],
        }

    user_id = _etsy_user_id_from_access_token(access_token)
    url = f"{API_BASE_URL}/users/{parse.quote(user_id)}/shops"
    payload = (get_json or _get_json)(url, headers)
    shops = payload.get("results") if isinstance(payload, MutableMapping) else None
    if shops is None:
        shops = payload.get("shops", []) if isinstance(payload, MutableMapping) else []
    return {
        "connected": True,
        "scope": " ".join(READ_ONLY_SCOPES),
        "shop_count": len(shops) if isinstance(shops, list) else payload.get("count", 0),
        "shops": shops,
    }


def run_read_only_connection_test(env_path: str | os.PathLike[str] | None = None) -> dict:
    """CLI/script helper for verifying the saved Etsy read-only OAuth connection."""
    config = load_etsy_config(env_path)
    if not config.access_token:
        raise EtsyConfigError("Missing ETSY_ACCESS_TOKEN. Visit /etsy/connect first.")
    return verify_read_only_connection(keystring=config.keystring, shared_secret=config.shared_secret, access_token=config.access_token, shop_id=config.shop_id)


if __name__ == "__main__":
    result = run_read_only_connection_test()
    safe_result = {
        "connected": result.get("connected", False),
        "scope": result.get("scope"),
        "shop_count": result.get("shop_count"),
        "shops": result.get("shops", []),
    }
    print(json.dumps(safe_result, indent=2))
