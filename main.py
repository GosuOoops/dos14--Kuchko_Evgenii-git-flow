import json
import yaml
import config
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config.PG_USER}:{config.PG_PASSWORD}@{config.PG_HOST}:{config.PG_PORT}/{config.PG_DATABASE}"
db = SQLAlchemy(app)


class AuthorizationError(BaseException):
    pass

class PermissionError(AuthorizationError):
    pass

class ClientNotFoundError(AuthorizationError):
    pass

class Permissions(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.Boolean)
    read = db.Column(db.Boolean)
    update = db.Column(db.Boolean)
    delete = db.Column(db.Boolean)


class Role(db.Model):
    __tablename__ = 'roles'
    
    name = db.Column(db.String, primary_key=True)
    identities = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Identities = db.relationship('Permissions', foreign_keys=[identities])
    credits = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Credits = db.relationship('Permissions', foreign_keys=[credits])
    deposits = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Deposits = db.relationship('Permissions', foreign_keys=[deposits])
    organisations = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Organisations = db.relationship('Permissions', foreign_keys=[organisations])
    users = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Users = db.relationship('Permissions', foreign_keys=[users])
    creditaccounts = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Creditaccounts = db.relationship('Permissions', foreign_keys=[creditaccounts])
    debitaccounts = db.Column(
      db.Integer,
      db.ForeignKey('permissions.id')
    )
    Debitaccounts = db.relationship('Permissions', foreign_keys=[debitaccounts])

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(
      db.String,
      db.ForeignKey('roles.name')
    )
    role = db.relationship('Role')
   

class User(db.Model):
    __tablename__ = 'users'

    client_id = db.Column(
      db.Integer,
      db.ForeignKey('clients.id')
    )

    client = db.relationship('Client')

    first_name = db.Column(db.String, primary_key=True)
    last_name = db.Column(db.String, primary_key=True)
    fathers_name = db.Column(db.String, primary_key=True)
    date_of_birth = db.Column(db.Integer, primary_key=True)

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth

class Organisation(db.Model):
    __tablename__ = 'organisations'

    client_id = db.Column(
      db.Integer,
      db.ForeignKey('clients.id')
    )

    client = db.relationship('Client')
    creation_date = db.Column(db.Integer, primary_key=True)
    unp = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, primary_key=True)
 
class App(db.Model):
    __tablename__ = 'apps'

    client_id = db.Column(
      db.Integer,
      db.ForeignKey('clients.id')
    )

    client = db.relationship('Client')

    name = db.Column(db.String, primary_key=True)

#
## Функция add_users использует модуль json для записи данных в файл
#def write_data(users, organisations):
#    data_to_save = {
#        'users': [],
#        'organisations': [],
#    }

#    for user in users:
#        data_to_save['users'].append(user.get_obj)
#    for organisation in organisations:
#        data_to_save['organisations'].append(organisation.get_obj)
#    with open("users-data.json", "w") as file:
#        json.dump(data_to_save, file, ensure_ascii=False)
#
#def get_client_by_id(client_id, clients):
#    for client in clients:
#        if client.client_id == client_id:
#            return client
#    raise ClientNotFoundError(f"No Client found with client_id = {client_id}")
#
#def get_client_id_from_header(header_name, headers):
#    if header_name not in headers:
#        raise ValueError(f"{header_name} header not found")
#
#    header = headers.get(header_name)
#    header = json.loads(header)
#    
#    if 'client_id' not in header:
#        raise ValueError(f"{header_name} header doesnt have client_id attribute")
#
#    return  header['client_id']
#
#def next_client_id(clients):
#    sorted_clients = sorted(clients, key=lambda x: x.client_id, reverse=True)
#    return sorted_clients[0].client_id + 1
#
#def check_permission(client, subject, permission):
#    if subject not in client.role:
#        raise PermissionError(f"Client with id {client.client_id} does not have {subject} subject in role {client.role.name}")
#    if not hasattr(client.role[subject], permission):
#        raise PermissionError(f"Client role {client.role.name} does not have such permission - {permission}")
#    if not getattr(client.role[subject], permission):
#        raise PermissionError(f"Client with id {client.client_id} does not have {subject}.{permission} permission")
#
#    return True
#

def seed_data():
  roles = []
  users = []
  organisations = []
  apps = []
  #with open('permissions.yaml', 'r') as f:
  #  permissions = yaml.safe_load(f)
  #  for permission in permissions:
  #    try:
  #      db.session.add(Permissions(**permission))
  #      db.session.commit()
  #    except IntegrityError as err:
  #      db.session.rollback()

  with open('roles.yaml', 'r') as f:
    roles_data = yaml.safe_load(f)
    for role_name, role_obj in roles_data.items():
      role = role_obj.copy()
      for entity, permissions in role_obj.items():
        p = Permissions(**permissions)
        role[entity] = p

      role['name'] = role_name
      
      role = Role(**role)
      print(role.users)
      #try:
      db.session.add(role)
      db.session.flush()
      db.session.commit()
      #except IntegrityError as err:
      #  db.session.rollback()


  
  return 
  #with open('users.json', 'r') as f:
  #    json_data = json.load(f)
  #    users_data = json_data['Users']
  #    for user in users_data:
  #        user['date_of_birth'] = int(user['date_of_birth'])
  #        user['role'] = roles[user['role']]
  #        users.append(User(**user))
  #
  #    organisations_data = json_data['Organisations']
  #    for organisation in organisations_data:
  #        organisation['role'] = roles[organisation['role']]
  #        organisations.append(Organisation(**organisation))
  #
  #with open('app.yaml', 'r') as f:
  #    apps_data = yaml.safe_load(f)['Apps']
  #    for a in apps_data:
  #        a['role'] = roles[a['role']]
  #        apps.append(App(**a))

  clients=(apps + users + organisations)

#@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
#def get_user(user_id):
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        user = get_client_by_id(user_id, users)
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#        check_permission(client,"users","read")
#        return json.dumps(user.get_obj, ensure_ascii=False)
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#        
#@app.route('/api/v1/organisations/<int:org_id>', methods=['GET'])
#def get_organisation(org_id):
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        org = get_client_by_id(org_id, organisations)
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#        check_permission(client,"organisations","read")
#        return json.dumps(org.get_obj, ensure_ascii=False)
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
#@app.route('/api/v1/users', methods=['GET'])
#def get_users():
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        user_list = [ u.get_obj for u in users]
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#        check_permission(client,"users","read")
#        return json.dumps(user_list, ensure_ascii=False)
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
#@app.route('/api/v1/organisations', methods=['GET'])
#def get_organisations():
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        org_list = [o.get_obj for o in organisations]
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#        check_permission(client,"organisations","read")
#        return json.dumps(org_list, ensure_ascii=False)
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
#@app.route('/api/v1/users', methods=['PUT'])
#def create_user():
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#
#        check_permission(client,"users","create")
#        data = request.get_json()
#        if not data or not all(key in data for key in ['role', 'first_name', 'fathers_name', 'date_of_birth', 'last_name']):
#            raise ValueError(f"Invalid organization data provided")
#        if data['role'] not in roles:
#            raise ValueError(f"Invalid role name provided")
#        data['client_id'] = next_client_id(clients)
#        data['role'] = roles[data['role']]
#        users.append(User(**data))
#        write_data(users, organisations)
#
#        return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
#@app.route('/api/v1/organisations', methods=['PUT'])
#def create_organisation():
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#
#        check_permission(client,"organisations","create")
#        data = request.get_json()
#        if not data or not all(key in data for key in ['role', 'creation_date', 'unp', 'name']):
#            raise ValueError(f"Invalid organization data provided")
#        if data['role'] not in roles:
#            raise ValueError(f"Invalid role name provided")
#        data['role'] = roles[data['role']]
#        data['client_id'] = next_client_id(clients)
#        organisations.append(Organisation(**data))
#        write_data(users, organisations)
#        return jsonify({"status": "success", "message": "Organization created successfully"}), 200
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 403
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
#@app.route('/api/v1/<string:subject>/authz/<string:permission>', methods=['GET'])
#def check_authorization(subject, permission):
#    try:
#        client_id = get_client_id_from_header('token', request.headers)
#        client = get_client_by_id(client_id, clients)
#        if not client:
#            raise ClientNotFoundError(f"No client with ID {client_id}")
#
#        check_permission(client,subject,permission)
#        return {"status": "success", "message": "Authorized"}, 200
#    except AuthorizationError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#    except ValueError as e:
#        return jsonify({"status": "error", "message": str(e)}), 400
#
@app.route('/api/v1/authz/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

with app.app_context():
    db.create_all()

    seed_data()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
