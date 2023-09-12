import json
import logging
import time
from enum import Enum

import requests
from pydantic import ValidationError

from .common import Method
from .entity import Ads, Ad, Payload, Keyword
from .entity import CrmCustomFields, CrmCustomField, CrmCustomFieldGroups, CrmCustomFieldGroup
from .entity import Campaigns, Campaign
from .entity import Channels, Placements
from .entity import FieldsRootEntity, FieldsEntity, RootEntity
from .entity import Keywords
from .errors import ApiLimitError, ApiInternalError
from .utils import clean_column_ids, ColumnType


class ContentType(Enum):
    application = "application/json"


def status_code_handler(response: requests.Response) -> None:
    """Status code preprocessing"""

    match response.status_code:
        case 200:
            return
        case 400 | 403:
            resp_body: dict = response.json()
            message = resp_body.get("error")
            raise ConnectionError(f"{response.status_code}:{response.text}. details: {message}")
        case 429:
            if int(response.headers['X-Ratelimit-Remaining']) == 0:
                logging.warning(f"Status code: {response.status_code}. "
                                f"Reason: {response.reason}. "
                                f"Retry after: {response.headers['Retry-After']} sec.")
                raise ApiLimitError(int(response.headers['Retry-After']), response.text)
        case 500 | 502:
            logging.warning(f"Status code: {response.status_code}. "
                            f"Reason: {response.reason}")
            raise ApiInternalError(response.text)
        case _:
            logging.warning(f" Unknown exception. "
                            f"Status code: {response.status_code}. "
                            f"Reason: {response.reason}. ")
            logging.info(response.headers)
            time.sleep(60)


class Client:
    TRY_REQUEST = 10
    REQUEST_PAUSE = 1
    FORCE_PAUSE = 600

    def __init__(self, api_key: str, crm_token: str = None, dev: bool = False) -> None:
        self.api_key = api_key
        self.crm_token = crm_token
        self.header = {'Authorization': f"Bearer {api_key}", "Content-Type": ContentType.application.value, }
        if dev:
            self.host = "https://dev.smartis.bi/api/"
        else:
            self.host = "https://my.smartis.bi/api/"

    def get_other(self, method: Method) -> []:
        response = self._prepare(method)
        status_code_handler(response)
        return response.json()[method.value.location]

    def _prepare(self, method: Method, parameters: str | None = None) -> requests.Response:
        if parameters:
            resp = requests.post(f"{self.host}{method.value.method}", headers=self.header, data=parameters)
        else:
            resp = requests.post(f"{self.host}{method.value.method}", headers=self.header)
        status_code_handler(resp)

        return resp

    def get_channels(self) -> Channels:
        response = self._prepare(Method.GET_CHANNELS)
        try:
            return Channels.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def get_placements(self) -> Placements:
        response = self._prepare(Method.GET_PLACEMENTS)
        try:
            return Placements.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def _get_entity(self, ids: list, method: Method,
                    model: type[RootEntity] | type[FieldsRootEntity]) -> RootEntity | FieldsRootEntity:
        params = {"ids": ids}
        if method in [Method.GET_CRM_CUSTOM_FIELDS, Method.GET_CRM_CUSTOM_FIELD_GROUPS]:
            params["smartis_crm_token"] = self.crm_token
        params_json = json.dumps(params)
        response = self._prepare(method, parameters=params_json)
        status_code_handler(response)
        try:
            return model.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def get_campaigns(self, campaigns_ids: list) -> list[Campaign]:
        items: RootEntity = self._get_entity(campaigns_ids, Method.GET_CAMPAIGNS, Campaigns)
        return items.items

    def get_ads(self, ads_ids: list) -> list[Ad]:
        items: RootEntity = self._get_entity(ads_ids, Method.GET_ADS, Ads)
        return items.items

    def get_keywords(self, keywords_ids: list) -> list[Keyword]:
        items: RootEntity = self._get_entity(keywords_ids, Method.GET_KEYWORDS, Keywords)
        return items.items

    def _get_fields(self, method: Method, model: type[FieldsRootEntity], fields_ids: list) -> list[FieldsEntity]:
        if self.crm_token is None:
            raise ValueError("Not found crm token")
        fields_ids = clean_column_ids(fields_ids, ColumnType.CustomField)
        return self._get_entity(fields_ids, method, model).items

    def get_crm_custom_fields(self, fields_ids: list) -> list[CrmCustomField]:
        return self._get_fields(Method.GET_CRM_CUSTOM_FIELDS, CrmCustomFields, fields_ids)

    def get_crm_custom_field_groups(self, fields_ids: list) -> list[CrmCustomFieldGroup]:
        return self._get_fields(Method.GET_CRM_CUSTOM_FIELD_GROUPS, CrmCustomFieldGroups, fields_ids)

    def get_report(self, payload: Payload, retry: int = TRY_REQUEST) -> requests.Response:
        payload_json = payload.to_json()
        try:
            time.sleep(self.REQUEST_PAUSE)
            answer = requests.post(f"{self.host}reports/getReport", headers=self.header, data=payload_json)
            status_code_handler(answer)
        except ApiLimitError as apiLimErr:
            if retry == 0:
                return self.retry_get_report(payload)
            logging.warning(f"error: {apiLimErr.message}")
            logging.info(
                f"Retry after {apiLimErr.retry_after} sec.: {self.TRY_REQUEST - retry + 1}/{self.TRY_REQUEST}")
            time.sleep(apiLimErr.retry_after)
            return self.get_report(payload, retry=retry - 1)
        except ApiInternalError as apiIntErr:
            if retry == 0:
                return self.retry_get_report(payload)
            logging.warning(f"error: {apiIntErr.message}")
            logging.info(f"Повтор запроса: {self.TRY_REQUEST - retry + 1}/{self.TRY_REQUEST}")
            return self.get_report(payload, retry=retry - 1)
        except Exception as er:
            if retry == 0:
                return self.retry_get_report(payload)
            logging.warning(f"Unknown exception. error: {er}")
            logging.info(f"Повтор запроса: {self.TRY_REQUEST - retry + 1}/{self.TRY_REQUEST}")
            return self.get_report(payload, retry=retry - 1)
        else:
            return answer

    def retry_get_report(self, payload: Payload) -> requests.Response:
        logging.warning("Количество ошибок больше заданного! Пауза 10 мин")
        time.sleep(self.FORCE_PAUSE)
        return self.get_report(payload)
