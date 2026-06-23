import os
from flask import Flask, request, jsonify, send_from_directory
from encode import encodeMessage, textToBinary, binaryToTrits

app = Flask(__name__, static_folder='.', static_url_path='')
APP_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    return send_from_directory(APP_DIR, 'frontend.html')


@app.route('/encode', methods=['POST'])
def encode():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON inválido'}), 400

    message = data.get('message', '')
    key = data.get('key', '')

    if not message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    if not key:
        return jsonify({'error': 'Chave vazia'}), 400

    try:
        encrypted = encodeMessage(message, key)
        binary = textToBinary(encrypted)
        trits = binaryToTrits(binary)
        return jsonify({
            'encrypted_text': encrypted,
            'binary': binary,
            'trits': trits,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
