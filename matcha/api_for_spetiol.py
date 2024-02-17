from datetime import datetime

from flask import Flask, jsonify, request, send_file, g

from TTS import TTS
import json

from matcha.Validator import Validator
from matcha.database import db
from matcha.models.entities.Query import Query
from matcha.models.entities.SuccessfulQuery import SuccessfulQuery
from matcha.models.entities.User import User
from werkzeug.exceptions import Unauthorized
from flask_caching import Cache

import pytz
kyrgyzstan_timezone = pytz.timezone('Asia/Bishkek')

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
with open('./matcha/config.json', 'r') as config_file:
    config = json.load(config_file)
config_jwt_token = config.get('jwt_token')
speaker_ids = ['1', '2']
# speakers = {"1": TTS("1"), "2": TTS("2")}

speakers = {"4": {"1": TTS("1", config, 4), "2": TTS("2", config, 4)}}
db_config = config.get('db_conf')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config.get('user_name')}:{db_config.get('password')}@localhost:3306/{db_config.get('db_name')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)




def auth():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        raise Unauthorized('Invalid token')

    token = token[len('Bearer '):]

    # Check cache for user
    user = cache.get(token)
    if user is None:
        # If not in cache, query the database
        user = User.query.filter(User.token == token).first()
        if user is not None:
            # Cache the user for future requests
            cache.set(token, user)

    if user is None:
        raise Unauthorized('Incorrect token')

    g.user = user


@app.before_request
def before_request():
    return auth()
@app.route('/api/tts', methods=['POST'])
def tts():
    
    try:
        current_utc_time = datetime.utcnow()
        new_query = Query(user_id=g.user.id, text_length=0, date=current_utc_time.replace(tzinfo=pytz.utc).astimezone(kyrgyzstan_timezone))

        text = request.json.get('text')
        speaker_id = str(request.json.get('speaker_id'))
        model = speakers[str(g.user.device)][speaker_id]
        result = model.generate_audio(text)
        new_query.text_length = len(text)
        new_query.status = 1
        db.session.add(new_query)
        db.session.commit()
        new_response = SuccessfulQuery(query_id=new_query.id, audio_path=result)
        db.session.add(new_response)
        db.session.commit()
        return send_file(result, mimetype='audio/mpeg')
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
    app.run(host='0.0.0.0', debug=True, port="8682")
