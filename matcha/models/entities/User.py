from matcha.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    device = db.Column(db.Integer, nullable=True)

    __tablename__ = "users"

    def __repr__(self):
        return f"User('{self.name}', '{self.token}')"
