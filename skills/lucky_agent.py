from datetime import datetime


def lucky_agent(task):
    """
    Lucky: Kingdom DJ and Atmosphere Director.

    Designs safe, practical atmosphere, music, livestream mood,
    milestone, intro, and celebration recommendations for RAMFAM KINGDOM,
    SIS Custom Creations, FRESH Apparel, and ATLAS.

    This worker does not send messages, publish posts, spend money,
    contact customers, delete files, or use external APIs.
    """
    if not isinstance(task, str):
        task = str(task)

    clean_task = task.strip()

    approval_keywords = [
        "public",
        "publish",
        "post",
        "social media",
        "livestream",
        "live stream",
        "customer",
        "client",
        "financial",
        "spend",
        "buy",
        "purchase",
        "paid",
        "ad",
        "advertisement",
        "sponsor",
        "legal",
        "reputation",
        "press",
        "announcement",
        "email",
        "text",
        "dm",
        "message",
        "contact",
        "release",
        "brand",
        "promotion",
        "promo",
        "sale",
    ]

    lowered_task = clean_task.lower()
    approval_required = any(keyword in lowered_task for keyword in approval_keywords)

    if not clean_task:
        summary = "Lucky received an empty task and cannot design atmosphere direction without more context."
        recommendation = (
            "Provide the event, audience, mood goal, location, timing, and whether this is for "
            "RAMFAM KINGDOM, SIS Custom Creations, FRESH Apparel, or ATLAS."
        )
        status = "needs_task"
    else:
        status = "ready"
        summary = (
            "Lucky reviewed the task and prepared a safe atmosphere direction focused on energy, "
            "celebration, music mood, and practical next steps without taking external action."
        )

        if "intro" in lowered_task:
            recommendation = (
                "Create a short high-energy intro with a clean opening line, upbeat instrumental mood, "
                "one Kingdom-centered phrase, and a clear transition into the main speaker or segment. "
                "Keep it positive, family-safe, and brand-aligned."
            )
        elif "milestone" in lowered_task or "celebration" in lowered_task or "celebrate" in lowered_task:
            recommendation = (
                "Frame the moment as a Kingdom win: name the milestone, recognize the people involved, "
                "use an upbeat celebratory music cue, invite gratitude, and close with the next mission-focused step."
            )
        elif "livestream" in lowered_task or "live stream" in lowered_task:
            recommendation = (
                "Use a clean pre-show atmosphere: warm welcome slide, upbeat but non-distracting music, "
                "clear start-time messaging, a brief host intro, and a smooth transition into the main content. "
                "Get Manny approval before anything public goes live."
            )
        elif "music" in lowered_task or "playlist" in lowered_task or "dj" in lowered_task:
            recommendation = (
                "Build the music direction around the audience and purpose: start welcoming, rise into energetic, "
                "hold a productive groove, and close with celebration. Use clean, brand-safe tracks only."
            )
        elif "fresh" in lowered_task:
            recommendation = (
                "Shape the atmosphere around hope, encouragement, and service. Use uplifting clean music, "
                "faith-forward language where appropriate, and connect the moment to the FRESH mission: "
                "One Shirt. One Meal."
            )
        elif "sis" in lowered_task or "custom creations" in lowered_task:
            recommendation = (
                "Shape the atmosphere around creativity, craftsmanship, and customer excitement. Highlight the "
                "custom work, keep the energy professional and fun, and prepare a short celebration cue for finished orders."
            )
        elif "atlas" in lowered_task:
            recommendation = (
                "Support ATLAS with calm, organized, executive atmosphere direction: clean intro, focused background mood, "
                "clear transition points, and a concise closing cue that reinforces next actions."
            )
        else:
            recommendation = (
                "Use a practical atmosphere plan: define the audience, choose the desired energy level, select a clean "
                "music mood, prepare a short intro or announcement, identify the celebration moment, and confirm whether "
                "Manny approval is needed before anything public or customer-facing happens."
            )

    return {
        "agent": "Lucky",
        "status": status,
        "task": clean_task,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(lucky_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
