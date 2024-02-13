from flask import Flask, jsonify, request, send_file, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length

from TTS import TTS
import json

from matcha.models.entities.User import User

app = Flask(__name__)

with open('./matcha/config.json', 'r') as config_file:
    config = json.load(config_file)
config_jwt_token = config.get('jwt_token')
speaker_ids = ['1', '2']
speakers = {"1": TTS("1"), "2": TTS("2")}

db_config = config.get('db_conf')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config.get('user_name')}:{db_config.get('password')}@localhost:3306/{db_config.get('db_name')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class TTSForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired(), Length(max=3000)])
    speaker_id = StringField('Speaker ID', validators=[DataRequired()])


def auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
    token = token[len('Bearer '):]
    user = User.query.filter_by(token=token).first()
    if user is None:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
    g.user = user

@app.before_request
def before_request():
    return auth()
@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        form = TTSForm(request.json)
        if form.validate():
            text = form.text.data
            speaker_id = form.speaker_id.data

            if speaker_id not in speaker_ids:
                return jsonify({'status': 'error', 'message': 'Invalid speaker_id'}), 400

            model = speakers[speaker_id]
            result = model.generate_audio(text)
            return send_file(result, mimetype='audio/mpeg')
        else:
            errors = form.errors
            return jsonify({'status': 'error', 'message': 'Validation failed', 'errors': errors}), 400
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'status': 'error', 'message': 'Error processing request'}), 500
@app.route("/")
def hello():
    return "Welcome to TTS KG Application!"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port="8089")
