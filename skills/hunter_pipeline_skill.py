import json
from pathlib import Path


HUNTER_PIPELINE_PATH = Path("data") / "hunter_pipeline.json"


def load_pipeline():
    if not HUNTER_PIPELINE_PATH.exists():
        return None

    with open(HUNTER_PIPELINE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_pipeline(data):
    with open(HUNTER_PIPELINE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def hunter_show_pipeline():
    data = load_pipeline()

    if data is None:
        return hunter_missing_pipeline_error()

    pipeline = data.get("pipeline", [])

    report = "🦅 HUNTER PIPELINE\n\n"

    if not pipeline:
        report += "No pipeline records found."
        return report

    for item in pipeline:
        report += format_pipeline_item(item)

    return report


def hunter_add_to_pipeline(
    lead_name,
    value=0,
    stage="New",
    notes="No notes"
):
    data = load_pipeline()

    if data is None:
        return hunter_missing_pipeline_error()

    clean_name = lead_name.strip()

    if not clean_name:
        return "🦅 HUNTER ERROR\n\nNo lead name provided."

    pipeline = data.get("pipeline", [])

    for item in pipeline:
        if item.get("lead_name", "").lower() == clean_name.lower():
            return (
                "🦅 HUNTER NOTICE\n\n"
                f"Lead already exists in pipeline:\n{clean_name}"
            )

    pipeline.append({
        "lead_name": clean_name,
        "value": value,
        "stage": stage,
        "notes": notes
    })

    data["pipeline"] = pipeline
    save_pipeline(data)

    return (
        "🦅 PIPELINE RECORD ADDED\n\n"
        f"Lead: {clean_name}\n"
        f"Value: ${value}\n"
        f"Stage: {stage}"
    )


def hunter_update_pipeline_stage(lead_name, new_stage):
    data = load_pipeline()

    if data is None:
        return hunter_missing_pipeline_error()

    clean_name = lead_name.strip().lower()
    clean_stage = normalize_stage(new_stage)

    pipeline = data.get("pipeline", [])

    for item in pipeline:
        item_name = item.get("lead_name", "").lower()

        if clean_name in item_name or item_name in clean_name:
            old_stage = item.get("stage", "Unknown")
            item["stage"] = clean_stage

            save_pipeline(data)

            return (
                "🦅 PIPELINE STAGE UPDATED\n\n"
                f"Lead: {item.get('lead_name')}\n"
                f"Old Stage: {old_stage}\n"
                f"New Stage: {clean_stage}"
            )

    return (
        "🦅 HUNTER ERROR\n\n"
        f"No pipeline record found matching:\n{lead_name}"
    )


def hunter_pipeline_report():
    data = load_pipeline()

    if data is None:
        return hunter_missing_pipeline_error()

    pipeline = data.get("pipeline", [])

    stage_counts = {}

    for item in pipeline:
        stage = item.get("stage", "Unknown")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    report = "🦅 HUNTER PIPELINE REPORT\n\n"
    report += f"Total Pipeline Records: {len(pipeline)}\n\n"

    report += "STAGE COUNTS:\n"

    if not stage_counts:
        report += "- None\n"
    else:
        for stage, count in stage_counts.items():
            report += f"- {stage}: {count}\n"

    return report


def normalize_stage(stage):
    cleaned = " ".join(stage.strip().split())

    stage_map = {
        "new": "New",
        "sent to hunter": "Sent To Hunter",
        "sent to amanda": "Sent To Amanda",
        "contacted": "Contacted",
        "interested": "Interested",
        "proposal sent": "Proposal Sent",
        "negotiating": "Negotiating",
        "closed won": "Closed Won",
        "won": "Closed Won",
        "closed lost": "Closed Lost",
        "lost": "Closed Lost"
    }

    lowered = cleaned.lower()

    if lowered in stage_map:
        return stage_map[lowered]

    return " ".join(word.capitalize() for word in cleaned.split())


def format_pipeline_item(item):
    return (
        f"- {item.get('lead_name', 'Unknown Lead')}\n"
        f"  Value: ${item.get('value', 0)}\n"
        f"  Stage: {item.get('stage', 'Unknown')}\n"
        f"  Notes: {item.get('notes', 'No notes')}\n\n"
    )


def hunter_missing_pipeline_error():
    return (
        "🦅 HUNTER ERROR\n\n"
        "I could not find Hunter's pipeline database.\n\n"
        "Expected file:\n"
        "data/hunter_pipeline.json"
    )


if __name__ == "__main__":
    print(hunter_show_pipeline())