from http import HTTPStatus

def test_404_in_json(client):
    response = client.get("/this-does-not-exist")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.mimetype == "application/json"
    assert response.json["type"] == "problems/404_not_found"
