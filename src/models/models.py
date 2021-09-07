from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# databse models definitions
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    # cohortID = db.Column(db.Integer, db.ForeignKey(
    #     'cohort.id'), unique=False, nullable=False)
    permissions = db.relationship('Employee', secondary = 'link')

    def __repr__(self):
        return '<Role %r>' % self.id

    def __init__(self, id, name, permissions):
        self.id = id
        self.name = name
        self.permissions = permissions

    def jsonify(self):
        data = {
            'id': self.id,
            'name': self.firstname,
            'permissions': self.surname,
        }
        return (data)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    namePretty = db.Column(db.String(300), unique=True, nullable=False)

    def __repr__(self):
        return '<Permission %r>' % self.id

    def __init__(self, id, name, namePretty):
        self.id = id
        self.name = name
        self.namePretty = namePretty

    def jsonify(self):
        data = {
            'id': self.id,
            'name': self.firstname,
            'namePretty': self.namePretty,
        }
        return (data)