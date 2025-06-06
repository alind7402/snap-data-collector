from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# GitHub Repo Config
OWNER = "yourusername"
REPO = "data-collector"
FILEPATH = "data.csv"

# Token is stored securely in the environment
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    name = data.get("name")
    value = data.get("value")

    if not name or not value:
        return jsonify({"error": "Invalid input"}), 400

    # Get current CSV content from GitHub
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILEPATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to read file"}), 500

    file_data = response.json()
    content = base64.b64decode(file_data['content']).decode()
    sha = file_data['sha']

    # Append new line
    new_line = f"{name},{value}\n"
    updated_content = content + new_line
    updated_base64 = base64.b64encode(updated_content.encode()).decode()

    # Send PUT request to update the file
    update_payload = {
        "message": f"Add entry: {name}, {value}",
        "content": updated_base64,
        "sha": sha
    }

    put_response = requests.put(url, headers=headers, json=update_payload)
    if put_response.status_code == 200:
        return jsonify({"message": "Success"})
    else:
        return jsonify({"error": "Failed to update file"}), 500

if __name__ == "__main__":
    app.run(debug=True)
