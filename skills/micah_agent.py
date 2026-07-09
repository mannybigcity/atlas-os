from datetime import datetime

AGENT_NAME = "Micah"

def micah_agent(task, context=None):
    task_text = str(task or "").strip()
    lowered = task_text.lower()
    context = context or {}

    approval_required = any(word in lowered for word in [
        "publish now", "post now", "send now", "run ad", "spend money", "contact customer", "delete file"
    ])

    if not task_text:
        return {
            "agent": AGENT_NAME,
            "status": "needs_task",
            "summary": "Micah needs a specific product, niche, or design direction.",
            "recommendation": "Ask Micah for shirt concepts, Etsy design concepts, PNG/SVG ideas, mockups, or visual directions.",
            "approval_required": False,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    concepts = [
        {
            "product_title": "Grace Built Different",
            "visual_description": "Oversized varsity-style text with a distressed vintage streetwear finish. Main words stacked bold: GRACE / BUILT / DIFFERENT. Small cross detail worked into the letterform.",
            "typography": "Heavy collegiate block font mixed with a small handwritten faith accent.",
            "color_palette": "Cream ink on black, washed charcoal, sand, or military green shirt.",
            "mockup_recommendation": "Use black oversized tee, flat lay, and lifestyle mockup with jeans and sneakers.",
            "why_it_stands_out": "It feels like modern streetwear instead of generic church merch."
        },
        {
            "product_title": "Kingdom Over Culture",
            "visual_description": "Bold arched headline with minimal crown/cross mark, distressed print texture, and small scripture-inspired footer text.",
            "typography": "Condensed athletic headline with small serif footer.",
            "color_palette": "Bone, faded red, navy, and vintage gold.",
            "mockup_recommendation": "Vintage wash tee or hoodie mockup.",
            "why_it_stands_out": "Strong faith message with patriotic/streetwear energy."
        },
        {
            "product_title": "Still Standing By Grace",
            "visual_description": "Large centered text with cracked ink effect, subtle sunrise line art behind the words, and small cross at bottom.",
            "typography": "Bold sans serif with worn texture and soft script accent for 'Grace'.",
            "color_palette": "White, muted gold, and charcoal.",
            "mockup_recommendation": "Heather gray tee and comfort colors mockup.",
            "why_it_stands_out": "Connects with people who have been through hard seasons but still have faith."
        },
        {
            "product_title": "Faith Moves Different",
            "visual_description": "Minimal front chest mark plus large back print with bold stacked typography and motion lines.",
            "typography": "Modern bold streetwear font, clean spacing, oversized back layout.",
            "color_palette": "Black and cream, or navy and faded white.",
            "mockup_recommendation": "Front/back mockup for Shopify and Etsy.",
            "why_it_stands_out": "Feels premium and wearable, not overly religious or cheesy."
        },
        {
            "product_title": "Saved Not Soft",
            "visual_description": "Hard-hitting faith statement with boxing/gym-inspired layout, distressed badge shape, and subtle cross detail.",
            "typography": "Bold condensed type with gritty athletic styling.",
            "color_palette": "Black, off-white, deep red.",
            "mockup_recommendation": "Streetwear gym-style tee mockup.",
            "why_it_stands_out": "Appeals to Christian men, dads, and faith-driven entrepreneurs."
        }
    ]

    return {
        "agent": AGENT_NAME,
        "status": "concepts_ready",
        "task": task_text,
        "summary": "Micah created 5 premium Christian streetwear shirt concepts.",
        "design_concepts": concepts,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(micah_agent("Micah create 5 Christian streetwear shirt concepts"))
