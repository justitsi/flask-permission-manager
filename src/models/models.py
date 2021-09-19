from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# databse models definitions
class User(db.Model):
    __tablename__ = 'permissions_user'
    id = db.Column(db.Integer, primary_key=True)
    roles = db.relationship('Role', secondary = 'permissions_role_user', backref="users", lazy="select")

    def __repr__(self):
        return '<User %r>' % self.id

    def __init__(self, id, roles):
        self.id = id
        self.roles = roles


    def jsonify(self):
        roles = self.roles
        roles_json = []

        for role in roles:
            roles_json.append ({
                "id": role.id,
                "name": role.name
        })

        data = {
            'id': self.id,
            'roles': roles_json
        }
        return (data)

# handle many-to-many relation between Role and User
users = db.Table(
    "permissions_role_user",
    db.Column("user_id", db.Integer, db.ForeignKey("permissions_user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("permissions_role.id")),
)

class Role(db.Model):
    __tablename__ = 'permissions_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    namePretty = db.Column(db.String(300), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary = 'permissions_role_permission', backref="roles", lazy="select")

    def __repr__(self):
        return '<Role %r>' % self.id

    def __init__(self, id, name, namePretty, permissions):
        self.id = id
        self.name = name
        self.namePretty = namePretty
        self.permissions = permissions

    def jsonify(self):
        permissions = self.permissions
        perms_json = []
        for perm in permissions:
            perms_json.append(Permission.jsonify(perm))

        data = {
            'id': self.id,
            'name': self.name,
            'namePretty': self.namePretty,
            'permissions': perms_json,
        }
        return (data)

# handle many-to-many relation between Permission and Role
permissions = db.Table(
    "permissions_role_permission",
    db.Column("permissions_id", db.Integer, db.ForeignKey("permissions_permission.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("permissions_role.id")),
)

class Permission(db.Model):
    __tablename__ = 'permissions_permission'
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
            'name': self.name,
            'namePretty': self.namePretty,
        }
        return (data)