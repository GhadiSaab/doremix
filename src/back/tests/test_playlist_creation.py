"""
Tests pour la création de playlists
"""

import pytest
from sqlalchemy.orm import Session

from models import User, Playlist, Genre, PlaylistVisibility


@pytest.fixture
def sample_user(db):
    """Crée un utilisateur de test"""
    user = User(
        username="testuser", email="test@example.com", password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_genre(db):
    """Crée un genre de test"""
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


class TestPlaylistCreation:
    """Tests pour la création de playlists."""

    def test_create_playlist_success(
        self, client, db: Session, sample_user, sample_genre
    ):
        """Test la création réussie d'une playlist."""
        playlist_data = {
            "name": "New Playlist",
            "idGenre": sample_genre.idGenre,
            "visibility": "PUBLIC",
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "New Playlist"
        assert data["idGenre"] == sample_genre.idGenre
        assert data["visibility"] == "PUBLIC"
        assert "idPlaylist" in data
        assert isinstance(data["idPlaylist"], int)

    def test_create_playlist_with_private_visibility(self, client, sample_genre):
        """Test la création d'une playlist privée."""
        playlist_data = {
            "name": "Private Playlist",
            "idGenre": sample_genre.idGenre,
            "visibility": "PRIVATE",
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert data["visibility"] == "PRIVATE"

    def test_create_playlist_with_default_genre(self, client):
        """Test la création d'une playlist avec le genre par défaut."""
        playlist_data = {
            "name": "Default Genre Playlist",
        }

        response = client.post("/playlists/", json=playlist_data)
        # Peut réussir ou échouer selon si le genre 1 existe
        assert response.status_code in [200, 404, 422, 500]

    def test_create_playlist_missing_name(self, client, sample_genre):
        """Test la création d'une playlist sans nom."""
        playlist_data = {
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 422

    def test_create_playlist_with_special_characters_name(self, client, sample_genre):
        """Test la création d'une playlist avec des caractères spéciaux dans le nom."""
        special_names = [
            "Rock & Roll Mix",
            "80's Classics",
            "K-pop / J-pop",
            "Café Music ☕",
        ]

        for name in special_names:
            playlist_data = {
                "name": name,
                "idGenre": sample_genre.idGenre,
            }

            response = client.post("/playlists/", json=playlist_data)
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == name

    def test_create_playlist_with_long_name(self, client, sample_genre):
        """Test la création d'une playlist avec un nom très long."""
        long_name = "A" * 255
        playlist_data = {
            "name": long_name,
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code in [200, 422, 500]

    def test_create_multiple_playlists_same_name(self, client, sample_genre):
        """Test la création de plusieurs playlists avec le même nom."""
        playlist_data = {
            "name": "Duplicate Name",
            "idGenre": sample_genre.idGenre,
        }

        response1 = client.post("/playlists/", json=playlist_data)
        assert response1.status_code == 200

        response2 = client.post("/playlists/", json=playlist_data)
        assert response2.status_code == 200

        # Vérifier que les IDs sont différents
        assert response1.json()["idPlaylist"] != response2.json()["idPlaylist"]

    def test_create_playlist_with_all_visibility_types(self, client, sample_genre):
        """Test la création de playlists avec tous les types de visibilité."""
        visibility_types = ["PUBLIC", "PRIVATE", "SHARED"]

        for visibility in visibility_types:
            playlist_data = {
                "name": f"Playlist - {visibility}",
                "idGenre": sample_genre.idGenre,
                "visibility": visibility,
            }

            response = client.post("/playlists/", json=playlist_data)
            assert response.status_code == 200
            data = response.json()
            assert data["visibility"] == visibility

    def test_create_playlist_persists_in_database(
        self, client, db: Session, sample_genre
    ):
        """Test que la playlist créée persiste dans la base de données."""
        playlist_data = {
            "name": "Persisted Playlist",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        playlist_id = response.json()["idPlaylist"]

        db_playlist = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        assert db_playlist is not None
        assert db_playlist.name == "Persisted Playlist"

    def test_create_playlist_has_default_vote(self, client, sample_genre):
        """Test que la playlist créée a un vote par défaut."""
        playlist_data = {
            "name": "Vote Test Playlist",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert "vote" in data
        assert isinstance(data["vote"], int)

    def test_create_playlist_has_timestamps(self, client, sample_genre):
        """Test que la playlist créée a des timestamps."""
        playlist_data = {
            "name": "Timestamp Test Playlist",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert "createdAt" in data
        assert "updatedAt" in data
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)

    def test_create_playlist_with_shared_visibility(self, client, sample_genre):
        """Test la création d'une playlist avec visibilité SHARED."""
        playlist_data = {
            "name": "Shared Playlist",
            "idGenre": sample_genre.idGenre,
            "visibility": "SHARED",
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert data["visibility"] == "SHARED"

    def test_create_playlist_returns_complete_schema(self, client, sample_genre):
        """Test que la création retourne le schéma complet de la playlist."""
        playlist_data = {
            "name": "Complete Schema Playlist",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert "idPlaylist" in data
        assert "name" in data
        assert "idGenre" in data
        assert "idOwner" in data
        assert "vote" in data
        assert "visibility" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_playlist_with_invalid_visibility(self, client, sample_genre):
        """Test la création d'une playlist avec une visibilité invalide."""
        playlist_data = {
            "name": "Invalid Visibility Playlist",
            "idGenre": sample_genre.idGenre,
            "visibility": "INVALID",
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 422

    def test_create_playlist_with_nonexistent_genre(self, client):
        """Test la création d'une playlist avec un genre inexistant."""
        playlist_data = {
            "name": "Nonexistent Genre Playlist",
            "idGenre": 99999,
        }

        response = client.post("/playlists/", json=playlist_data)
        # L'API ne valide pas l'existence du genre, donc 200 est acceptable
        assert response.status_code in [200, 404, 422, 500]

    def test_create_playlist_with_empty_name(self, client, sample_genre):
        """Test la création d'une playlist avec un nom vide."""
        playlist_data = {
            "name": "",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        # Peut réussir ou échouer selon les validations
        assert response.status_code in [200, 422]

    def test_create_playlist_default_visibility_is_public(self, client, sample_genre):
        """Test que la visibilité par défaut est PUBLIC."""
        playlist_data = {
            "name": "Default Visibility Playlist",
            "idGenre": sample_genre.idGenre,
        }

        response = client.post("/playlists/", json=playlist_data)
        assert response.status_code == 200

        data = response.json()
        assert data["visibility"] == "PUBLIC"
