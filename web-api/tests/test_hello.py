from http import HTTPStatus

def test_hello(data, client):
    data.clear()

    root_key = client.put("/v1/user/root").json["auth_key"]
    joe_key = client.put("/v1/user/joe", auth = ("root", root_key)).json["auth_key"]

    users = ["root", "joe"]
    keys = [root_key, joe_key]

    for user, key in zip(users, keys):
        response = client.get(f"/v1/{user}/hello", auth = (user, key))
        assert response.status_code == HTTPStatus.OK
        assert response.mimetype == "application/json"
        assert response.json["message"] == f"Hello, {user}!"
