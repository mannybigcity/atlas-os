# skills/datetime_skill.py — PUTER's first skill: telling the time

from datetime import datetime

def get_current_time():
    """Return the current date and time as a friendly string."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")

# --- Built-in test (runs only when you run THIS file directly) ---
if __name__ == "__main__":
    print(get_current_time())