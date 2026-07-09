from pathlib import Path
import json

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN_ROOT = ROOT / "RAMFAM_KINGDOM_BRAIN"
MEMORY_ROOT = BRAIN_ROOT / "99_MEMORY"

# Legacy paths are kept so older Atlas calls continue to work while the new
# deterministic registry becomes the source for executive/task routing.
MEMORY_PATHS = {
    "company": ROOT / "memory" / "memory.json",
    "agents": ROOT / "memory" / "memory" / "agents.json",
    "missions": ROOT / "missions" / "missions.json",
    "clients": ROOT / "CLIENTS",
    "crm": ROOT / "crm",
    "skills": ROOT / "skills",
    "governing_documents": BRAIN_ROOT,
}

GOVERNING_DOCUMENTS = {
    "ATLAS_CONSTITUTION_V2": {
        "title": "Atlas Constitution V2",
        "path": BRAIN_ROOT / "ATLAS_CONSTITUTION_V2.md",
        "layer": "constitution",
    },
    "KNOWLEDGE_ENGINE_SPEC": {
        "title": "Knowledge Engine Specification",
        "path": BRAIN_ROOT / "KNOWLEDGE_ENGINE_SPEC.md",
        "layer": "knowledge_engine",
    },
    "EXECUTIVE_HANDBOOK": {
        "title": "Executive Handbook",
        "path": BRAIN_ROOT / "EXECUTIVE_HANDBOOK.md",
        "layer": "executive_operations",
    },
    "EXECUTIVE_OFFICE_SPEC": {
        "title": "Executive Office Specification",
        "path": BRAIN_ROOT / "EXECUTIVE_OFFICE_SPEC.md",
        "layer": "executive_operations",
    },
    "ATLAS_MASTER_IMPLEMENTATION_PLAN": {
        "title": "Atlas Master Implementation Plan",
        "path": BRAIN_ROOT / "ATLAS_MASTER_IMPLEMENTATION_PLAN.md",
        "layer": "implementation",
    },
    "ATLAS_DEVELOPMENT_STANDARD": {
        "title": "Atlas Development Standard",
        "path": BRAIN_ROOT / "ATLAS_DEVELOPMENT_STANDARD.md",
        "layer": "development",
    },
}

KNOWLEDGE_AREAS = {
    "architecture": MEMORY_ROOT / "company_memory" / "standard_operating_procedures",
    "automation": ROOT / "skills",
    "brand": MEMORY_ROOT / "company_memory" / "branding",
    "budget": MEMORY_ROOT / "company_memory" / "pricing",
    "business_growth": MEMORY_ROOT / "company_memory" / "services",
    "client_communication": MEMORY_ROOT / "client_memory" / "communication_history",
    "client_operations": MEMORY_ROOT / "client_memory" / "project_references",
    "client_portal": ROOT / "ui",
    "community": MEMORY_ROOT / "company_memory" / "company_history",
    "compliance": MEMORY_ROOT / "company_memory" / "policies",
    "crm": ROOT / "crm",
    "customer_command": ROOT / "CLIENTS",
    "customer_success": MEMORY_ROOT / "client_memory" / "important_decisions",
    "finance": MEMORY_ROOT / "company_memory" / "pricing",
    "governance": MEMORY_ROOT / "company_memory" / "constitution",
    "knowledge_engine": BRAIN_ROOT / "KNOWLEDGE_ENGINE_SPEC.md",
    "marketplace": ROOT / "skills",
    "marketing": MEMORY_ROOT / "company_memory" / "branding",
    "opportunity_discovery": ROOT / "mason_workspace",
    "outreach": ROOT / "skills",
    "research": MEMORY_ROOT / "archive_memory" / "lessons_learned",
    "revenue": MEMORY_ROOT / "company_memory" / "products",
    "sales": MEMORY_ROOT / "company_memory" / "services",
    "treasury": MEMORY_ROOT / "company_memory" / "pricing",
    "trend_intelligence": MEMORY_ROOT / "archive_memory" / "previous_implementations",
    "ux": ROOT / "ui",
    "website": ROOT / "sis-website",
}

EXECUTIVE_ROUTES = {
    "atlas": {
        "department": "executive_coordination",
        "required_documents": [
            "ATLAS_CONSTITUTION_V2",
            "EXECUTIVE_HANDBOOK",
            "EXECUTIVE_OFFICE_SPEC",
            "ATLAS_MASTER_IMPLEMENTATION_PLAN",
        ],
        "required_knowledge": ["governance"],
        "optional_documents": ["KNOWLEDGE_ENGINE_SPEC", "ATLAS_DEVELOPMENT_STANDARD"],
        "optional_knowledge": ["architecture"],
    },
    "mason": {
        "department": "architecture",
        "required_documents": [
            "ATLAS_DEVELOPMENT_STANDARD",
            "ATLAS_MASTER_IMPLEMENTATION_PLAN",
            "KNOWLEDGE_ENGINE_SPEC",
        ],
        "required_knowledge": ["architecture", "automation"],
        "optional_documents": ["ATLAS_CONSTITUTION_V2"],
        "optional_knowledge": ["governance"],
    },
    "hunter": {
        "department": "revenue",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["revenue", "sales", "business_growth"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["crm"],
    },
    "micah": {
        "department": "marketing",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["marketing", "brand"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["website"],
    },
    "david": {
        "department": "crm",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["crm", "customer_command", "client_operations"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["client_communication"],
    },
    "amanda": {
        "department": "customer_experience",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["outreach", "marketplace", "client_communication"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["customer_success"],
    },
    "gideon": {
        "department": "finance",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["finance", "treasury", "budget"],
        "optional_documents": ["ATLAS_CONSTITUTION_V2"],
        "optional_knowledge": ["governance"],
    },
    "oracle": {
        "department": "research",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["research", "trend_intelligence"],
        "optional_documents": ["KNOWLEDGE_ENGINE_SPEC"],
        "optional_knowledge": ["archive"],
    },
    "scout": {
        "department": "lead_generation",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["opportunity_discovery"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["sales"],
    },
    "taylor": {
        "department": "website_design",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["website", "ux", "client_portal"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["brand"],
    },
    "ranger": {
        "department": "customer_success",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["customer_success"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["client_operations"],
    },
    "lucky": {
        "department": "media_community",
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["brand", "community"],
        "optional_documents": ["EXECUTIVE_HANDBOOK"],
        "optional_knowledge": ["marketing"],
    },
    "solomon": {
        "department": "governance",
        "required_documents": [
            "ATLAS_CONSTITUTION_V2",
            "EXECUTIVE_HANDBOOK",
            "ATLAS_DEVELOPMENT_STANDARD",
        ],
        "required_knowledge": ["governance", "compliance"],
        "optional_documents": ["KNOWLEDGE_ENGINE_SPEC", "EXECUTIVE_OFFICE_SPEC"],
        "optional_knowledge": ["archive"],
    },
}

DEPARTMENT_ROUTES = {
    "architecture": {
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["architecture"],
    },
    "governance": {
        "required_documents": ["ATLAS_CONSTITUTION_V2"],
        "required_knowledge": ["governance", "compliance"],
    },
    "revenue": {
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["revenue", "sales"],
    },
}

TASK_ROUTES = {
    "knowledge_engine": {
        "required_documents": ["KNOWLEDGE_ENGINE_SPEC", "ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["knowledge_engine"],
    },
    "governance": {
        "required_documents": ["ATLAS_CONSTITUTION_V2", "EXECUTIVE_HANDBOOK"],
        "required_knowledge": ["governance", "compliance"],
    },
    "sales": {
        "required_documents": [],
        "required_knowledge": ["sales", "revenue"],
    },
    "website": {
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["website", "ux"],
    },
    "crm": {
        "required_documents": ["ATLAS_DEVELOPMENT_STANDARD"],
        "required_knowledge": ["crm", "client_operations"],
    },
}


def normalize_key(value):
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def path_status(path):
    path = Path(path)
    return {
        "path": str(path),
        "exists": path.exists(),
        "type": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
    }


def _document_record(document_id, optional=False):
    source = GOVERNING_DOCUMENTS[document_id]
    status = path_status(source["path"])
    return {
        "id": document_id,
        "title": source["title"],
        "path": status["path"],
        "exists": status["exists"],
        "type": status["type"],
        "layer": source["layer"],
        "optional": optional,
    }


def _knowledge_record(knowledge_id, optional=False):
    path = KNOWLEDGE_AREAS.get(knowledge_id, BRAIN_ROOT / knowledge_id)
    status = path_status(path)
    return {
        "id": knowledge_id,
        "path": status["path"],
        "exists": status["exists"],
        "type": status["type"],
        "optional": optional,
    }


def _extend_unique(target, values):
    for value in values:
        if value and value not in target:
            target.append(value)


def knowledge_registry():
    return {
        "version": "1.0",
        "purpose": "Load only the governed knowledge required for the executive and task.",
        "uses_ai": False,
        "uses_vector_search": False,
        "governing_documents": {
            document_id: {
                "title": document["title"],
                "path": str(document["path"]),
                "exists": document["path"].exists(),
                "layer": document["layer"],
            }
            for document_id, document in GOVERNING_DOCUMENTS.items()
        },
        "knowledge_areas": {
            knowledge_id: path_status(path)
            for knowledge_id, path in KNOWLEDGE_AREAS.items()
        },
        "executives": EXECUTIVE_ROUTES,
        "departments": DEPARTMENT_ROUTES,
        "task_types": TASK_ROUTES,
        "routing_order": ["executive", "department", "task_type"],
    }


def load_knowledge_for(executive=None, department=None, task_type=None, include_optional=False):
    """Return the smallest deterministic knowledge bundle for a request.

    Routing order is intentionally explicit and cheap:
    1. Executive baseline gives each leader their normal required context.
    2. Department lane adds required context for cross-functional work.
    3. Task type adds only the documents/knowledge specific to the work.
    Optional context is excluded unless include_optional=True to protect tokens.
    """
    executive_key = normalize_key(executive)
    department_key = normalize_key(department)
    task_key = normalize_key(task_type)

    required_documents = []
    required_knowledge = []
    optional_documents = []
    optional_knowledge = []
    notes = []

    executive_route = EXECUTIVE_ROUTES.get(executive_key)
    if executive_route:
        department_key = department_key or executive_route["department"]
        _extend_unique(required_documents, executive_route.get("required_documents", []))
        _extend_unique(required_knowledge, executive_route.get("required_knowledge", []))
        _extend_unique(optional_documents, executive_route.get("optional_documents", []))
        _extend_unique(optional_knowledge, executive_route.get("optional_knowledge", []))
    else:
        notes.append("No exact executive route found; using minimal governance fallback.")

    department_route = DEPARTMENT_ROUTES.get(department_key)
    if department_route:
        _extend_unique(required_documents, department_route.get("required_documents", []))
        _extend_unique(required_knowledge, department_route.get("required_knowledge", []))

    task_route = TASK_ROUTES.get(task_key)
    if task_route:
        _extend_unique(required_documents, task_route.get("required_documents", []))
        _extend_unique(required_knowledge, task_route.get("required_knowledge", []))

    if not required_documents:
        required_documents = ["ATLAS_DEVELOPMENT_STANDARD"]

    document_records = [_document_record(document_id, optional=False) for document_id in required_documents]
    knowledge_records = [_knowledge_record(knowledge_id, optional=False) for knowledge_id in required_knowledge]

    if include_optional:
        for document_id in optional_documents:
            if document_id not in required_documents:
                document_records.append(_document_record(document_id, optional=True))
        for knowledge_id in optional_knowledge:
            if knowledge_id not in required_knowledge:
                knowledge_records.append(_knowledge_record(knowledge_id, optional=True))

    return {
        "executive": executive_key or None,
        "department": department_key or None,
        "task_type": task_key or None,
        "include_optional": include_optional,
        "documents": document_records,
        "knowledge": knowledge_records,
        "notes": notes,
    }


def atlas_knowledge_map():
    return {name: path_status(path) for name, path in MEMORY_PATHS.items()}


def load_json_memory(name):
    path = MEMORY_PATHS.get(name)
    if not path or not Path(path).is_file():
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except Exception as error:
        return {"error": str(error), "path": str(path)}


def mission_context(mission_type="general"):
    mission_type = str(mission_type).lower()
    needed = ["company", "agents", "missions"]

    if mission_type in ["client", "crm", "customer"]:
        needed += ["clients", "crm"]
    if mission_type in ["build", "code", "system", "mason"]:
        needed += ["skills"]

    return {
        "mission_type": mission_type,
        "load_only": needed,
        "paths": {name: path_status(MEMORY_PATHS[name]) for name in needed},
        "knowledge_route": load_knowledge_for(
            executive="mason" if mission_type in ["build", "code", "system", "mason"] else None,
            task_type="crm" if mission_type in ["client", "crm", "customer"] else mission_type,
        ),
    }


if __name__ == "__main__":
    demo = {
        "registry_summary": {
            "executives": len(EXECUTIVE_ROUTES),
            "governing_documents": len(GOVERNING_DOCUMENTS),
            "task_types": sorted(TASK_ROUTES),
        },
        "mason_knowledge_engine": load_knowledge_for("mason", task_type="knowledge_engine"),
        "solomon_governance": load_knowledge_for("solomon", task_type="governance"),
    }
    print(json.dumps(demo, indent=2))
