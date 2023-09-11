from datetime import datetime
from pprint import pprint

from gs_netsuite_api.custom_records import CustomRecordAPI
from gs_netsuite_api.ns_utils import NetSuiteCredential, SearchParams

NV_GROSS_SALES_FORECAST = 1101

if __name__ == "__main__":
    # Existe d'autre methode pour avoir un NetSuiteCredential
    cred = NetSuiteCredential.from_env_file("./auth_netsuite.env")

    api = CustomRecordAPI(NV_GROSS_SALES_FORECAST, credential=cred, search_params=SearchParams(page_size=5, nb_page=2))

    data_one = api.get_since(datetime(2023, 1, 1))
    pprint(data_one)
