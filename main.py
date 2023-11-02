import json
import yaml
import sys
import config
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import NotNullViolation, UniqueViolation


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_USER}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
db = SQLAlchemy(app)


class AuthorizationError(BaseException):
    pass


class PermissionError(AuthorizationError):
    pass


class WrongClientType(AuthorizationError):
    pass


class ClientNotFoundError(AuthorizationError):
    pass


class Permissions(db.Model):
    __tablename__ = "permissions"

    id = db.mapped_column(db.Integer, primary_key=True)
    create = db.mapped_column(db.Boolean)
    read = db.mapped_column(db.Boolean)
    update = db.mapped_column(db.Boolean)
    delete = db.mapped_column(db.Boolean)

    def __eq__(self, other):
        if isinstance(other, Permissions):
            return (
                self.create == other.create
                and self.read == other.read
                and self.update == other.update
                and self.delete == other.delete
            )

        return NotImplemented

    def __hash__(self):
        return hash((self.create, self.read, self.update, self.delete))


class Role(db.Model):
    __tablename__ = "roles"

    name = db.mapped_column(db.String, primary_key=True)
    identities = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Identities = db.relationship("Permissions", foreign_keys=[identities])
    credits = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Credits = db.relationship("Permissions", foreign_keys=[credits])
    deposits = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Deposits = db.relationship("Permissions", foreign_keys=[deposits])
    organisations = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Organisations = db.relationship("Permissions", foreign_keys=[organisations])
    users = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Users = db.relationship("Permissions", foreign_keys=[users])
    creditaccounts = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Creditaccounts = db.relationship("Permissions", foreign_keys=[creditaccounts])
    debitaccounts = db.mapped_column(db.Integer, db.ForeignKey("permissions.id"))
    Debitaccounts = db.relationship("Permissions", foreign_keys=[debitaccounts])

    def __eq__(self, other):
        if isinstance(other, Role):
            return self.name == other.name

        return NotImplemented

    def __hash__(self):
        return hash((self.name))


class Client(db.Model):
    __tablename__ = "clients"

    id = db.mapped_column(db.Integer, primary_key=True)
    role_name = db.mapped_column(db.String, db.ForeignKey("roles.name"))
    role = db.relationship("Role")

    @db.validates("role")
    def validate_role(self, key, value):
        if not value:
            raise ValueError("Client role must not be empty")
        return value


class User(db.Model):
    __tablename__ = "users"

    client_id = db.mapped_column(db.Integer, db.ForeignKey("clients.id"))

    client = db.relationship("Client")

    first_name = db.mapped_column(db.String, primary_key=True)
    last_name = db.mapped_column(db.String, primary_key=True)
    fathers_name = db.mapped_column(db.String, primary_key=True)
    date_of_birth = db.mapped_column(db.Date, primary_key=True)

    @db.validates("fathers_name")
    def validate_fathers_name(self, key, value):
        if not value:
            raise ValueError("Users fathers_name must not be empty")
        return value

    @db.validates("first_name")
    def validate_first_name(self, key, value):
        if not value:
            raise ValueError("Users first_name must not be empty")
        return value

    @db.validates("last_name")
    def validate_last_name(self, key, value):
        if not value:
            raise ValueError("Users last_name must not be empty")
        return value

    @db.validates("date_of_birth")
    def validate_date_of_birth(self, key, value):
        return datetime.strptime(value, "%d.%M.%Y").date()

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth

    def __eq__(self, other):
        if isinstance(other, User):
            return (
                self.first_name == other.first_name
                and self.last_name == other.last_name
                and self.fathers_name == other.fathers_name
                and self.date_of_birth == other.date_of_birth
            )

        return NotImplemented

    def __hash__(self):
        return hash(
            (
                self.first_name,
                self.last_name,
                self.fathers_name,
                self.date_of_birth,
            )
        )

    def to_dict(self):
        d = self.__dict__.copy()
        del d["_sa_instance_state"]
        return d


class Organisation(db.Model):
    __tablename__ = "organisations"

    client_id = db.mapped_column(db.Integer, db.ForeignKey("clients.id"))

    client = db.relationship("Client")
    creation_date = db.mapped_column(db.Date, primary_key=True)
    unp = db.mapped_column(db.String, primary_key=True)
    name = db.mapped_column(db.String, primary_key=True)

    @db.validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Organisations name must not be empty")
        return value

    @db.validates("unp")
    def validate_unp(self, key, value):
        if not value:
            raise ValueError("Organisations unp must not be empty")
        return value

    @db.validates("creation_date")
    def validate_creation_date(self, key, value):
        return datetime.strptime(value, "%d.%M.%Y").date()

    def __eq__(self, other):
        if isinstance(other, Organisation):
            return (
                self.name == other.name
                and self.creation_date == other.creation_date
                and self.unp == other.unp
            )

        return NotImplemented

    def __hash__(self):
        return hash(
            (
                self.name,
                self.creation_date,
                self.unp,
            )
        )

    def to_dict(self):
        d = self.__dict__.copy()
        del d["_sa_instance_state"]
        d["creation_date"] = self.creation_date.strftime("%d.%m.%Y")
        return d


class App(db.Model):
    __tablename__ = "apps"

    client_id = db.mapped_column(db.Integer, db.ForeignKey("clients.id"))

    client = db.relationship("Client")

    name = db.mapped_column(db.String, primary_key=True)

    @db.validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValueError("App name must not be empty")
        return value

    def __eq__(self, other):
        if isinstance(other, App):
            return self.name == other.name

        return NotImplemented

    def __hash__(self):
        return hash((self.name))

    def to_dict(self):
        d = self.__dict__.copy()
        del d["_sa_instance_state"]
        return d


def get_client_by_id(client_id, client_type=None):
    if client_type:
        client_class = getattr(sys.modules[__name__], client_type)
        client = db.session.query(client_class).filter_by(client_id=client_id).all()
        if client:
            return client[0]
        raise ClientNotFoundError(
            f"No {client_type} found with client_id = {client_id}"
        )

    user = db.session.query(User).filter_by(client_id=client_id).all()
    if user:
        return user[0]
    app = db.session.query(App).filter_by(client_id=client_id).all()
    if app:
        return app[0]
    org = db.session.query(Organisation).filter_by(client_id=client_id).all()
    if org:
        return org[0]

    raise ClientNotFoundError(f"No Client found with client_id = {client_id}")


def get_client_id_from_header(header_name, headers):
    if header_name not in headers:
        raise ValueError(f"{header_name} header not found")

    header = headers.get(header_name)
    header = json.loads(header)

    if "client_id" not in header:
        raise ValueError(f"{header_name} header doesnt have client_id attribute")

    return header["client_id"]


def check_permission(client, entity, permission):
    client = client.client
    permissions = getattr(client.role, entity)
    if not getattr(permissions, permission):
        raise PermissionError(
            f"Client with id {client.id} does not have {entity}.{permission} permission"
        )

    return True


def check_client_type(client_type):
    if client_type not in ["users", "organisations"]:
        raise WrongClientType(
            f"Client type {client_type} is wrong. Must be one of users, organisations"
        )


def client_from_dict(client_dict, roles):
    client = {}
    client["role"] = list(filter(lambda r: r.name == client_dict["role"], roles))[0]
    if "client_id" in client_dict:
        client["id"] = client_dict["client_id"]
    client = Client(**client)
    return client


def seed_data():
    roles = db.session.query(Role).all()
    organisations = db.session.query(Organisation).all()
    users = db.session.query(User).all()
    apps = db.session.query(App).all()
    permissions = db.session.query(Permissions).all()

    with open("data/permissions.yaml", "r") as f:
        for permission in yaml.safe_load(f):
            permission = Permissions(**permission)
            if permission not in permissions:
                db.session.add(permission)
                db.session.commit()
                permissions.append(permission)

    with open("data/roles.yaml", "r") as f:
        for role_name, role_obj in yaml.safe_load(f).items():
            role = {}
            for entity, permissions_dict in role_obj.items():
                permission = Permissions(**permissions_dict)
                permission = list(filter(lambda p: p == permission, permissions))[0]

                role[entity] = permission

            role["name"] = role_name

            role = Role(**role)
            if role not in roles:
                db.session.add(role)
                db.session.commit()
                roles.append(role)

    with open("data/app.yaml", "r") as f:
        apps_data = yaml.safe_load(f)["Apps"]
        for app in apps_data:
            app["client"] = client_from_dict(app, roles)
            del app["client_id"]
            del app["role"]

            app = App(**app)
            if app not in apps:
                db.session.add(app)
                db.session.commit()
                apps.append(app)

    with open("data/users.json", "r") as f:
        json_data = json.load(f)
        users_data = json_data["Users"]
        for user in users_data:
            user["client"] = client_from_dict(user, roles)
            del user["role"]

            user["date_of_birth"] = user["date_of_birth"]
            user = User(**user)
            if user not in users:
                db.session.add(user)
                db.session.commit()
                users.append(user)

        organisations_data = json_data["Organisations"]
        for organisation in organisations_data:
            organisation["client"] = client_from_dict(organisation, roles)
            del organisation["role"]

            organisation["creation_date"] = organisation["creation_date"]
            organisation = Organisation(**organisation)
            if organisation not in organisations:
                db.session.add(organisation)
                db.session.commit()
                organisations.append(organisation)


@app.route("/api/v1/<string:client_type>/<int:client_id>", methods=["GET"])
def get_client(client_type, client_id):
    try:
        check_client_type(client_type)
        requestor_id = get_client_id_from_header("token", request.headers)
        requestor = get_client_by_id(requestor_id)
        client_type = client_type.capitalize()
        client_type_single = client_type[0:-1]
        check_permission(requestor, client_type, "read")
        client = get_client_by_id(client_id, client_type_single)
        return json.dumps(client.to_dict(), ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/v1/<string:client_type>", methods=["GET"])
def get_clients(client_type):
    try:
        check_client_type(client_type)
        requestor_id = get_client_id_from_header("token", request.headers)
        requestor = get_client_by_id(requestor_id)
        client_type = client_type.capitalize()
        client_type_single = client_type[0:-1]
        check_permission(requestor, client_type, "read")
        client_class = getattr(sys.modules[__name__], client_type_single)
        clients = db.session.query(client_class).all()
        clients = [c.to_dict() for c in clients]
        return json.dumps(clients, ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/v1/<string:client_type>", methods=["PUT"])
def create_clients(client_type):
    try:
        check_client_type(client_type)
        requestor_id = get_client_id_from_header("token", request.headers)
        requestor = get_client_by_id(requestor_id)
        client_type = client_type.capitalize()
        client_type_single = client_type[0:-1]
        check_permission(requestor, client_type, "read")
        roles = db.session.query(Role).all()
        data = request.get_json()
        if "role" not in data:
            raise ValueError(f"{client_type} must have role attribute")
        data["client"] = client_from_dict(data, roles)
        del data["role"]
        client_class = getattr(sys.modules[__name__], client_type_single)
        client = client_class(**data)
        db.session.add(client)
        db.session.commit()

        return (
            jsonify({"status": "success", "message": "User created successfully"}),
            201,
        )
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except IntegrityError as e:
        if isinstance(e.orig, NotNullViolation):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Not all client attributes are spcified",
                    }
                ),
                400,
            )
        elif isinstance(e.orig, UniqueViolation):
            return jsonify({"status": "error", "message": "Client already exists"}), 400
        return jsonify({"status": "error", "message": str(e)}), 400
    except TypeError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/v1/<string:entity>/authz/<string:permission>", methods=["GET"])
def check_authorization(entity, permission):
    try:
        requestor_id = get_client_id_from_header("token", request.headers)
        requestor = get_client_by_id(requestor_id)
        check_permission(requestor, entity.capitalize(), permission)
        return {"status": "success", "message": "Authorized"}, 200
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except AttributeError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/v1/authz/health_check", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200


with app.app_context():
    db.create_all()

    seed_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
