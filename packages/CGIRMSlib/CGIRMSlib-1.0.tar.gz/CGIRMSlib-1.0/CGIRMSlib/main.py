from datetime import datetime
import pandas as pd
import json

class PowerPlantLibrary:
    def check_dates(self, start_date, end_date):
        start_date, end_date = map(lambda x: datetime.strptime(x, "%Y-%m-%d"), (start_date, end_date))
        if start_date > end_date:
            raise ValueError("A data de início não pode ser posterior à data de término.")
        return start_date, end_date

    def create_dataframe(self, data):
        return pd.DataFrame(data)

    def conv_to_json(self, **kwargs):
        return json.dumps(kwargs)

    def get_download_link(self, data, filename):
        temp_json_file = f"temp_{filename}.json"
        with open(temp_json_file, "w") as json_file:
            json.dump(data, json_file, indent=4)
        download_link = f"<a href='{temp_json_file}' download='{filename}.json'>Clique aqui para baixar o JSON</a>"

        return download_link


    def get_events(self, start_date, end_date, powerplantId, assetId):
        start_date, end_date = self.check_dates(start_date, end_date)
        data = [{"DataInicio": start_date, "DataFim": end_date, "NomeParque": powerplantId, "Ventoinha": assetId}]
        return self.create_dataframe(data)

    def get_statistical_data(self, start_date, end_date, powerplantId, assetId, signalId):
        start_date, end_date = self.check_dates(start_date, end_date)
        data = [{"DataInicio": start_date, "DataFim": end_date, "NomeParque": powerplantId, "Ventoinha": assetId, "Medida": signalId}]
        return self.create_dataframe(data)

    def get_plant_metadata(self, powerplantId):
        data = [{"NomeParque": powerplantId}]
        return self.create_dataframe(data)

    def get_asset_metadata(self, powerplantId, assetId):
        data = [{"NomeParque": powerplantId, "Ventoinhas": assetId}]
        return self.create_dataframe(data)

    def get_raw_data(self, start_date, end_date, powerplantId, assetId, signalId):
        start_date, end_date = self.check_dates(start_date, end_date)
        data = [{"DataInicio": start_date, "DataFim": end_date, "NomeParque": powerplantId, "Ventoinha": assetId, "Medida": signalId}]
        return self.create_dataframe(data)

