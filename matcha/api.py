from flask import Flask, jsonify, request, send_file
from TTS import TTS
app = Flask(__name__)

# Sample data
data = {'message': 'Hello, Flask API!'}
speaker_ids = ['1', '2', '3']
speakers = {"1": TTS("1"), "2": TTS("2"), "3": TTS("3")}
# Route to get the data
@app.route('/api/tts', methods=['POST'])
def tts():
    text = request.json.get('text')
    speaker_id = request.json.get('speaker_id')
    if text:
        if speaker_id:
            if speaker_id in speaker_ids:
                model = speakers[speaker_id]
                result = model.generate_audio(text)
                print(result)
                return jsonify({'status': 'success', 'result': str(result)})
            return jsonify({'status': 'error', 'result': 'speaker not found'}), 404
        return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
@app.route('/api/tts/file', methods=['POST'])
def tts_file():
    text = request.json.get('text')
    speaker_id = request.json.get('speaker_id')
    if text:
        if speaker_id:
            if speaker_id in speaker_ids:
                model = speakers[speaker_id]
                result = model.generate_audio(text)
                return send_file(result, mimetype='audio/mpeg')
            return jsonify({'status': 'success', 'message': 'speaker not found'}), 404
        return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=True)
