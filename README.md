# PUTER 🤖

My personal AI assistant — built from scratch in Python.
PUTER has a memory, an AI brain, skills, and a web-based chat dashboard.

## How to start PUTER
1. Open the PUTER folder in VS Code.
2. Open a terminal (Terminal -> New Terminal).
3. Turn on the virtual environment:
       .\venv\Scripts\Activate.ps1
   You should see "(venv)" at the start of the prompt.
4. Start the server:
       python app.py
5. Open your browser to: http://127.0.0.1:5000
6. To stop PUTER: click the terminal and press Ctrl + C.

## Folder map
- memory/    -> long-term facts PUTER remembers (memory.json)
- agents/    -> the AI assistant logic (assistant.py)
- skills/    -> abilities PUTER can use (datetime_skill.py)
- workflows/ -> multi-step automations (coming in a later phase)
- ui/        -> the chat dashboard (index.html)
- logs/      -> saved conversations (conversation.json)
- config/    -> settings + the secret API key (.env -- never share this!)
- app.py     -> the web server that ties it all together

## How PUTER works (short version)
1. You type a message in the browser (ui/index.html).
2. app.py receives it at the /chat route.
3. It calls ask_puter() in agents/assistant.py.
4. The agent gathers memory + skill results + the whole conversation,
   then sends it to the OpenAI brain.
5. The reply is shown in the browser and saved to logs/.

## Navigation routes
- `/` or `/neural` -> ATLAS Neural Core.
- `/crm` -> David CRM Command Center.
- `/commerce-command-center` -> newest local `commerce_approval_dashboard.html` under `RAMFAM_KINGDOM_BRAIN/06_MISSIONS/commerce_pipeline_runner/commerce_pipeline_mission_*`. If no dashboard exists, it shows "No Commerce Mission Dashboard Found."
- `/ramfam` -> Atlas Brain.
- `/kingdom` -> RamFam Kingdom.

## Built with
- Python, Flask (web server), OpenAI API (brain), python-dotenv (secret key)

## Fresh-computer setup (if I ever rebuild)
- Create venv:     python -m venv venv
- Activate venv:   .\venv\Scripts\Activate.ps1
- Install tools:   pip install openai python-dotenv flask
- Add the key to:  config/.env   (OPENAI_API_KEY=sk-...)