import datetime
import logging
from typing import Any, List, Optional, Sequence

import netsuite
import zeep

from .api import RT, BaseGsNetSuiteApi
from .data_types import CustomRecord
from .ns_utils import NetSuiteCredential, SearchParams, assertSuccess

logging.root.setLevel(logging.INFO)
logging.getLogger("netsuite-api").setLevel(logging.DEBUG)
logging.root.addHandler(logging.StreamHandler())


@netsuite.soap_api.decorators.WebServiceCall(
    "body.readResponseList.readResponse",
    extract=lambda resp: [r["record"] for r in resp],
)
async def _getListCustomRecord(
    ns: netsuite.NetSuiteSoapApi,
    recordType: str,
    *,
    internalIds: Optional[Sequence[int]] = None,
    externalIds: Optional[Sequence[str]] = None,
) -> List[zeep.xsd.CompoundValue]:
    """Get a list of records"""
    if internalIds is None:
        internalIds = []
    else:
        internalIds = list(internalIds)
    if externalIds is None:
        externalIds = []
    else:
        externalIds = list(externalIds)

    if len(internalIds) + len(externalIds) == 0:
        return []

    return await ns.request(
        "getList",
        ns.Messages.GetListRequest(
            baseRef=[
                ns.Core.CustomRecordRef(
                    typeId=recordType,
                    internalId=internalId,
                )
                for internalId in internalIds
            ]
            + [
                ns.Core.RecordRef(
                    typeId=recordType,
                    externalId=externalId,
                )
                for externalId in externalIds
            ],
        ),
    )


class CustomRecordAPI(BaseGsNetSuiteApi[CustomRecord]):
    _netsuite_ressource_name = "customRecord"

    def __init__(
        self, custom_record_type_internalId: int, credential: "NetSuiteCredential", search_params: SearchParams = None
    ):
        super().__init__(credential, search_params)
        self.custom_record_type_internalId: str = str(custom_record_type_internalId)

    def search_record_type(self, **construc_kwargs) -> Any:
        return self.netsuite_api.Customization.CustomRecordSearchAdvanced(**construc_kwargs)

    def _convert_to_data(self, record) -> CustomRecord:
        """
        TODO override
        Args:
            record: une instance de CustomRecord

        """
        return record

    def get_record_ref(self):
        return self.netsuite_api.Core.RecordRef(
            internalId=self.custom_record_type_internalId,
        )

    def _column_search_selector(self) -> Any:
        return self.netsuite_api.Customization.CustomRecordSearchRow(
            basic=self.netsuite_api.Common.CustomRecordSearchRowBasic(
                recType=self.get_record_ref(),
                internalId=self.netsuite_api.Core.SearchColumnSelectField(),
                # Selection du field internalId uniquement
            )
        )

    async def async_get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[RT]:
        """
        Surcharge de la fonction pour utiliser getListCustomRecord.
        Car la lib `netsuite` ne support pas la recherche de CustomRecord

        Voir la docUsing CustomRecordRef
        https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3768988.html#bridgehead_3987720012

        Args:
            internal_ids: les ids à rechercher
            params: les paramettres de pagination

        Returns:

        """
        internal_ids = sorted(list(set(internal_ids)))
        result_getList = await _getListCustomRecord(
            self.netsuite_api, self.custom_record_type_internalId, internalIds=internal_ids
        )
        elements = assertSuccess(result_getList.body.readResponseList, "readResponse")
        result = []
        for item in elements:
            result.append(self.convert_to_data(assertSuccess(item, "record")))
        result.sort(key=lambda it: it.internalId)
        return result

    def _default_criteria(self) -> Any:
        return self.netsuite_api.Customization.CustomRecordSearch(
            basic=self.netsuite_api.Common.CustomRecordSearchBasic(
                recType=self.get_record_ref(),
            )
        )

    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        return self.netsuite_api.Customization.CustomRecordSearch(
            basic=self.netsuite_api.Common.CustomRecordSearchBasic(
                recType=self.get_record_ref(),
                created=self.netsuite_api.Core.SearchDateField(searchValue=created_since, operator="after"),
            )
        )
