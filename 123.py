from flask import Flask, jsonify, request

import json

app = Flask(__name__)


@app.route('/api/v1/users/<int:client_id>', methods=['GET'])
def get_user(client_id):
    token = request.headers.get('token')
    if not token:
        return jsonify({"status": "error", "message": f"Token header not found"}), 400
    print(token)
    try:
        token_data = json.loads(token)
        if not isinstance(token_data, dict):
            return jsonify({"status": "error", "message": f"data type not Dict"}), 400
        if 'client_id' not in token_data:
            return jsonify({"status": "error", "message": f"Not key Client_id"}), 400

        return jsonify({"status": "success", 'client_id': client_id})
    except:
        return jsonify({"status": "error", "message": f"Invalid header token"}), 400


if __name__ == '__main__':
    app.run()
