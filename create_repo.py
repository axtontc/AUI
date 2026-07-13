import os
import sys
import json
import urllib.request

token = os.environ.get("GITHUB_TOKEN")
if not token or token == "dummy_token" or token.startswith("dummy"):
    print("Token is dummy or missing!")
    sys.exit(1)

url = "https://api.github.com/user/repos"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}
data = {
    "name": "AUI",
    "description": "AOS Unified UI Controller",
    "private": False,
    "has_issues": True,
    "has_projects": False,
    "has_wiki": False
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as response:
        if response.status in [200, 201]:
            print("Successfully created repository on GitHub!")
            print(json.loads(response.read().decode('utf-8'))['html_url'])
        else:
            print(f"Failed: {response.status} {response.read().decode()}")
except Exception as e:
    print(f"Error creating repo: {e}")
    sys.exit(1)
