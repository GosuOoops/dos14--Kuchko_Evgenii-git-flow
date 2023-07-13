import json
import yaml
from datetime import datetime, date
from flask import Flask, request, jsonify

app = Flask(__name__)

roles = {}
users = []
organisations = []
apps = []

class AuthorizationError(BaseException):
    pass

class PermissionError(AuthorizationError):
    pass

class ClientNotFoundError(AuthorizationError):
    pass

class Permissions:
    def __init__(self, create=False, read=False, update=False, delete=False):
        self._create = create
        self._read = read
        self._update = update
        self._delete = delete
    @property
    def create(self):
        return self._create
    @property
    def read(self):
        return self._read
    @property
    def update(self):
        return self._update
    @property
    def delete(self):
        return self._delete
    @property
    def get_obj(self):
        return {
            'create': self._create,
            'read': self._read,
            'update': self._update,
            'delete': self._delete,
        }

class Role:
    def __init__(self, name, permissions_dict):
        self._name = name
        self._role = {}
        for key, value in permissions_dict.items():
            self._role[key] = Permissions(**value)

    @property
    def name(self):
        return self._name

    def __contains__(self, key):
        return key in self._role

    def __getitem__(self, key):
        return self._role[key]
    @property
    def get_obj(self):
        permissions = {}
        for key, value in self._role.items():
            permissions[key] = value.get_obj
        return {
            'name': self._name,
            'permissions': permissions
        }

class Client:
    def __init__(self, client_id, role):
        self._client_id = client_id
        self._role = role

    @property
    def client_id(self):
        return self._client_id
    @property
    def role(self):
        return self._role


class User(Client):
    def __init__(self, client_id, role, first_name, last_name, fathers_name, date_of_birth):
        super().__init__(client_id, role)
        self._first_name = first_name
        self._last_name = last_name
        self._fathers_name = fathers_name
        self._date_of_birth = date_of_birth

    @property
    def first_name(self):
        return self._first_name
    @property
    def last_name(self):
        return self._last_name
    @property
    def fathers_name(self):
        return self._fathers_name
    @property
    def date_of_birth(self):
        return self._date_of_birth
    @property
    def age(self):
        today = date.today()
        return today.year - self._date_of_birth.year
    @property
    def get_obj(self):
        return {
            'client_id': self._client_id,
            'role': self._role.get_obj,
            'first_name': self._first_name,
            'last_name': self._last_name,
            'fathers_name': self._fathers_name,
            'date_of_birth': self._date_of_birth,
        }

class Organisation(Client):
    def __init__(self, client_id, role, creation_date, unp, name):
        super().__init__(client_id, role)
        self._creation_date = creation_date
        self._unp = unp
        self._name = name
    @property
    def creation_date(self):
        return self._creation_date
    @property
    def unp(self):
        return self._unp
    @property
    def name(self):
        return self._name
    @property
    def get_obj(self):
        return {
            'client_id': self._client_id,
            'role': self._role.get_obj,
            'creation_date': self._creation_date,
            'unp': self._unp,
            'name': self._name,
        }

class App(Client):
    def __init__(self, client_id, role, name):
        super().__init__(client_id, role)
        self._name = name

    @property
    def name(self):
        return self._name

# Функция add_users использует модуль json для записи данных в файл
def write_data(users, organisations):
    data_to_save = {
        'users': [],
        'organisations': [],
    }
    for user in users:
        data_to_save['users'].append(user.get_obj)
    for organisation in organisations:
        data_to_save['organisations'].append(organisation.get_obj)
    with open("users-data.json", "w") as file:
        json.dump(data_to_save, file, ensure_ascii=False)

def get_client_by_id(client_id, clients):
    for client in clients:
        if client.client_id == client_id:
            return client
    raise ClientNotFoundError(f"No Client found with client_id = {client_id}")

def get_client_id_from_header(header_name, headers):
    if header_name not in headers:
        raise ValueError(f"{header_name} header not found")

    header = headers.get(header_name)
    header = json.loads(header)
    
    if 'client_id' not in header:
        raise ValueError(f"{header_name} header doesnt have client_id attribute")

    return  header['client_id']

def next_client_id(clients):
    sorted_clients = sorted(clients, key=lambda x: x.client_id, reverse=True)
    return sorted_clients[0].client_id + 1

def check_permission(client, subject, permission):
    if subject not in client.role:
        raise PermissionError(f"Client with id {client.client_id} does not have {subject} subject in role {client.role.name}")
    if not hasattr(client.role[subject], permission):
        raise PermissionError(f"Client role {client.role.name} does not have such permission - {permission}")
    if not getattr(client.role[subject], permission):
        raise PermissionError(f"Client with id {client.client_id} does not have {subject}.{permission} permission")

    return True

with open('roles.yaml', 'r') as f:
    roles_data = yaml.safe_load(f)
    for roleK, roleV in roles_data.items():
        roles[roleK] = Role(roleK, roleV)

with open('users.json', 'r') as f:
    json_data = json.load(f)
    users_data = json_data['Users']
    for user in users_data:
        user['date_of_birth'] = int(user['date_of_birth'])
        user['role'] = roles[user['role']]
        users.append(User(**user))

    organisations_data = json_data['Organisations']
    for organisation in organisations_data:
        organisation['role'] = roles[organisation['role']]
        organisations.append(Organisation(**organisation))

with open('app.yaml', 'r') as f:
    apps_data = yaml.safe_load(f)['Apps']
    for a in apps_data:
        a['role'] = roles[a['role']]
        apps.append(App(**a))

clients=(apps + users + organisations)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        user = get_client_by_id(user_id, users)
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")
        check_permission(client,"users","read")
        return json.dumps(user.get_obj, ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
        
@app.route('/api/v1/organisations/<int:org_id>', methods=['GET'])
def get_organisation(org_id):
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        org = get_client_by_id(org_id, organisations)
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")
        check_permission(client,"organisations","read")
        return json.dumps(org.get_obj, ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        user_list = [ u.get_obj for u in users]
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")
        check_permission(client,"users","read")
        return json.dumps(user_list, ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/organisations', methods=['GET'])
def get_organisations():
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        org_list = [o.get_obj for o in organisations]
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")
        check_permission(client,"organisations","read")
        return json.dumps(org_list, ensure_ascii=False)
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/users', methods=['PUT'])
def create_user():
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")

        check_permission(client,"users","create")
        data = request.get_json()
        if not data or not all(key in data for key in ['role', 'first_name', 'fathers_name', 'date_of_birth', 'last_name']):
            raise ValueError(f"Invalid organization data provided")
        if data['role'] not in roles:
            raise ValueError(f"Invalid role name provided")
        data['client_id'] = next_client_id(clients)
        data['role'] = roles[data['role']]
        users.append(User(**data))
        write_data(users, organisations)

        return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/organisations', methods=['PUT'])
def create_organisation():
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")

        check_permission(client,"organisations","create")
        data = request.get_json()
        if not data or not all(key in data for key in ['role', 'creation_date', 'unp', 'name']):
            raise ValueError(f"Invalid organization data provided")
        if data['role'] not in roles:
            raise ValueError(f"Invalid role name provided")
        data['role'] = roles[data['role']]
        data['client_id'] = next_client_id(clients)
        organisations.append(Organisation(**data))
        write_data(users, organisations)
        return jsonify({"status": "success", "message": "Organization created successfully"}), 200
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/<string:subject>/authz/<string:permission>', methods=['GET'])
def check_authorization(subject, permission):
    try:
        client_id = get_client_id_from_header('token', request.headers)
        client = get_client_by_id(client_id, clients)
        if not client:
            raise ClientNotFoundError(f"No client with ID {client_id}")

        check_permission(client,subject,permission)
        return {"status": "success", "message": "Authorized"}, 200
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/v1/authz/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0")
