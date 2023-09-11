import dataclasses
import datetime
import logging
from pprint import pprint

from gs_netsuite_api.api import ItemFulFillmentAPI
from gs_netsuite_api.ns_utils import NetSuiteCredential, SearchParams

logging.root.setLevel(logging.INFO)
logging.root.addHandler(logging.StreamHandler())

# Question sur les datas

if __name__ == "__main__":
    # Existe d'autre methode pour avoir un NetSuiteCredential
    cred = NetSuiteCredential.from_env_file("./auth_netsuite.env")
    api = ItemFulFillmentAPI(credential=cred, search_params=SearchParams(page_size=5, nb_page=2))

    # api.get_one(6133226)

    all_ids = api.get_ids()
    print(len(all_ids), all_ids)

    data_all = api.get_all()
    pprint([dataclasses.asdict(p) for p in data_all])

    assert all_ids == [d.internalId for d in data_all]

    first_id = all_ids[0]
    data_one = api.get_one(first_id)
    pprint(data_one)

    multi_ids = all_ids[:3]
    data_multi = api.get_multi(multi_ids)
    pprint([dataclasses.asdict(p) for p in data_multi])

    ids_since = api.get_ids_since(datetime.datetime(2023, 1, 16))
    print(len(ids_since), ids_since)

    data_since = api.get_since(datetime.datetime(2023, 1, 16))
    print(len(data_since))
    pprint([dataclasses.asdict(p) for p in data_since])

    assert ids_since == [d.internalId for d in data_since]
