from skills.atlas_advisor import atlas_advisor


def atlas_strategic_command(question="What should we work on today?"):

    advisor_report = atlas_advisor()

    return f"""
🦁 ATLAS STRATEGIC COMMAND

Question:
{question}

=================================

EXECUTIVE ANALYSIS

{advisor_report}

=================================

ATLAS DECISION

Based on current Kingdom status and Mason's analysis:

1. Focus on the highest-value action.
2. Protect Manny's attention.
3. Revenue before expansion.
4. Complete existing systems before creating new systems.

EXECUTIVE ORDER

Complete the next Kingdom-awareness milestone before building additional agents.
"""


if __name__ == "__main__":
    print(
        atlas_strategic_command(
            "What should we work on today?"
        )
    )