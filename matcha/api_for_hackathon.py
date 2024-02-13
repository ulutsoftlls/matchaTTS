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
speakers = {"1": TTS("1"), "2": TTS("2")}

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
        form = Validator(request, speakers)
        current_utc_time = datetime.utcnow()
        new_query = Query(user_id=g.user.id, text_length=0, date=current_utc_time.replace(tzinfo=pytz.utc).astimezone(kyrgyzstan_timezone))
        if form.validate():
            text = form.getText()
            speaker_id = form.getSpeaker()

            if speaker_id not in speaker_ids:
                new_query.error_message = 'Invalid speaker ID'
                new_query.status = 0
                db.session.add(new_query)
                db.session.commit()
                return jsonify({'status': 'error', 'message': 'Invalid speaker_id'}), 400

            model = speakers[speaker_id]
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
    app.run(host='0.0.0.0', port="8089")
