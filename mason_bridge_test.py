import subprocess

BRIDGE = r"C:\Users\User\Desktop\PUTER\hermes_bridge.ps1"

prompt = "Return only this exact text: MASON_TO_HERMES_OK"

result = subprocess.run(
    [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        BRIDGE,
        "-Prompt",
        prompt
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=30
)

print("RETURN CODE:")
print(result.returncode)

print("\nSTDOUT:")
print(result.stdout)

print("\nSTDERR:")
print(result.stderr)