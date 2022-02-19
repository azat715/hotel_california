import pytest
import json
from requests.auth import AuthBase

from hotel_california.service_layer.service.hotel import add_user, decode_token
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW
from hotel_california.adapters.repository import UserRepository

PAYLOAD = {'email': "test@email.com", "password": "12345678"}
ADMIN = {
    "name": "test_user",
    "email": "test@email.com",
    "password": "12345678",
}


class JWTAuth(AuthBase):
    """JWTAuth"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer " + self.token
        return r


@pytest.fixture()
def admin(dbsession):
    worker = SqlAlchemyUOW(repo=UserRepository, session=dbsession)

    add_user(ADMIN['name'], ADMIN['email'], ADMIN['password'], is_admin=True, workers=worker)


def test_login(admin, client, engine):
    response = client.post("/users/login", data=json.dumps(PAYLOAD))
    assert response.status_code == 200
    res = response.json()
    assert res['access']
    assert res['refresh']
    with engine.connect() as con:
        rs = con.execute("SELECT * FROM user INNER JOIN refresh_token ON refresh_token.id = user.id WHERE email = 'test@email.com'")
        for row in rs:
            assert row["value"] == res['refresh']


def get_tokens(client):
    response = client.post("/users/login", data=json.dumps(PAYLOAD))
    return response.json()


def test_create(admin, client, engine):
    tokens = get_tokens(client)
    new_user = {
            "name": "test3_user",
            "email": "test3@email.com",
            "password": "15848484646464646416416",
            "is_admin": False
        }
    response = client.post("/users", data=json.dumps(new_user), auth=JWTAuth(tokens['access']))
    assert response.status_code == 201
    with engine.connect() as con:
        rs = con.execute("SELECT * FROM user WHERE email = 'test3@email.com'")
        for row in rs:
            assert row["name"] == new_user["name"]
            assert row["email"] == new_user["email"]
            assert row["is_admin"] == new_user["is_admin"]
