from matcha.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    device = db.Column(db.Integer, nullable=True)
    limit = db.Column(db.Integer, nullable=True)
    has_access = db.Column(db.Boolean, nullable=False, default=False)

    __tablename__ = "users"

    def __repr__(self):
        return f"User('{self.name}', '{self.token}')"
