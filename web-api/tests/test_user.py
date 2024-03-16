from http import HTTPStatus

TEST_AUTH_KEY = "77f3d4c5411d40a9b5ef18f8e4c16be3"

def test_root_user_creation_requirement(data, client):
    data.clear()

    for user in ["not_root", "bob", "dylan"]:
        response = client.put(f"/v1/user/{user}")

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.mimetype == "application/json"
        assert response.json["type"] == "problems/root_user_not_created"

    for user in ["root", "bob", "dylan"]:
        response = client.patch(f"/v1/user/{user}", json = {"auth_key": TEST_AUTH_KEY})

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.mimetype == "application/json"
        assert response.json["type"] == "problems/root_user_not_created"

def test_root_user_creation(data, client):
    data.clear()

    response = client.put("/v1/user/root")
    assert response.status_code == HTTPStatus.CREATED
    assert response.mimetype == "application/json"
    assert "auth_key" in response.json

def test_root_user_creation_with_auth_key(data, client):
    data.clear()

    response = client.put("/v1/user/root", json = {"auth_key": TEST_AUTH_KEY})

    assert response.status_code == HTTPStatus.CREATED
    assert response.mimetype == "application/json"
    assert "auth_key" not in response.json

    response = client.get("/v1/user/root", auth = ("root", TEST_AUTH_KEY))

    assert response.status_code == HTTPStatus.OK

def test_auth_required_after_root_user_creation(client):
    response = client.put("/v1/user/root")

    for user in ["root", "bob", "dylan"]:
        for method in ["GET", "PUT", "PATCH", "DELETE"]:
            response = client.open(f"/v1/user/{user}", method = method)
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.mimetype == "application/json"
            assert response.json["type"] == "problems/unauthorized"
