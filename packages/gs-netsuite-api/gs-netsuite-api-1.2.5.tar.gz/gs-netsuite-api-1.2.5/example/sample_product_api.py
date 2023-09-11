import dataclasses
import datetime
import logging
from pprint import pprint

from gs_netsuite_api.api import ProductAPI
from gs_netsuite_api.ns_utils import NetSuiteCredential, SearchParams

logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    # Existe d'autre methode pour avoir un NetSuiteCredential
    cred = NetSuiteCredential.from_env_file("./auth_netsuite.env")
    product_api = ProductAPI(credential=cred, search_params=SearchParams(page_size=5, nb_page=2))

    all_ids = product_api.get_ids()
    print(len(all_ids), all_ids)

    data_all = product_api.get_all()
    pprint([dataclasses.asdict(p) for p in data_all])

    assert all_ids == [d.internalId for d in data_all]

    first_id = all_ids[0]
    data_one = product_api.get_one(193)
    pprint(data_one)

    multi_ids = all_ids[:3]
    data_multi = product_api.get_multi(multi_ids)
    pprint([dataclasses.asdict(p) for p in data_multi])

    ids_since = product_api.get_ids_since(datetime.datetime(2023, 1, 16))
    print(len(ids_since), ids_since)

    data_since = product_api.get_since(datetime.datetime(2023, 1, 16))
    print(len(data_since))
    pprint([dataclasses.asdict(p) for p in data_since])

    assert ids_since == [d.internalId for d in data_since]
