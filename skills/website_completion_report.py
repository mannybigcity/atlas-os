from datetime import datetime

def website_completion_report(project_name="Website Prototype"):
    return f"""
PROJECT COMPLETE

Project:
{project_name}

Built By:
Taylor

Preview:
http://127.0.0.1:5000/prototype/

File Location:
C:\\Users\\User\\Desktop\\PUTER\\prototype

Files Updated:
- C:\\Users\\User\\Desktop\\PUTER\\prototype\\index.html
- C:\\Users\\User\\Desktop\\PUTER\\prototype\\css\\style.css
- C:\\Users\\User\\Desktop\\PUTER\\prototype\\js\\script.js

Timestamp:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""".strip()
