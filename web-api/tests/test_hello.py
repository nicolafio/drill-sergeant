from http import HTTPStatus

def test_hello(data, client, auth_headers):
    data.clear()

    root_auth_key = client.put("/v1/user/root").json["auth_key"]
    root_auth_headers = auth_headers("root", root_auth_key)

    joe_auth_key = client.put("/v1/user/joe", headers = root_auth_headers).json["auth_key"]
    joe_auth_headers = auth_headers("joe", joe_auth_key)

    users = ["root", "joe"]
    auth_headers = [root_auth_headers, joe_auth_headers]

    for user, headers in zip(users, auth_headers):
        response = client.get(f"/v1/{user}/hello", headers = headers)
        assert response.status_code == HTTPStatus.OK
        assert response.mimetype == "application/json"
        assert response.json["message"] == f"Hello, {user}!"
