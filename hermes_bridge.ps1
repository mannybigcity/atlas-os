param(
    [Parameter(Mandatory=$true)]
    [string]$Prompt
)

$Hermes = "C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"

& $Hermes -z $Prompt --ignore-rules --ignore-user-config