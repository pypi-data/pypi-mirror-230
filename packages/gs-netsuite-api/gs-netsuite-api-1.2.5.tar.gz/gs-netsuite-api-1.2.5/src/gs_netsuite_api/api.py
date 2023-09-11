import abc
import asyncio
import datetime
import logging
from functools import cached_property
from typing import Any, Callable, Coroutine, Generic, List, TypeVar

from netsuite import NetSuiteSoapApi

from .data_types import (
    InventoryAdjustment,
    InventoryAdjustmentLine,
    ItemMove,
    ItemPicking,
    ProductAvailability,
    ProductData,
    PurchaseOrderData,
    PurchaseOrderLineData,
    RecordRef,
    RelationShip,
    SaleOrderData,
    SaleOrderLineData,
)
from .ns_utils import NetSuiteCredential, SearchParams, assertSuccess, search_with_pref

_logger = logging.getLogger("netsuite-api")
RT = TypeVar("RT", bound=RecordRef)
R = TypeVar("R", bound=Any)


class GsNetSuiteApi(abc.ABC, Generic[RT]):
    credential: NetSuiteCredential
    """Les informations de connexion à netsuite"""
    default_search_params: SearchParams
    """Les parametres de recherche utilisé lors de la pagination. Peux être surchargé dans certaine methode"""

    def get_one(self, internal_id: int) -> RT:
        """
        Recupere un seul objet depuis l'id interne netsuite
        Args:
            internal_id: An id NetSuite

        Returns:
            L'objet avec l'id interne convertit dans le type de l'API
        Raises:
            ValueError: Si l'id interne ne renvoi pas de ressource
        """
        return asyncio.run(self.async_get_one(internal_id))

    @abc.abstractmethod
    async def async_get_one(self, internal_id: int) -> RT:
        """
        A utiliser via asyncio
        See Also : get_one
        """

    def get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[RT]:
        """
        Recupere les objets distant correspondant au id interne dans NetSuite.
        Si aucun id existe en distant alors une liste vide est retournée

        Args:
            internal_ids: Les ids a retrouver dans netsuite
            params: Les paramètres de recherche pour surcharger ceux par défaut définit lors de la connexion

        Returns: La liste des elements trouvé sur le serveur distant.
        """
        return asyncio.run(self.async_get_multi(internal_ids, params))

    @abc.abstractmethod
    async def async_get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[RT]:
        """
        A utiliser via asyncio
        See Also: get_multi
        """

    def get_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[RT]:
        """
        Retourne tous les objets dont la date de création se trouve apres `created_since`
        Args:
            created_since: La date de création, dont le objet sont crée depuis.
            params: Les paramètres de recherche pour surcharger ceux par défaut définit lors de la connexion
        """
        assert created_since
        return asyncio.run(self.async_get_since(created_since, params))

    @abc.abstractmethod
    async def async_get_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[RT]:
        """
        A utiliser via asyncio
        See Also: get_since
        """

    def get_all(self, params: SearchParams = None) -> List[RT]:
        """
        Retourne tous les objets de la base convertit.
        Args:
            params: Les paramètres de recherche pour surcharger ceux par défaut définit lors de la connexion
        Returns:
            La liste complete des ressources distantes
        """
        return asyncio.run(self.async_get_all(params))

    @abc.abstractmethod
    async def async_get_all(self, params: SearchParams = None) -> List[RT]:
        """
        A utiliser via asyncio
        See Also: get_all
        """

    def get_ids_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[int]:
        """
        Retourne tous les **id** dont la date de création se trouve apres `created_since`
        Args:
            created_since: La date de création, dont le objet sont crée depuis.
            params: Les paramètres de recherche pour surcharger ceux par défaut définit lors de la connexion
        """
        assert created_since
        return asyncio.run(self.async_get_ids_since(created_since, params))

    @abc.abstractmethod
    async def async_get_ids_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[int]:
        """
        A utiliser via asyncio
        See Also: get_ids_since
        """

    def get_ids(self, params: SearchParams = None) -> List[int]:
        """
        Retourne tous les id se trouvant dans netsuite pour la ressource en question.
        Args:
            params: Les paramètres de recherche pour surcharger ceux par défaut définit lors de la connexion
        Returns:
            La liste complete des ressources distantes
        """

    @abc.abstractmethod
    async def async_get_ids(self, params: SearchParams = None) -> List[int]:
        """
        A utiliser via asyncio
        See Also: get_ids
        """


class BaseGsNetSuiteApi(GsNetSuiteApi[RT], abc.ABC):
    """
    Base d'implementation de l'API Netsuite.
    Permet d'avoir à surcgharcgher les informations particulieres des objets, mais pas chaque fonction d'appel.
    """

    _netsuite_ressource_name: str = None
    """Champ a définir depuis la liste "RecordType" dans coreTypes.xsd de la wsdl"""

    netsuite_api: NetSuiteSoapApi
    """Le client pour se connecter à l'API NetSuite"""

    def __init__(self, credential: "NetSuiteCredential", search_params: SearchParams = None):
        assert self._netsuite_ressource_name
        self._credential = credential
        self.default_search_params = search_params or SearchParams(page_size=5, nb_page=1)

    @abc.abstractmethod
    def search_record_type(self, **construc_kwargs) -> Any:
        """
        Retourne Le record utilisé pour faire des recherches complexes
        Mettre `**contruct_kwargs` pour prendre en compte les prarametre de __init__
        """

    def convert_to_data(self, record) -> RT:
        """
        Convertit un Record Netsuite en une dataclass python.
        Affiche le record a convertir en cas d'erreur
        Args:
            record: Le record netsuite

        Returns: Le record convertit en class python
        Raises:
            AttributeError: Si un champ demandé n'existe pas dans record
        """
        _logger.debug(f"Convert {record} to data")
        try:
            return self._convert_to_data(record)
        except AttributeError as e:
            _logger.exception("Can't convert record to data\n%s", record, exc_info=e)
            raise e
        except TypeError as e:
            _logger.exception("Missing args to convert\n%s", record, exc_info=e)
            raise e

    @abc.abstractmethod
    def _convert_to_data(self, record) -> RT:
        """
        Convertit un Record Netsuite en une dataclass python.
        Affiche le record a convertir en cas d'erreur
        """

    @abc.abstractmethod
    def _column_search_selector(self) -> Any:
        """
        Retourne le moyen de selectionner l'internal id en fonction du type de ressource NetSuite.
        """

    @abc.abstractmethod
    def _default_criteria(self) -> Any:
        """
        Critere par default appliqué lors des recherches,
        surtout utile dans les record de type transaction pour préciser le type.
        See Also: api.py#_TransactionAPI
        Returns: Le critere de recherche par defaut.
        """

    async def _async_get_records(
        self,
        converter: Callable[[Any], Coroutine[Any, Any, R]],
        *,
        criteria: Any = None,
        params: SearchParams = None,
    ) -> R:
        """
        Fonction permetant la recherche avec pagination de ressource NetSuite.
        En plus de cela cette fonction convertit les records NetSuite grace au `converter`
        Args:
            converter: Un convertisseur de ressource netsuite en type pytho0n (Class ou type natif)
            criteria: Le critere de recherche
            params: Les parametre de pagination, utilisation de celui par defaut si non renseigné

        Returns: Une liste de ressource NetSuite convertie grace a `converter`

        """
        params = params or self.default_search_params
        criteria = criteria or self._default_criteria()

        async with self.netsuite_api as ns:
            _logger.info(f"1. Search product page [1 / {params.nb_page}]")
            response = await search_with_pref(
                ns,
                record=self.search_record_type(
                    criteria=criteria,
                    columns=self._column_search_selector(),
                ),
                searchPreference=ns.Messages.SearchPreferences(
                    bodyFieldsOnly=True,  # Je sais pas a quoi cela sert
                    returnSearchColumns=True,  # Laisser True sinon fonctionne pas
                    pageSize=params.page_size,
                    # Page size de 5 pour les test, ne pas dépasser 100 pour eviter le blomber le serveur
                ),
            )

            datas = await converter(response)  # Convert Soap Result du dataclass
            nb_pages = min(params.nb_page, response.body.searchResult.totalPages or 0)
            _logger.info(f"Get {nb_pages} pages of {params.page_size} elements")

            if nb_pages > 1:  # Si plus d'une page alors on process les autres
                for page_index in range(2, nb_pages + 1):  # Création d'une iteration en excluant la page 1
                    # Get the nextpage
                    _logger.info(f"Page [{page_index} / {nb_pages}]")
                    next_page = await ns.request(
                        "searchMoreWithId",
                        searchId=response.body.searchResult.searchId,
                        pageIndex=int(page_index),
                    )
                    # Process
                    datas.extend(await converter(next_page))

            return datas

    @abc.abstractmethod
    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        """
        Retourne le critere de recherche utilisé pour la recherche par date.
        Args:
            created_since: La date de création a utiliser dans le critere

        Returns: Le critère de recherche
        """

    @cached_property
    def netsuite_api(self) -> NetSuiteSoapApi:
        return self._credential.get_netSuite().soap_api

    def get_one(self, internal_id: int) -> RT:
        assert internal_id > 1
        return asyncio.run(self.async_get_one(internal_id))

    async def async_get_one(self, internal_id: int) -> RT:
        async with self.netsuite_api as ns:
            response = await ns.get(self._netsuite_ressource_name, internalId=internal_id)
        record = assertSuccess(response.body.readResponse, "record")
        return self.convert_to_data(record)

    def get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[RT]:
        return asyncio.run(self.async_get_multi(internal_ids, params))

    async def async_get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[RT]:
        internal_ids = sorted(list(set(internal_ids)))
        result_getList = await self.netsuite_api.getList(self._netsuite_ressource_name, internalIds=internal_ids)
        elements = assertSuccess(result_getList.body.readResponseList, "readResponse")
        result: List[RT] = []
        for item in elements:
            result.append(self.convert_to_data(assertSuccess(item, "record")))
        result.sort(key=lambda it: it.internalId)
        return result

    def get_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[RT]:
        assert created_since
        return asyncio.run(self.async_get_since(created_since, params))

    async def async_get_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[RT]:
        return await self._async_get_records(
            self._process_result_list,
            criteria=self._get_criteria_created_since(created_since),
            params=params,
        )

    def get_all(self, params: SearchParams = None) -> List[RT]:
        return asyncio.run(self.async_get_all(params))

    async def async_get_all(self, params: SearchParams = None) -> List[RT]:
        return await self._async_get_records(self._process_result_list, criteria=None, params=params)

    def get_ids_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[int]:
        assert created_since
        return asyncio.run(self.async_get_ids_since(created_since, params))

    async def async_get_ids_since(self, created_since: datetime.datetime, params: SearchParams = None) -> List[int]:
        assert created_since
        return await self._async_get_records(
            converter=self._process_result_list_ids,
            criteria=self._get_criteria_created_since(created_since),
            params=params,
        )

    def get_ids(self, params: SearchParams = None) -> List[int]:
        return asyncio.run(self.async_get_ids(params))

    async def async_get_ids(self, params: SearchParams = None) -> List[int]:
        return await self._async_get_records(self._process_result_list_ids, criteria=None, params=params)

    async def _process_result_list(self, response) -> List[RT]:
        """
        Process le resultat d'une recherche pour le convertir en une liste d'objet python

        1. Extraction des interlanId de `response`
        2. appel `async_get_multi` avec les internalId
        3. Extraction des infos

        """
        internal_ids = await self._process_result_list_ids(response)
        if not internal_ids:
            return []
        return await self.async_get_multi(internal_ids)

    async def _process_result_list_ids(self, response) -> List[int]:
        """
        Process le resultat d'une recherche pour en extraire les internalId

        1. Extraction des internalId de `response`
        """
        if not response.body.searchResult.status.isSuccess:
            raise ValueError(response.body.searchResult.status.statusDetail)

        if not response.body.searchResult.totalRecords or not response.body.searchResult.searchRowList:
            return []

        internal_ids = []
        for el in response.body.searchResult.searchRowList.searchRow:
            internal_ids.append(int(el.basic.internalId[0].searchValue.internalId))
        return sorted(list(set(internal_ids)))


class ProductAPI(BaseGsNetSuiteApi[ProductData]):
    _netsuite_ressource_name = "inventoryItem"

    async def async_get_one(self, internal_id: int) -> ProductData:
        product = await super(ProductAPI, self).async_get_one(internal_id)
        async with self.netsuite_api as ns:
            product_avalabities = await self._get_item_availability(ns, internal_ids=[internal_id])
        product.availabilities = product_avalabities
        return product

    async def _get_item_availability(
        self, current_netsuite: NetSuiteSoapApi, internal_ids: List[int]
    ) -> List[ProductAvailability]:
        product_avalabities: List[ProductAvailability] = []
        responseAvailability = await current_netsuite.getItemAvailability(internalIds=internal_ids)
        itemAvailabilityList = assertSuccess(
            responseAvailability.body.getItemAvailabilityResult, "itemAvailabilityList"
        )
        if not itemAvailabilityList:
            return product_avalabities
        for availability in itemAvailabilityList.itemAvailability:
            product_avalabities.append(
                ProductAvailability(
                    product=RecordRef.from_rec_named(availability.item),
                    location=RecordRef.from_rec_named(availability.locationId),
                    last_change_date=availability.lastQtyAvailableChange,
                    quantity_on_hand=availability.quantityOnHand,
                    quantity_on_order=availability.quantityOnOrder,
                    quantity_committed=availability.quantityCommitted,
                    quantity_back_ordered=availability.quantityBackOrdered,
                    quantity_available=availability.quantityAvailable,
                )
            )
        return product_avalabities

    async def async_get_multi(self, internal_ids: List[int], params: SearchParams = None) -> List[ProductData]:
        products: List[ProductData] = await super(ProductAPI, self).async_get_multi(internal_ids, params)
        async with self.netsuite_api as ns:
            product_avalabities = await self._get_item_availability(ns, internal_ids=internal_ids)
            product_availability_by_iid = {}
            for stock in product_avalabities:
                product_availability_by_iid.setdefault(int(stock.product.internalId), []).append(stock)
        for product in products:
            product.availabilities = product_availability_by_iid[product.internalId]
        return products

    def _convert_to_data(self, record) -> ProductData:
        """
        Convertit un resultat de recherche unique en PRoductNetSuite
        Ne s'occupe pas des champs dynamiques
        - online
        - sub_product
        - download ou check des images

        """
        product = ProductData(
            name=record.displayName,
            internalId=int(record.internalId),
            ean13=record.upcCode,
            ref=record.itemId,
            categories=[
                RecordRef.from_rec_named(node.hierarchyNode)
                for node in record.hierarchyVersionsList.inventoryItemHierarchyVersions
                if node.hierarchyNode
            ],
            qty_available=record.quantityAvailable,
            create_date=record.createdDate,
            last_write_date=record.lastModifiedDate,
            custom_fields=record.customFieldList.customField,
        )
        return product

    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        assert created_since
        return self.netsuite_api.Accounting.ItemSearch(
            basic=self.netsuite_api.Common.ItemSearchBasic(
                created=self.netsuite_api.Core.SearchDateField(searchValue=created_since, operator="after")
            )
        )

    def search_record_type(self, **construc_kwargs) -> Any:
        return self.netsuite_api.Accounting.ItemSearchAdvanced(**construc_kwargs)

    def _column_search_selector(self) -> Any:
        return self.netsuite_api.Accounting.ItemSearchRow(
            basic=self.netsuite_api.Common.ItemSearchRowBasic(
                internalId=self.netsuite_api.Core.SearchColumnSelectField(),
                # Selection du field internalId uniquement
            )
        )

    def _default_criteria(self) -> Any:
        return self.netsuite_api.Accounting.ItemSearch()


class _TransactionAPI(BaseGsNetSuiteApi[RT]):
    """
    Class interne permetant d'effectuer rapidement l'intégration des ressource de type Transaction
    Il reste uniquement `_convert_to_data` de `GsNetSuiteApi` a implementer
    """

    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        assert created_since
        return self.netsuite_api.Sales.TransactionSearch(
            basic=self.netsuite_api.Common.TransactionSearchBasic(
                dateCreated=self.netsuite_api.Core.SearchDateField(searchValue=created_since, operator="after"),
                type=self.netsuite_api.Core.SearchEnumMultiSelectField(
                    searchValue=self._netsuite_ressource_name, operator="anyOf"
                ),
            ),
        )

    def search_record_type(self, **construc_kwargs) -> Any:
        return self.netsuite_api.Sales.TransactionSearchAdvanced(**construc_kwargs)

    def _column_search_selector(self) -> Any:
        return self.netsuite_api.Sales.TransactionSearchRow(
            basic=self.netsuite_api.Common.TransactionSearchRowBasic(
                internalId=self.netsuite_api.Core.SearchColumnSelectField(),
                # Selection du field internalId uniquement
            )
        )

    def _default_criteria(self) -> Any:
        return self.netsuite_api.Sales.TransactionSearch(
            basic=self.netsuite_api.Common.TransactionSearchBasic(
                type=self.netsuite_api.Core.SearchEnumMultiSelectField(
                    searchValue=self._netsuite_ressource_name, operator="anyOf"
                ),
            )
        )


class PurchaseAPI(_TransactionAPI[PurchaseOrderData]):
    _netsuite_ressource_name = "purchaseOrder"

    def _convert_to_data(self, record) -> PurchaseOrderData:
        purchase = PurchaseOrderData(
            name=record.tranId,
            internalId=int(record.internalId),
            currency=RecordRef.from_rec_named(record.currency),
            supplier=RecordRef.from_rec_named(record.entity),
            employee=record.employee and RecordRef.from_rec_named(record.employee) or None,
            total_tax_excluded=record.subTotal,
            total_tax=record.taxTotal,
            total_tax_included=record.total,
            exchange_rate=record.exchangeRate,
            order_date=record.tranDate,
            state=record.status,
            create_date=record.createdDate,
            last_write_date=record.lastModifiedDate,
            custom_fields=record.customFieldList.customField,
        )
        for sub_el in record.itemList.item:
            pol = PurchaseOrderLineData(
                name=str(sub_el.line),
                internalId=0,
                product=RecordRef.from_rec_named(sub_el.item),
                expected_receipt_date=sub_el.expectedReceiptDate,
                amount_tax_excluded=sub_el.amount,
                amount_tax=sub_el.tax1Amt,
                amount_tax_included=sub_el.grossAmt,
                order_qty=sub_el.quantity,
                received_qty=sub_el.quantityReceived,
                on_shipments_qty=sub_el.quantityOnShipments,
                billed_qty=sub_el.quantityBilled,
                closed=sub_el.isClosed,
                custom_fields=sub_el.customFieldList.customField,
            )
            purchase.lines.append(pol)
        return purchase


class SaleAPI(_TransactionAPI[SaleOrderData]):
    _netsuite_ressource_name = "salesOrder"

    def _convert_to_data(self, record):
        sale = SaleOrderData(
            name=record.tranId,
            internalId=int(record.internalId),
            customer=RecordRef.from_rec_named(record.entity),
            currency=RecordRef.from_rec_named(record.currency),
            supplier=RecordRef.from_rec_named(record.entity),
            total_tax_excluded=record.subTotal,
            total_tax=record.taxTotal or record.tax2Total or 0,
            total_tax_included=record.total,
            order_date=record.tranDate,
            state=record.status,
            # discountRate contient en fait des montants de réduction.
            discount_amount=record.discountRate,
            shipping_cost=record.shippingCost,
            exchange_rate=record.exchangeRate,
            shipping_country=record.shippingAddress.country,
            custom_fields=record.customFieldList.customField,
        )

        for sub_el in record.itemList.item:
            sale.lines.append(
                SaleOrderLineData(
                    name=str(sub_el.line),
                    internalId=0,
                    product=RecordRef.from_rec_named(sub_el.item),
                    amount_tax_excluded=sub_el.amount,
                    amount_tax=sub_el.tax1Amt,
                    tax_rate=sub_el.taxRate1 or sub_el.taxRate2 or 0,
                    amount_tax_included=sub_el.grossAmt,
                    order_qty=sub_el.quantity,
                    billed_qty=sub_el.quantityBilled,
                    backordered_qty=sub_el.quantityBackOrdered,
                    committed_qty=sub_el.quantityCommitted,
                    on_hand_qty=sub_el.quantityOnHand,
                    closed=sub_el.isClosed,
                    custom_fields=sub_el.customFieldList and sub_el.customFieldList.customField or {},
                )
            )
        return sale


class _BaseItemStockAPI(_TransactionAPI[ItemPicking]):
    def _convert_to_data(self, record) -> ItemPicking:
        data = ItemPicking(
            name=record.tranId,
            internalId=int(record.internalId),
            create_date=record.createdDate,
            last_write_date=record.lastModifiedDate,
            date_done=record.tranDate,
            origin=RecordRef.from_rec_named(record.createdFrom),
            custom_fields={},
        )
        for sub_el in record.itemList.item:
            line = ItemMove(
                name=str(sub_el.line),
                internalId=sub_el.line,
                product=RecordRef.from_rec_named(sub_el.item),
                location=RecordRef.from_rec_named(sub_el.location),
                quantity=sub_el.quantity,
                quantity_remaining=sub_el.quantityRemaining,
                custom_fields={},
            )
            data.lines.append(line)
        return data


class ItemReceiptAPI(_BaseItemStockAPI):
    _netsuite_ressource_name = "itemReceipt"


class ItemFulFillmentAPI(_BaseItemStockAPI):
    _netsuite_ressource_name = "itemFulfillmentItem"


class InventoryAdjustmentAPI(_TransactionAPI[InventoryAdjustment]):
    _netsuite_ressource_name = "inventoryAdjustment"

    def _convert_to_data(self, record) -> InventoryAdjustment:
        data = InventoryAdjustment(
            name=record.tranId,
            internalId=int(record.internalId),
            create_date=record.createdDate,
            last_write_date=record.lastModifiedDate,
            date_done=record.tranDate,
            location=RecordRef.from_rec_named(record.location),
            adj_location=RecordRef.from_rec_named(record.adjLocation),
        )
        for sub_el in record.inventoryList.inventory:
            line = InventoryAdjustmentLine(
                name=str(sub_el.line),
                internalId=sub_el.line,
                product=RecordRef.from_rec_named(sub_el.item),
                units=RecordRef.from_rec_named(sub_el.units),
                quantity_on_hand=sub_el.quantityOnHand,
                current_value=sub_el.currentValue,
                adjust_qty_by=sub_el.adjustQtyBy,
                new_quantity=sub_el.newQuantity,
                inventory_detail=sub_el.inventoryDetail,
            )
            data.lines.append(line)
        return data


class VendorAPI(BaseGsNetSuiteApi[RelationShip]):
    _netsuite_ressource_name = "vendor"

    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        raise NotImplementedError()

    def search_record_type(self, **construc_kwargs) -> Any:
        raise NotImplementedError()

    def _column_search_selector(self) -> Any:
        raise NotImplementedError()

    def _default_criteria(self) -> Any:
        raise NotImplementedError()

    def _convert_to_data(self, record) -> RT:
        return RelationShip(
            internalId=record.internalId,
            name=record.entityId,
            company_name=record.companyName,
            email=record.email or record.altEmail,
            custom_fields=record.customFieldList.customField,
        )


class CustomerAPI(BaseGsNetSuiteApi[RelationShip]):
    _netsuite_ressource_name = "customer"

    def _get_criteria_created_since(self, created_since: datetime.datetime) -> Any:
        raise NotImplementedError()

    def search_record_type(self, **construc_kwargs) -> Any:
        raise NotImplementedError()

    def _column_search_selector(self) -> Any:
        raise NotImplementedError()

    def _default_criteria(self) -> Any:
        raise NotImplementedError()

    def _convert_to_data(self, record) -> RT:
        return RelationShip(
            internalId=record.internalId,
            name=record.entityId,
            company_name=record.companyName,
            email=record.email or record.altEmail,
            custom_fields=record.customFieldList.customField,
        )
