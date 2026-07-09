from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.atlas_delegation_router import ask_kingdom_brain, atlas_delegate, classify_atlas_request


def test_general_memory_question_returns_personal_summary():
    result = ask_kingdom_brain("Atlas, what do you remember about me?")
    assert "Atlas consulted 99_MEMORY first" in result
    assert "ATLAS_PERSONAL_MEMORY_SUMMARY.md" in result
    assert "Mission:" in result
    assert "Current focus:" in result


def test_memory_lookup_uses_words_not_substrings():
    result = ask_kingdom_brain("Atlas, who is my wife?")
    assert "- Wife:" in result
    assert "- Son:" not in result


def test_family_and_purpose_questions_route_to_memory():
    cases = [
        "Atlas, what is Danica nickname?",
        "Atlas, why does ATLAS exist?",
        "Atlas, who am I?",
    ]
    for text in cases:
        assert classify_atlas_request(text) == "kingdom_brain"


def test_json_memory_files_are_consulted_for_structured_facts():
    result = atlas_delegate("Atlas, what is Deleana current goal?")
    assert "FAMILY.json" in result
    assert "Bring Deleana home from work by building income through ATLAS" in result


def test_text_memory_files_are_consulted_for_plain_text_facts():
    result = atlas_delegate("Atlas, what does SIS believe every project tells?")
    assert "Deleana_website_ideas.txt" in result
    assert "every project tells a story" in result


if __name__ == "__main__":
    tests = [
        test_general_memory_question_returns_personal_summary,
        test_memory_lookup_uses_words_not_substrings,
        test_family_and_purpose_questions_route_to_memory,
        test_json_memory_files_are_consulted_for_structured_facts,
        test_text_memory_files_are_consulted_for_plain_text_facts,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: PASS")
    print("ATLAS MEMORY VERIFIED")
