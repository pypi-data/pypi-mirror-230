from datetime import datetime
import pandas as pd
import numpy as np

# Função para verificar datas
def check_dates(start_date, end_date):
    start_date, end_date = map(lambda x: datetime.strptime(x, "%Y-%m-%d"), (start_date, end_date))
    if start_date > end_date:
        raise ValueError("A data de início não pode ser posterior à data de término.")
    return start_date, end_date

# Função para criar um DataFrame
def create_dataframe(data):
    return pd.DataFrame(data)

# Função para obter eventos
def get_events(start_date, end_date, powerplantId, assetId):
    start_date, end_date = check_dates(start_date, end_date)
    data = [{"DataInicio": start_date, "DataFim": end_date, "NomeParque": powerplantId, "Ventoinha": assetId}]
    return create_dataframe(data)

# Função para obter dados estatísticos
def get_statistical_data(start_date, end_date,powerplantId, assetId, signalId):
    start_date, end_date = check_dates(start_date, end_date)
    date_range = pd.date_range(start=start_date, end=end_date, freq='5T').to_list()
    date_range.pop()

    # Gerar valores médios (AvgValue) para cada carimbo de hora
    avg_values = np.random.rand(len(date_range)) * 100
    data = pd.DataFrame({
        'Timestamp': date_range,
        'AvgValue': avg_values
    })
    return create_dataframe(data)

# Função para obter metadados da planta
def get_plant_metadata(powerplantId):
    data = [{"NomeParque": powerplantId}]
    return create_dataframe(data)

# Função para obter metadados do ativo
def get_asset_metadata(powerplantId, assetId):
    data = [{"NomeParque": powerplantId, "Ventoinhas": assetId}]
    return create_dataframe(data)

# Função para obter dados brutos
def get_raw_data(start_date, end_date, powerplantId, assetId, signalId):
    start_date, end_date = check_dates(start_date, end_date)
    data = [{"DataInicio": start_date, "DataFim": end_date, "NomeParque": powerplantId, "Ventoinha": assetId, "Medida": signalId}]
    return create_dataframe(data)