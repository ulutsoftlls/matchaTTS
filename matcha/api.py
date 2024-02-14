from datetime import datetime

from flask import Flask, jsonify, request, send_file, g

from TTS import TTS
import json

from matcha.Validator import Validator
from matcha.database import db
from matcha.models.entities.Query import Query
from matcha.models.entities.SuccessfulQuery import SuccessfulQuery
from matcha.models.entities.User import User

import pytz
kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')

app = Flask(__name__)

with open('./matcha/config.json', 'r') as config_file:
    config = json.load(config_file)
config_jwt_token = config.get('jwt_token')
speaker_ids = ['1', '2']
# speakers = {"1": TTS("1"), "2": TTS("2")}
# "2": {"1": TTS("1", 2), "2": TTS("2", 2)},
# "3": {"1": TTS("1", 3), "2": TTS("2", 3)},
speakers = {"4": {"1": TTS("1", config, 4), "2": TTS("2",config, 4)},
            "5": {"1": TTS("1", config, 5), "2": TTS("2", config, 5)},
            "6": {"1": TTS("1", config, 6), "2": TTS("2", config, 6)},
            "7": {"1": TTS("1", config, 7), "2": TTS("2", config, 7)}}
db_config = config.get('db_conf')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config.get('user_name')}:{db_config.get('password')}@localhost:3306/{db_config.get('db_name')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)




def auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
    token = token[len('Bearer '):]
    user = User.query.filter(User.token == token).first()
    if user is None:
        return jsonify({'status': 'error', 'message': 'incorrect token'}), 401
    g.user = user

@app.before_request
def before_request():
    return auth()
@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        form = Validator(request, speaker_ids)
        current_utc_time = datetime.utcnow()
        new_query = Query(user_id=g.user.id, text_length=0, date=current_utc_time.replace(tzinfo=pytz.utc).astimezone(kyrgyzstan_timezone))
        if form.validate():
            text = form.getText()
            speaker_id = form.getSpeaker()
            model = speakers[g.user.device][speaker_id]
            result = model.generate_audio(text)
            new_query.text_length = len(text)
            new_query.status = 1
            db.session.add(new_query)
            db.session.commit()
            new_response = SuccessfulQuery(query_id=new_query.id, audio_path=result)
            db.session.add(new_response)
            db.session.commit()
            return send_file(result, mimetype='audio/mpeg')
        else:
            errors = form.getErrorMessage()
            new_query.error_message = errors
            new_query.status = 0
            db.session.add(new_query)
            db.session.commit()
            return jsonify({'status': 'error', 'message': 'Validation failed', 'errors': errors}), 400
    except Exception as e:
        message = f"Error processing request: {e}"
        print(message)
        current_utc_time = datetime.utcnow()
        new_query = Query(user_id=g.user.id, text_length=0, date=current_utc_time.replace(tzinfo=pytz.utc).astimezone(kyrgyzstan_timezone), error_message=message)
        db.session.add(new_query)
        db.session.commit()
        return jsonify({'status': 'error', 'message': 'Error processing request'}), 500
@app.route("/")
def hello():
    return "Welcome to TTS KG Application!"
if __name__ == '__main__':
    app.run(host='0.0.0.0')


# from flask import Flask, jsonify, request, send_file
# from TTS import TTS
# import json
# app = Flask(__name__)
#
# with open('/mnt/ks/Works/matchaTTS/matcha/config.json', 'r') as config_file:
#     config = json.load(config_file)
# config_jwt_token = config.get('jwt_token')
# speaker_ids = ['1', '2', '3']
# speakers = {"1": TTS("1"), "2": TTS("2"), "3": TTS("3"), "4": TTS("4")}
# # Route to get the data
# @app.route('/api/tts', methods=['POST'])
# def tts():
#     text = request.json.get('text')
#     speaker_id = request.json.get('speaker_id')
#     if text:
#         if speaker_id:
#             if speaker_id in speaker_ids:
#                 model = speakers[speaker_id]
#                 result = model.generate_audio(text)
#                 print(result)
#                 return jsonify({'status': 'success', 'result': str(result)})
#             return jsonify({'status': 'error', 'result': 'speaker not found'}), 404
#         return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
#     else:
#         return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
# @app.route('/api/tts/file', methods=['POST'])
# def tts_file():
#     client_token = request.headers.get('Authorization')
#
#     if client_token and client_token.startswith('Bearer '):
#         client_token = client_token[len('Bearer '):]
#         if client_token == config_jwt_token:
#             text = request.json.get('text')
#             speaker_id = request.json.get('speaker_id')
#             if text:
#                 if speaker_id:
#                     if speaker_id in speaker_ids:
#                         model = speakers[speaker_id]
#                         result = model.generate_audio(text)
#                         return send_file(result, mimetype='audio/mpeg')
#                     return jsonify({'status': 'success', 'message': 'speaker not found'}), 404
#                 return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
#             else:
#                 return jsonify({'status': 'error', 'message': 'Missing or invalid data'}), 400
#         else:
#             return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#     else:
#         return jsonify({'status': 'error', 'message': 'Missing or invalid token in Authorization header'}), 401
# @app.route("/")
# def hello():
#     return "Welcome to TTS KG Application!"
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
