from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from agents.assistant import ask_puter
from agents.atlas_delegation_router import atlas_delegate
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

import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(BASE_DIR, "ui")
ASSETS_DIR = os.path.join(UI_DIR, "assets")
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


@app.route("/")
def home():
    return send_from_directory(UI_DIR, "atlas_neural_core.html")


@app.route("/neural")
def atlas_neural_core():
    return send_from_directory(UI_DIR, "atlas_neural_core.html")


@app.route("/ramfam")
def atlas_brain():
    return send_from_directory(UI_DIR, "atlas_brain.html")


@app.route("/kingdom")
def ramfam_kingdom():
    return send_from_directory(UI_DIR, "ramfam_kingdom.html")


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
    data = request.get_json()
    user_message = data.get("message", "")
    lowered_message = user_message.lower().strip()

    if "uploaded files" in lowered_message or "uploads" in lowered_message:
        uploads = list_uploaded_files()

        if not uploads:
            response = "No uploaded files found yet. Use the 📎 Upload button to add docs, images, audio, or video."
        else:
            lines = ["📎 Upload Center files Atlas can see:"]
            for item in uploads[:12]:
                lines.append(f"- {item['name']} | {item['category']} | {item['path']}")
            response = "\n".join(lines)

    elif lowered_message.startswith("mason, ask hermes"):
        task = user_message.replace("Mason, ask Hermes to", "").strip()
        response = mason_ask_hermes(task)

    elif lowered_message.startswith("atlas"):
        response = atlas_delegate(user_message)

    else:
        history = [{"role": "user", "content": user_message}]
        response = ask_puter(history)

    return jsonify({"response": response})


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


@app.route("/test-hermes")
def test_hermes():
    response = ask_hermes(
        "Atlas is testing Hermes from the RAMFAM KINGDOM dashboard. Confirm the handshake in one short sentence."
    )

    return jsonify({
        "response": response
    })


if __name__ == "__main__":
    app.run(debug=True)