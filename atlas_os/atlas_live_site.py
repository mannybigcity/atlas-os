# -*- coding: utf-8 -*-
import json
from pathlib import Path
from flask import Flask, jsonify, render_template_string

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BUS = ROOT / "atlas_os" / "communications" / "executive_messages.json"

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Atlas Mission Control</title>
<meta http-equiv="refresh" content="5">
<style>
body{font-family:Arial;background:#eef2f7;padding:30px}
h1{color:#0b3b75}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:15px}
.card{background:white;padding:15px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.1)}
.new{border-left:8px solid #2563eb}
.working{border-left:8px solid #f59e0b}
.complete{border-left:8px solid #16a34a}
.agent{font-size:22px;font-weight:bold}
.status{font-weight:bold}
</style>
</head>
<body>

<h1>ATLAS MISSION CONTROL</h1>
<h3>Executive Team Live</h3>

<div class="grid">
{% for m in messages %}
<div class="card {{m.status}}">
<div class="agent">{{m.to}}</div>
<p><b>Status:</b> {{m.status}}</p>
<p><b>Mission:</b> {{m.mission_id}}</p>
<p><b>Task:</b> {{m.summary}}</p>
<p><b>Next:</b> {{m.next_action}}</p>
{% if m.result_summary %}
<hr>
<p>{{m.result_summary}}</p>
{% endif %}
</div>
{% endfor %}
</div>

</body>
</html>
"""

@app.route("/")
def home():
    if BUS.exists():
        messages=json.loads(BUS.read_text(encoding="utf-8-sig"))
    else:
        messages=[]
    return render_template_string(HTML,messages=messages)

@app.route("/api/messages")
def api():
    if BUS.exists():
        return jsonify(json.loads(BUS.read_text(encoding="utf-8-sig")))
    return jsonify([])

app.run(host="127.0.0.1",port=5055)
