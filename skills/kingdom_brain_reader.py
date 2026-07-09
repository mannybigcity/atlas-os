from pathlib import Path


KINGDOM_BRAIN_PATH = Path("RAMFAM_KINGDOM_BRAIN")


def read_kingdom_brain(max_chars=100000):
    if not KINGDOM_BRAIN_PATH.exists():
        return (
            f"KINGDOM BRAIN STATUS: Folder not found.\n"
            f"Expected location: {KINGDOM_BRAIN_PATH.resolve()}"
        )

    markdown_files = sorted(
        KINGDOM_BRAIN_PATH.rglob("*.md")
    )

    if not markdown_files:
        return (
            "KINGDOM BRAIN STATUS: Folder found, "
            "but no markdown files were discovered."
        )

    sections = []

    for file_path in markdown_files:
        try:
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            relative_path = file_path.relative_to(
                KINGDOM_BRAIN_PATH
            )

            sections.append(
                f"""
=========================
FILE: {relative_path}
=========================

{content}
"""
            )

        except Exception as error:
            sections.append(
                f"""
=========================
FILE: {file_path.name}
=========================

ERROR READING FILE:
{error}
"""
            )

    full_context = "\n".join(sections)

    if len(full_context) > max_chars:
        full_context = (
            full_context[:max_chars]
            + "\n\n[Kingdom Brain truncated due to size.]"
        )

    return full_context