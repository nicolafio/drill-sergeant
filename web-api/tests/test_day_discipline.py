def test_day_discipline(client):
    response = client.get('/2023/02/29/discipline')
    assert response.text == "1"
    assert response.status_code == 200
