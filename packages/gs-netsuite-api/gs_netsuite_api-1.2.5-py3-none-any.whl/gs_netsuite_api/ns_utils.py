import dataclasses
import logging
import os
from typing import Any, Mapping, TypeVar

import zeep
from netsuite import Config, NetSuite, NetSuiteSoapApi, TokenAuth

_logger = logging.getLogger("netsuite-api")

__all__ = [
    "request_with_headers",
    "search_with_pref",
    "SearchParams",
    "NetSuiteCredential",
    "assertSuccess",
]


async def request_with_headers(client: NetSuiteSoapApi, service_name: str, *args, **kwargs):
    """
    Make a web service request to NetSuite

    Args:
        service_name:
            The NetSuite service to call
    Returns:
        The response from NetSuite
    """
    svc = getattr(client.service, service_name)
    headers = kwargs.pop("headers", {})
    headers.update(client.generate_passport())
    return await svc(*args, _soapheaders=headers, **kwargs)


async def search_with_pref(client: NetSuiteSoapApi, record: zeep.xsd.CompoundValue, searchPreference=None):
    if searchPreference:
        headers = {"searchPreferences": searchPreference}
    else:
        headers = None
    return await request_with_headers(client, "search", searchRecord=record, headers=headers)


@dataclasses.dataclass
class SearchParams:
    page_size: int
    nb_page: int


R = TypeVar("R", bound=Any)


@dataclasses.dataclass
class NetSuiteCredential:
    account: str
    consumer_key: str
    consumer_secret: str
    token_id: str
    token_secret: str

    @staticmethod
    def from_dict(values: Mapping[str, str]) -> "NetSuiteCredential":
        """
        Créer les informations de connexion depuis un dict python par exemple.
        Les clefs sont les attribut de la class en majuscule.
        Args:
            values: un dict avec les clefs

        Returns: Les informations de connexion, sans test de leurs validitées

        """
        return NetSuiteCredential(
            account=values["ACCOUNT"],
            consumer_key=values["CONSUMER_KEY"],
            consumer_secret=values["CONSUMER_SECRET"],
            token_id=values["TOKEN_ID"],
            token_secret=values["TOKEN_SECRET"],
        )

    @staticmethod
    def from_env() -> "NetSuiteCredential":
        """
        Utilise l'environement courant comme source de values pour `from_dict`
        """
        return NetSuiteCredential.from_dict(dict(os.environ))

    @staticmethod
    def from_env_file(file_path: str = None) -> "NetSuiteCredential":
        """
        Utilise la lib `dotenv` pour lire un fichier `file_path` ou `./auth_netsuite.env`.
        Ensuite utilise `from_dict`
        Args:
            file_path: Le path absolut ou non contenant les informations de connexion.
        """
        from dotenv import dotenv_values

        return NetSuiteCredential.from_dict(dotenv_values(file_path or "./auth_netsuite.env"))

    def get_netSuite(self) -> NetSuite:
        """
        Retourne une instance de la lit netsuite pour ensuite avec acces a l'API.
        Raises: ValueError si account n'est pas renseigné

        """
        if not self.account:
            raise ValueError("No authg token provided")

        config = Config(
            account=self.account,
            auth=TokenAuth(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                token_id=self.token_id,
                token_secret=self.token_secret,
            ),
        )

        return NetSuite(
            config,
            soap_api_options={"version": os.environ.get("SOAP_API_VERSION", "2022.2.0")},
        )


def assertSuccess(response, result_key: str):
    """
    Assert que la reponse est en succes, sinon raise
    Et retourne la valeur de la clef de resultat
    Raises: ValueError si la reponse n'est pas en succes
    """
    if not response.status.isSuccess:
        raise ValueError(response.status)
    return getattr(response, result_key)
