from flask import Flask, request, jsonify, redirect, send_from_directory, session
from functools import wraps
from agents.atlas_orchestrated_response import atlas_orchestrated_response
from agents.atlas_orchestrator import atlas_orchestrator
from atlas_os import executive_bus
from werkzeug.utils import secure_filename
from agents.assistant import ask_puter
from agents.atlas_delegation_router import atlas_delegate
from skills.atlas_revenue_council import atlas_revenue_council
from atlas_intent_router import route_intent
from skills.atlas_skill import show_missions
from atlas_hermes_bridge import ask_hermes
from skills.micah_deliverable import generate_micah_deliverables
from skills.amanda_deliverable import generate_amanda_deliverables
from skills.david_deliverable import generate_david_deliverables

from skills.atlas_brain import (
    alfred_daily_briefing_ai,
    alfred_run_the_kingdom_ai,
    atlas_kingdom_brain_status,
    atlas_consult_kingdom_brain
)

from skills.hunter_brain import (
    hunter_where_is_the_money_ai,
    hunter_rank_opportunities_ai,
    hunter_fastest_path_to_cash_ai
)

from skills.hunter_maps_skill import (
    hunter_maps_report,
    hunter_show_maps_targets,
    hunter_add_maps_target,
    hunter_rank_maps_targets,
    hunter_maps_summary,
    hunter_send_maps_target_to_amanda
)

from skills.mason_skill import (
    mason_report,
    mason_next_build,
    mason_construction_log,
    mason_inspect_kingdom,
    mason_project_blueprint,
    mason_active_projects,
    mason_planned_projects,
    mason_completed_projects,
    mason_create_project,
    mason_start_project,
    mason_test_project,
    mason_complete_project,
    mason_inspect_project,
    mason_launch_revenue_campaign,
    mason_next_project_recommendation,
    mason_revenue_recommendation,
    mason_bottleneck_report,
    mason_build_today_mission,
    mason_recommend_next_build_live
)

from skills.hunter_skill import (
    hunter_report,
    hunter_money_due,
    hunter_website_leads,
    hunter_commission_opportunities,
    hunter_show_leads,
    hunter_lead_report,
    hunter_add_lead,
    hunter_remove_lead,
    hunter_update_lead_status,
    hunter_send_lead_to_amanda,
    hunter_show_pipeline,
    hunter_add_to_pipeline,
    hunter_update_pipeline_stage,
    hunter_pipeline_report
)

from skills.scout_skill import (
    scout_report,
    scout_show_targets,
    scout_add_target,
    scout_opportunity_report,
    scout_show_opportunities,
    scout_add_opportunity,
    scout_send_opportunity_to_hunter
)

from skills.amanda_outreach_skill import (
    amanda_show_outreach_queue,
    amanda_add_outreach,
    amanda_complete_outreach,
    amanda_outreach_report
)

from skills.mason_hermes_skill import mason_ask_hermes
from skills.commerce import etsy_connector
from skills.meta_connector import get_meta_status

import os
import json
import secrets
from datetime import datetime
from html import escape
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY") or os.urandom(32)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ETSY_ENV_PATH = os.path.join(BASE_DIR, ".env")
ETSY_OAUTH_PENDING_PATH = os.path.join(BASE_DIR, "mason_workspace", "etsy_oauth_pending.json")
UI_DIR = os.path.join(BASE_DIR, "ui")
ASSETS_DIR = os.path.join(UI_DIR, "assets")
SIS_WEBSITE_DIR = os.path.join(BASE_DIR, "sis-website")
QTIME_CLIENT_DIR = os.path.join(BASE_DIR, "CLIENTS", "QTIME PRODUCTIONS")
HISTORY_FILE = os.path.join(BASE_DIR, "logs", "conversation.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
UPLOAD_CATEGORIES = {
    "docs": {"pdf", "doc", "docx", "txt", "rtf", "csv", "xlsx", "xls", "ppt", "pptx"},
    "images": {"png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "tif", "tiff"},
    "audio": {"mp3", "wav", "m4a", "aac", "ogg", "flac"},
    "video": {"mp4", "mov", "avi", "mkv", "webm", "m4v"}
}


def ensure_upload_folders():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for category in UPLOAD_CATEGORIES:
        os.makedirs(os.path.join(UPLOAD_DIR, category), exist_ok=True)


def upload_category_for(filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    for category, extensions in UPLOAD_CATEGORIES.items():
        if extension in extensions:
            return category
    return "docs"


def list_uploaded_files():
    ensure_upload_folders()
    files = []

    for category in UPLOAD_CATEGORIES:
        folder = os.path.join(UPLOAD_DIR, category)
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isfile(path):
                files.append({
                    "name": filename,
                    "category": category,
                    "path": os.path.join("uploads", category, filename).replace("\\", "/"),
                    "size": os.path.getsize(path),
                    "modified": os.path.getmtime(path)
                })

    files.sort(key=lambda item: item["modified"], reverse=True)
    return files


def read_local_env_file():
    env_path = os.path.join(BASE_DIR, ".env")
    values = {}
    if not os.path.isfile(env_path):
        return values

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def atlas_admin_credentials():
    local_env = read_local_env_file()
    username = os.getenv("ATLAS_ADMIN_USERNAME") or local_env.get("ATLAS_ADMIN_USERNAME")
    password = os.getenv("ATLAS_ADMIN_PASSWORD") or local_env.get("ATLAS_ADMIN_PASSWORD")
    return username, password


def atlas_is_logged_in():
    return session.get("atlas_admin_authenticated") is True


def atlas_safe_next(raw_next):
    if not raw_next or not isinstance(raw_next, str):
        return "/app"
    if not raw_next.startswith("/") or raw_next.startswith("//") or "://" in raw_next:
        return "/app"
    return raw_next


def atlas_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if atlas_is_logged_in():
            return view(*args, **kwargs)

        if request.path.startswith("/api/"):
            return jsonify({"success": False, "ok": False, "error": "Atlas admin login required."}), 401

        next_path = atlas_safe_next(request.full_path.rstrip("?") or request.path)
        return redirect(f"/login?next={quote(next_path, safe='')}")
    return wrapped


def atlas_login_page(error_message="", status_code=200):
    next_path = atlas_safe_next(request.values.get("next") or "/app")
    error_markup = f'<div class="atlas-login-error">{escape(error_message)}</div>' if error_message else ""
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex, nofollow, noarchive" />
  <title>Atlas Admin Login</title>
  <style>
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:#08111f; color:#f7f1e6; font-family:Arial, sans-serif; }}
    .atlas-login-card {{ width:min(440px, calc(100% - 32px)); background:#111c2e; border:1px solid rgba(255,255,255,.14); border-radius:22px; padding:30px; box-shadow:0 24px 80px rgba(0,0,0,.35); }}
    .eyebrow {{ color:#d7b56d; text-transform:uppercase; letter-spacing:.14em; font-size:.78rem; font-weight:700; }}
    h1 {{ margin:8px 0 10px; font-size:2rem; }}
    p {{ color:#c9d2df; line-height:1.55; }}
    label {{ display:block; margin:16px 0 7px; color:#f7f1e6; font-weight:700; }}
    input {{ width:100%; box-sizing:border-box; border-radius:12px; border:1px solid rgba(255,255,255,.18); padding:13px 14px; background:#08111f; color:#fff; }}
    button {{ display:inline-flex; align-items:center; justify-content:center; margin-top:20px; border:0; border-radius:999px; padding:12px 18px; background:#d7b56d; color:#08111f; font-weight:800; cursor:pointer; }}
    .atlas-login-error {{ margin:16px 0 0; padding:12px; border-radius:12px; background:#4b1720; color:#ffd6dc; }}
    .note {{ margin-top:18px; font-size:.9rem; color:#9fb0c6; }}
  </style>
</head>
<body>
  <main class="atlas-login-card">
    <p class="eyebrow">Atlas Operating System</p>
    <h1>Admin Login</h1>
    <p>Sign in to open Mission Control, CRM, Design Gallery, and Commerce Center.</p>
    {error_markup}
    <form method="post" action="/login">
      <input type="hidden" name="next" value="{escape(next_path)}" />
      <label for="username">Username</label>
      <input id="username" name="username" type="text" autocomplete="username" required autofocus />
      <label for="password">Password</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required />
      <button type="submit">Open Admin Dashboard</button>
    </form>
    <p class="note">Temporary local gate for ATL-119. Use ATLAS_ADMIN_USERNAME and ATLAS_ADMIN_PASSWORD from the runtime environment or local .env. Production still needs hardened identity, HTTPS, CSRF, and secure cookie deployment.</p>
  </main>
</body>
</html>
""", status_code


@app.route("/login", methods=["GET", "POST"])
@app.route("/admin-login", methods=["GET", "POST"])
def atlas_admin_login():
    if request.method == "GET":
        if atlas_is_logged_in():
            return redirect(atlas_safe_next(request.args.get("next") or "/app"))
        return atlas_login_page()

    configured_username, configured_password = atlas_admin_credentials()
    if not configured_username or not configured_password:
        return atlas_login_page("Atlas admin credentials are not configured. Set ATLAS_ADMIN_USERNAME and ATLAS_ADMIN_PASSWORD in the environment or local .env.", 503)

    submitted_username = request.form.get("username", "")
    submitted_password = request.form.get("password", "")
    username_ok = secrets.compare_digest(submitted_username, configured_username)
    password_ok = secrets.compare_digest(submitted_password, configured_password)
    if not username_ok or not password_ok:
        session.clear()
        return atlas_login_page("Invalid Atlas admin credentials.", 401)

    session.clear()
    session["atlas_admin_authenticated"] = True
    session["atlas_admin_username"] = configured_username
    return redirect(atlas_safe_next(request.form.get("next") or "/app"))


@app.route("/logout")
def atlas_admin_logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def home():
    return send_from_directory(UI_DIR, "atlas_neural_core.html")


@app.route("/neural")
def atlas_neural_core():
    return send_from_directory(UI_DIR, "atlas_neural_core.html")


@app.route("/app")
@app.route("/dashboard")
@app.route("/executive-dashboard")
@atlas_login_required
def atlas_app_dashboard():
    return send_from_directory(UI_DIR, "app.html")


@app.route("/ramfam")
def atlas_brain():
    return send_from_directory(UI_DIR, "atlas_brain.html")


@app.route("/kingdom")
def ramfam_kingdom():
    return send_from_directory(UI_DIR, "ramfam_kingdom.html")


@app.route("/prototype/")
@app.route("/sis/")
def sis_website_prototype():
    return send_from_directory(SIS_WEBSITE_DIR, "index.html")


@app.route("/business-assessment")
@app.route("/free-business-assessment")
def business_assessment():
    return redirect("/sis/#custom-orders")


@app.route("/atlas-chat")
@app.route("/website-chat")
def atlas_chat_area():
    return redirect("/neural#atlas-chat")


@app.route("/qtime-productions")
def qtime_productions_client_area():
    dashboard_path = os.path.join(QTIME_CLIENT_DIR, "REPORTS", "ATLAS_CLIENT_DASHBOARD.md")
    if not os.path.isfile(dashboard_path):
        return "QTime Productions client source files were not found locally. Status: Not Assessed.", 404

    with open(dashboard_path, "r", encoding="utf-8") as dashboard_file:
        dashboard_markdown = dashboard_file.read()

    links = [
        ("Project Memory", "PROJECT_MEMORY.md"),
        ("Business Assessment", "BUSINESS_ASSESSMENT.md"),
        ("Approval Queue", "APPROVAL_QUEUE/APPROVAL_QUEUE.md"),
        ("Manny Review Packet", "REPORTS/MANNY_REVIEW_PACKET.md"),
    ]
    link_markup = "".join(
        f'<li><a href="/qtime-productions/files/{escape(path)}">{escape(label)}</a></li>'
        for label, path in links
        if os.path.isfile(os.path.join(QTIME_CLIENT_DIR, path))
    )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>QTime Productions Client Area</title>
  <style>
    body {{ margin:0; padding:28px; font-family:Arial, sans-serif; color:#f8fafc; background:#020617; }}
    a {{ color:#00e5ff; }}
    .panel {{ max-width:1100px; margin:0 auto; padding:24px; border:1px solid rgba(0,229,255,.24); border-radius:22px; background:rgba(7,12,24,.88); }}
    pre {{ white-space:pre-wrap; line-height:1.55; color:#dbeafe; }}
  </style>
</head>
<body>
  <main class=\"panel\">
    <p><a href=\"/neural\">← Back to Atlas Dashboard</a></p>
    <h1>QTime Productions Client Area</h1>
    <p>Source-backed local client files only. Missing public-use details remain in the approval queue.</p>
    <ul>{link_markup}</ul>
    <pre>{escape(dashboard_markdown)}</pre>
  </main>
</body>
</html>"""


@app.route("/qtime-productions/files/<path:filename>")
def qtime_productions_file(filename):
    return send_from_directory(QTIME_CLIENT_DIR, filename)


@app.route("/prototype/<path:filename>")
@app.route("/sis/<path:filename>")
def sis_website_static(filename):
    return send_from_directory(SIS_WEBSITE_DIR, filename)


def etsy_oauth_redirect_uri():
    redirect_uri = etsy_connector.read_dotenv(ETSY_ENV_PATH).get("ETSY_REDIRECT_URI") or os.getenv("ETSY_REDIRECT_URI")
    if not redirect_uri:
        raise etsy_connector.EtsyConfigError(
            "Missing required Etsy .env value: ETSY_REDIRECT_URI. "
            "Set ETSY_REDIRECT_URI=https://YOUR-TUNNEL-DOMAIN/etsy/callback"
        )
    return redirect_uri


def save_etsy_oauth_pending(oauth_state, code_verifier):
    os.makedirs(os.path.dirname(ETSY_OAUTH_PENDING_PATH), exist_ok=True)
    pending = {
        "expected_state": oauth_state,
        "code_verifier": code_verifier,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(ETSY_OAUTH_PENDING_PATH, "w", encoding="utf-8") as pending_file:
        json.dump(pending, pending_file, indent=2)


def read_etsy_oauth_pending():
    with open(ETSY_OAUTH_PENDING_PATH, "r", encoding="utf-8") as pending_file:
        return json.load(pending_file)


def delete_etsy_oauth_pending():
    try:
        os.remove(ETSY_OAUTH_PENDING_PATH)
    except FileNotFoundError:
        pass


@app.route("/etsy/connect")
def etsy_connect():
    try:
        config = etsy_connector.load_etsy_config(ETSY_ENV_PATH)
        redirect_uri = etsy_oauth_redirect_uri()
        auth_url, oauth_state, code_verifier = etsy_connector.build_authorization_url(
            keystring=config.keystring,
            redirect_uri=redirect_uri,
        )
    except etsy_connector.EtsyConnectorError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    app.logger.info("Etsy OAuth redirect_uri: %s", redirect_uri)
    app.logger.info("Etsy OAuth authorization URL: %s", auth_url)
    save_etsy_oauth_pending(oauth_state, code_verifier)
    return redirect(auth_url)


@app.route("/etsy/callback")
def etsy_callback():
    error = request.args.get("error")
    if error:
        return jsonify({"success": False, "error": error}), 400

    code = request.args.get("code")
    returned_state = request.args.get("state")

    if not code:
        return jsonify({"success": False, "error": "Missing Etsy authorization code."}), 400

    try:
        pending_oauth = read_etsy_oauth_pending()
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "Missing pending Etsy OAuth file. Restart /etsy/connect.",
            "debug": {
                "pending_path": ETSY_OAUTH_PENDING_PATH,
                "returned_state_present": bool(returned_state),
            },
        }), 400
    except (OSError, json.JSONDecodeError) as exc:
        return jsonify({
            "success": False,
            "error": "Unable to read pending Etsy OAuth file. Restart /etsy/connect.",
            "debug": {
                "pending_path": ETSY_OAUTH_PENDING_PATH,
                "details": str(exc),
            },
        }), 400

    expected_state = pending_oauth.get("expected_state")
    code_verifier = pending_oauth.get("code_verifier")

    if not expected_state or returned_state != expected_state:
        return jsonify({"success": False, "error": "Invalid Etsy OAuth state."}), 400
    if not code_verifier:
        return jsonify({"success": False, "error": "Missing Etsy PKCE verifier. Restart /etsy/connect."}), 400

    try:
        config = etsy_connector.load_etsy_config(ETSY_ENV_PATH)
        tokens = etsy_connector.exchange_code_for_tokens(
            code=code,
            redirect_uri=etsy_oauth_redirect_uri(),
            code_verifier=code_verifier,
            keystring=config.keystring,
        )
        save_result = etsy_connector.save_tokens_safely(tokens, env_path=ETSY_ENV_PATH)
    except etsy_connector.EtsyConnectorError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    delete_etsy_oauth_pending()
    return (
        "Etsy OAuth connection saved. "
        "Saved ETSY_ACCESS_TOKEN and ETSY_REFRESH_TOKEN to .env without printing token values. "
        f"Backup created: {escape(str(save_result.get('backup_path', '')))}"
    )


@app.route("/etsy/test")
def etsy_test_read_only_connection():
    try:
        config = etsy_connector.load_etsy_config(ETSY_ENV_PATH)
        if not config.access_token:
            return jsonify({
                "success": False,
                "error": "Missing ETSY_ACCESS_TOKEN. Visit /etsy/connect first.",
                "connect_url": "/etsy/connect",
            }), 400
        token_refreshed = False
        try:
            result = etsy_connector.verify_read_only_connection(
                keystring=config.keystring,
                shared_secret=config.shared_secret,
                access_token=config.access_token,
            )
        except etsy_connector.EtsyOAuthError as exc:
            if "invalid_token" not in str(exc) or not config.refresh_token:
                raise
            tokens = etsy_connector.refresh_access_token(
                refresh_token=config.refresh_token,
                keystring=config.keystring,
            )
            etsy_connector.save_tokens_safely(tokens, env_path=ETSY_ENV_PATH)
            token_refreshed = True
            result = etsy_connector.verify_read_only_connection(
                keystring=config.keystring,
                shared_secret=config.shared_secret,
                access_token=tokens["access_token"],
            )
    except etsy_connector.EtsyConnectorError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    return jsonify({
        "success": True,
        "message": "Etsy read-only OAuth connection verified.",
        "token_refreshed": token_refreshed,
        "scope": "shops_r listings_r",
        "shop_count": result.get("shop_count", 0),
        "shops": result.get("shops", []),
    })


@app.route("/api/website-leads", methods=["POST"])
def capture_website_lead():
    from datetime import datetime, timezone
    import uuid

    data = request.get_json(silent=True) or {}
    required_fields = ["Name", "Email", "Service", "Quantity", "Needed By", "Project Details"]
    missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]

    if missing_fields:
        return jsonify({
            "success": False,
            "error": "Missing required lead fields.",
            "missing_fields": missing_fields
        }), 400

    now = datetime.now(timezone.utc).isoformat()
    lead = {
        "id": f"web-{uuid.uuid4().hex[:10]}",
        "created_at": now,
        "source": "SIS cinematic landing page prototype",
        "status": "New Website Prototype Lead",
        "assigned_agent": "Amanda",
        "priority_signal": data.get("Decision Stage", "Ready for quote"),
        "fields": data,
    }

    leads_dir = os.path.join(BASE_DIR, "RAMFAM_KINGDOM_BRAIN", "07_WEBSITE_LEADS")
    leads_file = os.path.join(leads_dir, "website_leads.json")
    os.makedirs(leads_dir, exist_ok=True)

    leads = []
    if os.path.exists(leads_file):
        with open(leads_file, "r", encoding="utf-8") as f:
            try:
                leads = json.load(f)
            except json.JSONDecodeError:
                leads = []

    leads.append(lead)
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    brief_lines = [
        "AMANDA WEBSITE LEAD BRIEF",
        f"Lead ID: {lead['id']}",
        f"Captured: {now}",
        f"Name: {data.get('Name')}",
        f"Organization: {data.get('Organization', 'Not provided')}",
        f"Email: {data.get('Email')}",
        f"Phone: {data.get('Phone', 'Not provided')}",
        f"Service: {data.get('Service')}",
        f"Quantity / group size: {data.get('Quantity')}",
        f"Needed by: {data.get('Needed By')}",
        f"Artwork status: {data.get('Artwork Status', 'Not provided')}",
        f"Preferred contact: {data.get('Preferred Contact', 'Not provided')}",
        f"Best contact time: {data.get('Best Contact Time', 'Not provided')}",
        f"Decision stage: {data.get('Decision Stage', 'Not provided')}",
        f"Timeline pressure: {data.get('Timeline Pressure', 'Not provided')}",
        f"Project details: {data.get('Project Details')}",
        "Next step: Amanda follows up with quote-ready questions and confirms timeline feasibility."
    ]

    return jsonify({
        "success": True,
        "lead_id": lead["id"],
        "brief": "\n".join(brief_lines)
    })


@app.route("/crm")
@app.route("/customer-dashboard")
@app.route("/client-crm")
@atlas_login_required
def crm_command_center():
    return send_from_directory(UI_DIR, "crm.html")

COMMERCE_PIPELINE_ROOT = os.path.join(
    BASE_DIR,
    "RAMFAM_KINGDOM_BRAIN",
    "06_MISSIONS",
    "commerce_pipeline_runner",
)
COMMERCE_DASHBOARD_FILENAME = "commerce_approval_dashboard.html"
COMMERCE_IMAGE_PROMPT_ROOT = os.path.join(
    BASE_DIR,
    "RAMFAM_KINGDOM_BRAIN",
    "06_MISSIONS",
    "commerce_image_prompt_exporter",
)
COMMERCE_IMAGE_PROMPT_EXPORTER_DIRNAME = "05_commerce_image_prompt_exporter"
COMMERCE_IMAGE_PROMPTS_LATEST_JSON = "commerce_image_prompts_latest.json"
COMMERCE_IMAGE_PROMPTS_LATEST_MD = "commerce_image_prompts_latest.md"
DESIGN_GALLERY_DIR = os.path.join(BASE_DIR, "design_gallery")
DESIGN_GALLERY_ASSET_REGISTRY = "asset_registry.json"
DESIGN_GALLERY_REVENUE_TRACKING = "revenue_tracking.json"
KINGDOM_GALLERY_PENDING_APPROVAL_DIR = os.path.join(
    BASE_DIR,
    "RAMFAM_KINGDOM_BRAIN",
    "90_ASSETS",
    "KINGDOM_GALLERY",
    "PENDING_APPROVAL",
)
DESIGN_GALLERY_PUBLICATION_CHANNELS = {
    "digital": ["kingdom_gallery"],
}
INTERNAL_AUTO_EXECUTE_WORK_TYPES = [
    "bug_fixes",
    "reports",
    "research",
    "asset_creation",
    "code_generation",
    "ui_improvements",
    "verification",
    "testing",
    "internal_refactoring",
    "dashboard_improvements",
]
MANUAL_APPROVAL_REQUIRED_ACTIONS = [
    "customer_contact",
    "invoices",
    "emails",
    "publishing_to_etsy",
    "publishing_to_shopify",
    "money_movement",
    "deleting_files",
    "external_actions",
]
MISSIONS_FILE = os.path.join(BASE_DIR, "missions", "missions.json")


def latest_commerce_dashboard_path():
    pipeline_root = os.fspath(COMMERCE_PIPELINE_ROOT)
    if not os.path.isdir(pipeline_root):
        return None

    mission_folders = []
    for name in os.listdir(pipeline_root):
        mission_folder = os.path.join(pipeline_root, name)
        if os.path.isdir(mission_folder) and name.startswith("commerce_pipeline_mission_"):
            mission_folders.append(mission_folder)

    for mission_folder in sorted(mission_folders, key=lambda path: os.path.basename(path), reverse=True):
        dashboard_path = os.path.join(mission_folder, COMMERCE_DASHBOARD_FILENAME)
        if os.path.isfile(dashboard_path):
            return dashboard_path

    return None


def latest_design_gallery_export_dir():
    pipeline_root = os.fspath(COMMERCE_PIPELINE_ROOT)
    if os.path.isdir(pipeline_root):
        mission_folders = []
        for name in os.listdir(pipeline_root):
            mission_folder = os.path.join(pipeline_root, name)
            if os.path.isdir(mission_folder) and name.startswith("commerce_pipeline_mission_"):
                mission_folders.append(mission_folder)

        for mission_folder in sorted(mission_folders, key=lambda path: os.path.basename(path), reverse=True):
            exporter_dir = os.path.join(mission_folder, COMMERCE_IMAGE_PROMPT_EXPORTER_DIRNAME)
            if os.path.isfile(os.path.join(exporter_dir, COMMERCE_IMAGE_PROMPTS_LATEST_JSON)) or os.path.isfile(os.path.join(exporter_dir, COMMERCE_IMAGE_PROMPTS_LATEST_MD)):
                return exporter_dir

    fallback_dir = os.fspath(COMMERCE_IMAGE_PROMPT_ROOT)
    if os.path.isfile(os.path.join(fallback_dir, COMMERCE_IMAGE_PROMPTS_LATEST_JSON)) or os.path.isfile(os.path.join(fallback_dir, COMMERCE_IMAGE_PROMPTS_LATEST_MD)):
        return fallback_dir

    return None


def design_gallery_output_links():
    exporter_dir = latest_design_gallery_export_dir()
    if not exporter_dir:
        return ""

    links = []
    latest_report = os.path.join(exporter_dir, COMMERCE_IMAGE_PROMPTS_LATEST_MD)
    latest_json = os.path.join(exporter_dir, COMMERCE_IMAGE_PROMPTS_LATEST_JSON)
    if os.path.isfile(latest_report):
        links.append(("Latest prompt report", f"/design-gallery/export/{COMMERCE_IMAGE_PROMPTS_LATEST_MD}"))
    if os.path.isfile(latest_json):
        links.append(("Latest prompt JSON", f"/design-gallery/export/{COMMERCE_IMAGE_PROMPTS_LATEST_JSON}"))

    prompt_text_dir = os.path.join(exporter_dir, "openai_image_prompts")
    if os.path.isdir(prompt_text_dir):
        prompt_files = sorted(
            name for name in os.listdir(prompt_text_dir)
            if os.path.isfile(os.path.join(prompt_text_dir, name)) and name.lower().endswith(".txt")
        )
        for name in prompt_files:
            links.append((f"Prompt text: {name}", f"/design-gallery/export/openai_image_prompts/{name}"))

    if not links:
        return ""

    items = "".join(f'<li><a href="{escape(url)}" target="_blank">{escape(label)}</a></li>' for label, url in links)
    return f"""
    <section class="outputs">
      <h2>Latest Commerce Image Prompt Exporter Outputs</h2>
      <ul>{items}</ul>
    </section>
    """


def read_design_gallery_json(filename, fallback):
    path = os.path.join(os.fspath(DESIGN_GALLERY_DIR), filename)
    if not os.path.isfile(path):
        return fallback

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return fallback


def write_design_gallery_json(filename, data):
    path = os.path.join(os.fspath(DESIGN_GALLERY_DIR), filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def design_gallery_assets_from_registry(registry_data):
    if isinstance(registry_data, list):
        return registry_data
    if isinstance(registry_data, dict):
        assets = registry_data.get("assets") or registry_data.get("asset_registry") or []
        if isinstance(assets, dict):
            return [dict({"asset_id": asset_id}, **asset) for asset_id, asset in assets.items() if isinstance(asset, dict)]
        if isinstance(assets, list):
            return assets
    return []


def find_design_gallery_registry_asset(registry_data, asset_id):
    target = str(asset_id)
    if isinstance(registry_data, list):
        assets = registry_data
    elif isinstance(registry_data, dict):
        assets = registry_data.get("assets") or registry_data.get("asset_registry") or []
    else:
        return None

    if isinstance(assets, dict):
        for key, asset in assets.items():
            if not isinstance(asset, dict):
                continue
            candidate = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or key)
            if str(key) == target or candidate == target:
                asset.setdefault("asset_id", str(key))
                return asset
        return None

    if isinstance(assets, list):
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            candidate = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "")
            if candidate == target:
                return asset
    return None


def design_gallery_revenue_lookup(revenue_data):
    if not isinstance(revenue_data, dict):
        return {}

    assets = revenue_data.get("assets") or revenue_data.get("revenue_tracking") or revenue_data
    if isinstance(assets, list):
        return {
            str(item.get("asset_id") or item.get("id") or item.get("asset_name") or ""): item
            for item in assets
            if isinstance(item, dict)
        }
    if isinstance(assets, dict):
        return {str(asset_id): value for asset_id, value in assets.items() if isinstance(value, dict)}
    return {}


def normalize_approval_status(value):
    status = str(value or "").strip().lower().replace("_", " ")
    if "reject" in status or "revision" in status or "needs" in status:
        return "Rejected"
    if "approve" in status and "pending" not in status:
        return "Approved"
    return "Pending Approval"


def normalize_marketplace_status(value):
    status = str(value or "").strip().lower().replace("_", " ")
    if "top" in status and "seller" in status:
        return "Top Seller"
    if "publish" in status or "live" in status:
        return "Published"
    return "Review Queue"


def design_gallery_file_url(path):
    if not path:
        return ""

    gallery_root = os.path.abspath(os.fspath(DESIGN_GALLERY_DIR))
    pending_approval_root = os.path.abspath(os.fspath(KINGDOM_GALLERY_PENDING_APPROVAL_DIR))
    raw_path = os.fspath(path)
    if raw_path.startswith(("/", "http://", "https://")):
        return raw_path
    candidate = raw_path if os.path.isabs(raw_path) else os.path.join(gallery_root, raw_path)
    candidate = os.path.abspath(candidate)

    if os.path.isdir(candidate):
        for filename in ("etsy_listing.txt", "listing_package.txt", "asset_metadata.json"):
            preferred_path = os.path.join(candidate, filename)
            if os.path.isfile(preferred_path):
                candidate = preferred_path
                break

    try:
        if os.path.commonpath([gallery_root, candidate]) != gallery_root:
            if os.path.commonpath([pending_approval_root, candidate]) == pending_approval_root:
                relative_path = os.path.relpath(candidate, pending_approval_root).replace("\\", "/")
                return f"/design-gallery/kingdom-gallery-pending/{relative_path}"
            return ""
    except ValueError:
        return ""

    relative_path = os.path.relpath(candidate, gallery_root).replace("\\", "/")
    return f"/design-gallery/file/{relative_path}"


def design_gallery_preview_url(path):
    if not path:
        return ""
    return design_gallery_file_url(path) or os.fspath(path)


def read_design_gallery_metadata_for_asset(asset):
    metadata_path = design_gallery_metadata_path_for_asset(asset)
    if not metadata_path or not os.path.isfile(metadata_path):
        return {}, ""

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}, metadata_path
    return metadata if isinstance(metadata, dict) else {}, metadata_path


def infer_design_gallery_file_locations(asset, metadata, metadata_path):
    file_locations = {}
    for source in (metadata.get("file_locations"), asset.get("file_locations")):
        if isinstance(source, dict):
            file_locations.update({key: value for key, value in source.items() if value})

    if metadata_path:
        file_locations.setdefault("metadata", metadata_path)
        asset_folder = os.path.dirname(metadata_path)
    else:
        asset_folder = ""

    if asset_folder and os.path.isdir(asset_folder):
        asset_id = str(asset.get("asset_id") or metadata.get("asset_id") or "")
        for extension, key in ((".svg", "svg"), (".png", "png")):
            if key in file_locations:
                continue
            candidates = [
                os.path.join(asset_folder, name)
                for name in os.listdir(asset_folder)
                if name.lower().endswith(extension)
            ]
            preferred = [path for path in candidates if asset_id and os.path.splitext(os.path.basename(path))[0] == asset_id]
            if preferred or candidates:
                file_locations[key] = (preferred or sorted(candidates))[0]

        listing_folder = os.path.join(asset_folder, "listing_package")
        if os.path.isdir(listing_folder):
            file_locations.setdefault("listing_package", listing_folder)
            file_locations.setdefault("seo_tags", os.path.join(listing_folder, "seo_tags.txt"))
            file_locations.setdefault("marketing_copy", os.path.join(listing_folder, "marketing_copy.txt"))

    return file_locations


def design_gallery_file_links(file_locations):
    links = {}
    for key in ("svg", "png", "metadata", "listing_package", "seo_tags", "marketing_copy"):
        url = design_gallery_file_url(file_locations.get(key))
        if url:
            links[key] = url
    return links


def design_gallery_asset_timeline(asset, metadata, file_links):
    asset_name = asset.get("asset_name") or metadata.get("asset_name") or "Unnamed Kingdom Asset"
    created_at = asset.get("creation_date") or metadata.get("creation_date") or metadata.get("date_created") or "Untracked"
    timeline = []

    if asset.get("opportunity") or asset.get("opportunity_agent") or metadata.get("opportunity_agent"):
        timeline.append({"timestamp": created_at, "agent": "Hunter", "action": "Hunter discovered opportunity", "asset": asset_name})

    creator = str(asset.get("creator_agent") or metadata.get("creator_agent") or "").split()[0]
    if creator.lower() == "micah" or file_links.get("svg") or file_links.get("png"):
        timeline.append({"timestamp": created_at, "agent": "Micah", "action": "Micah created asset", "asset": asset_name})

    if file_links or asset.get("file_location"):
        timeline.append({"timestamp": created_at, "agent": "Mason", "action": "Mason stored asset", "asset": asset_name})

    if file_links.get("listing_package") or file_links.get("seo_tags") or file_links.get("marketing_copy"):
        timeline.append({"timestamp": asset.get("updated_at") or created_at, "agent": "Amanda", "action": "Amanda created listing package", "asset": asset_name})

    marketplace_status = str(asset.get("marketplace_status") or metadata.get("marketplace_status") or "").lower()
    if "published" in marketplace_status or "live" in marketplace_status:
        publication_type = asset.get("publication_type") or metadata.get("publication_type")
        action = f"Published {str(publication_type).title()}" if publication_type else "Published"
        timeline.append({"timestamp": asset.get("updated_at") or created_at, "agent": "Marketplace", "action": action, "asset": asset_name})

    return timeline


def normalize_design_asset(asset, revenue):
    asset_id = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "untracked-asset")
    revenue_record = revenue.get(asset_id, {})
    if not revenue_record and asset.get("asset_name"):
        revenue_record = revenue.get(str(asset.get("asset_name")), {})

    metadata, metadata_path = read_design_gallery_metadata_for_asset(asset)
    file_locations = infer_design_gallery_file_locations(asset, metadata, metadata_path)
    file_links = design_gallery_file_links(file_locations)

    normalized_asset = {
        "asset_id": asset_id,
        "asset_preview": design_gallery_preview_url(asset.get("asset_preview") or asset.get("preview") or asset.get("preview_url") or asset.get("thumbnail")) or file_links.get("png") or file_links.get("svg") or "",
        "asset_name": asset.get("asset_name") or asset.get("name") or metadata.get("asset_name") or "Unnamed Kingdom Asset",
        "creator_agent": asset.get("creator_agent") or asset.get("agent") or asset.get("creator") or metadata.get("creator_agent") or "Unassigned",
        "creation_date": asset.get("creation_date") or asset.get("created_at") or asset.get("date") or metadata.get("creation_date") or metadata.get("date_created") or "Untracked",
        "approval_status": normalize_approval_status(asset.get("approval_status") or asset.get("status") or metadata.get("approval_status")),
        "marketplace_status": normalize_marketplace_status(asset.get("marketplace_status") or asset.get("publishing_status") or metadata.get("marketplace_status")),
        "publication_type": asset.get("publication_type") or metadata.get("publication_type") or "",
        "publication_scope": asset.get("publication_scope") or metadata.get("publication_scope") or "",
        "channels": asset.get("channels") if isinstance(asset.get("channels"), list) else metadata.get("channels") if isinstance(metadata.get("channels"), list) else [],
        "external_channels": asset.get("external_channels") if isinstance(asset.get("external_channels"), list) else metadata.get("external_channels") if isinstance(metadata.get("external_channels"), list) else [],
        "manual_approval_required": bool(asset.get("manual_approval_required") or metadata.get("manual_approval_required") or False),
        "manual_approval_scope": asset.get("manual_approval_scope") or metadata.get("manual_approval_scope") or "",
        "external_publication_blocked": bool(asset.get("external_publication_blocked") or metadata.get("external_publication_blocked") or False),
        "blocked_external_channels": asset.get("blocked_external_channels") if isinstance(asset.get("blocked_external_channels"), list) else metadata.get("blocked_external_channels") if isinstance(metadata.get("blocked_external_channels"), list) else [],
        "internal_publication": asset.get("internal_publication") if isinstance(asset.get("internal_publication"), dict) else metadata.get("internal_publication") if isinstance(metadata.get("internal_publication"), dict) else {},
        "revenue_tracking": {
            "total_revenue": float(revenue_record.get("total_revenue") or revenue_record.get("revenue") or 0),
            "units_sold": int(revenue_record.get("units_sold") or revenue_record.get("sales") or 0),
            "profit": float(revenue_record.get("profit") or 0),
            "is_top_seller": bool(revenue_record.get("is_top_seller") or revenue_record.get("top_seller") or False),
        },
        "file_location": asset.get("file_location") or asset.get("path") or asset.get("file_path") or metadata_path or "Untracked",
        "file_links": file_links,
    }
    normalized_asset["timeline"] = design_gallery_asset_timeline(normalized_asset, metadata, file_links)
    return normalized_asset


def grouped_design_gallery_assets():
    registry_data = read_design_gallery_json(DESIGN_GALLERY_ASSET_REGISTRY, {"assets": []})
    revenue_data = read_design_gallery_json(DESIGN_GALLERY_REVENUE_TRACKING, {"assets": {}})
    revenue = design_gallery_revenue_lookup(revenue_data)
    assets = [
        normalize_design_asset(asset, revenue)
        for asset in design_gallery_assets_from_registry(registry_data)
        if isinstance(asset, dict)
    ]

    sections = {
        "pending_approval": [],
        "approved": [],
        "rejected": [],
        "published_digital": [],
        "top_sellers": [],
    }

    for asset in assets:
        approval_status = asset["approval_status"].strip().lower()
        marketplace_status = asset["marketplace_status"].strip().lower()
        revenue_record = asset["revenue_tracking"]

        if approval_status == "rejected":
            sections["rejected"].append(asset)
        elif approval_status == "pending approval":
            sections["pending_approval"].append(asset)
        elif marketplace_status == "published" or marketplace_status == "top seller":
            sections["published_digital"].append(asset)
        elif approval_status == "approved":
            sections["approved"].append(asset)
        else:
            sections["pending_approval"].append(asset)

        if revenue_record["is_top_seller"] or revenue_record["total_revenue"] > 0 or revenue_record["units_sold"] > 0:
            sections["top_sellers"].append(asset)

    return sections


def recent_design_gallery_activity(sections, limit=12):
    activity = []
    seen_asset_ids = set()
    for assets in sections.values():
        for asset in assets:
            asset_id = asset.get("asset_id")
            if asset_id in seen_asset_ids:
                continue
            seen_asset_ids.add(asset_id)
            for step in reversed(asset.get("timeline") or []):
                agent = step.get("agent") or "Kingdom"
                action = step.get("action") or "updated asset"
                prefix = f"{agent} "
                if action.startswith(prefix):
                    action = action[len(prefix):]
                activity.append({
                    "timestamp": step.get("timestamp") or asset.get("creation_date") or "Untracked",
                    "agent": agent,
                    "action": action,
                    "asset": step.get("asset") or asset.get("asset_name") or "Unnamed Kingdom Asset",
                    "asset_id": asset_id,
                })

    activity.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    return activity[:limit]


def design_gallery_metadata_path_for_asset(asset):
    file_locations = asset.get("file_locations") if isinstance(asset.get("file_locations"), dict) else {}
    metadata_path = file_locations.get("metadata") or ""
    if metadata_path:
        return os.fspath(metadata_path)

    file_location = os.fspath(asset.get("file_location") or "")
    if os.path.basename(file_location) == "asset_metadata.json":
        return file_location

    target_id = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "")
    gallery_root = os.fspath(DESIGN_GALLERY_DIR)
    if not target_id or not os.path.isdir(gallery_root):
        return ""

    for root, _, files in os.walk(gallery_root):
        if "asset_metadata.json" not in files:
            continue
        candidate = os.path.join(root, "asset_metadata.json")
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        metadata_id = str(metadata.get("asset_id") or metadata.get("id") or metadata.get("asset_name") or "")
        if metadata_id == target_id:
            return candidate
    return ""


def update_design_gallery_metadata_file(asset, approval_status, marketplace_status, changed_at, publication_type=None, channels=None, manual_approval_required=None, manual_approval_scope=None):
    metadata_path = design_gallery_metadata_path_for_asset(asset)
    if not metadata_path:
        asset_id = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "untracked-asset")
        safe_asset_id = asset_id.replace("/", "_").replace("\\", "_").strip() or "untracked-asset"
        metadata_path = os.path.join(os.fspath(DESIGN_GALLERY_DIR), "pending", safe_asset_id, "asset_metadata.json")

    if os.path.isfile(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        if not isinstance(metadata, dict):
            metadata = {}
    else:
        metadata = {
            "asset_id": asset.get("asset_id") or asset.get("id"),
            "asset_name": asset.get("asset_name") or asset.get("name"),
            "creator_agent": asset.get("creator_agent") or asset.get("agent") or asset.get("creator"),
            "creation_date": asset.get("creation_date") or asset.get("created_at") or asset.get("date"),
            "file_location": asset.get("file_location") or asset.get("path") or asset.get("file_path"),
        }

    file_locations = asset.get("file_locations") if isinstance(asset.get("file_locations"), dict) else {}
    file_locations["metadata"] = metadata_path
    asset["file_locations"] = file_locations
    metadata_file_locations = metadata.get("file_locations") if isinstance(metadata.get("file_locations"), dict) else {}
    metadata_file_locations["metadata"] = metadata_path
    metadata["file_locations"] = metadata_file_locations

    metadata["approval_status"] = approval_status
    metadata["marketplace_status"] = marketplace_status
    if publication_type is not None:
        metadata["publication_type"] = publication_type
    if channels is not None:
        metadata["channels"] = channels
    if manual_approval_required is not None:
        metadata["manual_approval_required"] = manual_approval_required
    if manual_approval_scope is not None:
        metadata["manual_approval_scope"] = manual_approval_scope
    metadata["updated_at"] = changed_at
    metadata["last_status_change"] = changed_at

    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        f.write("\n")
    return metadata_path


def apply_design_gallery_asset_action(asset, action):
    normalized = normalize_design_asset(asset, {})
    approval_status = normalized["approval_status"].strip().lower()
    marketplace_status = normalized["marketplace_status"].strip().lower()
    is_reviewable_result = "pending" in approval_status or "review" in approval_status

    if action == "approve":
        if not is_reviewable_result:
            raise ValueError("Only queued results can be approved.")
        return {"approval_status": "Approved", "marketplace_status": "Review Queue"}
    if action == "reject":
        if not is_reviewable_result:
            raise ValueError("Only queued results can be marked for revision.")
        return {"approval_status": "Rejected", "marketplace_status": "Review Queue"}
    if action == "publish_digital":
        if "approved" not in approval_status or "published" in marketplace_status or "rejected" in marketplace_status:
            raise ValueError("Only approved, unpublished assets can be published to the internal Kingdom Gallery.")
        return {
            "approval_status": "Approved",
            "marketplace_status": "Published",
            "publication_type": "digital",
            "publication_scope": "internal_kingdom_gallery_only",
            "channels": DESIGN_GALLERY_PUBLICATION_CHANNELS["digital"],
            "external_channels": [],
            "manual_approval_required": False,
            "manual_approval_scope": "internal_kingdom_gallery_only",
            "external_publication_blocked": True,
            "blocked_external_channels": ["etsy", "shopify", "printify", "social_media", "customers", "ads", "payments"],
        }
    if action in {"publish_physical", "publish_both"}:
        raise ValueError('"Published Digital" is internal Kingdom Gallery only; external publishing actions are blocked.')
    raise ValueError("Action must be approve, reject, or publish_digital.")


def design_gallery_status_payload(updated_asset=None, metadata_path="", approval_result=None):
    sections = grouped_design_gallery_assets()
    payload = {
        "success": True,
        "sections": sections,
        "review_queue": sections["pending_approval"],
        "counts": {name: len(assets) for name, assets in sections.items()},
        "recent_activity": recent_design_gallery_activity(sections),
        "workflow": {
            "internal_work_auto_authorized": True,
            "approval_target": "results_not_work",
            "internal_auto_execute_work_types": INTERNAL_AUTO_EXECUTE_WORK_TYPES,
            "manual_approval_required_actions": MANUAL_APPROVAL_REQUIRED_ACTIONS,
        },
    }
    if updated_asset is not None:
        payload["asset"] = updated_asset
    if metadata_path:
        payload["metadata_path"] = metadata_path
    if isinstance(approval_result, dict):
        payload["external_side_effects"] = approval_result.get("external_side_effects", [])
        payload["external_publication_blocked"] = approval_result.get("external_publication_blocked", False)
        payload["blocked_external_channels"] = approval_result.get("blocked_external_channels", [])
    return payload


@app.route("/commerce-command-center")
@atlas_login_required
def commerce_command_center():
    dashboard_path = latest_commerce_dashboard_path()
    if not dashboard_path:
        return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Commerce Command Center</title>
  <link rel="stylesheet" href="/assets/atlas-saas.css" />
</head>
<body data-atlas-app data-atlas-page="commerce">
  <section class="atlas-card">
    <h3>No Commerce Mission Dashboard Found</h3>
    <p>Run the commerce approval dashboard builder after a commerce pipeline mission, then open this command center again.</p>
  </section>
  <script src="/assets/atlas-saas-layout.js"></script>
</body>
</html>
"""

    return f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Commerce Command Center</title>
  <link rel=\"stylesheet\" href=\"/assets/atlas-saas.css\" />
</head>
<body data-atlas-app data-atlas-page=\"commerce\">
  <section class=\"atlas-card\">
    <h3>Latest Commerce Approval Dashboard</h3>
    <p>Real generated commerce data is preserved below from {escape(os.path.basename(os.path.dirname(dashboard_path)))}.</p>
    <iframe class=\"commerce-frame\" src=\"/commerce-command-center/source\" title=\"Latest commerce approval dashboard\"></iframe>
  </section>
  <script src=\"/assets/atlas-saas-layout.js\"></script>
</body>
</html>
"""


@app.route("/commerce-command-center/source")
@atlas_login_required
def commerce_command_center_source():
    dashboard_path = latest_commerce_dashboard_path()
    if not dashboard_path:
        return "Commerce Mission Dashboard not found.", 404
    return send_from_directory(os.path.dirname(dashboard_path), os.path.basename(dashboard_path))


@app.route("/design-gallery")
@atlas_login_required
def design_gallery():
    return send_from_directory(UI_DIR, "design_gallery.html")


@app.route("/api/design-gallery/assets")
@atlas_login_required
def design_gallery_assets_api():
    sections = grouped_design_gallery_assets()
    return jsonify({
        "sections": sections,
        "review_queue": sections["pending_approval"],
        "counts": {name: len(assets) for name, assets in sections.items()},
        "recent_activity": recent_design_gallery_activity(sections),
        "workflow": {
            "internal_work_auto_authorized": True,
            "approval_target": "results_not_work",
            "internal_auto_execute_work_types": INTERNAL_AUTO_EXECUTE_WORK_TYPES,
            "manual_approval_required_actions": MANUAL_APPROVAL_REQUIRED_ACTIONS,
        },
        "data_sources": {
            "asset_registry": os.path.join(os.fspath(DESIGN_GALLERY_DIR), DESIGN_GALLERY_ASSET_REGISTRY),
            "revenue_tracking": os.path.join(os.fspath(DESIGN_GALLERY_DIR), DESIGN_GALLERY_REVENUE_TRACKING),
        }
    })


@app.route("/api/design-gallery/assets/<asset_id>/status", methods=["PATCH", "POST"])
@atlas_login_required
def design_gallery_asset_status_api(asset_id):
    data = request.get_json(silent=True) or {}
    action = str(data.get("action") or data.get("status") or "").strip().lower()
    return commerce_approval_action_response(asset_id, action)


def commerce_approval_action_response(asset_id, action):
    from skills.commerce.commerce_approval_pipeline import apply_asset_action

    try:
        approval_result = apply_asset_action(asset_id, action, os.fspath(DESIGN_GALLERY_DIR))
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Design Gallery asset not found."}), 404
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400

    revenue_data = read_design_gallery_json(DESIGN_GALLERY_REVENUE_TRACKING, {"assets": {}})
    normalized_asset = normalize_design_asset(approval_result["asset"], design_gallery_revenue_lookup(revenue_data))
    return jsonify(design_gallery_status_payload(normalized_asset, approval_result.get("metadata_path", ""), approval_result))


@app.route("/api/commerce/approval/assets/<asset_id>/approve", methods=["POST"])
@atlas_login_required
def commerce_approval_approve_asset_api(asset_id):
    return commerce_approval_action_response(asset_id, "approve")


@app.route("/api/commerce/approval/assets/<asset_id>/reject", methods=["POST"])
@atlas_login_required
def commerce_approval_reject_asset_api(asset_id):
    return commerce_approval_action_response(asset_id, "reject")


@app.route("/api/commerce/approval/assets/<asset_id>/publish-digital", methods=["POST"])
@atlas_login_required
def commerce_approval_publish_digital_asset_api(asset_id):
    return commerce_approval_action_response(asset_id, "publish_digital")


@app.route("/design-gallery/export/<path:filename>")
@atlas_login_required
def design_gallery_export(filename):
    exporter_dir = latest_design_gallery_export_dir()
    if not exporter_dir:
        return "Design Gallery export not found.", 404
    return send_from_directory(exporter_dir, filename)


@app.route("/design-gallery/pending/<path:filename>")
@atlas_login_required
def design_gallery_pending_asset(filename):
    return send_from_directory(os.path.join(os.fspath(DESIGN_GALLERY_DIR), "pending"), filename)


@app.route("/design-gallery/kingdom-gallery-pending/<path:filename>")
@atlas_login_required
def design_gallery_kingdom_pending_asset(filename):
    pending_root = os.path.abspath(os.fspath(KINGDOM_GALLERY_PENDING_APPROVAL_DIR))
    requested_path = os.path.abspath(os.path.join(pending_root, filename))
    try:
        if os.path.commonpath([pending_root, requested_path]) != pending_root:
            return "Kingdom Gallery pending approval file not found.", 404
    except ValueError:
        return "Kingdom Gallery pending approval file not found.", 404
    return send_from_directory(os.path.dirname(requested_path), os.path.basename(requested_path))


@app.route("/design-gallery/file/<path:filename>")
@atlas_login_required
def design_gallery_file(filename):
    gallery_root = os.path.abspath(os.fspath(DESIGN_GALLERY_DIR))
    requested_path = os.path.abspath(os.path.join(gallery_root, filename))
    try:
        if os.path.commonpath([gallery_root, requested_path]) != gallery_root:
            return "Kingdom Gallery file not found.", 404
    except ValueError:
        return "Kingdom Gallery file not found.", 404
    return send_from_directory(os.path.dirname(requested_path), os.path.basename(requested_path))


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route("/history")
def history():
    if not os.path.exists(HISTORY_FILE):
        return jsonify([])

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))




@app.route("/upload", methods=["POST"])
def upload_file():
    ensure_upload_folders()

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file received."}), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    safe_name = secure_filename(uploaded_file.filename)

    if not safe_name:
        return jsonify({"success": False, "error": "Invalid file name."}), 400

    category = upload_category_for(safe_name)
    destination = os.path.join(UPLOAD_DIR, category, safe_name)

    base_name, extension = os.path.splitext(safe_name)
    counter = 1

    while os.path.exists(destination):
        safe_name = f"{base_name}_{counter}{extension}"
        destination = os.path.join(UPLOAD_DIR, category, safe_name)
        counter += 1

    uploaded_file.save(destination)

    return jsonify({
        "success": True,
        "filename": safe_name,
        "category": category,
        "path": os.path.join("uploads", category, safe_name).replace("\\", "/")
    })


@app.route("/uploaded-files")
def uploaded_files():
    return jsonify(list_uploaded_files())


@app.route("/uploads/<category>/<path:filename>")
def uploaded_file_download(category, filename):
    if category not in UPLOAD_CATEGORIES:
        return jsonify({"success": False, "error": "Invalid upload category."}), 404

    return send_from_directory(os.path.join(UPLOAD_DIR, category), filename)


@app.route("/v2")
def atlas_v2():
    return send_from_directory(UI_DIR, "index_v2.html")

@app.route("/missions")
@atlas_login_required
def missions():
    return send_from_directory(UI_DIR, "missions.html")

def clean_title(text):
    cleaned = text.strip().strip(",")
    cleaned = " ".join(cleaned.split())

    formatted_words = []

    for word in cleaned.split():
        if word.lower() in ["llc", "hvac", "tx", "bb", "b&b"]:
            formatted_words.append(word.upper())
        elif word.lower().startswith("v") and len(word) > 1:
            formatted_words.append(word.lower())
        else:
            formatted_words.append(word.capitalize())

    return " ".join(formatted_words)


def safe_load_json(path, default_value):
    if not os.path.exists(path):
        return default_value

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_value


def extract_project_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "mason,", "mason", "please", "create project",
        "inspect project", "start project", "complete project",
        "test project", "move project to testing", "project"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_mason_blueprint_target(lowered_message):
    targets = [
        "alfred", "david", "gideon", "amanda", "micah",
        "mason", "hunter", "scout", "taylor", "ranger"
    ]

    for target in targets:
        if target in lowered_message:
            return target

    return ""


def extract_hunter_lead_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "hunter,", "hunter", "please", "add lead",
        "remove lead", "delete lead", "send lead",
        "to amanda", "lead"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_hunter_status_update(lowered_message):
    cleaned = lowered_message

    for phrase in ["hunter,", "hunter", "please", "update lead"]:
        cleaned = cleaned.replace(phrase, " ")

    if " status " not in cleaned:
        return "", ""

    parts = cleaned.split(" status ", 1)
    return clean_title(parts[0]), clean_title(parts[1])


def extract_hunter_pipeline_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "hunter,", "hunter", "please", "add pipeline",
        "update pipeline", "pipeline", "status"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_hunter_pipeline_update(lowered_message):
    cleaned = lowered_message

    for phrase in ["hunter,", "hunter", "please", "update pipeline"]:
        cleaned = cleaned.replace(phrase, " ")

    if " status " not in cleaned:
        return "", ""

    parts = cleaned.split(" status ", 1)
    return clean_title(parts[0]), clean_title(parts[1])


def extract_hunter_maps_target_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "hunter,", "hunter", "please",
        "send maps target", "send map target",
        "add maps target", "add map target",
        "maps target", "map target",
        "to amanda", "amanda"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_scout_target_name(lowered_message):
    cleaned = lowered_message

    for phrase in ["scout,", "scout", "please", "add target", "target", "business"]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_scout_opportunity_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "scout,", "scout", "please", "add opportunity",
        "send opportunity", "to hunter", "opportunity"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def extract_amanda_business_name(lowered_message):
    cleaned = lowered_message

    for phrase in [
        "amanda,", "amanda", "please", "add outreach",
        "complete outreach", "outreach"
    ]:
        cleaned = cleaned.replace(phrase, " ")

    return clean_title(cleaned)


def complete_mission(agent_name):
    missions_path = os.path.join(BASE_DIR, "agents", "missions.json")

    if not os.path.exists(missions_path):
        return "No missions file found."

    with open(missions_path, "r", encoding="utf-8") as f:
        missions = json.load(f)

    found = False

    for mission in missions:
        if mission.get("agent", "").lower() == agent_name.lower():
            mission["status"] = "Complete"
            found = True

    if not found:
        return f"No active mission found for {agent_name}."

    with open(missions_path, "w", encoding="utf-8") as f:
        json.dump(missions, f, indent=2)

    return f"✅ Mission complete for {agent_name}."


@app.route("/chat", methods=["POST"])
def chat():
    import time
    start_time = time.time()
    data = request.get_json() or {}
    user_message = data.get("message", "")
    lowered_message = user_message.lower().strip()

    route = route_intent(user_message)
    intent = route.get("intent")
    direct_response = route.get("response")

    if "uploaded files" in lowered_message or "uploads" in lowered_message:
        uploads = list_uploaded_files()

        if not uploads:
            response = "No uploaded files found yet. Use the ?? Upload button to add docs, images, audio, or video."
        else:
            lines = ["Uploaded files:"]
            for item in uploads:
                lines.append(f"- {item.get('name')} ({item.get('category')})")
            response = "\n".join(lines)

    elif lowered_message.startswith("mason, ask hermes"):
        task = user_message.replace("Mason, ask Hermes to", "").strip()
        response = mason_ask_hermes(task)

    elif intent == "direct":
        response = direct_response

    elif intent == "revenue_council":
        report = atlas_revenue_council(user_message)
        top = report.get("top_recommendation", {})
        agents = report.get("agents", {})
        actions = report.get("manny_action_plan_today", [])

        response = "ATLAS REVENUE COUNCIL ACTIVE\n\n"
        response += "Hunter: " + agents.get("Hunter", "") + "\n"
        response += "Scout: " + agents.get("Scout", "") + "\n"
        response += "Amanda: " + agents.get("Amanda", "") + "\n"
        response += "David: " + agents.get("David", "") + "\n\n"
        response += "Atlas Recommendation:\n"
        response += top.get("name", "Opportunity") + " - " + top.get("offer", "") + "\n"
        response += "Target: " + top.get("target", "") + "\n"
        response += "Why now: " + top.get("why_now", "") + "\n\n"
        response += "Manny Action Plan Today:\n"
        for index, action in enumerate(actions, start=1):
            response += str(index) + ". " + action + "\n"

    elif intent == "executive_briefing":
        response = atlas_delegate(
            "Atlas, morning briefing. Give Manny a CEO executive summary only. "
            "Keep it 15 to 30 seconds. Top 3 actions only. No file dumps. "
            "Do not read internal files verbatim."
        )

    elif intent == "expand":
        response = atlas_delegate(user_message)

    elif intent == "scripture":
        history = [{
            "role": "user",
            "content": (
                "SCRIPTURE MODE. Answer as a Christian devotional assistant. "
                "Do not search or quote RAMFAM operational files. "
                "Keep it encouraging, practical, and suitable for Manny's morning reading. "
                f"User request: {user_message}"
            )
        }]
        response = ask_puter(history)

    elif intent == "retrieval":
        response = atlas_delegate(user_message)

    elif intent == "hermes":
        response = ask_hermes(user_message)

    elif lowered_message.startswith("atlas") and any(word in lowered_message for word in [
        "slow", "speed", "speech", "speak faster", "respond faster", "voice", "tts",
        "what should", "what do you think", "improve", "next", "conversation",
        "talk", "feel", "frustrated", "tired", "pressure", "direction"
    ]):
        history = [{"role": "user", "content": user_message}]
        response = ask_puter(history)

    elif lowered_message.startswith("atlas"):
        response = atlas_delegate(user_message)

    elif intent == "chat":
        response = ask_hermes(user_message)

    else:
        orchestrated = atlas_orchestrated_response(user_message, {"source": "normal_chat"})
        response = str(orchestrated.get("orchestrator_result", orchestrated))

    # print("[ATLAS CHAT TIMER] disabled due to Windows console OSError")
    return jsonify({"response": response})

@app.route("/api/crm/prospects")
def api_crm_prospects():
    from crm.crm_skill import search_prospects

    query = request.args.get("q", "")
    status = request.args.get("status", "")
    return jsonify({"prospects": search_prospects(query=query, status=status)})


@app.route("/api/crm/prospects", methods=["POST"])
def api_crm_create_prospect():
    from crm.crm_skill import create_prospect

    data = request.get_json() or {}
    try:
        prospect = create_prospect(data)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400

    return jsonify({"success": True, "prospect": prospect}), 201


@app.route("/api/crm/prospects/<prospect_id>", methods=["PATCH"])
def api_crm_update_prospect(prospect_id):
    from crm.crm_skill import update_prospect

    data = request.get_json() or {}
    try:
        prospect = update_prospect(prospect_id, data)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 404

    return jsonify({"success": True, "prospect": prospect})


@app.route("/api/crm/prospects/<prospect_id>", methods=["DELETE"])
def api_crm_delete_prospect(prospect_id):
    from crm.crm_skill import delete_prospect

    try:
        delete_prospect(prospect_id)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 404

    return jsonify({"success": True})


@app.route("/api/crm/summary")
def api_crm_summary():
    from crm.crm_skill import get_crm_dashboard
    return jsonify({"summary": get_crm_dashboard()})


@app.route("/api/crm/followups")
def api_crm_followups():
    from crm.crm_skill import get_followups
    return jsonify({"followups": get_followups()})


@app.route("/api/crm/timeline")
def api_crm_timeline():
    from crm.crm_skill import get_activity_timeline
    limit = request.args.get("limit", 25)
    return jsonify({"timeline": get_activity_timeline(limit=limit)})


@app.route("/api/crm/prospects/<prospect_id>/touchpoints", methods=["POST"])
def api_crm_add_prospect_touchpoint(prospect_id):
    from crm.crm_skill import add_prospect_touchpoint

    data = request.get_json() or {}
    try:
        touchpoint = add_prospect_touchpoint(prospect_id, data)
    except ValueError as error:
        status = 400 if "required" in str(error).lower() else 404
        return jsonify({"success": False, "error": str(error)}), status

    return jsonify({"success": True, "touchpoint": touchpoint}), 201


@app.route("/api/crm/customers/<customer_id>/touchpoints", methods=["POST"])
def api_crm_add_customer_touchpoint(customer_id):
    from crm.crm_skill import add_customer_touchpoint

    data = request.get_json() or {}
    try:
        touchpoint = add_customer_touchpoint(customer_id, data)
    except ValueError as error:
        status = 400 if "required" in str(error).lower() else 404
        return jsonify({"success": False, "error": str(error)}), status

    return jsonify({"success": True, "touchpoint": touchpoint}), 201


@app.route("/api/crm/customers")
def api_crm_customers():
    from crm.crm_skill import search_customers

    query = request.args.get("q", "")
    status = request.args.get("status", "")
    return jsonify({"customers": search_customers(query=query, status=status)})


@app.route("/api/crm/customers", methods=["POST"])
def api_crm_create_customer():
    from crm.crm_skill import create_customer

    data = request.get_json() or {}
    try:
        customer = create_customer(data)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400

    return jsonify({"success": True, "customer": customer}), 201


@app.route("/api/crm/customers/<customer_id>", methods=["PATCH"])
def api_crm_update_customer(customer_id):
    from crm.crm_skill import update_customer

    data = request.get_json() or {}
    try:
        customer = update_customer(customer_id, data)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 404

    return jsonify({"success": True, "customer": customer})


@app.route("/api/crm/customers/<customer_id>", methods=["DELETE"])
def api_crm_delete_customer(customer_id):
    from crm.crm_skill import delete_customer

    try:
        delete_customer(customer_id)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 404

    return jsonify({"success": True})


@app.route("/api/crm/prospects/<prospect_id>/convert", methods=["POST"])
def api_crm_convert_prospect(prospect_id):
    from crm.crm_skill import convert_prospect_to_customer, update_prospect

    try:
        prospect = update_prospect(prospect_id, {"status": "Closed Won"})
        customer = convert_prospect_to_customer(prospect_id)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 404

    return jsonify({"success": True, "prospect": prospect, "customer": customer})


@app.route("/api/meta/status")
def api_meta_status():
    return jsonify(get_meta_status(env_path=os.path.join(BASE_DIR, ".env")))


@app.route("/dashboard-data")
def dashboard_data():
    from orders.order_skill import load_orders
    from crm.followups import get_follow_up_summary
    from crm.crm_skill import get_prospect_summary

    orders = load_orders()
    followup_summary = get_follow_up_summary()
    prospect_summary = get_prospect_summary()

    paid_revenue = 0
    outstanding_revenue = 0
    paid_orders = 0
    awaiting_payment_orders = 0
    next_money_target = None

    missions_path = os.path.join(BASE_DIR, "agents", "missions.json")
    open_missions = 0

    if os.path.exists(missions_path):
        try:
            with open(missions_path, "r", encoding="utf-8") as f:
                missions = json.load(f)

            if isinstance(missions, list):
                open_missions = len([
                    mission for mission in missions
                    if mission.get("status", "").lower() != "complete"
                ])
        except Exception:
            open_missions = 0

    for order in orders:
        amount = float(order.get("total", 0))
        status = str(order.get("status", "")).lower()

        if "paid" in status:
            paid_revenue += amount
            paid_orders += 1

        elif (
            "awaiting" in status
            or "outstanding" in status
            or "invoice" in status
            or "unpaid" in status
            or "due" in status
        ):
            outstanding_revenue += amount
            awaiting_payment_orders += 1

            if next_money_target is None or amount > next_money_target["amount"]:
                next_money_target = {
                    "customer": order.get("customer", "Unknown Customer"),
                    "product": order.get("product", "Unknown Product"),
                    "amount": amount,
                    "status": order.get("status", "Outstanding")
                }

    hunter_maps_path = os.path.join(BASE_DIR, "data", "hunter_maps_targets.json")
    hunter_pipeline_path = os.path.join(BASE_DIR, "data", "hunter_pipeline.json")
    amanda_outreach_path = os.path.join(BASE_DIR, "data", "amanda_outreach.json")
    neural_nodes_path = os.path.join(BASE_DIR, "data", "neural_nodes.json")

    hunter_maps_data = safe_load_json(hunter_maps_path, {})
    hunter_pipeline_data = safe_load_json(hunter_pipeline_path, {})
    amanda_outreach_data = safe_load_json(amanda_outreach_path, {})
    neural_nodes = safe_load_json(neural_nodes_path, [])

    if not isinstance(neural_nodes, list):
        neural_nodes = []

    maps_targets = hunter_maps_data.get("targets", [])
    hunter_pipeline_records = hunter_pipeline_data.get("pipeline", [])
    outreach_queue = amanda_outreach_data.get("outreach_queue", [])

    hunter_maps_targets = len(maps_targets)
    hunter_high_score_targets = len([
        target for target in maps_targets
        if int(target.get("opportunity_score", 0)) >= 8
    ])
    hunter_maps_sent_to_amanda = len([
        target for target in maps_targets
        if "sent to amanda" in str(target.get("status", "")).lower()
    ])
    hunter_no_website_targets = len([
        target for target in maps_targets
        if "no website" in str(target.get("website_status", "")).lower()
    ])
    hunter_facebook_only_targets = len([
        target for target in maps_targets
        if "facebook" in str(target.get("website_status", "")).lower()
    ])
    hunter_weak_website_targets = len([
        target for target in maps_targets
        if (
            "weak" in str(target.get("website_status", "")).lower()
            or "outdated" in str(target.get("website_status", "")).lower()
            or "old" in str(target.get("website_status", "")).lower()
        )
    ])

    amanda_pending_outreach = len([
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ])
    amanda_contacted_outreach = len([
        item for item in outreach_queue
        if item.get("status") == "Contacted"
    ])

    return jsonify({
        "cave_status": "GREEN",
        "paid_revenue": paid_revenue,
        "outstanding_revenue": outstanding_revenue,
        "pipeline": outstanding_revenue,
        "prospects": prospect_summary["total"],
        "hot_prospects": prospect_summary["hot"],
        "quoted_prospects": prospect_summary["quoted"],
        "invoice_sent_prospects": prospect_summary["invoice_sent"],
        "closed_won_prospects": prospect_summary["won"],
        "closed_lost_prospects": prospect_summary["lost"],
        "followups": followup_summary["total"],
        "followups_due_today": followup_summary["due_today"],
        "followups_overdue": followup_summary["overdue"],
        "followups_upcoming": followup_summary["upcoming"],
        "paid_orders": paid_orders,
        "awaiting_payment_orders": awaiting_payment_orders,
        "next_money_target": next_money_target,
        "open_missions": open_missions,

        "hunter_maps_targets": hunter_maps_targets,
        "hunter_high_score_targets": hunter_high_score_targets,
        "hunter_maps_sent_to_amanda": hunter_maps_sent_to_amanda,
        "hunter_no_website_targets": hunter_no_website_targets,
        "hunter_facebook_only_targets": hunter_facebook_only_targets,
        "hunter_weak_website_targets": hunter_weak_website_targets,
        "hunter_pipeline_records": len(hunter_pipeline_records),
        "amanda_pending_outreach": amanda_pending_outreach,
        "amanda_contacted_outreach": amanda_contacted_outreach,
        "neural_node_count": len(neural_nodes),
        "neural_nodes": neural_nodes
    })


def load_missions_data():
    if not os.path.exists(MISSIONS_FILE):
        return {"missions": []}

    with open(MISSIONS_FILE, "r", encoding="utf-8") as f:
        missions_data = json.load(f)

    if isinstance(missions_data, list):
        return {"missions": missions_data}
    if not isinstance(missions_data, dict):
        return {"missions": []}

    missions_data.setdefault("missions", [])
    return missions_data


def save_missions_data(missions_data):
    os.makedirs(os.path.dirname(MISSIONS_FILE), exist_ok=True)
    with open(MISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(missions_data, f, indent=2)


def mission_runtime_id(mission):
    return str(mission.get("mission_id") or mission.get("runtime_mission_id") or mission.get("id") or "")


def latest_executive_update(mission_id):
    if not mission_id:
        return None
    messages = executive_bus.get_messages()
    matching = [message for message in messages if str(message.get("mission_id")) == str(mission_id)]
    if not matching:
        return None
    return matching[-1]


def mission_with_runtime_update(mission):
    mission = dict(mission)
    update = latest_executive_update(mission_runtime_id(mission))
    if not update:
        mission.setdefault("mission_id", mission_runtime_id(mission))
        mission.setdefault("task", mission.get("mission") or mission.get("title") or "")
        mission.setdefault("latest_result_summary", mission.get("hermes_response", ""))
        mission.setdefault("result_file", "")
        mission.setdefault("timestamp", mission.get("updated_at") or mission.get("created_at") or "")
        return mission

    mission["agent"] = update.get("to") or mission.get("agent")
    mission["status"] = update.get("status") or mission.get("status")
    mission["mission_id"] = update.get("mission_id") or mission_runtime_id(mission)
    mission["task"] = update.get("task") or mission.get("mission") or mission.get("title") or ""
    mission["latest_result_summary"] = update.get("result_summary") or update.get("summary") or ""
    mission["result_file"] = update.get("result_file") or ""
    mission["timestamp"] = update.get("timestamp") or mission.get("updated_at") or mission.get("created_at") or ""
    mission["executive_message_id"] = update.get("message_id")
    return mission


def extract_runtime_summary(result):
    if isinstance(result, dict):
        for key in ("summary", "message", "recommendation", "report", "result_preview", "error"):
            value = result.get(key)
            if value:
                return str(value)
        nested = result.get("result")
        if nested is not result:
            return extract_runtime_summary(nested)
        return json.dumps(result, ensure_ascii=False)[:800]
    if result:
        return str(result)
    return "Atlas routed the mission to the real runtime."


def extract_runtime_result_file(result):
    if isinstance(result, dict):
        for key in ("result_file", "file", "path", "report_file", "output_file"):
            value = result.get(key)
            if value:
                return str(value)
        nested = result.get("result")
        if nested is not result:
            return extract_runtime_result_file(nested)
    return ""


def normalize_runtime_status(result):
    if not isinstance(result, dict):
        return "complete"
    statuses = [str(result.get("status", "")).lower()]
    nested = result.get("result")
    if isinstance(nested, dict):
        statuses.append(str(nested.get("status", "")).lower())

    if any(status in {"blocked", "error", "unknown_agent", "needs_agent", "needs_task"} for status in statuses):
        return "blocked"
    if any(status in {"queued", "dispatched", "working", "pending"} for status in statuses):
        return "working"
    return "complete"


def run_atlas_runtime_for_mission(mission):
    selected_agent = str(mission.get("agent", "")).strip()
    task = mission.get("mission", "")
    mission_id = mission_runtime_id(mission)
    priority = str(mission.get("priority", "normal")).lower()

    executive_bus.record_mission_update(
        selected_agent,
        mission_id,
        task,
        "new",
        "Mission Control accepted the mission and is handing it to Atlas runtime.",
        priority=priority,
    )
    executive_bus.record_mission_update(
        selected_agent,
        mission_id,
        task,
        "working",
        "Atlas is routing through atlas_orchestrator.py and atlas_agent_delegation.py.",
        priority=priority,
    )

    context = {
        "source": "mission_control",
        "mission_id": mission_id,
        "priority": priority,
        "auto_execute": True,
    }
    if selected_agent.lower() != "atlas":
        context["agent"] = selected_agent.lower()

    runtime_result = atlas_orchestrator(task, context)
    routed_agent = runtime_result.get("routed_to") or selected_agent
    status = normalize_runtime_status(runtime_result)
    summary = extract_runtime_summary(runtime_result)
    result_file = extract_runtime_result_file(runtime_result)

    executive_bus.record_mission_update(
        routed_agent,
        mission_id,
        task,
        status,
        summary,
        result_file=result_file,
        priority=priority,
        details=json.dumps(runtime_result, ensure_ascii=False, indent=2)[:4000],
    )

    mission["agent"] = routed_agent
    mission["status"] = status
    mission["runtime_result"] = runtime_result
    mission["latest_result_summary"] = summary
    mission["result_file"] = result_file
    mission["updated_at"] = datetime.now().isoformat(timespec="seconds")
    return runtime_result


@app.route("/api/missions/create", methods=["POST"])
@atlas_login_required
def create_mission():
    data = request.get_json() or {}

    agent = data.get("agent", "").strip()
    priority = data.get("priority", "MEDIUM").strip()
    mission_text = data.get("mission", "").strip()

    if not agent or not mission_text:
        return jsonify({"success": False, "ok": False, "error": "Agent and mission are required."}), 400

    missions_data = load_missions_data()
    missions = missions_data.get("missions", [])
    next_id = max([int(m.get("id", 0)) for m in missions if str(m.get("id", "")).isdigit()] or [0]) + 1
    runtime_mission_id = "MISSION_CONTROL_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    mission = {
        "id": next_id,
        "mission_id": runtime_mission_id,
        "agent": agent,
        "priority": priority,
        "mission": mission_text,
        "task": mission_text,
        "status": "new",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "latest_result_summary": "Mission Control accepted the mission.",
        "result_file": "",
    }

    missions.append(mission)
    missions_data["missions"] = missions
    save_missions_data(missions_data)

    runtime_result = None
    if agent.strip().lower() == "atlas":
        try:
            runtime_result = run_atlas_runtime_for_mission(mission)
            save_missions_data(missions_data)
        except Exception as error:
            mission["status"] = "blocked"
            mission["latest_result_summary"] = str(error)
            mission["updated_at"] = datetime.now().isoformat(timespec="seconds")
            executive_bus.record_mission_update(
                agent,
                runtime_mission_id,
                mission_text,
                "blocked",
                f"Atlas runtime failed: {error}",
                priority=priority.lower(),
            )
            save_missions_data(missions_data)

    return jsonify({
        "success": True,
        "ok": True,
        "status": mission.get("status", "new"),
        "result": "success",
        "message": "WORK ORDER ASSIGNED TO ATLAS RUNTIME" if runtime_result else "WORK ORDER ASSIGNED",
        "mission": mission_with_runtime_update(mission),
        "runtime_result": runtime_result,
    })


@app.route("/api/missions/list")
@atlas_login_required
def list_missions():
    missions_data = load_missions_data()
    missions = [mission_with_runtime_update(mission) for mission in missions_data.get("missions", [])]

    return jsonify({
        "success": True,
        "ok": True,
        "missions": missions,
        "executive_messages": executive_bus.get_messages(),
    })


@app.route("/api/missions/status", methods=["POST"])
@atlas_login_required
def update_mission_status():
    data = request.get_json() or {}

    mission_id = data.get("id")
    new_status = data.get("status", "")

    if not mission_id or not new_status:
        return jsonify({"success": False, "ok": False, "error": "Mission id and status are required."}), 400

    missions_data = load_missions_data()
    selected_mission = None

    for mission in missions_data.get("missions", []):
        if str(mission.get("id")) == str(mission_id):
            mission["status"] = new_status
            mission["updated_at"] = datetime.now().isoformat(timespec="seconds")
            selected_mission = mission
            break

    if not selected_mission:
        return jsonify({"success": False, "ok": False, "error": "Mission not found."}), 404

    save_missions_data(missions_data)

    complete_statuses = {"complete", "completed", "build complete"}
    is_complete = str(new_status).strip().lower() in complete_statuses
    bus_status = "complete" if is_complete else "working"
    executive_bus.record_mission_update(
        selected_mission.get("agent", "Atlas"),
        mission_runtime_id(selected_mission),
        selected_mission.get("mission") or selected_mission.get("task") or "",
        bus_status,
        "Mission status updated from Mission Control.",
        priority=str(selected_mission.get("priority", "normal")).lower(),
    )
    return jsonify({
        "success": True,
        "ok": True,
        "status": "complete" if is_complete else str(new_status),
        "result": "success",
        "message": "BUILD COMPLETE" if is_complete else "MISSION STATUS UPDATED",
        "mission": mission_with_runtime_update(selected_mission),
    })


@app.route("/api/missions/hermes", methods=["POST"])
@atlas_login_required
def mission_to_hermes():
    data = request.get_json() or {}
    mission_id = data.get("id")

    missions_data = load_missions_data()
    selected_mission = None

    for mission in missions_data.get("missions", []):
        if str(mission.get("id")) == str(mission_id):
            selected_mission = mission
            break

    if not selected_mission:
        return jsonify({"success": False, "ok": False, "error": "Mission not found."}), 404

    prompt = f"""
RAMFAM KINGDOM WORK ORDER

Assigned Agent: {selected_mission.get('agent')}
Priority: {selected_mission.get('priority')}
Mission: {selected_mission.get('mission')}

Respond as a practical builder.
Give Manny the next clear implementation steps.
Keep it direct.
"""

    response = ask_hermes(prompt)

    selected_mission["status"] = "Hermes Reviewed"
    selected_mission["hermes_response"] = response
    save_missions_data(missions_data)

    return jsonify({
        "success": True,
        "ok": True,
        "status": "complete",
        "result": "success",
        "message": "BUILD COMPLETE",
        "response": response,
        "mission": selected_mission,
    })
@app.route("/test-hermes")
def test_hermes():
    response = ask_hermes(
        "Atlas is testing Hermes from the RAMFAM KINGDOM dashboard. Confirm the handshake in one short sentence."
    )

    return jsonify({
        "response": response
    })



@app.route("/api/atlas/tts", methods=["POST"])
def atlas_tts():
    import time
    tts_start = time.time()
    from openai import OpenAI
    from dotenv import load_dotenv
    import uuid
    import re

    load_dotenv(os.path.join(BASE_DIR, ".env"))

    data = request.get_json() or {}
    text = data.get("text", "").strip()

    # Clean text before TTS so ATLAS does not read markdown/code symbols out loud
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"#+", "", text)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"_+", " ", text)
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r"\.{3,}", ".", text)
    text = re.sub(r"\n+", " ", text)
    text = text.strip()

    # Voice mode: speak a short summary only. Full text stays on screen.
    if len(text) > 180:
        text = text[:180].rsplit(" ", 1)[0] + ". Details are on screen."

    if not text:
        return jsonify({"success": False, "error": "No text provided."}), 400

    voice_dir = os.path.join(BASE_DIR, "voice_cache")
    os.makedirs(voice_dir, exist_ok=True)

    filename = f"atlas_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(voice_dir, filename)

    client = OpenAI()

    print(f"[ATLAS TTS TIMER] input_chars={len(text)}")
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input=text,
        instructions="Speak as ATLAS: calm, confident, intelligent, warm, and slightly mysterious. Use short natural sentences. Sound like a loyal Chief of Staff, not a narrator. Speak clearly with light Mad Scientist energy, but do not overact. Keep it fast, crisp, and human."
    )

    speech.write_to_file(output_path)

    print(f"[ATLAS TTS TIMER] total={time.time() - tts_start:.2f}s output={filename}")

    return jsonify({
        "success": True,
        "audio_url": "/voice_cache/" + filename
    })


@app.route("/voice_cache/<filename>")
def serve_voice_cache(filename):
    from flask import send_from_directory
    return send_from_directory(os.path.join(BASE_DIR, "voice_cache"), filename)

if __name__ == "__main__":
    app.run(debug=True)









