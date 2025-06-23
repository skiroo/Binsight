from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/github_images')
def github_images():
    try:
        github_api_url = "https://api.github.com/repos/AGhaziBla/Solution_Factory_Data/contents/Data/test"
        response = requests.get(github_api_url)
        response.raise_for_status()  # lève une exception si erreur HTTP

        content = response.json()
        images = []

        for item in content:
            if item['type'] == 'file' and item['name'].lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(item['download_url'])

        return jsonify(images)

    except Exception as e:
        return jsonify({"error": "Impossible de charger les images", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)