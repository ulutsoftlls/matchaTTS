from matcha.database import db


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    text_length = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.String, nullable=True)

    __tablename__ = "queries"

    def __repr__(self):
        return f"User('{self.name}', '{self.token}')"
