import requests
import pandas as pd


class RetrieveData:
    def __init__(self, url):
        self.url = url


    # On extrait les données des chansons du API
    def data_tracks(self):
        try:
            response = requests.get(f"{self.url}/tracks")
            if response.status_code == 200:
                print("tracks data retrieved successfully")
                return response.json()
            else:
                print("error retrieving tracks data")
                return None
        except requests.exceptions.Timeout:
            print("request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print("the following error ocurred: ", e)

    # On extrait les données des utilisateurs du API
    def data_users(self):
        try:
            response = requests.get(f"{self.url}/users")
            if response.status_code == 200:
                print("user data retrieved successfully")
                return response.json()
            else:
                print("error retrieving user data")
                return None
        except requests.exceptions.Timeout:
            print("request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print("the following error ocurred: ", e)

    # On extrait les données de l'historique d'écoute des utilisateurs du API
    def data_listen_history(self):
        try:
            response = requests.get(f"{self.url}/listen_history")
            if response.status_code == 200:
                print("user listen history retrieved successfully")
                return response.json()
            else:
                print("error retrieving listen history data")
                return None
        except requests.exceptions.Timeout:
            print("request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print("the following error ocurred: ", e)

    # Fonction pour vérifier si les types des données sont valides
    def data_types_check(self, data, table_name):
        expected_types = {
            'tracks': {
                'id': int,
                'name': str,
                'artist': str,
                'duration': str,
                'created_at': str,
                'updated_at': str,
            },
            'users': {
                'id': int,
                'first_name': str,
                'last_name': str,
                'email': str,
                'gender': str,
                'favorite_genres': str,
                'created_at': str,
                'updated_at': str,
            },
            'history': {
                'user_id': int,
                'items': list,
                'created_at': str,
                'updated_at': str,
            }
        }

        expected_columns = expected_types[table_name]

        # On itère à travers le dictionnaire crée afin de comparer le type de la colonne avec celui du dataframe
        for column, expected_type in expected_columns.items():
            type = data[column].dtype
            
            value = data[column].iloc[0]
            if value is None:
                continue
            
            # Pandas utilise int64 pour les colonnes integer et object pour les colonnes string
            if type == 'int64' and expected_type == int:
                type = int
            elif type == 'object' and expected_type == str:
                type = str

            if type != expected_type:
                raise TypeError(f"invalid data type")




    # Fonction pour transformer et nettoyer les données retirées avant leur stockage
    def retrieve_data(self):
        tracks = self.data_tracks()
        users = self.data_users()
        listen_history = self.data_listen_history()

        tracks_items = tracks.get("items", [])
        users_items = users.get("items", [])
        history_items = listen_history.get("items", [])

        # Fonction qui vérifie si la table contient seulement des None values
        def has_none_values(items):
            return any(value is None for item in items for value in item.values())

        if has_none_values(tracks_items):
            raise ValueError("tracks dataset contains None values")

        if has_none_values(users_items):
            raise ValueError("users dataset contains None values")

        if has_none_values(history_items):
            raise ValueError("listen_history dataset contains None values")
        
        
        """
        tracks_items =tracks.get("items")
        users_items = users.get("items")
        history_items = listen_history.get("items")


        # Si les datasets sont vides, on sort de la fonction
        if tracks_items not in tracks or users_items not in users or history_items not in listen_history or history_items.get("items") not in history_items:
            raise ValueError("datasets are empty")
        """

        
        # Transformation et normalization des données des chansons
        df_tracks = pd.DataFrame(tracks)
        df_tracks = df_tracks[['items']]
        df_tracks = pd.json_normalize(df_tracks['items'])
        
        # Transformation et normalization des données des utilisateurs
        df_users = pd.DataFrame(users)
        df_users = df_users[['items']]
        df_users = pd.json_normalize(df_users['items'])
        
        # Transformation et normalization des données de l'historique d'écoute
        df_history = pd.DataFrame(listen_history)
        df_history = df_history[['items']]
        df_history = pd.json_normalize(df_history['items'])



        # Vérification des types des données 
        self.data_types_check(df_tracks, 'tracks')
        self.data_types_check(df_users, 'users')
        self.data_types_check(df_history, 'history')


        
        # On combine les données d'utilisateurs et d'historique d'écoute sur les user id
        df_merged_id = pd.merge(df_users, df_history, left_on='id', right_on='user_id')
        
        # On divise la colonne 'items' afin de transformer les listes en rangées distinctes
        df_merged_id = df_merged_id.explode('items', ignore_index = True)

        # On combine les données précédemment combinées avec les données des chansons sur les song ids
        df_merged_final = pd.merge(df_merged_id, df_tracks, left_on = 'items', right_on = 'id')
        
        # On supprime les colonnes duplicate
        df_merged_final.drop(columns = ["user_id", "items"], inplace = True)
        
        # On renomme les colonnes afin de faciliter l'analyse
        df_merged_final.rename(columns = {"id_x" : "user_id", "id_y" : "song_id", "created_at_x" : "user_created_at", "updated_at_x" : "user_updated_at", "created_at_y" : "history_created_at", "updated_at_y" : "history_updated_at", "created_at" : "song_created_at", "updated_at" : "song_updated_at"}, inplace = True)
        
        # On supprime les rangées contenant des valeurs NaN et les duplicates
        df_merged_final = df_merged_final.dropna()
        df_merged_final = df_merged_final.drop_duplicates()
        
        # On transforme le tout en fichier CSV
        df_merged_final.to_csv('final_data.csv', index = False)




if __name__ == "__main__":
    data = RetrieveData("http://127.0.0.1:8000")
    data.retrieve_data()



