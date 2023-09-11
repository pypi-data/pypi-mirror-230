import logging
from pprint import pprint

from gs_netsuite_api.api import CustomerAPI
from gs_netsuite_api.ns_utils import NetSuiteCredential, SearchParams

logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    # Existe d'autre methode pour avoir un NetSuiteCredential
    cred = NetSuiteCredential.from_env_file("./auth_netsuite.env")
    api = CustomerAPI(credential=cred, search_params=SearchParams(page_size=5, nb_page=2))

    data_one = api.get_one(2173028)
    pprint(data_one)
