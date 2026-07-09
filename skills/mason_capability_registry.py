"""Mason capability registry.

This module declares Mason's permitted capabilities and approval boundaries
for Atlas orchestration inside PUTER.
"""

from __future__ import annotations

import json
from typing import Any


MASON_CAPABILITY_REGISTRY: dict[str, Any] = {
    "can_write_files": True,
    "can_read_files": True,
    "can_run_python": True,
    "can_verify_outputs": True,
    "can_retry_failed_tasks": True,
    "can_plan_projects": True,
    "can_store_memory": True,
    "can_report_to_atlas": True,
    "allowed_dirs": [
        "agents",
        "skills",
        "ui",
        "mason_workspace",
    ],
    "approval_required_for": [
        "external_messages",
        "money_actions",
        "deleting_files",
        "customer_contact",
    ],
}


def get_capability_registry() -> dict[str, Any]:
    """Return Mason's capability registry."""
    return MASON_CAPABILITY_REGISTRY.copy()


if __name__ == "__main__":
    print(json.dumps(get_capability_registry(), indent=4))
