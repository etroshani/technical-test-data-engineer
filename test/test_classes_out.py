import datetime
from unittest.mock import patch, MagicMock
from src.moovitamix_fastapi.classes_out import TracksOut, UsersOut, ListenHistoryOut, gender_list, genre_list
from src.moovitamix_fastapi.retrieve_data import RetrieveData
import os
import pandas as pd
import pytest


# Testing TracksOut
def test_tracks_out_generate_fake():
    track = TracksOut.generate_fake()
    assert isinstance(track.id, int)
    assert isinstance(track.name, str)
    assert isinstance(track.artist, str)
    assert isinstance(track.songwriters, str)
    assert isinstance(track.duration, str)
    assert isinstance(track.genres, str)
    assert isinstance(track.album, str)
    assert isinstance(track.created_at, datetime.datetime)
    assert isinstance(track.updated_at, datetime.datetime)

# Testing UsersOut
def test_users_out_generate_fake():
    user = UsersOut.generate_fake()
    assert isinstance(user.id, int)
    assert isinstance(user.first_name, str)
    assert isinstance(user.last_name, str)
    assert isinstance(user.email, str)
    assert user.gender in gender_list()
    assert user.favorite_genres in genre_list()
    assert isinstance(user.created_at, datetime.datetime)
    assert isinstance(user.updated_at, datetime.datetime)

# Testing ListenHistoryOut
def test_listen_history_out_generate_fake():
    history = ListenHistoryOut.generate_fake()
    assert history.user_id is None
    assert history.items is None
    assert isinstance(history.created_at, datetime.datetime)
    assert isinstance(history.updated_at, datetime.datetime)


# Fonction qui simule une réponse si le code du status est de 200 (succès)
@patch('src.moovitamix_fastapi.retrieve_data.requests')
def test_listen_history_status_code_200(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "user_id": 16973,
        "items": [42227, 40077, 45919, 68602, 12934],
        "created_at": "2024-11-22T15:07:11.257620",
        "updated_at": "2024-12-07T20:50:12.540729"
    }

    mock_requests.get.return_value = mock_response

    data = RetrieveData("http://127.0.0.1:8000")
    result = data.data_listen_history()

    # Asserts qui test les types des réponses
    assert result['user_id'] == 16973
    assert isinstance(result['created_at'], str)
    assert isinstance(result['items'], list)
    assert len(result['items']) > 0


# Fonction qui simule une réponse si le code du status est de 400 (échec)
@patch('src.moovitamix_fastapi.retrieve_data.requests')
def test_listen_history_status_code_400(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "response": "Unsuccesful Request",
    }

    mock_requests.get.return_value = mock_response

    data = RetrieveData("http://127.0.0.1:8000")
    result = data.data_listen_history()

    # Assert qui détermine si le retour est None
    assert result is None



# Fonction pour tester si la fonction retrieve_data fonctionne comme attendu
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_retrieve_data(mock_history, mock_users, mock_tracks):
    mock_tracks.return_value = {
        "items": [
            {
                "id": 26813,	
                "name": "place",	
                "artist": "Aimee Phillips",	
                "songrwriters": "Cathy Davis",	
                "duration": "49:57",	
                "genres": "up",	
                "album": "movement",	
                "created_at": "2024-03-13T02:37:54.266027",
                "updated_at": "2024-08-09T21:44:49.758256"
            }
        ]
    }
    mock_users.return_value = {
        "items": [
            {
                "id": 16973,	
                "first_name": "Christine",	
                "last_name": "Pham",	
                "email": "bdavis@example.com",	
                "gender": "Agender",	
                "favorite_genres": "Pop",	
                "created_at": "2024-10-09T10:52:19.403119",	
                "updated_at": "2025-01-23T22:44:19.190295"
            }
        ]
    }
    mock_history.return_value = {
        "items": [
            {
                "user_id": 16973,

                # Besoin d'un matching song id
                "items": [26813, 40077, 45919, 68602, 12934],
                "created_at": "2024-11-22T15:07:11.257620",
                "updated_at": "2024-12-07T20:50:12.540729"
            }
        ]
    }

    data = RetrieveData("http://127.0.0.1:8000")
    data.retrieve_data()

    assert os.path.exists('final_data.csv')

    df = pd.read_csv('final_data.csv')
    assert 'user_id' in df.columns
    assert 'artist' in df.columns
    assert 'album' in df.columns
    assert 'duration' in df.columns
    assert 'gender' in df.columns
    assert 'song_id' in df.columns
    assert 'email' in df.columns
    assert 'user_created_at' in df.columns
    assert 'history_created_at' in df.columns
    assert 'song_created_at' in df.columns
    assert len(df) > 0

    ### Acceptable de ne pas supprimer le fichier csv car on n'exécute pas les tests en parallèle
    ### Si c'était le cas, on donnerait un nouveau nom au fichier pour chaque test
    ### Et on le supprimerait à la fin du test (os.remove("filename.csv"))





# Fonction pour tester si la fonction retrieve_data gère les duplicates correctement
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_retrieve_data(mock_history, mock_users, mock_tracks):
    mock_tracks.return_value = {
        "items": [
            {
                "id": 26813,	
                "name": "place",	
                "artist": "Aimee Phillips",	
                "songrwriters": "Cathy Davis",	
                "duration": "49:57",	
                "genres": "up",	
                "album": "movement",	
                "created_at": "2024-03-13T02:37:54.266027",
                "updated_at": "2024-08-09T21:44:49.758256"
            },
            {
                "id": 26813,	
                "name": "place",	
                "artist": "Aimee Phillips",	
                "songrwriters": "Cathy Davis",	
                "duration": "49:57",	
                "genres": "up",	
                "album": "movement",	
                "created_at": "2024-03-13T02:37:54.266027",
                "updated_at": "2024-08-09T21:44:49.758256"
            }
        ]
    }
    mock_users.return_value = {
        "items": [
            {
                "id": 16973,	
                "first_name": "Christine",	
                "last_name": "Pham",	
                "email": "bdavis@example.com",	
                "gender": "Agender",	
                "favorite_genres": "Pop",	
                "created_at": "2024-10-09T10:52:19.403119",	
                "updated_at": "2025-01-23T22:44:19.190295"
            }
        ]
    }
    mock_history.return_value = {
        "items": [
            {
                "user_id": 16973,
                "items": [26813, 40077, 45919, 68602, 12934],
                "created_at": "2024-11-22T15:07:11.257620",
                "updated_at": "2024-12-07T20:50:12.540729"
            }
        ]
    }

    data = RetrieveData("http://127.0.0.1:8000")
    data.retrieve_data()

    df = pd.read_csv('final_data.csv')

    assert df.duplicated().sum() == 0



# Fonction pour tester si la fonction retrieve_data gère les types de données invalides
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_invalid_types(mock_history, mock_users, mock_tracks):
    mock_tracks.return_value = {
        "items": [
            {
                "id": "string",	
                "name": "place",	
                "artist": "Aimee Phillips",	
                "songrwriters": "Cathy Davis",	
                "duration": "49:57",	
                "genres": "up",	
                "album": "movement",	
                "created_at": "2024-03-13T02:37:54.266027",
                "updated_at": "2024-08-09T21:44:49.758256"
            }
        ]
    }
    mock_users.return_value = {
        "items": [
            {
                "id": "string",	
                "first_name": "Christine",	
                "last_name": "Pham",	
                "email": "bdavis@example.com",	
                "gender": "Agender",	
                "favorite_genres": "Pop",	
                "created_at": "2024-10-09T10:52:19.403119",	
                "updated_at": "2025-01-23T22:44:19.190295"
            }
        ]
    }
    mock_history.return_value = {
        "items": [
            {
                "user_id": "string",
                "items": [26813, 40077, 45919, 68602, 12934],
                "created_at": "2024-11-22T15:07:11.257620",
                "updated_at": "2024-12-07T20:50:12.540729"
            }
        ]
    }

    data = RetrieveData("http://127.0.0.1:8000")
    with pytest.raises(TypeError):
        data.retrieve_data()


   

#Fonction pour tester les cas ou les données tirées du API sont vides mais ont une bonne structure
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_retrieve_data_empty(mock_history, mock_users, mock_tracks):

    mock_tracks.return_value = {
        "items": [
            {
                "id": None,	
                "name": None,	
                "artist": None,	
                "songrwriters": None,	
                "duration": None,	
                "genres": None,	
                "album": None,	
                "created_at": None,
                "updated_at": None
            }
        ]
    }
    mock_users.return_value = {
        "items": [
            {
                "id": None,	
                "first_name": None,	
                "last_name": None,	
                "email": None,	
                "gender": None,	
                "favorite_genres": None,	
                "created_at": None,	
                "updated_at": None
            }
        ]
    }
    mock_history.return_value = {
        "items": [
            {
                "user_id": None,
                "items": [],
                "created_at": None,
                "updated_at": None,
            }
        ]
    }

    data = RetrieveData("http://127.0.0.1:8000")
    data.retrieve_data()

    df = pd.read_csv('final_data.csv')
    assert df.empty




# Pour tester les cas où les données tirées du API n'ont pas de clés (dictionaire vide)
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_empty_keys(mock_history, mock_users, mock_tracks):
    data = RetrieveData("http://127.0.0.1:8000")
    with pytest.raises(KeyError):
        data.retrieve_data()




#Pour tester les cas où le API échoue (aucune réponse --> échec de connexion, timeout du serveur, etc.)
@patch.object(RetrieveData, 'data_tracks')
@patch.object(RetrieveData, 'data_users')
@patch.object(RetrieveData, 'data_listen_history')
def test_API_failure(mock_history, mock_users, mock_tracks):
    data = RetrieveData("http://127.0.0.1:8000")
    with pytest.raises(Exception):
        data.retrieve_data()

        

