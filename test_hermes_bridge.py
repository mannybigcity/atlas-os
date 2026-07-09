import subprocess

HERMES_PATH = r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"

result = subprocess.run(
    [
        HERMES_PATH,
        "-z",
        "Create a 5 step business growth plan for a local HVAC company. Use ASCII plain text only."
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

output = result.stdout.decode("utf-8", errors="replace")
errors = result.stderr.decode("utf-8", errors="replace")

print(output)

if errors:
    print("\n[ERRORS]")
    print(errors)