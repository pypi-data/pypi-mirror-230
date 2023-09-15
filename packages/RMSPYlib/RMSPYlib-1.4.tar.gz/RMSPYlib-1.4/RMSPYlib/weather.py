import requests

class RMSAPI:

    def __init__(self):
        self.token = None
        self.url_base = 'https://rmsrestapi20230313150335.azurewebsites.net/api/v1'

    def getToken(self, username, password):
        login_url = "https://rmsrestapi20230313150335.azurewebsites.net/api/v1/session/login"
        payload = {
            "username": username,
            "password": password
        }

        response = requests.get(login_url, params=payload)

        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                self.token = data["token"]
                return self.token
            else:
                return None
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None

    def login(self, username, password):
        login_url = "https://rmsrestapi20230313150335.azurewebsites.net/api/v1/session/login"
        payload = {
            "username": username,
            "password": password
        }

        response = requests.get(login_url, params=payload)

        if response.status_code == 200:
            data = response.json()
            for key, value in data.items():
                print(f"{key}: {value}")
            return None
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None

    def getStatisticalData(self, token, powerPlantId, signalId, iniDate, endDate):
        complete_url = (f"https://rmsrestapi20230313150335.azurewebsites.net/api/v1/data/"
                        f"powerplant/{powerPlantId}/signal/{signalId}/statisticaldata")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "iniDate": iniDate,
            "endDate": endDate
        }

        response = requests.get(complete_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                grouped_data = {}
                for item in data:
                    group_key = item.get("utcTimestamp", "Outros")  # Supondo que "group" seja a chave de agrupamento
                    if group_key not in grouped_data:
                        grouped_data[group_key] = []
                    grouped_data[group_key].append(item)

                # Imprimir os grupos
                for group_key, group_items in grouped_data.items():
                    print(f"Grupo: {group_key}")
                    for item in group_items:
                        for key, value in item.items():
                            print(f"{key}: {value}")
                    print()
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None

    def getPowerPlantKpiData(self, token, powerPlantId, assetId, iniDate, endDate):
        complete_url = (f"https://rmsrestapi20230313150335.azurewebsites.net/api/v1/data/powerplant/"
                        f"{powerPlantId}/kpidata/{assetId}")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "iniDate": iniDate,
            "endDate": endDate
        }
        response = requests.get(complete_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None

    def getAssetKpiData(self,token, powerPlantId, assetId, iniDate, endDate):
        complete_url = (f"https://rmsrestapi20230313150335.azurewebsites.net/api/v1/data/powerplant/"
                        f"{powerPlantId}/asset/{assetId}/kpidata")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "iniDate": iniDate,
            "endDate": endDate
        }
        response = requests.get(complete_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None


    def getEvents(self,token, powerPlantId, assetId, iniDate, endDate):
        complete_url = (f"https://rmsrestapi20230313150335.azurewebsites.net/api/v1/data/powerplant/"
                        f"{powerPlantId}/asset/{assetId}/events")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "iniDate": iniDate,
            "endDate": endDate
        }
        response = requests.get(complete_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Erro ao obter dados. Código de status: {response.status_code}")
            return None
