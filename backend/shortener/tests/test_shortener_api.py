from fastapi import status


def test_create_short_link(client, test_api_key):
    response = client.post(
        "/links",
        json={
            "api_key": test_api_key,
            "original_url": "https://www.example.com",
            "short_url": "test-link"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["original_url"] == "https://www.example.com"
    assert data["short_url"] == "test-link"
    assert data["is_active"] is True


def test_create_short_link_invalid_api_key(client):
    response = client.post(
        "/links",
        json={
            "api_key": "wrong-key",
            "original_url": "https://www.example.com"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_short_link_redirect(client, test_api_key):
    # First create a link
    client.post(
        "/links",
        json={
            "api_key": test_api_key,
            "original_url": "https://www.example.com",
            "short_url": "redirect-me"
        }
    )

    # Then try to access it
    response = client.get("/redirect-me", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "https://www.example.com"


def test_get_nonexistent_link(client):
    response = client.get("/nonexistent-link")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_links(client, test_api_key):
    # Create a couple of links
    client.post(
        "/links",
        json={"api_key": test_api_key,
              "original_url": "https://a.com", "short_url": "a"}
    )
    client.post(
        "/links",
        json={"api_key": test_api_key,
              "original_url": "https://b.com", "short_url": "b"}
    )

    response = client.get("/links")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_delete_link(client, test_api_key):
    # Create link
    client.post(
        "/links",
        json={"api_key": test_api_key,
              "original_url": "https://del.com", "short_url": "del"}
    )

    # Delete link
    response = client.request(
        "DELETE",
        "/links/del",
        json={"api_key": test_api_key}
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify it's deactivated (should return 404 on redirect)
    response = client.get("/del")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_generate_api_key(client):
    # Test generating first key (no old key needed if none exists?
    # Actually the logic says if not api_key_old: existing_key = session.exec... if existing_key: raise 400)
    # Since our fixture creates a key, we expect failure if we don't provide old key

    response = client.post(
        "/links/apikey",
        json={"api_key": "new-key"}
    )
    # Because one already exists from fixture
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rotate_api_key(client, test_api_key):
    new_key = "brand-new-key"
    response = client.post(
        "/links/apikey",
        json={
            "old_api_key": test_api_key,
            "api_key": new_key
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_key
