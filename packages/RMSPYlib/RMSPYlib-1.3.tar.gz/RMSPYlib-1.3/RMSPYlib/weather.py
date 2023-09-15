import requests

class ClimaAPI:
    def __init__(self, chave_api):
        self.chave_api = chave_api
        self.url_base = 'http://api.openweathermap.org/data/2.5/weather'

    def kelvin_para_celsius(self, temp_kelvin):
        return temp_kelvin - 273.15

    def obter_dados_clima_por_cidade(self, cidade):
        complete_url = f'{self.url_base}?q={cidade}&appid={self.chave_api}'
        response = requests.get(complete_url)

        if response.status_code == 200:
            data = response.json()
            temperatura_kelvin = data['main']['temp']
            temperatura_celsius = self.kelvin_para_celsius(temperatura_kelvin)
            return temperatura_celsius, data['weather'][0]['description']
        else:
            raise Exception("Falha na solicitação. Status code:", response.status_code)

    def ver_latitude_e_longitude(self, latitude, longitude):
        latitude = round(latitude, 4)
        longitude = round(longitude, 4)
        complete_url = f'{self.url_base}lat={latitude}&lon={longitude}&appid={self.chave_api}'
        response = requests.get(complete_url)

        if response.status_code == 200:
            data = response.json()
            temperatura_kelvin = data['main']['temp']
            temperatura_celsius = self.kelvin_para_celsius(temperatura_kelvin)
            print("Temperatura:", temperatura_celsius, "°C")
            print("Condição:", data['weather'][0]['description'])
        else:
            print("Falha na solicitação. Status code:", response.status_code)
