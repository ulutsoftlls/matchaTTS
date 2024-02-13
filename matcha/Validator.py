class Validator:
    error_message = ''
    text = ''
    speaker_id = ''
    def __init__(self, request, speakers):
        self.request = request
        self.speakers = speakers
    def validate(self):
        if not self.request.is_json:
            self.error_message = 'invalid fields, "text" and "speaker_id"'
            return False
        text = self.request.json.get('text')
        if not text:
            self.error_message = 'invalid text'
            return False
        if len(text) > 1000:
            self.error_message = 'max text length is 100'
            return False
        speaker = str(self.request.json.get('speaker_id'))
        if not speaker:
            self.error_message = 'invalid speaker_id'
            return False
        if speaker not in self.speakers:
            self.error_message = 'speaker id not found'
            return False
        self.text = text
        self.speaker_id = speaker
        return True
    def getText(self):
        return self.text

    def getSpeaker(self):
        return self.speaker_id

    def getErrorMessage(self):
        return self.error_message
