def test_root_works(client):
    response = client.get("/me")
    assert response.status_code == 401  # без токена — неавторизований
    assert response.json() == {"detail": "Not authenticated"}
