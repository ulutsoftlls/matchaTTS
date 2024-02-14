from matcha.database import db


class SuccessfulQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_id = db.Column(db.Integer, nullable=False)
    audio_path = db.Column(db.String, nullable=False)

    __tablename__ = "successful_responses"
    def __repr__(self):
        return f"User('{self.name}', '{self.token}')"
