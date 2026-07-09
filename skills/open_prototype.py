import webbrowser

def open_prototype():
    url = "http://127.0.0.1:5000/prototype/"

    webbrowser.open(url)

    return {
        "status": "opened",
        "url": url
    }